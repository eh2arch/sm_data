#x -*- coding: utf-8 -*-

import time
import json
import sys
from tasks import insertTweetIntoDB


consumer_key = ''
consumer_secret = ''
access_token = ''
access_secret = ''

from twython import Twython
from twython import TwythonStreamer

twitter = Twython(consumer_key, consumer_secret, access_token, access_secret)

def collect():

    class MyStreamer(TwythonStreamer):

        def on_success(self, tweet):

            if 'retweeted_status' in tweet:
                # Its a retweet, ignore !!
                return

            if 'text' in tweet:
                print '\n\n', '===DEBUG : New Data Point : ', tweet['text'], '\n\n'
                # Push onto celery
                insertTweetIntoDB.delay(tweet)

 
        def on_error(self, status_code, data):
            
            print "Error : ", status_code

            with open("error.log", 'a') as fp:
                fp.write(str(status_code) + "\n")

    stream = MyStreamer(consumer_key, consumer_secret, access_token, access_secret)
    
    print '\n\n', '===DEBUG : Beginning collection', '\n\n'

    stream.statuses.filter(locations = [76.8383, 28.4042, 77.3437, 28.8838])

if __name__ == "__main__":

    while True:
        try:
            collect()
        except KeyboardInterrupt:
            sys.exit()
        except Exception,e:
            print str(e)
            time.sleep(30)
            continue


