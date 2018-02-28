from django.utils import timezone
from datetime import datetime
from datetime import timedelta
from models import ToolboxCache
import httplib2
import urlparse
import json
import socket
import os
import sys
import time

API_PATH = '/v2/UserServices'
PROD     = 'https://api.tbxnet.com'
STAGING	 = 'https://api-cert.tbxnet.com'

class ToolBox(object):
    def __init__(self, api_key, prod=True):
	self._api_key = api_key
	if prod:
	    self._url = PROD
	else:
	    self._url = STAGING

	self.toolbox_user_token = ''

    def header(self):
	header = {'Accept': 'application/json',
		  'Authorization': self._api_key }
	return header


    def GET(self, url):
	method = 'GET'
	header = self.header()
	h = httplib2.Http()

	uri = urlparse.urlparse(self._url + API_PATH + url)
	
	try:
            response, content = h.request(uri.geturl(),method,'',header)
        except socket.error as err:
            raise socket.error

	return response, content

class Device(object):
    def __init__(self, api_key, toolbox_user_token, prod=True):
	self.tbx        = ToolBox(api_key, prod)
	self.user_token = toolbox_user_token

    def getInfo(self):
	doGet = False
	try:
	    cache = ToolboxCache.objects.get(user_token=self.user_token)
	    if cache.info_data != "":
		return cache.info_data

	except:
	    cache = None

	try:
	    ret, content = self.tbx.GET('/device/' + self.user_token)
		
	except:
	    pass
	
	if ret['status'] == '200':
	    if cache is not None:
		cache.info_data = content
		cache.save()
	    return content
	else:
	    return None



    def hasAccessTo(self, urn):
	doGet = False
	try:
	    cache = ToolboxCache.objects.get(user_token=self.user_token,urn=urn)
	    if cache.expiration < timezone.now():
		cache.delete()
		doGet = True
	except:
	    doGet = True

	if doGet:
	    try:
		ret, content = self.tbx.GET('/device/' +  self.user_token + '/hasAccessTo?urn=%s&action=VIEW&ip=127.0.0.1' % urn)
	    except:
		return None

	    if ret['status'] == '200':
		cache = ToolboxCache()
		cache.expiration  = datetime.now() + timedelta(0,7200)
		cache.urn         = urn
		cache.user_token  = self.user_token
		cache.access_data = content
		cache.save()
	    else:
		return None

	return cache.access_data

class Customer(object):
    def __init__(self, api_key, customer_id, prod=True):
	self.tbx = ToolBox(api_key, prod)
	self.customer = customer_id

    def hasAccessTo(self, urn):
	try:
	    ret, content = self.tbx.GET('/' + self.customer + '/hasAccessTo?urn=%s&action=VIEW&ip=127.0.0.1' % urn)
	except:
	    pass

	if ret['status'] == '200':
	    return content
	else:
	    return None
					       
