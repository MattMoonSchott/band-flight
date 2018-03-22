import requests, json, urllib
from config import client_id, client_secret

def getTracks(events):
    for event in events:
        name = urllib.parse.quote(event.name)
        authorization = base64.standard_b64encode(client_id + ':' + client_secret)

        headers = {'Authorization' : 'Basic ' + authorization} 
        request = 'https://api.spotify.com/v1/search?q=' + name + '&type=artist'
        request = requests.get(request, headers=headers).text
        results = json.loads(request).get('artists')
        if not results:
            print(request)
            return False
        if results['total'] > 0:
            id = results['items'][0]['id']
            request = 'https://api.spotify.com/v1/artists/'+ id +'/top-tracks?country=US'
            result = json.loads(requests.get(request).text)['tracks']
            if len(result) == 0:
                continue
            event.settname(result[0]['name'])
            event.setsample(result[0]['id'])
            event.isonSpotify()
    return True
