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
import csv
import string

db_api_keys	= db.collection('api_keys')
db_osn_meta_data = db.collection('osn_meta_data')
db_instagram_posts = db.collection('instagram_posts')
db_instagram_likes = db.collection('instagram_likes')
db_instagram_comments = db.collection('instagram_comments')
db_twitter_posts = db.collection('twitter_posts')
SENTISTRENGTHDIR = '/home/archit/Desktop/codes/SentiStrength/'

def create_wkb_dictionary():
	wkb_words = {}
	with open('Ratings_Warriner_et_al.csv', 'rb') as f:
		reader = csv.DictReader(f)
		for row in reader:
			wkb_words[row['Word']] = {'valence': row['V.Mean.Sum'], 'arousal': row['A.Mean.Sum'], 'dominance': row['D.Mean.Sum']}
	return wkb_words

def do_wkb_analysis(db_name=db_twitter_posts, field_name='text', query={'coordinates':{'$ne':None}}):
	wkb_words = create_wkb_dictionary()
	db_data = db_name.find(query)
	for data_val in db_data:
		text = ''
		if field_name != 'text':
			try:
				text = data_val['caption']['text']
			except:
				pass
		else:
			text = data_val['text']
		text_list = map(lambda x: x.lower().replace('#', ''), text.split())
		valence, dominance, arousal, total_count = [0.0, 0.0, 0.0, 0]
		for word in text_list:
			if word in wkb_words:
				valence = valence + float(wkb_words[word]['valence'])
				dominance = dominance + float(wkb_words[word]['dominance'])
				arousal = arousal + float(wkb_words[word]['arousal'])
				total_count = total_count + 1
		if total_count > 0:
			db_name.update({'_id': data_val['_id']}, {'$set': {'valence': valence/total_count, 'arousal': arousal/total_count, 'dominance': dominance/total_count, 'wkb_sentiment_analysis_flag': True}})

# do_wkb_analysis(db_name=db_twitter_posts)
# do_wkb_analysis(db_name=db_instagram_posts, field_name='caption.text', query={'caption.text':{'$ne':None}})
do_wkb_analysis(db_name=db_instagram_comments, query={})