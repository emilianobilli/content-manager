from django.shortcuts import render
from django.http import HttpResponse
import httplib2
import urlparse

# Create your views here.
from models import Video
from models import Profile
from models import Config
from models import Customer
from models import Token

from django.utils import timezone

from datetime import datetime
from datetime import timedelta

from root_m3u8 import M3U8Playlist
from gatra_tpp import gatra_tpp

import tbx
import json
import md5
import time

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


def CreateToken (house_id):
    
    try:
	video = Video.objects.get(house_id=house_id)
        token = Token()
        token.expiration = datetime.now() + timedelta(0,7200)
        m = md5.md5()
        s = str(time.time())
        m.update(s + house_id)
        token.token = m.hexdigest()
        token.video = video
        token.save()
        return token.token 
    except:
	return ''


#
# Checkea los permisos de acuerdo a la configuracion del IDP
# 
def CheckAuthIdp ( tbxDevice, idp ):
    
    if idp.access_type == 'full':
	ret = tbxDevice.hasAccessTo('urn:tve:hotgo')
	access = json.loads(ret)
	if access['access']:
	    return 'full_access'
	else:
	    return 'none'

    elif idp.access_type == 'full_payment':
	ret = tbxDevice.hasAccessTo('urn:tve:hotgo')
	access = json.loads(ret)

	if access['access']:
	    return 'full_access'
	else:
	    ret = tbxDevice.hasAccessTo('urn:tve:hotgo_ott')
	    access = json.loads(ret)
	    if access['access']:
		return 'payment'
	    else:
		return 'none'

    elif idp.access_type == 'payment':
	ret = tbxDevice.hasAccessTo('urn:tve:hotgo_ott')
	access = json.loads(ret)
	if access['access']:
	    return 'payment'
	else:
	    return 'none'

    return 'none'


#
# Esta funcion retorna el archivo de manifest M3U8
#
def vm_GetManifest(device, info ,idp, house_id, conf):

    access = CheckAuthIdp(device,idp)
    if access != 'none':
        cdn_url      = build_cdn_url(house_id)
	response     = build_M3U8(house_id, cdn_url)
        status       = http_REQUEST_OK
	content_type = 'application/x-mpegURL'
    else:
	response     = json.dumps({'error': 'The Customer Have Not Autorization to View this Content'})
	status       = http_UNAUTHORIZED
	content_type = 'application/json'

    if conf.gatra_enabled:
	gatra_tpp(conf.gatra_url,info,access, house_id)

    return HttpResponse(response, status=status,content_type=content_type)



def vm_GetManifestByToken (request, token):
    try:
	t = Token.objects.get(token=token)
	if t.expiration < timezone.now():
	    t.delete()
	    return HttpResponse(json.dumps({'error': 'Expired Token'}), status=http_UNAUTHORIZED, content_type='application/json')
	cdn_url      = build_cdn_url(t.video.house_id)
	response     = build_M3U8(t.video.house_id, cdn_url)
        status       = http_REQUEST_OK
	content_type = 'application/x-mpegURL'
	return HttpResponse(response, status=status,content_type=content_type)
    except:
	return HttpResponse(json.dumps({'error': 'Invalid Token'}), status=http_UNAUTHORIZED, content_type='application/json')


def vm_GetUrl(device, info, idp, house_id, conf):

    for t in Token.objects.all():
        if t.expiration < timezone.now():
	    t.delete()

    content_type = 'application/json'

    access = CheckAuthIdp(device,idp)
    if access != 'none':
	token        = CreateToken(house_id)
	if token == '':
	    response = json.dumps({ 'error': 'Internal Server Error'})
	    status   = 500
	else:
	    response = json.dumps({ 'url': '%s/%s/' % (conf.tokenurl, token), 'expiration': 7200 })
	    status   = http_REQUEST_OK
    else:
	response     = json.dumps({'error': 'The Customer Have Not Autorization to View this Content'})
	status       = http_UNAUTHORIZED

    if conf.gatra_enabled and status != 500:
	gatra_tpp(conf.gatra_url,info,access, house_id)

    return HttpResponse(response, status=status,content_type=content_type)


def vm_PostRoot(request):

    if request.method != 'POST':
        return HttpResponse(json.dumps({ 'error': 'Method Not Allowed' }), status=http_NOT_ALLOWED)

    try:
        jsonData = json.loads(request.body)
    except:
        return HttpResponse(json.dumps({ 'error': 'Could Not Load Json' }), status=http_BAD_REQUEST)

    if ( 'api_key'            in jsonData.keys() and
	 'toolbox_user_token' in jsonData.keys() and
	 'house_id'	      in jsonData.keys()):

	# Si la media no existe
	try:
	    video = Video.objects.get(house_id=jsonData['house_id'])
	except:
	    status = http_NOT_FOUND
	    return HttpResponse(json.dumps({ 'error': 'Media: %s Not Found' % jsonData['house_id']}), status=status,content_type='application/json')

	conf = Config.objects.get(enabled=True)

	device = tbx.Device(conf.tbx_api_key,jsonData['toolbox_user_token'])
	# Info para gatra
	ret    = device.getInfo()
	if ret is None:
	    status = http_UNAUTHORIZED
	    return HttpResponse(json.dumps({ 'error': 'Unable to Find Device: %s' % jsonData['toolbox_user_token']}), status=status,content_type='application/json')

	tbx_info = ret
	info     = json.loads(ret)

	# Traigo el cableoperador por api_key
	try:
	    idp = Customer.objects.get(api_key=jsonData['api_key'])
	except:
	    status = http_UNAUTHORIZED
	    return HttpResponse(json.dumps({ 'error': 'Api key Is Invalid' }), status=status, content_type='application/json')

	if idp.idp_code != info['customer']['idp']['code']:
	    status = http_BAD_REQUEST
	    return HttpResponse(json.dumps({ 'error': 'Api key and Token Not Match' }), status=status, content_type='application/json')

	return vm_GetUrl(device, info ,idp, jsonData['house_id'], conf)
    else:
	return HttpResponse(json.dumps({ 'error': 'Incomplete Json' }), status=http_BAD_REQUEST, content_type='application/json')


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


	return vm_GetManifest(device, info ,idp, house_id, conf)
    else:
	status = http_BAD_REQUEST
	return HttpResponse(json.dumps({ 'error': 'Bad Request, End Point Does not Exist' }), status=status,content_type='application/json')









