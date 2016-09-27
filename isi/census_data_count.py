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

def get_value(obj, key):
	return_val = obj
	# print key
	# print return_val
	for attr in key.split('.'):
		return_val = return_val[attr]
	return return_val

def count_tract_posts(type_db, db_name=db_twitter_posts, field_name='text', query={'coordinates':{'$ne':None}}):
	prop_list = ['arousal', 'dominance', 'valence', 'sentstrength_positive_sentiment', 'sentstrength_negative_sentiment','likes.count', 'comments.count']
	db_data = db_name.find(query, dict({'coordinates.coordinates':1, 'location':1}.items()+{prop:1 for prop in prop_list}.items()))
	for data_val in db_data:
		try:
			try:
				point = Point(data_val['location']['longitude'], data_val['location']['latitude'])
			except:
				try:
					point = Point(data_val['coordinates']['coordinates'][0], data_val['coordinates']['coordinates'][1])
				except:
					pass
			# check each polygon to see if it contains the point
			for feature in js['features']:
				if type_db not in feature['properties']:
					feature['properties'][type_db] = {}
				if 'count' not in feature['properties'][type_db]:
					feature['properties'][type_db]['count'] = 0.0
				for prop in prop_list:
					if prop not in feature['properties'][type_db]:
						feature['properties'][type_db][prop] = 0.0
						feature['properties'][type_db][prop+'_count'] = 0.0
				polygon = shape(feature['geometry'])
				if polygon.contains(point):
					for prop in prop_list:
						try:
							feature['properties'][type_db][prop] = feature['properties'][type_db][prop] + get_value(data_val, prop)
							feature['properties'][type_db][prop+'_count'] = feature['properties'][type_db][prop+'_count'] + 1.0
						except:
							pass
					feature['properties'][type_db]['count'] = feature['properties'][type_db]['count'] + 1.0
		except:
			# print idx
			# idx=idx+1
			pass

	for feature in js['features']:
		for prop in prop_list:
			try:
				feature['properties'][type_db][prop+'_avg'] = feature['properties'][type_db][prop] / feature['properties'][type_db][prop+'_count']
			except:
				pass

count_tract_posts('twitter_posts')
count_tract_posts('instagram_posts', db_instagram_posts, query={})


with open('tract_data.geojson', 'w') as outfile:
	json.dump(js, outfile)