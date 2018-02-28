from models import Video
from models import Profile
from models import ProfileFile

from m3u8 import M3U8Playlist
from m3u8 import M3U8Rendition


def save_manifest_in_model(house_id, m3u8_manifest):
    
    # 
    # Search de Video, if exist return Error
    try:
	video = Video.objects.get(house_id=house_id)
	return False
    except:
	video = Video()
	video.house_id = house_id
	video.format   = 'hls'
	video.save()

    for rendition in m3u8_manifest.files:
	profile = Profile()
	profile.video = video
	profile.bandwidth  	= rendition['bandwidth']
        profile.average    	= rendition['average']
        profile.codecs     	= rendition['codecs']
        profile.resolution 	= rendition['resolution']
        profile.filename   	= rendition['filename']
	profile.version	   	= rendition['rendition'].header['version']
	profile.media_seq  	= rendition['rendition'].header['media_seq']
	profile.allow_cache	= rendition['rendition'].header['allow_cache']
	profile.target_duration = rendition['rendition'].header['target_duration']
	profile.save()
	for tsfile in rendition['rendition'].files:
	    profile_file = ProfileFile()
	    profile_file.profile  = profile
	    profile_file.number   = tsfile['number']
	    profile_file.extinf   = tsfile['extinf']
	    profile_file.filename = tsfile['filename']
	    profile_file.save()

    return True


def build_root_manifest (house_id, cdnurl = ''):
    #
    # Fist, find the video
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


def build_rendition_manifest (house_id, filename, cdnbase, path, gen='', key='', stime='', etime='',idp=''):
    try:
	video   = Video.objects.get(house_id=house_id)
    except:
	return ''
    try:
	profile = Profile.objects.get(video=video, filename=filename)
    except:
	return ''

    tsfiles = ProfileFile.objects.filter(profile=profile).order_by('number')
    
    manifest = M3U8Rendition()
    manifest.setHeader(profile.version,profile.media_seq,profile.allow_cache,profile.target_duration)
    for ts in tsfiles:
	manifest.addfile(ts.extinf, ts.filename,ts.number)

    return manifest.toStringHash(cdnbase,path,gen,key,stime,etime,idp)
