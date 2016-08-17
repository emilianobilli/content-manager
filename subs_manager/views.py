from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import *
import json

# Create your views here.

from models import Config
from models import Language
from models import Subtitle

from stl import STL

http_POST_OK    = 201
http_REQUEST_OK = 200
http_NOT_FOUND  = 404
FORMATS = ['srt', 'vtt']


def sm_GetSub(request, house_id, lang, format, ret):
    if request.method != 'GET':
        status = http_NOT_FOUND
        return HttpResponse(json.dumps({'message': 'Incorrect METHOD'}), status=status, content_type='application/json')

    try:
        language = Language.objects.get(code = lang)
    except ObjectDoesNotExist:
        status = http_NOT_FOUND
        return HttpResponse(json.dumps({'message': 'Language not found'}), status=status, content_type='application/json')

    try:
        sub = Subtitle.objects.get(house_id = house_id, language = language)
    except ObjectDoesNotExist:
        status = http_NOT_FOUND
        return HttpResponse(json.dumps({'message': 'House ID not found'}), status=status, content_type='application/json')

    try:
        config = Config.objects.get(enabled = 'True')
        sub_path = config.subtitle_path
    except:
        status = http_NOT_FOUND
        return HttpResponse(json.dumps({'message': 'Config not found'}), status=status, content_type='application/json')


    if sub_path.endswith('/'):
        stl_path = sub_path + sub.filename
    else:
        stl_path = sub_path + '/' + sub.filename

    stl_sub = STL()
    try: 
        stl_sub.load(stl_path)
    except:
        status = http_NOT_FOUND
        return HttpResponse(json.dumps({'message': 'STL file not found'}), status=status, content_type='application/json')

    if format in FORMATS:
        stl_str = stl_sub.toString(format, sub.som, sub.timecode_in, sub.timecode_out, sub.adjustment)
    else:
        status = http_NOT_FOUND
        return HttpResponse(json.dumps({'message': 'Incorrect Format'}), status=status, content_type='application/json')

    status = http_REQUEST_OK
    if ret == 'sub' and sub.enabled and stl_str != '':
        return HttpResponse(stl_str, status=status, content_type='octet-stream')
    elif ret == 'check' and sub.enabled and stl_str != '':
        return HttpResponse('', status=status)
    elif ret == 'debug':
        return HttpResponse(stl_str, status=status, content_type='octet-stream')
    else:
        status = http_NOT_FOUND
        return HttpResponse(json.dumps({'message': 'Subtitle not found'}), status=status, content_type='application/json')


def sm_PostSub(request):
    if request.method != 'POST':
        status = http_NOT_FOUND
        return HttpResponse(json.dumps({'message': 'Incorrect METHOD'}), status=status, content_type='application/json')

    try:
        json_data = json.loads(request.body)
    except:
        status = http_NOT_FOUND
        return HttpResponse(json.dumps({'message': 'json loaded failed'}), status=status, content_type='application/json')

    if 'house_id' in json_data.keys():
        house_id = json_data['house_id']
    else:
        status = http_NOT_FOUND
        return HttpResponse(json.dumps({'message': 'house_id not defined'}), status=status, content_type='application/json')

    if 'filename' in json_data.keys():
        filename = json_data['filename']
    else:
        status = http_NOT_FOUND
        return HttpResponse(json.dumps({'message': 'filename not defined'}), status=status, content_type='application/json')

    if 'language' in json_data.keys():
        language = json_data['language']
    else:
        status = http_NOT_FOUND
        return HttpResponse(json.dumps({'message': 'language not defined'}), status=status, content_type='application/json')

    try:
        lang = Language.objects.get(code = language)
    except ObjectDoesNotExist:
        status = http_NOT_FOUND
        return HttpResponse(json.dumps({'message': 'Language not found'}), status=status, content_type='application/json')

    sub = Subtitle()
    sub.house_id = house_id
    sub.language = lang
    sub.filename = filename
    sub.enabled  = True
    sub.save()

    response = {"id": sub.id}
    status = http_POST_OK
    return HttpResponse(json.dumps(response), status=status, content_type='application/json')