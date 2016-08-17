#
#
# Libreria para leer y escribir STL
#
# Emiliano A. Billi 2013
#
#

from struct import *
from timecode import *
import sys

#
# Tabla de translacion ISO/6937-2 a UTF-8
# Ejemplo: Palabra = '\xC1\x41' -> return STL_TO_UTF8_ACCENT[Pablabra[0]][chr(Palabra[1])]
# Todos los acentos en utf-8 comienzan por 0xC3
#
STL_TO_UTF8_ACCENT = {
	0xC1 :{ 'A':'\xC3\x80','E':'\xC3\x88','I':'\xC3\x8C','O':'\xC3\x92','U':'\xC3\x99','a':'\xC3\xA0','e':'\xC3\xA8','i':'\xC3\xAC','o':'\xC3\xB2','u':'\xC3\xB9'},
	0xC2 :{ 'A':'\xC3\x81','E':'\xC3\x89','I':'\xC3\x8D','O':'\xC3\x93','U':'\xC3\x9A','a':'\xC3\xA1','e':'\xC3\xA9','i':'\xC3\xAD','o':'\xC3\xB3','u':'\xC3\xBA', '\xc2':'\x34' }, 
	0xC3 :{ 'A':'\xC3\x82','E':'\xC3\x8A','O':'\xC3\x94','a':'\xC3\xA2','e':'\xC3\xAA','o':'\xC3\xB4'},
	0xC4 :{ 'A':'\xC3\x83','N':'\xC3\x91','O':'\xC3\x95','a':'\xC3\xA3','n':'\xC3\xB1','o':'\xC3\xB5'},
	0xCB :{ 'C':'\xC3\x87','c':'\xC3\xa7' },
	0xC8 :{ 'U':'\xC3\x9C','u':'\xC3\xBC' } }
    

def BytesToString(bytes=None, length=0):
    ret = ''
    if bytes is not None and len(bytes) == length:
	tmp = bytearray(bytes)
	i = 0
	while i < length:
	    ret = ret + chr(tmp[i])
	    i = i + 1
    return ret


class Date(object):
    def __init__(self, DateBuff=None):
	if DateBuff is not None and len(DateBuff) == 6:
	    self.date = BytesToString(DateBuff, 6)
	else:
	    self.date = ''
    def __repr__(self):
	return self.date



class GSI_Block(object):
    def __init__(self, GSI_Data=None):
	if GSI_Data is not None and len(GSI_Data) == 1024:
	    self.allData = GSI_Data
	    self.cpn = BytesToString(GSI_Data[0:3],3)
	    self.dfc = BytesToString(GSI_Data[3:11],8)
	    self.dsc = BytesToString(GSI_Data[11:12],1)
	    self.cct = BytesToString(GSI_Data[12:14],2)
	    self.lc  = BytesToString(GSI_Data[14:16],2)
	    self.opt = BytesToString(GSI_Data[16:48],32)
	    self.oet = BytesToString(GSI_Data[48:80],32)
	    self.tpt = BytesToString(GSI_Data[80:112],32) 
	    self.tet = BytesToString(GSI_Data[112:144],32)
	    self.tn  = BytesToString(GSI_Data[144:176],32)
	    self.tcd = BytesToString(GSI_Data[176:208],32)
	    self.slr = BytesToString(GSI_Data[208:224],16)
	    self.cd  = Date(GSI_Data[224:230])
	    self.rd  = Date(GSI_Data[230:236])


    def repack(self):
	return bytearray(self.allData)


class SubTiming(object):
    def __init__(self):
	self.tci  = None
	self.tco  = None
	self.text = None

class SUB(object):
    def __init__(self):
	self.timing = []

    def load(self, filename = ''):
	if filename.endswith('.sub'):
	    print filename
	    try:
		fd = open(filename, 'rt')
	    except:
		pass	

	    line = fd.readline()
	    while line:
#	    print line
#	    for line in fd.readline():
		print line
		tci, tco, text = line.split(';')
		STiming = SubTiming()
		hh, mm, ss = tci.split(':')
		STiming.tci = fromSplitedValues(int(hh),int(mm),int(ss),00,29.97)
		hh, mm, ss = tco.split(':')
		STiming.tco = fromSplitedValues(int(hh),int(mm),int(ss),00,29.97)
		STiming.text = text
		self.timing.append(STiming)
		line = fd.readline()

	    fd.close()


