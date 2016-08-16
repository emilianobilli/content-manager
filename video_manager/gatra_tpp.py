import httplib2
import json


def gatra_tpp (url, json_data, access_type, video_id):

    method = 'POST'
    header = { 'Content-type': 'application/json' }

    h = httplib2.Http()

    #try:
    #json_data = json.loads(content)
    #except:
    #    return None

    if 'title' in json_data.keys():
        title = json_data['title']
    else:
        title = None
    user_id         = json_data['customer']['subscriberId']
    if 'season' in json_data.keys():
        season = json_data['season']
    else:
        season = None
    if 'episode' in json_data.keys():
        episode = json_data['episode']
    else:
        episode = None
    if 'duration' in json_data.keys():
        duration = json_data['duration']
    else:
        duration = None
    device_type     = json_data['type']['description']
    user_agent      = json_data['description']
    if 'ip_source' in json_data.keys():
        ip_source = json_data['ip_source']
    else:
        ip_source = None
    access          = access_type
    country         = json_data['customer']['country']['code']
    idp             = json_data['customer']['idp']['code']
    idp_name        = json_data['customer']['idp']['description']
    user_name       = country + "_" + idp + "_" + user_id
    media_id        = video_id
    if 'media_filename' in json_data.keys():
        media_filename = json_data['media_filename']
    else:
        media_filename = None
    if 'media_type' in json_data.keys():
        media_type = json_data['media_type']
    else:
        media_type = None

    content = {
                "title": title,
                "user_id": user_id,
                "season": season,
                "episode": episode,
                "duration": duration,
                "device_type": device_type,
                "user_agent": user_agent,
                "ip_souce": ip_source,
                "access": access,
                "country": country,
                "idp": idp,
                "idp_name": idp_name,
                "user_name": user_name,
                "media_id": media_id,
                "media_filename": media_filename,
                "media_type": media_type
              }

    try:
	response = h.request(url, method, json.dumps(content), header)
    except:
        return None

    return response[0]['status']
