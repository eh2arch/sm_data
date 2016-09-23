from __future__ import absolute_import
from vaderSentiment.vaderSentiment import sentiment as vaderSentiment
from bson.objectid import ObjectId
import sys
import pymongo
import database_connector as db
import json
import traceback
from datetime import datetime
from pytz import timezone
import feedparser
from datetime import timedelta
from dateutil.tz import tzutc
from hashlib import md5
from subprocess import Popen, PIPE, STDOUT

db_api_keys	= db.collection('api_keys')
db_osn_meta_data = db.collection('osn_meta_data')
db_instagram_posts = db.collection('instagram_posts')
db_instagram_likes = db.collection('instagram_likes')
db_instagram_comments = db.collection('instagram_comments')
db_twitter_posts = db.collection('twitter_posts')
SENTISTRENGTHDIR = '/home/archit/Desktop/codes/SentiStrength/'

def get_sentistrength_sentiment(text):
	p = Popen(['java', '-jar', './SentiStrength.jar', 'sentidata', './data/', 'text', text], stdout=PIPE, stderr=STDOUT, cwd=SENTISTRENGTHDIR)
	for line in p.stdout:
		return map(int, line.split())

def make_sentiment(line):
	return map(int, line.split()[0:2])

# # print map(lambda x: x['text'], list(db_twitter_posts.find({},{'text':1, '_id':-1}).limit(10)))
# for model in [db_twitter_posts]:
# 	cursor = model.find({'coordinates':{'$ne':None}})
# 	for post in cursor:
# 		# print json.dumps(post['text'].encode('utf-8'))
# 		# sentiment = get_sentistrength_sentiment(post['text'].encode('utf-8'))
# 		# print vaderSentiment(post['text'].encode('utf-8'))
# 		model.update({'_id': post['_id']}, {'$set': {'sentstrength_positive_sentiment': sentiment[0], 'sentstrength_negative_sentiment': sentiment[1]}})

# for model in [db_instagram_posts]:
# 	cursor = model.find({'caption.text':{'$ne':None}}, {'text':1, 'caption.text':1})
# 	for post in cursor:
# 		# print vaderSentiment(post['text'].encode('utf-8'))
# 		if 'caption' in post and post['caption'] is not None:
# 			try:
# 				print json.dumps(post['caption']['text'].encode('utf-8'))
# 				# sentiment = get_sentistrength_sentiment(post['caption']['text'].encode('utf-8'))
# 				# model.update({'_id': post['_id']}, {'$set': {'sentstrength_positive_sentiment': sentiment[0], 'sentstrength_negative_sentiment': sentiment[1]}})
# 			except:

# 				pass

# for model in [db_instagram_comments]:
# 	cursor = model.find({}, {'text':1})
# 	for post in cursor:
# 		# sentiment = get_sentistrength_sentiment(post['text'].encode('utf-8'))
# 		print json.dumps(post['text'].encode('utf-8'))
# 		# # print vaderSentiment(post['text'].encode('utf-8'))
# 		# model.update({'_id': post['_id']}, {'$set': {'sentstrength_positive_sentiment': sentiment[0], 'sentstrength_negative_sentiment': sentiment[1]}})

for model, query, file_name in [[db_instagram_comments, {}, 'instagram_comments0_out.txt']]:#, [db_twitter_posts, {'coordinates':{'$ne':None}}, 'twitter_posts0_out.txt']]:#, [db_instagram_posts, {'caption.text':{'$ne':None}}, 'instagram_posts0_out.txt']]:
	with open(file_name) as f:
		contents = f.readlines()
	contents = contents[1:]
	cursor = model.find(query)
	# print cursor.count()
	# print len(contents)
	idx = 0
	for post in cursor:
		print idx
		sentiment = make_sentiment(contents[idx])
		model.update({'_id': post['_id']}, {'$set': {'sentstrength_positive_sentiment': sentiment[0], 'sentstrength_negative_sentiment': sentiment[1]}})
		idx = idx + 1

# for model, query, file_name in [[db_instagram_posts, {'caption.text':{'$ne':None}}, 'instagram_posts0_out.txt']]:
# 	with open(file_name) as f:
# 		contents = f.readlines()
# 	contents = contents[1:]
# 	cursor = model.find(query)
# 	print cursor.count()
# 	print len(contents)
	# idx = 0
	# for post in cursor:
	# 	if 'caption' in post and post['caption'] is not None:
	# 		try:
	# 			post['caption']['text'].encode('utf-8')
	# 			sentiment = make_sentiment(contents[idx])
	# 			model.update({'_id': post['_id']}, {'$set': {'sentstrength_positive_sentiment': sentiment[0], 'sentstrength_negative_sentiment': sentiment[1]}})
	# 			idx = idx + 1
	# 		except:
	# 			pass