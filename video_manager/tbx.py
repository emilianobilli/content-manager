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
	try:
	    ret, content = self.tbx.GET('/device/' + self.user_token)
	except:
	    pass
	
	if ret['status'] == '200':
	    return content
	else:
	    return None

    def hasAccessTo(self, urn):
	try:
	    ret, content = self.tbx.GET('/device/' +  self.user_token + '/hasAccessTo?urn=%s&action=VIEW&ip=127.0.0.1' % urn)
	except:
	    pass

	
	if ret['status'] == '200':
	    return content
	else:
	    return None

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
					       
#t = Device('dfGna9356QYO6ENI6J1GMt8o6UGj2o1p', '237f0e775195b98ee507abf39be71a4365554504')
#t = ToolBox('dfGna9356QYO6ENI6J1GMt8o6UGj2o1p', True)
#t.toolbox_user_token = '9e6346cbcdf8b9e3de87cb64066e46ab12b807ea'
#info = json.loads(t.getInfo())
#print t.hasAccessTo('urn:tve:hotgo')
#c = Customer('dfGna9356QYO6ENI6J1GMt8o6UGj2o1p', '5302a46965b81441128b4e88')
#print c.hasAccessTo('urn:tve:hotgo')
#print info['customer']['idp']['code']