class STL(object):

    def __init__(self):
	self.gsi  = None
	self.tti  = []

    def load(self, filename = ''):
	if filename.endswith('.stl') or filename.endswith('.STL'):
	    try:
    		fd = open(filename,'rb')
	    except:
		pass
		
	    buff = fd.read(1024)
	    self.gsi = GSI_Block(buff)
	    buff = fd.read(128)
	    while buff != b'':
	        tti = TTI_Block(buff)
	        self.tti.append(tti)
	        buff = fd.read(128)
	    
	    fd.close()    
	else:
	    print filename

    def save(self, filename =''):
	if filename.endswith('.stl') or filename.endswith('.STL'):
	    try:
		fd = open(filename, 'wb')
	    except:
		pass

	    GSI = self.gsi.repack()
	    fd.write(GSI)
	    for TTI in self.tti:
		TTI_Data,TTI_Text = TTI.repack()
		fd.write(TTI_Data)
		fd.write(TTI_Text)
		
	    fd.close()

    def __vtt(self, som = '01:00:00;00'):
	vtt = ''

	stc = fromString(som)
	
	vtt = vtt + 'WEBVTT\n\n'
	i = 0
	for tti in self.tti:
	    if tti.tci > stc:
		tcin  = tti.tci - stc
    		tcout = tti.tco - stc
    
		srt = u'%s --> %s\n%s' % (tcin.msstr(), tcout.msstr(), tti.tf.encode_utf8())
		srt = srt.replace('\n\n', '\n')
		srt = srt + '\n\n' if not srt.endswith('\n') else srt + '\n'	
		i = i + 1
		vtt = vtt + srt	

	return vtt    

    def __srt(self, som = '01:00:00;00'):

	srt = ''
	stc = fromString(som)
		
	i = 0    
	for tti in self.tti:
	    if tti.tci > stc:
		tcin  = tti.tci - stc
    		tcout = tti.tco - stc
    
		srt = srt + u'%d\n%s --> %s\n%s' % (i, tcin.msstring(), tcout.msstring(), tti.tf.encode_utf8())
		srt = srt.replace('\n\n', '\n')
		srt = srt + '\n\n' if not srt.endswith('\n') else srt + '\n'	
		i = i + 1
	return srt


    def toString(self, format =  'srt', som = '01:00:00;00'):
	srt = ''
	if format == 'srt':
	    srt = self.__srt(som)
	if format == 'vtt':
	    srt = self.__vtt(som)

	return srt.encode('utf-8')

    
    def export(self, filename = '', format = 'srt', som = '01:00:00;00'):
	if filename != '':
	    try:
		fd = open(filename, 'wb')
	    except:
		pass
	    if format == 'srt':
		srt = self.__srt(som)
		fd.write(srt.encode('utf-8'))	
		fd.close()
	
	    if format == 'vtt':
		srt = self.__vtt(som)
		stc = fromString(som)
		fd.write(srt.encode('utf-8'))	
		fd.close()



