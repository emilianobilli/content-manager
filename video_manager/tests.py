from django.test import TestCase

import httplib2
import urlparse
import socket
from root_m3u8 import M3U8Rendition
from root_m3u8 import M3U8Playlist
from root_m3u8 import dtime
from models import Video

# Create your tests here.
'''
def get_hls_manifest(cdn_url, manifest):

    method = 'GET'
    h = httplib2.Http()

    if not cdn_url.endswith('/'):
	cdn_url = cdn_url + '/'
    
    uri = urlparse.urlparse(cdn_url +  manifest)
    try:
        response, content = h.request(uri.geturl(),method,'')
    except socket.error as err:
        raise socket.error

    m3u8_manifest = M3U8Playlist()
    m3u8_manifest.fromString(content)

    for f in m3u8_manifest.files:
	uri = urlparse.urlparse(cdn_url + f['filename'])
	try:
    	    response, content = h.request(uri.geturl(),method,'')
	except socket.error as err:
    	    raise socket.error
	
	f['rendition'] = M3U8Rendition()
	f['rendition'].fromString(content)

    return m3u8_manifest


x = get_hls_manifest('http://cdnlevel3.zolechamedia.net/009642/hls/', '009642.m3u8')

for i in x.files:
    print i
    print i['rendition'].header
    start,end = dtime(2)
    print i['rendition'].toStringHash('http://cdnlevel3token.zolechamedia.net', '009642/hls/', '0', '7a62159a1c33cff8a5ee55d99a40842d', '201609141400','201609141402')
#    for j in i['rendition'].files:
#	print j.toString()
#	print j

'''
video = Video.objects.all()
print video