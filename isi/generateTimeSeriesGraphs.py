from __future__ import absolute_import
import sys
import pandas as pd
import numpy as np
import matplotlib.pylab as plt
from matplotlib.dates import date2num
import pymongo
import database_connector as db
from datetime import datetime
import time
from statsmodels.tsa.stattools import adfuller

from matplotlib.pylab import rcParams
rcParams['figure.figsize'] = 15, 6

db_api_keys	= db.collection('api_keys')
db_osn_meta_data = db.collection('osn_meta_data')
db_instagram_posts = db.collection('instagram_posts')
db_instagram_likes = db.collection('instagram_likes')
db_instagram_comments = db.collection('instagram_comments')
db_twitter_posts = db.collection('twitter_posts')


def create_time_series_plot(db_name, time_field, query={}):
	db_data = list(getattr(sys.modules[__name__], 'db_%s' % db_name).find(query))

	if time_field == 'created_time':
		map(lambda x: x.update({'date_index_temp': datetime.fromtimestamp(float(x[time_field])).isoformat()}), db_data)
	elif time_field == 'created_at':
		map(lambda x: x.update({'date_index_temp': datetime.fromtimestamp(time.mktime(time.strptime(x[time_field],'%a %b %d %H:%M:%S +0000 %Y'))).isoformat()}), db_data)
	elif time_field == 'saved_at':
		map(lambda x: x.update({'date_index_temp': x[time_field]}), db_data)

	data = pd.DataFrame(db_data, columns=['date_index_temp', 'date_index', time_field])
	data['date_index'] = pd.DatetimeIndex(pd.to_datetime(data['date_index_temp']))
	data.index = data['date_index']
	x = [row['date_index'] for index, row in data.iterrows()]

	# Used for the count
	data[db_name] = 1

	data = data.resample('30Min').sum()
	data.plot(label='%s_%s' % (db_name, ''.join(e for e in query if e.isalnum())))
	plt.legend(loc='upper left')
	plt.xlabel('DateTime')
	plt.ylabel('Frequency every 30 minutes')
	plt.gcf().autofmt_xdate()

	# Save the figure
	plt.savefig('%s_frequency_graph_%s_%s.png' % (db_name, datetime.now().strftime("%Y_%m_%d_%H_%M_%S"), ''.join(e for e in query if e.isalnum())))


graph_dbs_list = [['instagram_posts', 'created_time', {}], ['instagram_likes', 'saved_at', {}], ['instagram_comments', 'created_time', {}], ['twitter_posts', 'created_at', {}], [['twitter_posts', 'created_at', {'coordinates':{'$ne':None}}]]]
[create_time_series_plot(db_name, time_field) for (db_name, time_field, query) in graph_dbs_list]