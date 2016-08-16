from __future__ import absolute_import
from isi.celery import app
from bson.objectid import ObjectId
import sys
from celery_once import QueueOnce
import redis
import pymongo
import isi.database_connector as db
import json
import traceback
import datetime
from pytz import timezone
import feedparser
from datetime import timedelta
from dateutil.tz import tzutc
from hashlib import md5

#Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

db_api_keys	= db.collection('api_keys')
db_twitter_posts = db.collection('twitter_posts')

def _get_api_client(api_key):
	#Variables that contains the user credentials to access Twitter API
	access_token = api_key['access_token']
	access_token_secret = api_key['access_token_secret']
	consumer_key = api_key['api_key']
	consumer_secret = api_key['api_secret']

	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	return auth

def get_api_key():
	twitter_keys = db_api_keys.find({'api': 'twitter'})
	api_key = db.get_random_record(twitter_keys)
	return api_key

class StdOutListener(StreamListener):

	def on_data(self, data):
		post_data = json.loads(data)
		post_data['_id'] = str(post_data['id_str'])
		db_twitter_posts.insert(post_data)
		print "Data inserted"
		return True

	def on_error(self, status):
		raise Exception("Twitter Streaming error", str(status))

class TwitterTasks:
	#This is a basic listener that just prints received tweets to stdout.

	@app.task(bind=True, max_retries=None, default_retry_delay=1, base=QueueOnce, once={'graceful': True})
	def get_tweets(self, location_bounding_box=None, search_terms=None):

		try:
			auth = _get_api_client(get_api_key())
			# print(type(location_bounding_box))
			# print location_bounding_box
			#This handles Twitter authentication and the connection to Twitter Streaming API
			l = StdOutListener()
			stream = Stream(auth, l)

			#This line filter Twitter Streams to capture data by search terms or locations
			stream.filter(track=search_terms, locations=location_bounding_box)
		except Exception as e:
			print "Error: %s" % e
			traceback.print_exc()
			self.retry(exc=e, countdown=1)