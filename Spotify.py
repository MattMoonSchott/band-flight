def getTracks(events, spotify):
    for event in events:
        results = spotify.search(q=event.name, type="artist", limit=1).get('artists')
        if results['total']:
            id = results['items'][0]['id']
            result = spotify.artist_top_tracks(id).get('tracks')
            if len(result) == 0:
                continue
            event.settname(result[0]['name'])
            event.setsample(result[0]['id'])
            event.isonSpotify()
    return True
