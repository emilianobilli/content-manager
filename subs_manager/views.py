from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.core.exceptions import *
from django.template import loader
import boto3
import json
import re


# Create your views here.

from models import Config
from models import Language
from models import Subtitle
from models import SubtitleFile

#from stl import STL
from vmutils.stl import STL
from translation import translateSubtitle
from django.contrib.auth.decorators import login_required

http_POST_OK    = 201
http_REQUEST_OK = 200
http_NOT_FOUND  = 404
FORMATS = ['srt', 'vtt', 'json' ]


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
        config = Config.objects.get(enabled = True)
        sub_path = config.subtitle_path
    except:
        status = http_NOT_FOUND
        return HttpResponse(json.dumps({'message': 'Config not found'}), status=status, content_type='application/json')

    stl_sub = STL()
    if config.repository == 'L':
	if sub_path.endswith('/'):
    	    stl_path = sub_path + sub.file.name
	else:
    	    stl_path = sub_path + '/' + sub.file.name
    
	try: 
    	    stl_sub.load(stl_path)
	except:
    	    status = http_NOT_FOUND
    	    return HttpResponse(json.dumps({'message': 'STL file not found'}), status=status, content_type='application/json')
    else:
	try:
	    s3  = boto3.resource('s3',aws_access_key_id=config.aws_access_key, aws_secret_access_key=config.aws_secret_key)
	    obj = s3.Object(sub_path, sub.file.name)
	    stl_sub.fromString(obj.get()['Body'].read())
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
#        return HttpResponse(stl_str, status=status, content_type='octet-stream')
	return HttpResponse(stl_str, status=status, content_type='text/vtt;charset=utf-8')
    elif ret == 'check' and sub.enabled and stl_str != '':
        return HttpResponse('', status=status)
    elif ret == 'debug':
        return HttpResponse(stl_str, status=status, content_type='octet-stream')
    elif ret.startswith('translate'):
	_x, l = ret.split(':')
	status = http_REQUEST_OK
	return HttpResponse(translateSubtitle(lang, l, stl_sub.toString('json',sub.som, sub.timecode_in, sub.timecode_out, sub.adjustment), format), status=status, content_type='application/json')
    else:
        status = http_NOT_FOUND
        return HttpResponse(json.dumps({'message': 'Subtitle not found'}), status=status, content_type='application/json')


@login_required(login_url='/admin/login/')
def sm_UploadFile(request):
    if request.method == 'POST':
        try:
            config = Config.objects.get(enabled = True)
            sub_path = config.subtitle_path
        except:
            status = http_NOT_FOUND
            return HttpResponse('', status=status)
        
        subs = SubtitleFile.objects.filter(name = request.FILES['datafile'].name)
        
        if len(subs) != 0:
            message = {'message':'ERROR: Subtitle already exist.'}
            return TemplateResponse(request, "sub_upload_failed.html", message)
       
        if not request.FILES['datafile'].name.endswith(".stl"):
            message = {'message':'ERROR: Incorrect subtitle extension.'}
            return TemplateResponse(request, "sub_upload_failed.html", message)

	if config.repository == 'L':
	    if handle_uploaded_file(sub_path, request.FILES['datafile']):
        	sub_file = SubtitleFile()
        	sub_file.name = request.FILES['datafile']
        	sub_file.save()
        	return TemplateResponse(request, "sub_upload_ok.html")
#            	return HttpResponseRedirect('/static/front/subtitulos_uploaded_successfully.html')
	    else:
        	message = {'message':'ERROR: Subtitle could not be saved.'}
        	return TemplateResponse(request, "sub_upload_failed.html", message)

	elif config.repository == 'A':
	    if handle_uploaded_file_s3(sub_path, config.aws_access_key, config.aws_secret_key, request.FILES['datafile']):
        	sub_file = SubtitleFile()
        	sub_file.name = request.FILES['datafile']
        	sub_file.save()
        	return TemplateResponse(request, "sub_upload_ok.html")
#            	return HttpResponseRedirect('/static/front/subtitulos_uploaded_successfully.html')
	    else:
        	message = {'message':'ERROR: Subtitle could not be saved.'}
        	return TemplateResponse(request, "sub_upload_failed.html", message)

    return render(request, 'sub_upload.html')