class TextField(object):
    def __init__(self, TFBuff=None):
	if TFBuff is not None and len(TFBuff) == 112:
	    self.tf = bytearray(TFBuff)
	else:
	    self.tf = bytearray(112)

    def repack(self):
	return self.tf

    def isControl(self, index=0):
	return True if (self.tf[index] >= 0x00 and self.tf[index] <= 0x1F )   else False 

    def isBoxingOn(self, index=0):
	return True if (self.tf[index] == 0x84 ) else False

    def isBoxingOff(self, index=0):
	return True if (self.tf[index] == 0x85 ) else False

    def isUnderlineOn(self, index=0):
	return True if (self.tf[index] == 0x82 ) else False

    def isUnderlineOff(self, index=0):
	return True if (self.tf[index] == 0x83 ) else False

    def isAccent(self, index=0):
	return True if ( ( self.tf[index] >> 4 ) == 0x0C) and (self.tf[index] != 0xC9) else False

    def isRareSymbol(self, index=0):
	return True if ( ( self.tf[index] >= 0xe0 ) and (self.tf[index] <= 0xef ) ) else False

    def isSign(self,index=0):
	return True if (self.tf[index] == 0xBF) or (self.tf[index] == 0xA1) or (self.tf[index] == 0xEC) or (self.tf[index] == 0xE1) or (self.tf[index] == 0xED) or (self.tf[index] == 0xAA ) or (self.tf[index] == 0xBA) or (self.tf[index] == 0xA4) or (self.tf[index] == 0xB0) or (self.tf[index] == 0xA9) or (self.tf[index] == 0xB9) or (self.tf[index] == 0xC9 ) or (self.tf[index] == 0xA6) else False

    def isItalicOn(self, index=0):
	return True if ( self.tf[index] == 0x80 ) else False

    def isItalicOff(self, index=0):
	return True if ( self.tf[index] == 0x81 ) else False

    def isEnd(self, index=0):
	return True if ( self.tf[index] == 0x8F ) else False

    def isCrLf(self, index=0):
	return True if ( self.tf[index] == 0x8A ) else False

    def encode_utf8(self, italic_on='', italic_off=''):
	utf8_str = ''
	i = 0
	while not self.isEnd(i) and i < 112 -1:
	    if self.isControl(i):
		pass
	    else:
		if self.isItalicOn(i):
		    utf8_str = utf8_str + italic_on
		elif self.isItalicOff(i):
		    utf8_str = utf8_str + italic_off
		elif self.isAccent(i):
		    utf8_str = utf8_str + STL_TO_UTF8_ACCENT[self.tf[i]][chr(self.tf[i+1])]
		    i = i + 1
		elif self.isSign(i):
		    if self.tf[i] == 0xBF:
			utf8_str = utf8_str + '\xC2\xBF'
		    elif self.tf[i] == 0xA1:
			utf8_str = utf8_str + '\xC2\xA1'
		    elif self.tf[i] == 0xAA or self.tf[i] == 0xBA:
			utf8_str = utf8_str + '\x22'
		    elif self.tf[i] == 0xA4:
			utf8_str = utf8_str + '\x24'	
		    elif self.tf[i] == 0xA6:
			utf8_str = utf8_str + ' '
		    elif self.tf[i] == 0xB0:
			utf8_str = utf8_str + '\xC2\xB0'
		    elif self.tf[i] == 0xA9:
			utf8_str = utf8_str + '\x60'	
		    elif self.tf[i] == 0xB9:
			utf8_str = utf8_str + '\xC2\xB4'
		    elif self.tf[i] == 0xC9:
			utf8_str = utf8_str + ' '
		    
		    else:
			utf8_str = utf8_str + '*'
		elif self.isCrLf(i):
		    utf8_str = utf8_str + '\n'
		elif self.isBoxingOn(i) or self.isBoxingOff(i):
		    pass
		elif self.isUnderlineOn(i) or self.isUnderlineOff(i):
		    pass
		elif self.isRareSymbol(i):
		    pass    
		else:
		    utf8_str = utf8_str + chr(self.tf[i])
	    i = i + 1
	return utf8_str.decode('utf-8')
    

class TTI_Block(object):
    def __init__(self, TTI_Data=None):
	if TTI_Data is not None and len(TTI_Data) == 128:
	    self.sgn,self.sn,self.ebn,self.cs  = unpack('=BHBB', TTI_Data[0:5])
	    hh,mm,ss,ff = unpack('BBBB', TTI_Data[5:9])
	    self.tci = fromSplitedValues(hh,mm,ss,ff,29.97)
	    hh,mm,ss,ff = unpack('BBBB', TTI_Data[9:13])
	    self.tco = fromSplitedValues(hh,mm,ss,ff,29.97)
	    self.vp,self.jc,self.cf = unpack('=BBB', TTI_Data[13:16])
	    self.tf = TextField(TTI_Data[16:])
	else:
	    self.sgn = None
	    self.sn  = None
	    self.ebn = None
	    self.cs  = None
	    self.tci = None
	    self.tco = None
	    self.vp  = None
	    self.jc  = None
	    self.cf  = None
	    self.tf  = None
    
    def isComment(self):
	return True if self.cf == 0x01 else False

    def isSubtitle(self):
	return True if self.cf == 0x00 else False

    def repack(self):
	#
	# Separa en todos los valores TCI y TCO
	#
	hh_in,mm_in,ss_in,ff_in,fr     = self.tci.splitedvalues()
	hh_out,mm_out,ss_out,ff_out,fr = self.tco.splitedvalues()
	#
	# Agrupa todos los valores del area de datos en un bytearray
	#
	TTI_Data = bytearray(pack('=BHBBBBBBBBBBBBB', self.sgn,
						      self.sn,
						      self.ebn,
						      self.cs,
						      hh_in,
						      mm_in,
						      ss_in,
						      ff_in,
						      hh_out,
						      mm_out,
						      ss_out,
						      ff_out,
						      self.vp, self.jc, self.cf))
	TTI_Text = self.tf.repack()
	return TTI_Data, TTI_Text



