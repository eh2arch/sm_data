from pymongo import MongoClient
import random

db_client = MongoClient()
db_object = db_client.isi_santa_monica_09_12_2016

def collection(collection_name):
	return db_object[str(collection_name)]

def get_random_record(collection_object):
	num_records = collection_object.count()
	return collection_object[random.randrange(num_records)]
