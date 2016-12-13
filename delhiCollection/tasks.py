from pymongo import MongoClient
from celery import Celery

import json
from shapely.geometry import shape, Point
import requests

import csv
app = Celery('twitterCollecter', broker='redis://localhost:6379/0')

client = MongoClient('localhost', 27017)
db = client['kushUSC']

""" Adding tracts """

# load GeoJSON file containing sectors
with open('districts.json', 'r') as f:
    districtsJson = json.load(f)

def findTract(latitude, longitude):

    point = Point(longitude, latitude)

    for feature in districtsJson['features']:
        polygon = shape(feature['geometry'])
        if polygon.contains(point):
            return feature['properties']['DISTRICT']

def addTractToTweet(tweet):

    latitude = tweet['coordinates']['coordinates'][1]
    longitude = tweet['coordinates']['coordinates'][0]

    tweet['tract'] = findTract(latitude, longitude)

    return tweet

""" WKB count """

wkb_words = {}

with open('Ratings_Warriner_et_al.csv', 'rb') as f:
    reader = csv.DictReader(f)
    for row in reader:
        wkb_words[row['Word']] = {'valence': row['V.Mean.Sum'],\
        						  'arousal': row['A.Mean.Sum'],\
        						  'dominance': row['D.Mean.Sum']}

def wkbAnalysis(tweet):

    text = tweet['text']
    allTokens = map(lambda x: x.lower().replace('#', ''), text.split())
    valence, dominance, arousal, total_count = [0.0, 0.0, 0.0, 0]
    count = 0

    for token in allTokens:
        if token in wkb_words:
            valence += float(wkb_words[token]['valence'])
            dominance += float(wkb_words[token]['dominance'])
            arousal += float(wkb_words[token]['arousal'])
            count = count + 1

    if count > 0:
    	tweet['valence'] = valence/count
    	tweet['arousal'] = arousal/count
    	tweet['dominance'] = dominance/count
    	tweet['wkb_sentiment_analysis_flag'] = True

    return tweet


@app.task
def insertTweetIntoDB(tweet):

    if tweet['coordinates'] is not None:

    	""" decide tract """

        tweet = addTractToTweet(tweet)
        tweet = wkbAnalysis(tweet)

    db.twitter_stream.save(tweet)
    print '\n\n', '===DEBUG : Inserted', '\n\n'


@app.task
def collectFromInstagram(accessToken, latitude, longitude):

    url_ = "https://api.instagram.com/v1/media/search?lat=" + \
            str(latitude) + "&lng=" + str(longitude) + \
            "&count=33&distance=5000&access_token=" + str(accessToken)

    print '\n\n', '===DEBUG : Instagram URL : ', url_, '\n\n'

    response = requests.get(url = url_, headers={'Connection':'close'})
    jsonResponse = json.loads(response.content)

    code = jsonResponse['meta']['code']

    if int(code) == 429:
        with open('error.log', 'a') as fp:
            fp.write('Too many requests\n' + url_ + '\n' + str(jsonResponse) + '\n\n')

    data = jsonResponse['data']

    for post in data:

        if db.instagram.find({'id' : post['id']}).count() > 0:
            continue

        latitude = post['location']['latitude']
        longitude = post['location']['longitude']

        post['tract'] = findTract(latitude, longitude)

        if 'caption' not in post:
            continue

	if post['caption'] is None:
            continue

        text = post['caption']['text']

        allTokens = map(lambda x: x.lower().replace('#', ''), text.split())
        valence, dominance, arousal, total_count = [0.0, 0.0, 0.0, 0]
        count = 0

        for token in allTokens:
            if token in wkb_words:
                valence += float(wkb_words[token]['valence'])
                dominance += float(wkb_words[token]['dominance'])
                arousal += float(wkb_words[token]['arousal'])
                count = count + 1

        if count > 0:
            post['valence'] = valence / count
            post['arousal'] = arousal / count
            post['dominance'] = dominance / count
            post['wkb_sentiment_analysis_flag'] = True

        db.instagram.save(post)
        print '\n\n', '===DEBUG : Inserted Instagram post', '\n\n'

    # db.instagram.update({'id' : int(post['id'])}, post, upsert = True)

