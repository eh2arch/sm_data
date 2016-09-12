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

db_api_keys	= db.collection('api_keys')
db_osn_meta_data = db.collection('osn_meta_data')
db_instagram_posts = db.collection('instagram_posts')
db_instagram_likes = db.collection('instagram_likes')
db_instagram_comments = db.collection('instagram_comments')
db_twitter_posts = db.collection('twitter_posts')

print map(lambda x: x['text'], list(db_twitter_posts.find({},{'text':1, '_id':-1}).limit(10)))
for model in [db_twitter_posts]:
	cursor = model.find({})
	for post in cursor:
		# print vaderSentiment(post['text'].encode('utf-8'))
		model.update({'_id': post['_id']}, {'$set': {'vaderSentiment': vaderSentiment(post['text'].encode('utf-8'))}})

for model in [db_instagram_posts]:
	cursor = model.find({}, {'text':1, 'caption.text':1})
	for post in cursor:
		# print vaderSentiment(post['text'].encode('utf-8'))
		try:
			model.update({'_id': post['_id']}, {'$set': {'vaderSentiment': vaderSentiment(post['caption']['text'].encode('utf-8'))}})
		except:
			pass