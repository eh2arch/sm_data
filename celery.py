from __future__ import absolute_import
from celery import Celery
import redis
import datetime
from pytz import timezone
import feedparser
from datetime import timedelta
from dateutil.tz import tzutc

app = Celery('isi', broker = 'amqp://', backend = 'amqp://', include=['isi.twitter_tasks', 'isi.instagram_tasks'])

app.conf.update(
	BROKER_POOL_LIMIT=None,
	CELERYD_PREFETCH_MULTIPLIER = 1,
	CELERY_ACKS_LATE = True
	#BROKER_CONNECTION_MAX_RETRIES = None,
   # BROKER_TRANSPORT_OPTIONS={"SOCKET_TIMEOUT" : 60}
)

CELERY_ROUTES = {
    'isi.instagram_tasks.get_instagram_attributes': {'queue': 'secondary_queue'},
}

app.conf.CELERYBEAT_SCHEDULE = {
	'instagram-stream-every-60-minutes': {
		'task': 'isi.instagram_tasks.get_instagram_posts',
		'schedule': timedelta(minutes=1),
		'kwargs': ({'lat': 34.0231837184805, 'lng': -118.481569383702, 'radius': 5000})
	},
	'twitter-stream-every-60-minutes': {
		'task': 'isi.twitter_tasks.get_tweets',
		'schedule': timedelta(minutes=60),
		'kwargs': ({'location_bounding_box': [-118.517415, 33.995416, -118.443517, 34.05056]})
	}

}


if __name__ == '__main__':
	app.start()