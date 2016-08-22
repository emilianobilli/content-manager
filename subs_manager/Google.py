
#
# Google Api Key
#
from GoogleApiKey import TRANSLATE_SERVER_API

#
# Libraries
#
import json
import httplib2
import urlparse
import urllib 
import json


class Translate (object):
    def __init__(self):
	self.google_translate_endpoint = 'https://www.googleapis.com/language/translate/v2?'
	self.google_translate_apikey   = TRANSLATE_SERVER_API

    def __get(self, url):
	method = 'GET'
	body   = ''

	if url is not None:
	    uri = urlparse.urlparse(url)
        else:
	    return ''

	h = httplib2.Http()

	return h.request(uri.geturl(), method, body)

    def translateString (self, source, target, q):
	url_arg = 'key=%s&' % self.google_translate_apikey
	url_arg = url_arg + 'source=%s&target=%s&' % (source, target)
	url_arg = url_arg + 'q=%s' % (urllib.quote_plus(q))
	
	ret, content =  self.__get(self.google_translate_endpoint + url_arg)	

	if ret['status'] == '200':
	    return content
	
	return ''

    def translateList (self, source, target, q):
	url_arg = 'key=%s&' % self.google_translate_apikey
	url_arg = url_arg + 'source=%s&target=%s&' % (source, target)

	query = []
	i     = 0 
	for s in q:
	    if len(query) == i:
		query.append('')

	    query[i] = query[i] + 'q=%s' % (urllib.quote_plus(s.encode('utf-8')))

	    if len(query[i]) + len(url_arg) + len(self.google_translate_endpoint) > 2048 - 255:
		i = i + 1
	    else:
		query[i] = query[i] + '&'

	t = []

	for param in query:
	    ret, content = self.__get(self.google_translate_endpoint + url_arg + param)
	    if ret['status'] == '200':
		t.append(content)

	return t

