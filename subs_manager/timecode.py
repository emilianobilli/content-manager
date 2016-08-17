import re
#
# Funcion para crear un objeto de tipo TimeCode a partir de un string ("08:37:45:17" o "08:37:45;17") y de un entero con el Frame Rate
#
# Emiliano A. Billi 2011
#

class TimeCodeError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class TimeCode(object):
    
    def __init__(self):
	self.frames		= 0			# Frames desde cero del objeto TC
        self.frameRate		= 30			# FrameRate asociado al TC

    
    def __add__(self, other):
	if self.frameRate == other.frameRate:
    	    frames = self.frames + other.frames
    	    ret = TimeCode()
    	    ret.frameRate = self.frameRate
    	    ret.frames = frames
    	    return ret
	else:
    	    raise TimeCodeError('FrameRate does not match')
    	    

    def __sub__(self, other):
	if self.frameRate == other.frameRate:
    	    frames = self.frames - other.frames
    	    ret = TimeCode()
    	    ret.frameRate = self.frameRate
    	    ret.frames = frames
    	    return ret
	else:
    	    raise TimeCodeError('FrameRate does not match')
    
    def __eq__(self, other):
	if self.frameRate == other.frameRate:
    	    if self.frames == other.frames:
		return True
	    else:
		return False
	else:
    	    raise TimeCodeError('FrameRate does not match')

    def __ne__(self, other):
	if self.frameRate == other.frameRate:
    	    if self.frames != other.frames:
		return True
	    else:
		return False
	else:
    	    raise TimeCodeError('FrameRate does not match')

    def __lt__(self, other):
	if self.frameRate == other.frameRate:
    	    if self.frames < other.frames:
		return True
	    else:
		return False
	else:
    	    raise TimeCodeError('FrameRate does not match')

    def __le__(self, other):
	if self.frameRate == other.frameRate:
    	    if self.frames <= other.frames:
		return True
	    else:
		return False
	else:
    	    raise TimeCodeError('FrameRate does not match')

    def __ge__(self, other):
	if self.frameRate == other.frameRate:
    	    if self.frames >= other.frames:
		return True
	    else:
		return False
	else:
    	    raise TimeCodeError('FrameRate does not match')

    def __gt__(self, other):
	if self.frameRate == other.frameRate:
    	    if self.frames > other.frames:
		return True
	    else:
		return False
	else:
    	    raise TimeCodeError('FrameRate does not match')

    def __str__(self):
	if self.frameRate ==  29.97:
    	    hh, ff = divmod(self.frames, 107892)
    	    mm = int((self.frames + (2 * int(ff / 1800)) - (2 * (int(ff / 18000))) - (107892 * hh)) / 1800)
    	    ss = int((self.frames - (1798 * mm) - (2 * int(mm / 10)) - (107892 * hh)) / 30)
    	    ff = int(self.frames - (30 * ss) - (1798 * mm) - (2 * int(mm / 10)) - (107892 * hh))
	    lastcolon = ';' 

	elif self.frameRate == 30:
    	    ss, ff = divmod( int(self.frames), int(self.frameRate) )
    	    mm, ss = divmod( ss, 60 )
    	    hh, mm = divmod( mm, 60 )
	    lastcolon = ':'
	else:
    	    pass
    
	hhstr = str(hh) if hh > 9 else '0' + str(hh)
	mmstr = str(mm) if mm > 9 else '0' + str(mm)
	ssstr = str(ss) if ss > 9 else '0' + str(ss)
	ffstr = str(ff) if ff > 9 else '0' + str(ff)
	return ('%s:%s:%s%s%s' % (hhstr,mmstr,ssstr,lastcolon,ffstr))


    def splitedvalues(self):
	if self.frameRate ==  29.97:
    	    hh, ff = divmod(self.frames, 107892)
    	    mm = int((self.frames + (2 * int(ff / 1800)) - (2 * (int(ff / 18000))) - (107892 * hh)) / 1800)
    	    ss = int((self.frames - (1798 * mm) - (2 * int(mm / 10)) - (107892 * hh)) / 30)
    	    ff = int(self.frames - (30 * ss) - (1798 * mm) - (2 * int(mm / 10)) - (107892 * hh))
	    lastcolon = ';' 

	elif self.frameRate == 30:
    	    ss, ff = divmod( int(self.frames), int(self.frameRate) )
    	    mm, ss = divmod( ss, 60 )
    	    hh, mm = divmod( mm, 60 )
	    lastcolon = ':'
	else:
    	    pass

	return hh,mm,ss,ff,self.frameRate

    def __repr__(self):
	return str(self)

    def msstr(self, lastcolon = '.', mslen = 3):
	if self.frameRate ==  29.97:
    	    hh, ff = divmod(self.frames, 107892)
    	    mm = int((self.frames + (2 * int(ff / 1800)) - (2 * (int(ff / 18000))) - (107892 * hh)) / 1800)
    	    ss = int((self.frames - (1798 * mm) - (2 * int(mm / 10)) - (107892 * hh)) / 30)
    	    ff = int(self.frames - (30 * ss) - (1798 * mm) - (2 * int(mm / 10)) - (107892 * hh))

	elif self.frameRate == 30:
    	    ss, ff = divmod( int(self.frames), int(self.frameRate) )
    	    mm, ss = divmod( ss, 60 )
    	    hh, mm = divmod( mm, 60 )
	else:
    	    pass
    
	hhstr = str(hh) if hh > 9 else '0' + str(hh)
	mmstr = str(mm) if mm > 9 else '0' + str(mm)
	ssstr = str(ss) if ss > 9 else '0' + str(ss)
	ffstr = str(int (( ff * 1000) / 30))

	while len(ffstr) < mslen:
	    ffstr = ffstr + '0'

	return ('%s:%s:%s%s%s' % (hhstr,mmstr,ssstr,lastcolon,ffstr))


    def msstring(self):
	if self.frameRate ==  29.97:
    	    hh, ff = divmod(self.frames, 107892)
    	    mm = int((self.frames + (2 * int(ff / 1800)) - (2 * (int(ff / 18000))) - (107892 * hh)) / 1800)
    	    ss = int((self.frames - (1798 * mm) - (2 * int(mm / 10)) - (107892 * hh)) / 30)
    	    ff = int(self.frames - (30 * ss) - (1798 * mm) - (2 * int(mm / 10)) - (107892 * hh))

	elif self.frameRate == 30:
    	    ss, ff = divmod( int(self.frames), int(self.frameRate) )
    	    mm, ss = divmod( ss, 60 )
    	    hh, mm = divmod( mm, 60 )
	else:
    	    pass
    
	lastcolon = ','

	hhstr = str(hh) if hh > 9 else '0' + str(hh)
	mmstr = str(mm) if mm > 9 else '0' + str(mm)
	ssstr = str(ss) if ss > 9 else '0' + str(ss)
	ffstr = str(int (( ff * 1000) / 30))
	return ('%s:%s:%s%s%s' % (hhstr,mmstr,ssstr,lastcolon,ffstr))


def fromSplitedValues(hh,mm,ss,ff, frameRate):
    if frameRate == 29.97:
        totalMinutes = 60 * int(hh) + int(mm)
    	totalFrames  = 108000 * int(hh) + 1800 * int(mm) + 30 * int(ss) + int(ff) - 2 * (totalMinutes - int(totalMinutes / 10))
    
    elif frameRate == 30:
	totalSeconds = (int(hh) * 3600) + (int(mm) * 60) + int(ss)
    	totalFrames = (totalSeconds * frameRate) + int(ff)
    else:
	raise TimeCodeError('Invalid Frame Rate')

    timecode		= TimeCode()
    timecode.frames	= totalFrames
    timecode.frameRate	= frameRate
    return timecode

def fromString(string):
    
    if re.search(";", string):
    	frameRate = 29.97
        string = re.sub(";", ":", string)
    else:
	frameRate = 30

    tc = re.match("([0-9][0-9]):([0-5][0-9]):([0-5][0-9]):([0-2][0-9])", string)
    
    if tc:
	hh = tc.group(1)
	mm = tc.group(2)
        ss = tc.group(3)
        ff = tc.group(4)

    return fromSplitedValues(hh,mm,ss,ff,frameRate)
