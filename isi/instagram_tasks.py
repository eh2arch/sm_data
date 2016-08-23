from __future__ import absolute_import
from isi.tasks import app
from bson.objectid import ObjectId
import sys
import redis
import pymongo
import urllib2
import isi.database_connector as db
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

def get_api_key():
	instagram_keys = db_api_keys.find({'api': 'instagram'})
	api_key = db.get_random_record(instagram_keys)
	return api_key

def get_max_timestamp():
	instagram_meta_data = db_osn_meta_data.find_one({'social_network': 'instagram'})
	if instagram_meta_data != None and instagram_meta_data['max_timestamp'] != None:
		return instagram_meta_data['max_timestamp']

def get_instagram_data(base_url):
	media_pre = urllib2.urlopen(base_url,timeout=30)
	media = json.load(media_pre)
	media_pre.close()
	return media

def check_and_get_comments(data):
	if int(data['comments']['count']) != 0:
		InstagramTasks.get_instagram_attributes.delay(data['_id'], media_type='comments')

def check_and_get_likes(data):
	if int(data['likes']['count']) != 0:
		InstagramTasks.get_instagram_attributes.delay(data['_id'], media_type='likes')

# Add _id field to posts and insert instagram_post_id to comments/likes
def process_instagram_data(data, db_name='db_instagram_posts', db_dict=None):
	map(lambda x: x.update({'_id': str(x['id']), 'saved_at': datetime.now().isoformat()}), data)
	if db_dict != None:
		map(lambda x: x.update(db_dict), data)
	try:
		getattr(sys.modules[__name__], db_name).insert(data, continue_on_error=True)
		print 'Data inserted'
	except pymongo.errors.DuplicateKeyError:
		pass

# Get comments, likes for the instagram posts
def post_process_instagram_post_data(data):
	map(check_and_get_comments, data)
	map(check_and_get_likes, data)

class InstagramTasks:

	@app.task(bind=True, max_retries=5, default_retry_delay=5, queue='instagram_search_queue')
	def get_instagram_posts(self, lat=None, lng=None, radius=5000, max_timestamp=None):

		unlocked = False
		lock     = redis.Redis().lock(
			'instagram_posts_%s_%s_%s_%s' % (lat, lng, radius, max_timestamp),
			timeout = 120) # expire in 120 seconds

		try:
			unlocked = lock.acquire(blocking = False)

			if unlocked:
				# Do stuff here
				api_key = get_api_key()
				base_url = 'https://api.instagram.com/v1/media/search?access_token=%s&count=33' % api_key['api_key']
				if lat != None and lng !=None:
					base_url += '&lat=%s&lng=%s&distance=%s' % (lat, lng, radius)
				max_timestamp = max_timestamp or get_max_timestamp()
				if max_timestamp != None:
					base_url += '&max_timestamp=%s' % max_timestamp

				data = get_instagram_data(base_url)['data']

				process_instagram_data(data, db_name='db_instagram_posts')

				new_max_timestamp = str(data[-1]['created_time'])
				db_osn_meta_data.update({'social_network': 'instagram'}, {'$set':{'max_timestamp': new_max_timestamp}}, upsert=True)
				InstagramTasks().get_instagram_posts.delay(lat, lng, radius, new_max_timestamp)

				post_process_instagram_post_data(data)

		except Exception as e:
			print "Error: %s" % e
			traceback.print_exc()
			self.retry(exc=e, countdown=1)
		finally:
			if unlocked:
				lock.release()

	@app.task(bind=True, max_retries=5, default_retry_delay=5, queue='instagram_secondary_queue')
	def get_instagram_attributes(self, media_id, media_type='comments'):
		unlocked = False
		lock     = redis.Redis().lock(
			'instagram_%s_%s' % (media_type, media_id),
			timeout = 120) # expire in 120 seconds

		try:
			unlocked = lock.acquire(blocking = False)

			if unlocked:
				# Do stuff here
				api_key = get_api_key()
				base_url = 'https://api.instagram.com/v1/media/%s/%s?access_token=%s&count=33' % (media_id, media_type, api_key['api_key'])
				data = get_instagram_data(base_url)['data']
				process_instagram_data(data, db_name='db_instagram_%s' % media_type, db_dict={'instagram_post_id': media_id})

		except Exception as e:
			print "Error: %s" % e
			traceback.print_exc()
			self.retry(exc=e, countdown=1)
		finally:
			if unlocked:
				lock.release()
