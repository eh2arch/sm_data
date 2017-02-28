from __future__ import absolute_import
from bson.objectid import ObjectId
import re
import csv
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
from copy import deepcopy

db_api_keys	= db.collection('api_keys')
db_osn_meta_data = db.collection('osn_meta_data')
db_instagram_posts = db.collection('instagram_posts')
db_instagram_likes = db.collection('instagram_likes')
db_instagram_comments = db.collection('instagram_comments')
db_twitter_posts = db.collection('twitter_posts')

# load GeoJSON file containing sectors
with open('tract_data_news_2014_polices.geojson') as f:
	js = json.load(f)
	# js_copy = deepcopy(js)
	# police_incidents_hash = {}
	# # def correct_prop_names():
	# js_copy = deepcopy(js)
	# for idx, feature in enumerate(js['features']):
	# 	for type_db in ['twitter_posts', 'instagram_posts']:
	# 		if type_db not in feature['properties']:
	# 			feature['properties'][type_db] = {}
	# 		for key in feature['properties'][type_db]:
	# 			new_key = key.replace(' ','_').replace('-','_').replace('/','_')
	# 			js_copy['features'][idx]['properties'][type_db][new_key] = feature['properties'][type_db][key]
	# 			if key != new_key:
	# 				police_incidents_hash[new_key] = 0
	# js = js_copy
	# # correct_prop_names()
	# print police_incidents_hash
	# with open('tract_data_news_2014_polices.geojson', 'w') as outfile:
	# 	json.dump(js, outfile)

# f = open('full.matrix1.csv', 'rb')
# reader = csv.reader(f)
# headers = reader.next()

police_incidents_hash = {}
with open('Police_Incidents_2014.csv') as csvfile:
	reader_police = csv.DictReader(csvfile)

	def police_incidents_into_tracts():
		for reader in reader_police:
			if reader['Latitude'] and reader['Longitude']:
				# print reader
				# prop_list = ["%s_%s" % (reader['UCR'], reader['UCR Description'])]
				police_incidents_hash["%s_%s" % (reader['UCR'], reader['UCR Description'])] = 0
				point = Point(float(reader['Longitude']), float(reader['Latitude']))
				# check each polygon to see if it contains the point
				for feature in js['features']:
					for type_db in ['twitter_posts', 'instagram_posts']:
						if type_db not in feature['properties']:
							feature['properties'][type_db] = {}
						if 'gang_related' not in feature['properties'][type_db]:
							feature['properties'][type_db]['gang_related'] = 0.0
						if 'gang_unrelated' not in feature['properties'][type_db]:
							feature['properties'][type_db]['gang_unrelated'] = 0.0							
						# for prop in prop_list:
						# 	if prop not in feature['properties'][type_db]:
						# 		feature['properties'][type_db][prop] = 0.0
						polygon = shape(feature['geometry'])
						if polygon.contains(point):
							# print reader['Gang Related'].__class__.__name__
							if reader['Gang Related'] == 'true':
								try:
									feature['properties'][type_db]['gang_related'] = feature['properties'][type_db]['gang_related'] + 1.0
								except:
									pass
							elif reader['Gang Related'] == 'false':
								try:
									feature['properties'][type_db]['gang_unrelated'] = feature['properties'][type_db]['gang_unrelated'] + 1.0
								except:
									pass
							# for prop in prop_list:
							# 	try:
							# 		feature['properties'][type_db][prop] = feature['properties'][type_db][prop] + 1.0
							# 	except:
							# 		pass
							# feature['properties'][type_db]['count'] = feature['properties'][type_db]['count'] + 1.0
	police_incidents_into_tracts()
	with open('tract_data_news_2014_policess.geojson', 'w') as outfile:
		json.dump(js, outfile)	

def correct_prop_names():
	# js_copy = deepcopy(js)
	for idx, feature in enumerate(js['features']):
		for type_db in ['twitter_posts', 'instagram_posts']:
			if type_db not in feature['properties']:
				feature['properties'][type_db] = {}
			for key in feature['properties'][type_db]:
				new_key = key.replace(' ','_').replace('-','_').replace('/','_')
				js_copy['features'][idx]['properties'][type_db][new_key] = feature['properties'][type_db][key]
				if key != new_key:
					police_incidents_hash[new_key] = 0
	js = js_copy
# correct_prop_names()
# print police_incidents_hash

def get_value(obj, key):
	return_val = obj
	# print key
	# print return_val
	for attr in key.split('.'):
		return_val = return_val[attr]
	return return_val

def count_tract_posts(type_db, db_name=db_twitter_posts, field_name='text', query={'coordinates':{'$ne':None}}):
	# prop_list = ['arousal', 'dominance', 'valence', 'sentstrength_positive_sentiment', 'sentstrength_negative_sentiment','likes.count', 'comments.count']
	prop_list = ['arousal', 'dominance', 'valence']
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

# count_tract_posts('twitter_posts')
print 'done'
# count_tract_posts('instagram_posts', db_instagram_posts, query={'coordinates':{'$ne':None}})

def get_census_data():
	for row in reader:
		tract_no = row[1]
		for feature in js['features']:
			for type_db in ['twitter_posts', 'instagram_posts']:
				for header in headers[2:]:
					if header.replace('.','_') not in feature['properties'][type_db]:
						feature['properties'][type_db][header.replace('.','_')] = 0.0
				if (feature['properties']['TRACT'] == re.sub(r'[^\w\s]','',tract_no))or(feature['properties']['TRACT'] == re.sub(r'[^\w\s]','',tract_no)+'00'):
					# print dict(zip([g.replace('.','_') for g in headers[2:]],map(float,row[2:])))
					feature['properties'][type_db].update(dict(zip([g.replace('.','_') for g in headers[2:]],map(float,row[2:]))))

# get_census_data()

# with open('tract_data_newssss.geojson', 'w') as outfile:
# 	json.dump(js, outfile)

def update_tract_data(db_name='twitter_posts'):
	if(db_name=='twitter_posts'):
		data = getattr(sys.modules[__name__], 'db_%s' % db_name).find({'tract_found_flag': {'$exists': False}, 'wkb_sentiment_analysis_flag': True, 'coordinates':{'$ne':None}, 'coordinates.coordinates': {'$geoWithin': {'$center': [ [ -118.481569383702, 34.0231837184805 ], (float(5.0))/111.12 ] } } }, {'coordinates.coordinates':1, 'location':1})#, 'created_time': 1, 'sentstrength_negative_sentiment': 1, 'sentstrength_positive_sentiment':1})))
	else:
		data = getattr(sys.modules[__name__], 'db_%s' % db_name).find({'tract_found_flag': {'$exists': False}, 'wkb_sentiment_analysis_flag': True, 'coordinates':{'$ne':None}, 'coordinates.coordinates': {'$geoWithin': {'$center': [ [ -118.481569383702, 34.0231837184805 ], (float(5.0))/111.12 ] } } }, {'coordinates.coordinates':1, 'location':1})#, 'created_time': 1, 'sentstrength_negative_sentiment': 1, 'sentstrength_positive_sentiment':1})))
	for data_val in data:
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
				polygon = shape(feature['geometry'])
				if polygon.contains(point):
					# print feature['properties']['TRACT']
					getattr(sys.modules[__name__], 'db_%s' % db_name).update({'_id': data_val['_id']}, {'$set': {'tract_no':feature['properties']['TRACT'], 'tract_found_flag': True}})
		except:
			# print idx
			# idx=idx+1
			pass
# update_tract_data()			
# update_tract_data(db_name='instagram_posts')