from vmutils import stl
import Google
import json

def __joinJsonList (jsonList):
    if jsonList is []:
	return {}

    if len(jsonList) > 1:
	element = json.loads(jsonList[0])
	for js in jsonList[1:]:
	    element_i = json.loads(js)
	    for etrans in element_i['data']['translations']:
		element['data']['translations'].append(etrans)
    else:
	return jsonList[0]

    return element
#    return json.dumps(element)

def translateSubtitle (source, target, json_subtitle, format):
    #
    # Se genera la lista de palabras para Google
    #
    queryString = []
    for jss in json_subtitle:
	queryString.append(jss['text'])

    #
    # Query para hacer la traduccion
    # 
    gt = Google.Translate()
    #
    #
    # Retorna un array de json
    translatedStringsList = gt.translateList(source, target, queryString)

#    translatedString = json.loads( __joinJsonList(translatedStringsList))
    translatedString = __joinJsonList(translatedStringsList)

    if len(json_subtitle) == len(translatedString['data']['translations']):
        i = 0
	for jss in json_subtitle:
	    jss['translatedText'] = translatedString['data']['translations'][i]['translatedText']
	    i = i + 1

    
    if format == 'vtt':
	vtt = 'WEBVTT\n\n'
	for jss in json_subtitle:
	    vtt = vtt + '%s --> %s\n' % (jss['tc_in'], jss['tc_out'])
	    vtt = vtt + '%s\n\n' % jss['translatedText'].encode('utf-8')

    return vtt

