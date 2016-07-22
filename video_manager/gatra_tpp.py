import httplib2
import json


def gatra_tpp (url, content, access_type, video_id):

    method = 'POST'
    header = { 'Content-type': 'application/json' }

    h = httplib2.Http()

    try:
        json_data = json.loads(content)
    except:
        return None

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
        print None

    return response['status']

url = "http://localhost:8080/thirdpartyplay/"
access_type = "none"
video_id = "001545"
content = """{ "token": "f8225387593c20880404b20a98aa205076a1ef06",
            "description": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
            "createdAt": "2016-07-21T18:53:18.653Z",
            "type": {
                     "code": "WEB",
                     "description": "Web"
                    },
            "customer": {
                         "id": "52d542bf66b81471618b4567",
                         "subscriberId": "1311490993",
                         "country": {
                                     "code": "AR",
                                     "description": "Argentina"
                                    },
                         "idp": {
                                "code": "cv",
                                "description": "Cablevision S.A."
                                },
                         "createdAt": "2014-01-14T13:59:27.000Z"
                        }
            }"""
print post_play(url, content, access_type, video_id)
