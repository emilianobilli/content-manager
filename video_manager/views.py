from django.shortcuts import render
from django.http import HttpResponse
import httplib2
import urlparse

# Create your views here.
from models import Video
from models import Profile
from models import Config
from models import Customer

from root_m3u8 import M3U8Playlist
from gatra_tpp import gatra_tpp
import tbx
import json

http_POST_OK      = 201
http_REQUEST_OK   = 200
http_NOT_FOUND    = 404
http_BAD_REQUEST  = 400
http_NOT_ALLOWED  = 405
http_UNAUTHORIZED = 401

def build_cdn_url(house_id):
    conf = Config.objects.get(enabled=True)
    return conf.cdnurl + '%s/hls/' % house_id


def save_M3U8(house_id, m3u8):
    try:
        video = Video.objects.get(house_id=house_id)
        return False
    except:
        video = Video()
        video.house_id = house_id
        video.save()

    for f in m3u8.files:
        profile = Profile()
        profile.video = video
        profile.bandwidth  = f['bandwidth']
        profile.average    = f['average']
        profile.codecs     = f['codecs']
        profile.resolution = f['resolution']
        profile.filename   = f['filename']
        profile.save()

    return True


def build_M3U8(house_id, cdnurl = ''):
    try:
        video = Video.objects.get(house_id=house_id)
    except:
        return ''

    profiles = Profile.objects.filter(video=video)

    m3u8 = M3U8Playlist()
    m3u8.version = 3
    for p in profiles:
        m3u8.addfile(p.filename,p.bandwidth,p.average,p.codecs,p.resolution)

    return m3u8.toString(cdnurl)


def vm_Crossdomain(request):
    # Si el request no es GET
    if request.method != 'GET':
	status = http_BAD_REQUEST
	return HttpResponse('', status=status)

    status = http_REQUEST_OK
    return HttpResponse('<?xml version="1.0"?><!DOCTYPE cross-domain-policy SYSTEM "http://www.macromedia.com/xml/dtds/cross-domain-policy.dtd"><cross-domain-policy><allow-access-from domain="*"/></cross-domain-policy>', 
		        status=status)


def vm_PostVideo(request):
    
    allowed_methods = ['POST', 'OPTIONS']

    if request.method == 'OPTIONS':
        response = HttpResponse('', status=http_REQUEST_OK)
        response['Allow'] = ', '.join(allowed_methods)
        return response

    if request.method != 'POST':
        return HttpResponse('', status=http_NOT_ALLOWED)
    try:
        jsonData = json.loads(request.body)
    except:
        return HttpResponse('Could not load json', status=http_BAD_REQUEST)


    method = 'GET'
    h = httplib2.Http()

    root = jsonData['root']

    house_id, ext = root.split('.')

    cdn_url = build_cdn_url(house_id)
    uri = urlparse.urlparse(cdn_url + '/' + root)

    try:
        response, content = h.request(uri.geturl(),method,'')
    except socket.error as err:
        raise socket.error

    m3u8 = M3U8Playlist()
    m3u8.fromString(content)
    save_M3U8(house_id, m3u8)

    return HttpResponse('', status=http_POST_OK)


