import requests, json, urllib
from datetime import datetime

API_KEY = "apikey=wVWWl5T2JQmUREhe"


# Event class, stores all info necessary for displaying an event
class SKEvent:
    def __init__(self, name, date, time, evtid, venue, link, addr):
        self.name = name
        self.date = date
        self.time = time
        self.evtid = evtid
        self.venue = venue
        self.addr = addr
        self.sample = "error"
        self.Tname = ""
        self.link = link

    def isonSpotify(self):
        self.onSpotify = True

    def __repr__(self):
        return self.name + " at " + self.venue + " (" + self.date + ")"

    def setsample(self, sample):
        self.sample = sample

    def settname(self, Tname):
        self.Tname = Tname


def gig_find(page, start, end, location):

    # builds a query to the songkick api to find concerts according to search
    base = "http://api.songkick.com/api/3.0/events.json?"
    api = API_KEY
    start = "&min_date=" + start
    end = "&max_date=" + end
    location = "&location=sk:" + str(location)
    page = "&page=" + str(page)
    per_page = "&per_page=5"
    events = []
    r = requests.get(base + api + start + end + location + page + per_page)
    data = json.loads(r.text)['resultsPage']

    # if there are no results return 0
    if len(data['results']) == 0:
        events.append(0)
        return events
    for i in range(len(data['results']['event'])):
        name = data['results']['event'][i]['performance'][0]['artist']['displayName']
        date = data['results']['event'][i]['start']['date']
        date = datetime.strptime(date, "%Y-%m-%d")
        date = date.strftime('%a %d %b %Y')

        # get the time if available
        if data['results']['event'][i]['start']['time'] is None:
            time = "To be confirmed."
        else:
            time = data['results']['event'][i]['start']['time']
            time = datetime.strptime(time, "%H:%M:%S")
            time = time.strftime("%I:%M %p")
        venue = data['results']['event'][i]['venue']['displayName']
        evtid = data['results']['event'][i]['id']
        venid = data['results']['event'][i]['venue']['id']

        # get venue address if available
        if venid:
            addr = get_addr(venid)
        else:
            addr = "Address Unavailable"
        link = data['results']['event'][i]['uri']
        # create a new event object and append to list
        events.append(SKEvent(name, date, time, evtid, venue, link, addr))

    # append the total number of events
    events.append(data['totalEntries'])
    return events


def place_find(term="Boston"):
    # find the location id
    base = "http://api.songkick.com/api/3.0/search/locations.json?"
    api = API_KEY
    location = "&query=" + urllib.parse.quote(term)
    places = []
    r = requests.get(base + api + location)
    data = json.loads(r.text)['resultsPage']
    if data['totalEntries'] == 0:
        places.append(0)
        return places
    count = 0
    for i in data['results']['location']:
        count += 1
        if count == 10:
            break
        metro = i['city']['displayName']
        city = i['metroArea']['displayName'] + ", "

        if not i['metroArea']['displayName'] == metro:
            city = city + metro + ", "
        # set the state if it's available
        if i['metroArea'].get('state'):
            state = i['metroArea']['state']['displayName'] + ", "
        else:
            state = ""
        country = i['metroArea']['country']['displayName']
        pid = i['metroArea']['id']
        places.append({'value': pid, 'label': city + state + country})
    return places


def get_addr(id):
    # find the address of the venue
    top = 'http://api.songkick.com/api/3.0/venues/'
    bottom = '.json?' + API_KEY
    query = top + str(id) + bottom
    r = json.loads(requests.get(query).text)['resultsPage']['results']['venue']
    venue = r['street'] + ", " + r['city']['displayName']
    return venue
