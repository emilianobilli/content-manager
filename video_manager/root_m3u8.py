
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