def vm_GetRoot(request, api_key, token_type, token, house_id):

    # Si el request no es GET
    if request.method != 'GET':
	status = http_NOT_ALLOWED
	return HttpResponse(json.dumps({ 'error': 'Method Not Allowed' }), status=status,content_type='application/json')

    # Si el token no es valido
    if token_type != 'toolbox_user_token' and token_type != 'customer_id':
	status = http_BAD_REQUEST
	return HttpResponse(json.dumps({ 'error': 'Ivalid Auth Type' }), status=status,content_type='application/json')

    # Si la media no existe
    try:
	video = Video.objects.get(house_id=house_id)
    except:
	status = http_NOT_FOUND
	return HttpResponse(json.dumps({ 'error': 'Media: %s Not Found' % house_id}), status=status,content_type='application/json')

    conf = Config.objects.get(enabled=True)

    if token_type == 'toolbox_user_token':
	device = tbx.Device(conf.tbx_api_key,token)
	# Info para gatra
	ret    = device.getInfo()
	if ret is None:
	    status = http_UNAUTHORIZED
	    return HttpResponse(json.dumps({ 'error': 'Unable to Find Device: %s' % token}), status=status,content_type='application/json')

	tbx_info = ret
	info     = json.loads(ret)

	# Traigo el cableoperador por api_key
	try:
	    idp = Customer.objects.get(api_key=api_key)
	except:
	    status = http_UNAUTHORIZED
	    return HttpResponse(json.dumps({ 'error': 'Api key Is Invalid' }), status=status, content_type='application/json')

	if idp.idp_code != info['customer']['idp']['code']:
	    status = http_BAD_REQUEST
	    return HttpResponse(json.dumps({ 'error': 'Api key and Token Not Match' }), status=status, content_type='application/json')

	# Chequeo los permisos
	if idp.access_type == 'full':
	    ret = device.hasAccessTo('urn:tve:hotgo')
	    if ret is not None:
		access = json.loads(ret)
	    else:
		status = http_NOT_FOUND
		return HttpResponse(json.dumps({'error': 'Unable to Connect with TBX'}), status=status, content_type='application/json')

	    if access['access']:
		cdn_url  = build_cdn_url(house_id)
		response = build_M3U8(house_id, cdn_url)
		status   = http_REQUEST_OK  

		if conf.gatra_enabled:
		    gatra_tpp(conf.gatra_url, tbx_info, 'full_access', house_id)
		return HttpResponse(response, status=status,content_type='application/x-mpegURL')
	    else:
		status = http_UNAUTHORIZED

		if conf.gatra_enabled:
		    gatra_tpp(conf.gatra_url, tbx_info, 'none', house_id)
		return HttpResponse(json.dumps({'error': 'The Customer Have Not Autorization to View this Content'}), status=status, content_type='application/json')

	elif idp.access_type == 'full_payment':
	    ret = device.hasAccessTo('urn:tve:hotgo')
	    if ret is not None:
		access = json.loads(ret)
	    else:
		status = http_NOT_FOUND
		return HttpResponse(json.dumps({'error': 'Unable to Connect with TBX'}), status=status, content_type='application/json')

	    if access['access']:
		cdn_url  = build_cdn_url(house_id)
		response = build_M3U8(house_id, cdn_url)
		status   = http_REQUEST_OK  
		
		if conf.gatra_enabled:
		    gatra_tpp(conf.gatra_url, tbx_info,'full_access', house_id)
		return HttpResponse(response, status=status,content_type='application/x-mpegURL')
	    else:
		ret = device.hasAccessTo('urn:tve:hotgo_ott')
		if ret is not None:
		    access = json.loads(ret)
		else:
		    status = http_NOT_FOUND
		    return HttpResponse(json.dumps({'error': 'Unable to Connect with TBX'}), status=status, content_type='application/json')

		if access['access']:
		    cdn_url  = build_cdn_url(house_id)
		    response = build_M3U8(house_id, cdn_url)
		    status   = http_REQUEST_OK  

		    if conf.gatra_enabled:
			gatra_tpp(conf.gatra_url, tbx_info, 'payment', house_id)
		    return HttpResponse(response, status=status,content_type='application/x-mpegURL')
		else:
		    if conf.gatra_enabled:
			gatra_tpp(conf.gatra_url, ret, 'none', house_id)
		    status = http_UNAUTHORIZED
		    return HttpResponse(json.dumps({'error': 'The Customer Have Not Autorization to View this Content'}), status=status, content_type='application/json')


	elif idp.access_type == 'payment':
	    ret = device.hasAccessTo('urn:tve:hotgo_ott')
	    if ret is not None:
		access = json.loads(ret)
	    else:
		status = http_NOT_FOUND
		return HttpResponse(json.dumps({'error': 'Unable to Connect with TBX'}), status=status, content_type='application/json')

	    if access['access']:
		cdn_url  = build_cdn_url(house_id)
		response = build_M3U8(house_id, cdn_url)
		status   = http_REQUEST_OK  
		if conf.gatra_enabled:
		    gatra_tpp(conf.gatra_url, tbx_info, 'payment', house_id)
		return HttpResponse(response, status=status,content_type='application/x-mpegURL')
	    else:
		status = http_UNAUTHORIZED
		if conf.gatra_enabled:
		    gatra_tpp(conf.gatra_url, tbx_info, 'none', house_id)
		return HttpResponse(json.dumps({'error': 'The Customer Have Not Autorization to View this Content'}), status=status, content_type='application/json')


