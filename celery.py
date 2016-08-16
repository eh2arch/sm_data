from __future__ import absolute_import
from celery import Celery
from celery_once import QueueOnce
import redis
import datetime
from pytz import timezone
import feedparser
from datetime import timedelta
from dateutil.tz import tzutc

app = Celery('isi', broker = 'amqp://', backend = 'amqp://', include=['isi.twitter_tasks'])
app.conf.ONCE_REDIS_URL = 'redis://localhost:6379/0'
app.conf.ONCE_DEFAULT_TIMEOUT = 60 * 60 # Lock expires in 10 minutes

app.conf.update(
	BROKER_POOL_LIMIT=None,
	CELERYD_PREFETCH_MULTIPLIER = 1,
	CELERY_ACKS_LATE = True
	#BROKER_CONNECTION_MAX_RETRIES = None,
   # BROKER_TRANSPORT_OPTIONS={"SOCKET_TIMEOUT" : 60}
)

app.conf.CELERYBEAT_SCHEDULE = {
	'twitter-stream-every-60-minutes': {
		'task': 'isi.twitter_tasks.get_tweets',
		'schedule': timedelta(minutes=1),
		'kwargs': ({'location_bounding_box': [-118.517415, 33.995416, -118.443517, 34.05056]})
	}
}


if __name__ == '__main__':
	app.start()