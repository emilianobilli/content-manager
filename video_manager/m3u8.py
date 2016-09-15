from hashlib import sha1
import datetime
import hmac
import httplib2
import urlparse
import socket



def ComputeHash (gen, key, uri):
    h = hmac.new(str(key), str(uri), sha1)
    return '%1.1s%20.20s' % (gen,h.hexdigest())

def dtime(delta):
        return (datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M'), datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(0,0,0,0,0,delta,0), '%Y%m%d%H%M'))


def get_hls_manifest(cdnbase, path , manifest, gen='', key=''):

    method = 'GET'
    hreq = httplib2.Http()

    if not cdnbase.endswith('/'):
	cdnbase = cdnbase + '/'
    
    if not path.endswith('/'):
	path    = path + '/'

    if gen != '' and key != '':
	h   = ComputeHash(gen,key,path+manifest)
	url = cdnbase + path + manifest + '?hash=%s' % h
    else:
	url = cdnbase + path + manifest

    uri = urlparse.urlparse(url)
    try:
        response, content = hreq.request(uri.geturl(),method,'')
    except socket.error as err:
        raise socket.error

    m3u8_manifest = M3U8Playlist()
    m3u8_manifest.fromString(content)

    for f in m3u8_manifest.files:
	if gen != '' and key != '':
	    h   = ComputeHash(gen,key, path+f['filename'])
	    url = cdnbase + path + f['filename'] + '?hash=%s' % h
	else:
	    url = cdnbase + path + f['filename']

	uri = urlparse.urlparse(url)
	try:
    	    response, content = hreq.request(uri.geturl(),method,'')
	except socket.error as err:
    	    raise socket.error
	
	f['rendition'] = M3U8Rendition()
	f['rendition'].fromString(content)

    return m3u8_manifest


class M3U8Rendition(object):
    def __init__(self):
	self.header  = {}
	self.files   = []


    def setHeader(self, version, media_seq, allow_cache, target_duration):
	self.header['version']         = version
	self.header['media_seq']       = media_seq
	self.header['allow_cache']     = allow_cache
	self.header['target_duration'] = target_duration

    def addfile(self, extinf, filename, number):
	self.files.append({'extinf':extinf, 'filename': filename, 'number': number})

    def headerToString(self):
	m3u8 = ''
	m3u8 = m3u8 + '#EXTM3U\n'
	m3u8 = m3u8 + '#EXT-X-VERSION:%s\n' % self.header['version']
	m3u8 = m3u8 + '#EXT-X-MEDIA-SEQUENCE:%s\n' % self.header['media_seq']
	m3u8 = m3u8 + '#EXT-X-ALLOW-CACHE:%s\n' % self.header['allow_cache']
	m3u8 = m3u8 + '#EXT-X-TARGETDURATION:%s\n' % self.header['target_duration']
	return m3u8

    def toStringHash(self, cdnbase, path, gen, key, stime='', etime=''):
	m3u8 = ''
	m3u8 = m3u8 + self.headerToString()

	flag = False

	if cdnbase != '':
	    if not cdnbase.endswith('/'):
	        cdnbase = cdnbase + '/'
	if path != '':
	    if not path.endswith('/'):
	        path = path + '/'
	
	for f in self.files:
	    if stime != '' and etime != '':
		filename = f['filename'] + '?stime=%s&etime=%s' % (stime,etime)
		m3u8 = m3u8 + '#EXTINF:%s\n%s%s&hash=%s\n' % (f['extinf'], cdnbase+path,  filename, ComputeHash(gen,key, '/'+path+filename))
	    else:
		m3u8 = m3u8 + '#EXTINF:%s\n%s%s?hash=%s\n' % (f['extinf'], cdnbase+path,  f['filename'], ComputeHash(gen,key, '/'+path+f['filename']))

	m3u8 = m3u8 + '#EXT-X-ENDLIST'
	return m3u8

    def toString(self,  cdnurl):
	m3u8 = ''
	m3u8 = m3u8 + self.headerToString()
	for f in self.files:
	    if cdnurl != '':
		if not cdnurl.endswith('/'):
		    cdnurl = cdnurl + '/'
	    m3u8 = m3u8 + '#EXTINF:%s\n%s%s\n' % (f['extinf'], cdnurl, f['filename'])
    
	m3u8 = m3u8 + '#EXT-X-ENDLIST'
	return m3u8

    def fromFile(self, file):
	with open(file) as f:
	    content = f.read()
	    f.close()
	self.fromString(content)


    def fromString(self, string):
	lines = string.splitlines()
	i = 0

	while i <= len(lines)-1:
	    if lines[i].startswith('#EXTM3U'):
		i = i + 1
	    if lines[i].startswith('#EXT-X-VERSION'):
		out,ver = lines[i].split(':')
		self.header['version'] = int(ver)
		i = i + 1
		continue
	    if lines[i].startswith('#EXT-X-MEDIA-SEQUENCE'):
		out,seq = lines[i].split(':')
		self.header['media_seq'] = int(seq)
		i = i + 1
		continue
	    if lines[i].startswith('#EXT-X-ALLOW-CACHE'):
		out,value = lines[i].split(':')
		self.header['allow_cache'] = value
		i = i + 1
		continue
	    if lines[i].startswith('#EXT-X-TARGETDURATION'):
		out,value = lines[i].split(':')
		self.header['target_duration'] = value
		i = i + 1
		continue
	    if lines[i].startswith('#EXTINF'):
		out,value 	   = lines[i].split(':')
		n,ext     	   = lines[i+1].split('.')
		hid,quality,number = n.split('_')
		self.files.append({'number': int(number),'extinf': value, 'filename': lines[i+1].replace('\n', '')})
		i = i + 2
	        continue
	
	    i = i + 1


class M3U8Playlist(object):
    def __init__(self):
	self.version = -1
	self.files   = []


    def addfile(self, filename, bandwidth, average, codecs, resolution):
	self.files.append({ 'filename'  : filename,
			    'bandwidth' : bandwidth,
			    'average'   : average,
			    'codecs'    : codecs,
			    'resolution': resolution })

    def __addfile(self, info, filename):
	data = info.split(',')
	band       = ''
	average    = ''
	codecs     = ''
	resolution = ''

	for d in data:
	    try:
		key,value = d.split('=')
	    except:
		if codecs != '':
		    codecs = codecs + ',' + d
		    continue

	    if key == 'BANDWIDTH':
		band = value
	    if key == 'AVERAGE-BANDWIDTH':
		average = value
	    if key == 'CODECS':
		codecs = value
	    if key == 'RESOLUTION':
		resolution = value

	self.files.append({ 'filename'  : filename,
			    'bandwidth' : band,
			    'average'   : average,
			    'codecs'    : codecs,
			    'resolution': resolution })

    def fromString(self, string):

	lines = string.splitlines()
	i = 0

	while i <= len(lines)-1:
	    if lines[i].startswith('#EXTM3U'):
		i = i + 1
		continue
	    if lines[i].startswith('#EXT-X-VERSION'):
		out,ver = lines[i].split(':')
		self.version = int(ver)
		i = i + 1
		continue
	    if lines[i].startswith('#EXT-X-STREAM-INF'):
		hdr,info = lines[i].split(':')
		self.__addfile(info,lines[i+1])
		i = i + 2
		continue
	
	    i = i + 1

    def fromFile(self, file):
	with open(file) as f:
	    content = f.read()
	    f.close()
	self.fromString(content)


    def toString(self, cdnurl = ''):
	if self.version != -1:
	    m3u8 = '#EXTM3U\n#EXT-X-VERSION:%d\n' % self.version
	    for f in self.files:
		m3u8 = m3u8 + '#EXT-X-STREAM-INF:BANDWIDTH=%s,AVERAGE-BANDWIDTH=%s,CODECS=%s,RESOLUTION=%s\n' % ( f['bandwidth'],
													          f['average'],
														  f['codecs'],
														  f['resolution'] )
		if cdnurl != '':
		    if not cdnurl.endswith('/'):
			cdnurl = cdnurl + '/'
		    m3u8 = m3u8 + '%s%s\n' % (cdnurl,f['filename'])
		else:
		    m3u8 = m3u8 + '%s\n' % f['filename']
	    return m3u8
	else:
	    return ''