def handle_uploaded_file(path, file):
    full_path = path + file.name
    try:
        with open(full_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        return True
    except:
        return False

def handle_uploaded_file_s3(path, aws_access_key, aws_secret_key, file):
    buffer = None
    try:
	for chunk in file.chunks():
    	    if buffer is None:
		buffer = chunk
	    else:
    		buffer = buffer + chunk

	s3 = boto3.resource('s3',aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
	s3.Bucket(path).put_object(Key=file.name, Body=buffer)
	return True
    except:
	return False


def sm_add_subtitle_page(request):
    subs        = SubtitleFile.objects.all().order_by("-id")
    template    = loader.get_template("sub_files.html")
    context     = { "sub_list": subs, }
    return HttpResponse(template.render(context, request))

@login_required(login_url='/admin/login/')
def sm_home_subtitle_page(request):
    return TemplateResponse(request, 'index.html')


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

    if 'file_id' in json_data.keys():
        file_id = json_data['file_id']
    else:
        status = http_NOT_FOUND
        return HttpResponse(json.dumps({'message': 'file_id not defined'}), status=status, content_type='application/json')

    try:
        file = SubtitleFile.objects.get(id = file_id)
    except ObjectDoesNotExist:
        status = http_NOT_FOUND
        return HttpResponse(json.dumps({'message': 'File ID not found'}), status=status, content_type='application/json')

    if 'language' in json_data.keys():
        language = json_data['language']
    else:
        status = http_NOT_FOUND
        return HttpResponse(json.dumps({'message': 'Language not found'}), status=status, content_type='application/json')

    try:
        lang = Language.objects.get(code = language)
    except ObjectDoesNotExist:
        status = http_NOT_FOUND
        return HttpResponse(json.dumps({'message': 'Language not found'}), status=status, content_type='application/json')

    if 'som' in json_data.keys():
        som = json_data['som']
        if not __valid_timecode(som):
            som = ''
    else:
        som = '00:00:00;00'

    if 'tc_in' in json_data.keys():
        tc_in = json_data['tc_in']
        if not __valid_timecode(tc_in):
            tc_in = ''
    else:
        tc_in = ''

    if 'tc_out' in json_data.keys():
        tc_out = json_data['tc_out']
        if not __valid_timecode(tc_out):
            tc_out = ''
    else:
        tc_out = ''

    if 'adjustment' in json_data.keys():
        adjustment = json_data['adjustment']
        if not __valid_timecode(adjustment):
            adjustment = ''
    else:
        adjustment = ''

    sub = Subtitle()
    sub.house_id     = house_id
    sub.language     = lang
    sub.file         = file
    sub.som          = som
    sub.timecode_in  = tc_in
    sub.timecode_out = tc_out
    sub.adjustment   = adjustment
    sub.enabled      = True
    sub.save()

    response = {"id": sub.id}
    status = http_POST_OK
    return HttpResponse(json.dumps(response), status=status, content_type='application/json')


def sm_HPostSub(request):
    if request.method != 'POST':
        status = http_NOT_FOUND
        return HttpResponse('', status=status)

    if 'house_id' in request.POST.keys():
        house_id = request.POST['house_id']
    else:
        status = http_NOT_FOUND
        return HttpResponse('', status=status)

    if 'file_id' in request.POST.keys():
        file_id = request.POST['file_id']
    else:
        status = http_NOT_FOUND
        return HttpResponse('', status=status)

    try:
        file = SubtitleFile.objects.get(id=file_id)
    except ObjectDoesNotExist:
        status = http_NOT_FOUND
        return HttpResponse('', status=status)

    if 'language' in request.POST.keys():
        language = request.POST['language']
    else:
        status = http_NOT_FOUND
        return HttpResponse('', status=status)

    try:
        lang = Language.objects.get(code=language)
    except ObjectDoesNotExist:
        status = http_NOT_FOUND
        return HttpResponse('', status=status)

    if 'som' in request.POST.keys():
        som = request.POST['som']
        if not __valid_timecode(som):
            som = '00:00:00;00'
    else:
        som = '00:00:00;00'

    if 'tc_in' in request.POST.keys():
        tc_in = request.POST['tc_in']
        if not __valid_timecode(tc_in):
            tc_in = ''
    else:
        tc_in = ''

    if 'tc_out' in request.POST.keys():
        tc_out = request.POST['tc_out']
        if not __valid_timecode(tc_out):
            tc_out = ''
    else:
        tc_out = ''

    if 'adjustment' in request.POST.keys():
        adjustment = request.POST['adjustment']
        if not __valid_timecode(adjustment):
            adjustment = ''
    else:
        adjustment = ''

    sub = Subtitle()
    sub.house_id = house_id
    sub.language = lang
    sub.file = file
    sub.som = som
    sub.timecode_in = tc_in
    sub.timecode_out = tc_out
    sub.adjustment = adjustment
    sub.enabled = True
    sub.save()

    status = http_POST_OK
    return HttpResponse('', status=status)

def __valid_timecode(tc):
    valid = re.match("([0-9][0-9]):([0-5][0-9]):([0-5][0-9])(;|:)([0-2][0-9])", tc)
    if valid:
        return True
    else:
        return False