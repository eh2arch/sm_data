# Usage python weatherVsWKB.py {{index}} 
# index : weather variable (0 index value from SantaMonicaWeather.csv) 
# ex. for mean temp, index = 2

import json
from pymongo import MongoClient
import datetime
import sys

index = int(sys.argv[1])

client = MongoClient('localhost', 27017)
db = client['isi_santa_monica_11_07_2016']

twitterPostCount = db.twitter_posts.count()

cursor = db.twitter_posts.find({'tract_found_flag': True}, {'timestamp_ms': 1, 'created_time': 1, 'arousal': 1, 'valence': 1, 'dominance': 1})
twitterValidPosts = cursor.count()

cursor = db.twitter_posts.find({'wkb_sentiment_analysis_flag' : True}, {'timestamp_ms': 1, 'created_time': 1, 'arousal': 1, 'valence': 1, 'dominance': 1})
wkbAnalysisPosts = cursor.count()

print "Total tweets : ", twitterPostCount
print "Total valid tweets : ", twitterValidPosts, "percentage : ", float(twitterValidPosts)/twitterPostCount * 100
print "WKB analysis scores on tweets : ", wkbAnalysisPosts, "percentage : ", float(wkbAnalysisPosts)/twitterPostCount * 100

with open('SantaMonicaWeather.csv', 'r') as fp:
    data = fp.readlines()[:-1]
    weatherData = data[1:]
    variables = data[0].split(',')
    weatherVariable = variables[index]

weatherVariableValue = {}
seenVariableValues = []

for i in range(len(weatherData)):
    weatherData[i] = weatherData[i].strip('\r\n')
    weatherData[i] = weatherData[i].split(',')
    currDate = weatherData[i][0]

    currDate = datetime.datetime.strptime(weatherData[i][0], '%Y-%m-%d').strftime('%Y-%m-%d')
    weatherVariableValue[currDate] = weatherData[i][index]

    if int(weatherVariableValue[currDate]) not in seenVariableValues:
        seenVariableValues.append(int(weatherVariableValue[currDate]))

valenceValue = {}
arousalValue = {}
dominanceValue = {}
counts = {}

for i in range(min(seenVariableValues) - 5, max(seenVariableValues) + 5):
    valenceValue[i] = 0.
    arousalValue[i] = 0.
    dominanceValue[i] = 0.
    counts[i] = 0.
print weatherVariableValue
for doc in cursor:

    currDate = datetime.datetime.fromtimestamp(int(doc['timestamp_ms'])/1000).strftime('%Y-%m-%d')

    currValue = int(weatherVariableValue[currDate])
    if currValue not in seenVariableValues:
        seenVariableValues.append(currValue)

    valenceValue[currValue] += doc['valence']
    arousalValue[currValue] += doc['arousal']
    dominanceValue[currValue] += doc['dominance']
    counts[currValue] += 1

print '\n\n==== Twitter WKB vs ' + weatherVariable + ' (temp, valence, arousal, dominance, count) ====\n\n'

for i in range(min(seenVariableValues) - 5, max(seenVariableValues) + 5):
    if counts[i] > 0:

        valenceValue[i] /= counts[i]
        arousalValue[i] /= counts[i]
        dominanceValue[i] /= counts[i]

    print i, valenceValue[i], arousalValue[i], dominanceValue[i], counts[i]

print '\n\n'

instagramPostCount = db.instagram_posts.count()
cursor = db.instagram_posts.find({'tract_found_flag': True}, {'timestamp_ms': 1, 'created_time': 1, 'arousal': 1, 'valence': 1, 'dominance': 1})
instagramValidPosts = cursor.count()

cursor = db.instagram_posts.find({'wkb_sentiment_analysis_flag' : True}, {'timestamp_ms': 1, 'created_time': 1, 'arousal': 1, 'valence': 1, 'dominance': 1})
wkbAnalysisPosts = cursor.count()

print "Total intagram posts : ", instagramPostCount
print "Total valid posts : ", instagramValidPosts, "percentage : ", float(instagramValidPosts)/instagramPostCount * 100
print "WKB analysis scores on posts : ", wkbAnalysisPosts, "percentage : ", float(wkbAnalysisPosts)/instagramPostCount * 100

for i in range(min(seenVariableValues) - 5, max(seenVariableValues) + 5):
    valenceValue[i] = 0.
    arousalValue[i] = 0.
    dominanceValue[i] = 0.
    counts[i] = 0.

for doc in cursor:

    currDate = datetime.datetime.fromtimestamp(int(doc['created_time'])).strftime('%Y-%m-%d')

    try:
        currValue = int(weatherVariableValue[currDate])
        if currValue not in seenVariableValues:
            seenVariableValues.append(currValue)
    except:
        continue
    valenceValue[currValue] += doc['valence']
    arousalValue[currValue] += doc['arousal']
    dominanceValue[currValue] += doc['dominance']
    counts[currValue] += 1

print '\n\n==== Instagramr WKB vs ' + weatherVariable + ' (temp, valence, arousal, dominance, count) ====\n\n'

for i in range(min(seenVariableValues) - 5, max(seenVariableValues) + 5):
    if counts[i] > 0:

        valenceValue[i] /= counts[i]
        arousalValue[i] /= counts[i]
        dominanceValue[i] /= counts[i]

    print i, valenceValue[i], arousalValue[i], dominanceValue[i], counts[i]