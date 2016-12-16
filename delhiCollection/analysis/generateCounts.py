import json
from pymongo import MongoClient
import datetime

client = MongoClient('localhost', 27017)
db = client['kushUSC']

twitterPostCount = db.twitter_stream.count()

cursor = db.twitter_stream.find({'tract' : {'$exists' : True}})
twitterValidPosts = cursor.count()

cursor = db.twitter_stream.find({'wkb_sentiment_analysis_flag' : True})
wkbAnalysisPosts = cursor.count()

print "Total tweets : ", twitterPostCount
print "Total valid tweets : ", twitterValidPosts, "percentage : ", float(twitterValidPosts)/twitterPostCount * 100
print "WKB analysis scores on tweets : ", wkbAnalysisPosts, "percentage : ", float(wkbAnalysisPosts)/twitterPostCount * 100

twitterDailyCount = {}

print cursor[0]['timestamp_ms']

for doc in cursor:

	currDate = datetime.datetime.fromtimestamp(int(doc['timestamp_ms'])/1000).strftime('%Y-%m-%d')
	if currDate not in twitterDailyCount:
		twitterDailyCount[currDate] = 0

	twitterDailyCount[currDate] += 1

print "==== Twitter Counts ====\n\n"
for date in twitterDailyCount:
	print date, twitterDailyCount[date]

print '\n\n'

instagramPostCount = db.instagram.count()
cursor = db.instagram.find({'tract' : {'$exists' : True}})
instagramValidPosts = cursor.count()

cursor = db.instagram.find({'wkb_sentiment_analysis_flag' : True})
wkbAnalysisPosts = cursor.count()

print "Total intagram posts : ", instagramPostCount
print "Total valid posts : ", instagramValidPosts, "percentage : ", float(instagramValidPosts)/instagramPostCount * 100
print "WKB analysis scores on posts : ", wkbAnalysisPosts, "percentage : ", float(wkbAnalysisPosts)/instagramPostCount * 100

instagramDailyCount = {}

for doc in cursor:
	currDate = datetime.datetime.fromtimestamp(int(doc['created_time'])).strftime('%Y-%m-%d')
	if currDate not in instagramDailyCount:
		instagramDailyCount[currDate] = 0

	instagramDailyCount[currDate] += 1

print "==== Instagram Counts ====\n\n"

for date in instagramDailyCount:
	print date, instagramDailyCount[date]



