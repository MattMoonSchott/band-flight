import requests, json, urllib

def getTracks(events):
    for event in events:
        name = urllib.parse.quote(event.name)
        header = {"Authorization" : "Bearer 44f10b7bf4cc45a39a55a7d3d96bc7de"}
        request = 'https://api.spotify.com/v1/search?q=' + name + '&type=artist'
        results = json.loads(requests.get(request, headers=header).text)['artists']
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
