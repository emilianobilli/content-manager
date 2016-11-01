from django.shortcuts import render
from django.template.response import TemplateResponse
from django.http import HttpResponse

from django.contrib.auth.decorators import login_required

import json
from vmutils import timecode

# Create your views here.

from models import Language
from models import Video
from models import CuePoint

http_POST_OK            = 201
http_REQUEST_OK         = 200
http_BAD_REQUEST        = 400
http_NOT_FOUND          = 404
http_METHOD_NOT_ALLOWED = 405
FORMATS = ['json', 'vtt']

@login_required(login_url='/admin/login/')
def cm_PostCuePoint(request):
    if request.method == 'GET':
        return TemplateResponse(request, 'cue_manager.html')

    if request.method != 'POST':
        status = http_METHOD_NOT_ALLOWED
        return HttpResponse('', status=status)

    if 'house_id' in request.POST.keys():
        house_id = request.POST['house_id']
    else:
       status = http_BAD_REQUEST
       return HttpResponse('', status=status)

    if house_id == '':
        status = http_BAD_REQUEST
        return HttpResponse('', status=status)

    languages = Language.objects.all()

    for key, value  in request.POST.iteritems():
        if key.endswith('_tc') and value != '':
            i, t = key.split('_')
            for lang in languages:
                lang_key = '%s_%s' % (i, lang.code)
                if lang_key in request.POST.keys() and request.POST[lang_key] != '':
                    try:
                        video = Video.objects.get(house_id = house_id)
                    except:
                        video = Video()
                        video.house_id = house_id
                        video.save()
                    cuepoint          = CuePoint()
                    cuepoint.video    = video
                    cuepoint.timecode = value
                    cuepoint.language = lang
                    cuepoint.name     = request.POST[lang_key]
                    cuepoint.save()

    status = http_POST_OK
    return TemplateResponse(request, 'cue_manager.html')


def cm_GetCuePoint(request, house_id, lang, format, ret):
    if request.method != 'GET':
        status = http_METHOD_NOT_ALLOWED
        return HttpResponse('', status = status, content_type='application/json')

    if format not in FORMATS:
        status = http_NOT_FOUND
        return HttpResponse(json.dumps({'message':'Incorrect Format'}), status = status, content_type='application/json')

    try:
        video = Video.objects.get(house_id = house_id)
    except ObjectDoesNotExist:
        status = http_NOT_FOUND
        return HttpResponse(json.dumps({'message':'house_id not found'}), status = status, content_type='application/json')

    try:
        language = Language.objects.get(code = lang)
    except ObjectDoesNotExist:
        status = http_NOT_FOUND
        return HttpResponse(json.dumps({'message':'language not found'}), status = status, content_type='application/json')

    cuepoints = CuePoint.objects.filter(video = video, language = language)
    if len(cuepoints) == 0:
        status = http_NOT_FOUND
        return HttpResponse(json.dumps({'message':'house_id not found'}), status = status, content_type='application/json')

    status = http_REQUEST_OK
    if ret == 'check':
        return HttpResponse('', status = status)
    elif ret != 'cuepoint':
        status = http_BAD_REQUEST
        return HttpResponse(json.dumps({'message':'Unsupported command'}), status = status, content_type='application/json')

    if format == 'json':
        i = 1
        cp_list = []
        for cp in cuepoints:
            tc = timecode.fromString(cp.timecode)
            tc_sec = tc.tosec(30)
            cp_list.append(tc_sec)

        response = {'timecode':cp_list}
        return HttpResponse(json.dumps(response), status = status, content_type='application/json')
    elif format == 'vtt':
        vtt = 'WEBVTT\n\n'
        
        for cp in cuepoints:
            tc = timecode.fromString(cp.timecode)
            vtt = vtt + '%s --> %s\n%s\n\n' % (tc.msstr(), tc.msstr(), cp.name)
        return HttpResponse(vtt, status = status, content_type='octet-stream')