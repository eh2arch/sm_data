from __future__ import absolute_import
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
from shapely.geometry import shape, Point

db_api_keys	= db.collection('api_keys')
db_osn_meta_data = db.collection('osn_meta_data')
db_instagram_posts = db.collection('instagram_posts')
db_instagram_likes = db.collection('instagram_likes')
db_instagram_comments = db.collection('instagram_comments')
db_twitter_posts = db.collection('twitter_posts')

# load GeoJSON file containing sectors
with open('158-00.geojson', 'r') as f:
	js = json.load(f)

def count_tract_posts(db_name=db_twitter_posts, field_name='text', query={'coordinates':{'$ne':None}}):
	db_data = db_name.find(query, {'coordinates.coordinates':1, 'location':1}).limit(10000)
	idx=0
	for data_val in db_data:
		try:
			idx=idx+1
			print idx
			point = Point(data_val['location']['longitude'], data_val['location']['latitude'])
			print point
			# point = Point(data_val['coordinates']['coordinates'][1], data_val['coordinates']['coordinates'][0])
			# check each polygon to see if it contains the point
			for feature in js['features']:
				if 'count' not in feature['properties']:
					feature['properties']['count'] = 0
				polygon = shape(feature['geometry'])
				# print polygon
				if polygon.contains(point):
					feature['properties']['count'] = feature['properties']['count'] + 1
					print 'found'
		except:
			# print idx
			# idx=idx+1
			pass
	with open('158-00_changed_instagram.geojson', 'w') as outfile:
		json.dump(js, outfile)

count_tract_posts(db_instagram_posts, query={})
# count_tract_posts()