from __future__ import absolute_import
from isi.tasks import app
from bson.objectid import ObjectId
import sys
import redis
import pymongo
import isi.database_connector as db
import json
import traceback
from datetime import datetime
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

	# After getting data from twitter stream
	def on_data(self, data):
		post_data = json.loads(data)
		post_data['_id'] = str(post_data['id_str'])
		post_data['saved_at'] = datetime.now().isoformat()
		try:
			db_twitter_posts.insert(post_data, continue_on_error=True)
		except pymongo.errors.DuplicateKeyError:
			pass
		print "Data inserted"
		return True

	def on_error(self, status):
		raise Exception("Twitter Streaming error", str(status))

class TwitterTasks:
	#This is a basic listener that just prints received tweets to stdout.

	@app.task(bind=True, max_retries=5, default_retry_delay=5, queue='twitter_streaming_queue')
	def get_tweets(self, location_bounding_box=None, search_terms=None):

		unlocked = False
		lock     = redis.Redis().lock(
			'twitter_stream_%s_%s' % (location_bounding_box, search_terms),
			timeout = 600) # expire in 600 seconds

		try:
			unlocked = lock.acquire(blocking = False)

			if unlocked:
				# Do stuff here
				auth = _get_api_client(get_api_key())
				# print(type(location_bounding_box))
				# print location_bounding_box
				#This handles Twitter authentication and the connection to Twitter Streaming API
				l = StdOutListener()
				stream = Stream(auth, l)

				#This line filter Twitter Streams to capture data by locations or search terms
				stream.filter(locations=location_bounding_box, track=search_terms)
		except Exception as e:
			print "Error: %s" % e
			traceback.print_exc()
			self.retry(exc=e, countdown=1)
		finally:
			if unlocked:
				lock.release()