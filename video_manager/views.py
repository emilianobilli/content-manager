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
from models import CdnSecret

from django.utils import timezone

from datetime import datetime
from datetime import timedelta

from m3u8 import M3U8Playlist
from m3u8 import M3U8Rendition
from m3u8 import get_hls_manifest
from m3u8 import dtime
from gatra_tpp import gatra_tpp

from Utils import save_manifest_in_model
from Utils import build_root_manifest
from Utils import build_rendition_manifest

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

def getcdnbase ():
    conf = Config.objects.get(enabled=True)
    return conf.cdnurl

def getpath (house_id):
    return '%s/hls' % house_id

def usesecret():
    conf = Config.objects.get(enabled=True)
    return conf.secret


def build_cdn_url(house_id):
    conf = Config.objects.get(enabled=True)
    return conf.cdnurl + '%s/hls/' % house_id


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

    root = jsonData['root']

    house_id, ext = root.split('.')

    config = Config.objects.get(enabled=True)
    
    gen = ''
    key = ''
    if config.secret:
	secret   = CdnSecret.objects.filter(enabled=True)
	if len(secret) != 0:
	    gen = secret[0].gen
	    key = secret[0].key

    cdnurl   = config.cdnurl
    path     = getpath(house_id)
    manifest = get_hls_manifest(config.cdnurl, path ,root, gen, key)
    
    if manifest is None:
	return HttpResponse('', status=http_BAD_REQUEST)
    try:
	ret = save_manifest_in_model(house_id, manifest)
	if not ret:
	    return HttpResponse('',status=500)
    except:
	return HttpResponse('',status=500)

    return HttpResponse('', status=http_POST_OK)


def _get_md5_hash(house_id):
    m = md5.md5()
    s = str(time.time())
    m.update(s + house_id)
    return m.hexdigest()


def CreateToken (house_id):
    try:
	video = Video.objects.get(house_id=house_id)
    except:
	return ''
    
    token = Token()
    token.expiration 	= datetime.now() + timedelta(0,7200)
    token.token      	= _get_md5_hash(house_id)
    token.video		= video
    token.save()
    return token.token


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
def vm_GetManifest(device, info ,idp, house_id, config):

    access = CheckAuthIdp(device,idp)
    if access != 'none':
	
	if config.secret:
	    token    = CreateToken(house_id)
	    cdnurl   = config.tokenurl
	    if not cdnurl.endswith('/'):
		cdnurl = cdnurl + '/'
	    cdnurl   = cdnurl + token
	else:
	    cdnurl   = config.cdnurl
	    if not cdnurl.endswith('/'):
		cdnurl = cdnurl + '/'
	    cdnurl   = cdnurl + getpath(house_id)

	if not cdnurl.endswith('/'):
	    cdnurl = cdnurl + '/'

	response     = build_root_manifest (house_id, cdnurl)
        status       = http_REQUEST_OK
	content_type = 'application/x-mpegURL'
    else:
	response     = json.dumps({'error': 'The Customer Have Not Autorization to View this Content'})
	status       = http_UNAUTHORIZED
	content_type = 'application/json'

    if config.gatra_enabled:
	gatra_tpp(config.gatra_url,info,access, house_id)

    return HttpResponse(response, status=status,content_type=content_type)



def vm_GetManifestByToken (request, token):
    try:
	t = Token.objects.get(token=token)
	if t.expiration < timezone.now():
	    t.delete()
	    return HttpResponse(json.dumps({'error': 'Expired Token'}), status=http_UNAUTHORIZED, content_type='application/json')

	config   = Config.objects.get(enabled=True)
	house_id = t.video.house_id

	if config.secret:
	    cdnurl   = config.tokenurl
	    if not cdnurl.endswith('/'):
		cdnurl = cdnurl + '/'
	    cdnurl   = cdnurl + token
	else:
	    cdnurl   = config.cdnurl
	    if not cdnurl.endswith('/'):
		cdnurl = cdnurl + '/'
	    cdnurl   = cdnurl + getpath(house_id)

	if not cdnurl.endswith('/'):
	    cdnurl = cdnurl + '/'

	response     = build_root_manifest (house_id, cdnurl)
        status       = http_REQUEST_OK
	content_type = 'application/x-mpegURL'
	return HttpResponse(response, status=status,content_type=content_type)
    except:
	return HttpResponse(json.dumps({'error': 'Invalid Token'}), status=http_UNAUTHORIZED, content_type='application/json')



def vm_GetRenditionByToken(request, token, filename):
    try:
	t = Token.objects.get(token=token)
	if t.expiration < timezone.now():
	    t.delete()
	    return HttpResponse('', status=http_UNAUTHORIZED)
    except:
	return HttpResponse('', status=http_UNAUTHORIZED)


    respose  = ''
    house_id = t.video.house_id
    cdnbase  = getcdnbase()
    path     = getpath(house_id)
    secret   = CdnSecret.objects.filter(enabled=True)
    if len(secret) != 0:
	stime,etime = dtime(3)
	response = build_rendition_manifest(house_id, filename, cdnbase, path, secret[0].gen, secret[0].key, stime, etime)

    if response != '':
	status       = http_REQUEST_OK
	content_type = 'application/x-mpegURL'
	return HttpResponse(response, status=status,content_type=content_type)
    
    return HttpResponse(response, status=http_NOT_FOUND)


def vm_GetUrl(device, info, idp, house_id, conf):

    #
    # Borra los tokens expirados
    #
    for t in Token.objects.all():
        if t.expiration < timezone.now():
	    t.delete()

    content_type = 'application/json'

    if device is not None and idp.auth_method.name == 'TOOLBOX':
	access = CheckAuthIdp(device,idp)
    elif idp.auth_method.name == 'DIRECT':
	if idp.access_type == 'full':
	    access = 'full'
	else:
	    access = 'none'

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

    if idp.gatra_post == True and info is not None and conf.gatra_enabled and status != 500:
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
       ( 'toolbox_user_token' in jsonData.keys() or 'token' in jsonData.keys()) and
	 'house_id'	      in jsonData.keys()):

	# Si la media no existe
	try:
	    video = Video.objects.get(house_id=jsonData['house_id'])
	except:
	    status = http_NOT_FOUND
	    return HttpResponse(json.dumps({ 'error': 'Media: %s Not Found' % jsonData['house_id']}), status=status,content_type='application/json')

	conf = Config.objects.get(enabled=True)

	# Traigo el cableoperador por api_key
	try:
	    idp = Customer.objects.get(api_key=jsonData['api_key'])
	except:
	    status = http_UNAUTHORIZED
	    return HttpResponse(json.dumps({ 'error': 'Api key Is Invalid' }), status=status, content_type='application/json')

	if idp.auth_method.name == 'TOOLBOX':
	    device = tbx.Device(conf.tbx_api_key,jsonData['toolbox_user_token'])
	    # Info para gatra
	    ret    = device.getInfo()
	    if ret is None:
		status = http_UNAUTHORIZED
	        return HttpResponse(json.dumps({ 'error': 'Unable to Find Device: %s' % jsonData['toolbox_user_token']}), status=status,content_type='application/json')

	    tbx_info = ret
	    info     = json.loads(ret)

	    if idp.idp_code != info['customer']['idp']['code']:
		status = http_BAD_REQUEST
		return HttpResponse(json.dumps({ 'error': 'Api key and Token Not Match' }), status=status, content_type='application/json')

	elif idp.auth_method.name == 'DIRECT':
	    device = None
	    info   = None
	    #
	    # Falta checkear que el token sea valido
	    #

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









