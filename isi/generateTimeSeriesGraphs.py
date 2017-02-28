from __future__ import absolute_import
import re
import sys
import pandas as pd
import pytz
import numpy as np
import matplotlib.pylab as plt
from pylab import text
from matplotlib.dates import date2num
import collections
import pymongo
import scipy.stats as st
import database_connector as db
from datetime import datetime
import time
# from statsmodels.tsa.stattools import adfuller
import json
from wordcloud import WordCloud, STOPWORDS
from bson.code import Code
from matplotlib.pylab import rcParams
from collections import defaultdict
import csv
import string
import seaborn as sns; sns.set(color_codes=True)
import matplotlib
from matplotlib.pyplot import xcorr
from pandas.tools.plotting import autocorrelation_plot
from statsmodels.graphics.tsaplots import plot_acf
from pandas.compat import range, lrange, lmap, map, zip, string_types
matplotlib.style.use('ggplot')
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


def create_instagram_graphs(db_name, field, query={}):
	reducer = Code("""function(obj, prev){ prev.count++;}""")
	db_data = list(getattr(sys.modules[__name__], 'db_%s' % db_name).group(key={field:1}, condition={}, initial={"count": 0}, reduce=reducer))
	# print db_data
	df = pd.DataFrame(db_data)
	# print df
	data = df.groupby('count').count()
	data.plot(label='%s_%s' % (db_name, ''.join(e for e in query if e.isalnum())))
	plt.legend(loc='upper left')
	plt.xlabel('No of %s' % field)
	plt.ylabel('No of posts')
	# plt.show()

# def create_word_cloud(json_file, field_name='text', query={}):
def create_word_cloud(db_name='twitter_posts', field_name='text', query={}):
	stop_words = ['https', 'co', "rt", "amp", "able" , "about" , "above" , "abroad" , "according" , "accordingly" , "across" , "actually" , "adj" , "after" , "afterwards" , "again" , "against" , "ago" , "ahead" , "ain't" , "all" , "allow" , "allows" , "almost" , "alone" , "along" , "alongside" , "already" , "also" , "although" , "always" , "am" , "amid" , "amidst" , "among" , "amongst" , "an" , "and" , "another" , "any" , "anybody" , "anyhow" , "anyone" , "anything" , "anyway" , "anyways" , "anywhere" , "apart" , "appear" , "appreciate" , "appropriate" , "are" , "aren't" , "around" , "as" , "a's" , "aside" , "ask" , "asking" , "associated" , "at" , "available" , "away" , "awfully" , "back" , "backward" , "backwards" , "be" , "became" , "because" , "become" , "becomes" , "becoming" , "been" , "before" , "beforehand" , "begin" , "behind" , "being" , "believe" , "below" , "beside" , "besides" , "best" , "better" , "between" , "beyond" , "both" , "brief" , "but" , "by" , "came" , "can" , "cannot" , "cant" , "can't" , "caption" , "cause" , "causes" , "certain" , "certainly" , "changes" , "clearly" , "c'mon" , "co" , "co." , "com" , "come" , "comes" , "concerning" , "consequently" , "consider" , "considering" , "contain" , "containing" , "contains" , "corresponding" , "could" , "couldn't" , "course" , "c's" , "currently" , "dare" , "daren't" , "definitely" , "described" , "despite" , "did" , "didn't" , "different" , "directly" , "do" , "does" , "doesn't" , "doing" , "done" , "don't" , "down" , "downwards" , "during" , "each" , "edu" , "eg" , "eight" , "eighty" , "either" , "else" , "elsewhere" , "end" , "ending" , "enough" , "entirely" , "especially" , "et" , "etc" , "even" , "ever" , "evermore" , "every" , "everybody" , "everyone" , "everything" , "everywhere" , "ex" , "exactly" , "example" , "except" , "fairly" , "far" , "farther" , "few" , "fewer" , "fifth" , "first" , "five" , "followed" , "following" , "follows" , "for" , "forever" , "former" , "formerly" , "forth" , "forward" , "found" , "four" , "from" , "further" , "furthermore" , "get" , "gets" , "getting" , "given" , "gives" , "go" , "goes" , "going" , "gone" , "got" , "gotten" , "greetings" , "had" , "hadn't" , "half" , "happens" , "hardly" , "has" , "hasn't" , "have" , "haven't" , "having" , "he" , "he'd" , "he'll" , "hello" , "help" , "hence" , "her" , "here" , "hereafter" , "hereby" , "herein" , "here's" , "hereupon" , "hers" , "herself" , "he's" , "hi" , "him" , "himself" , "his" , "hither" , "hopefully" , "how" , "howbeit" , "however" , "hundred" , "i'd" , "ie" , "if" , "ignored" , "i'll" , "i'm" , "immediate" , "in" , "inasmuch" , "inc" , "inc." , "indeed" , "indicate" , "indicated" , "indicates" , "inner" , "inside" , "insofar" , "instead" , "into" , "inward" , "is" , "isn't" , "it" , "it'd" , "it'll" , "its" , "it's" , "itself" , "i've" , "just" , "k" , "keep" , "keeps" , "kept" , "know" , "known" , "knows" , "last" , "lately" , "later" , "latter" , "latterly" , "least" , "less" , "lest" , "let" , "let's" , "like" , "liked" , "likely" , "likewise" , "little" , "look" , "looking" , "looks" , "low" , "lower" , "ltd" , "made" , "mainly" , "make" , "makes" , "many" , "may" , "maybe" , "mayn't" , "me" , "mean" , "meantime" , "meanwhile" , "merely" , "might" , "mightn't" , "mine" , "minus" , "miss" , "more" , "moreover" , "most" , "mostly" , "mr" , "mrs" , "much" , "must" , "mustn't" , "my" , "myself" , "name" , "namely" , "nd" , "near" , "nearly" , "necessary" , "need" , "needn't" , "needs" , "neither" , "never" , "neverf" , "neverless" , "nevertheless" , "new" , "next" , "nine" , "ninety" , "no" , "nobody" , "non" , "none" , "nonetheless" , "noone" , "no-one" , "nor" , "normally" , "not" , "nothing" , "notwithstanding" , "novel" , "now" , "nowhere" , "obviously" , "of" , "off" , "often" , "oh" , "ok" , "okay" , "old" , "on" , "once" , "one" , "ones" , "one's" , "only" , "onto" , "opposite" , "or" , "other" , "others" , "otherwise" , "ought" , "oughtn't" , "our" , "ours" , "ourselves" , "out" , "outside" , "over" , "overall" , "own" , "particular" , "particularly" , "past" , "per" , "perhaps" , "placed" , "please" , "plus" , "possible" , "presumably" , "probably" , "provided" , "provides" , "que" , "quite" , "qv" , "rather" , "rd" , "re" , "really" , "reasonably" , "recent" , "recently" , "regarding" , "regardless" , "regards" , "relatively" , "respectively" , "right" , "round" , "said" , "same" , "saw" , "say" , "saying" , "says" , "second" , "secondly" , "see" , "seeing" , "seem" , "seemed" , "seeming" , "seems" , "seen" , "self" , "selves" , "sensible" , "sent" , "serious" , "seriously" , "seven" , "several" , "shall" , "shan't" , "she" , "she'd" , "she'll" , "she's" , "should" , "shouldn't" , "since" , "six" , "so" , "some" , "somebody" , "someday" , "somehow" , "someone" , "something" , "sometime" , "sometimes" , "somewhat" , "somewhere" , "soon" , "sorry" , "specified" , "specify" , "specifying" , "still" , "sub" , "such" , "sup" , "sure" , "take" , "taken" , "taking" , "tell" , "tends" , "th" , "than" , "thank" , "thanks" , "thanx" , "that" , "that'll" , "thats" , "that's" , "that've" , "the" , "their" , "theirs" , "them" , "themselves" , "then" , "thence" , "there" , "thereafter" , "thereby" , "there'd" , "therefore" , "therein" , "there'll" , "there're" , "theres" , "there's" , "thereupon" , "there've" , "these" , "they" , "they'd" , "they'll" , "they're" , "they've" , "thing" , "things" , "think" , "third" , "thirty" , "this" , "thorough" , "thoroughly" , "those" , "though" , "three" , "through" , "throughout" , "thru" , "thus" , "till" , "to" , "together" , "too" , "took" , "toward" , "towards" , "tried" , "tries" , "truly" , "try" , "trying" , "t's" , "twice" , "two" , "un" , "under" , "underneath" , "undoing" , "unfortunately" , "unless" , "unlike" , "unlikely" , "until" , "unto" , "up" , "upon" , "upwards" , "us" , "use" , "used" , "useful" , "uses" , "using" , "usually" , "v" , "value" , "various" , "versus" , "very" , "via" , "viz" , "vs" , "want" , "wants" , "was" , "wasn't" , "way" , "we" , "we'd" , "welcome" , "well" , "we'll" , "went" , "were" , "we're" , "weren't" , "we've" , "what" , "whatever" , "what'll" , "what's" , "what've" , "when" , "whence" , "whenever" , "where" , "whereafter" , "whereas" , "whereby" , "wherein" , "where's" , "whereupon" , "wherever" , "whether" , "which" , "whichever" , "while" , "whilst" , "whither" , "who" , "who'd" , "whoever" , "whole" , "who'll" , "whom" , "whomever" , "who's" , "whose" , "why" , "will" , "willing" , "wish" , "with" , "within" , "without" , "wonder" , "won't" , "would" , "wouldn't" , "yes" , "yet" , "you" , "you'd" , "you'll" , "your" , "you're" , "yours" , "yourself" , "yourselves" , "you've" , "zero", "gt", "lt", "I", "a", "u"]
	# with open(json_file) as data_file:

	# data = json.load(data_file)
	# for q,l in [[{'sentstrength_negative_sentiment':{'$lte':-1}}, 'Negative'], [{'sentstrength_negative_sentiment':{'$lt':-1}}, 'Negative Without One'], [{'sentstrength_positive_sentiment':{'$gte':1}}, 'Positive'], [{'sentstrength_positive_sentiment':{'$gt':1}}, 'Positive Without One']]:
	data = getattr(sys.modules[__name__], 'db_%s' % db_name).find(query, {'text':1, 'tags':1, 'caption.text':1})
	text_list = []
	for data_val in data:
		try:
			if field_name in ['text', 'tags']:
				# url_less = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', data_val[field_name])
				# symbol_less = re.sub(r'[^\w]', ' ', url_less)
				text_list.append(' '.join([re.sub(r'[^\w\s]','',word.replace('lt', '').replace('gt','').replace('amp','').replace('#', '').replace('.','').replace('https', '').replace('co', '').lower(), re.UNICODE)  for word in data_val[field_name].split() if word.lower() not in stop_words]))
			else:
				# url_less = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', data_val['caption']['text'])
				# symbol_less = re.sub(r'[^\w]', ' ', url_less)
				text_list.append(' '.join([re.sub(r'[^\w\s]','',word.replace('lt', '').replace('gt','').replace('amp','').replace('#', '').replace('.','').replace('https', '').replace('co', '').lower(), re.UNICODE) for word in data_val['caption']['text'].split() if word.lower() not in stop_words]))
		except:
			pass
	# print text_list
	text_list = filter(None, text_list)
	# map(lambda x: text_list.append(x[field_name]), data)
	text = ' '.join(text_list)
	lent = len(text.split())
	c = collections.Counter(text.split())
	# with open('%s_%s_words_7.439_7.803' % (db_name, ('_').join(l.split())), 'w') as f:
	with open('%s_words_7.076_7.439_r' % (db_name), 'w') as f:
		for k,v in  c.most_common():
			f.write( "{} {}\n".format(k.encode('utf-8'),(float(v)*100)/lent) )
	# wordcloud = WordCloud().generate(text)
	# # Open a plot of the generated image.
	# plt.imshow(wordcloud)
	# plt.axis("off")
	# # plt.show()
	# # Save the figure
	# # plt.savefig('%s_spike_word_cloud.png' % (db_name))
	# plt.savefig('%s_word_cloud_7.439_7.803.png' % (db_name))

# create_word_cloud(db_name='twitter_posts', field_name='text', query={})
# create_word_cloud(db_name='instagram_posts', field_name='caption.text', query={})
# create_word_cloud(db_name='instagram_comments', field_name='text', query={})
# create_word_cloud(db_name='instagram_comments', field_name='text', query={'valence': {'$gt':7.076}, 'valence': {'$lte':7.439}})
# create_word_cloud(db_name='instagram_comments', field_name='text', query={'valence': {'$gt':7.439}, 'valence': {'$lte':7.803}})
# create_word_cloud('twitter_posts', 'text', query={''})

# create_word_cloud('twitter_posts_dump_08_25_2016_06_49.json', 'text')
# create_word_cloud('instagram_posts_dump_08_25_2016_06_47.json', 'caption.text')
# create_word_cloud('instagram_posts_dump_08_25_2016_06_47.json', 'tags')
# create_instagram_graphs('instagram_posts', 'likes.count', {})
# create_instagram_graphs('instagram_posts', 'comments.count', {})

# graph_dbs_list = [['instagram_posts', 'created_time', {}], ['instagram_likes', 'saved_at', {}], ['instagram_comments', 'created_time', {}], ['twitter_posts', 'created_at', {}], ['twitter_posts', 'created_at', {'coordinates':{'$ne':None}}]]
# [create_time_series_plot(db_name, time_field) for (db_name, time_field, query) in graph_dbs_list]

def create_vader_sentiment_charts(db_name='twitter_posts', query={}):
	ranges = np.linspace(-1,1,21)
	db_data = list(getattr(sys.modules[__name__], 'db_%s' % db_name).find())
	data = []
	for row in db_data:
		try:
			data.append({'sentiment': row['vaderSentiment']['compound']})
		except:
			pass
	data = pd.DataFrame(data, columns=['sentiment'])
	data = data.groupby(pd.cut(data.sentiment, ranges)).count()
	data.plot()
	plt.xlabel('Vader Sentiment Ranges')
	plt.ylabel('Count')
	plt.savefig('%s_vader_sentiment_%s.png' % (db_name, datetime.now().strftime("%Y_%m_%d_%H_%M_%S")))
	# plt.show()

# create_vader_sentiment_charts('twitter_posts')
# create_vader_sentiment_charts('instagram_posts')

def create_wkb_dictionary():
	wkb_words = {}
	with open('Ratings_Warriner_et_al.csv', 'rb') as f:
		reader = csv.DictReader(f)
		for row in reader:
			wkb_words[row['Word']] = {'valence': row['V.Mean.Sum'], 'affect': row['A.Mean.Sum'], 'dominance': row['D.Mean.Sum']}
	return wkb_words

def get_wkb_data(db_name='twitter_posts', field_name='text', query={}):
	db_words = defaultdict(lambda:{'count': 0, 'valence': 0, 'dominance': 0, 'affect': 0}, {})
	wkb_words = create_wkb_dictionary()
	text_list = []
	db_data = getattr(sys.modules[__name__], 'db_%s' % db_name).find().limit(10)
	valence, dominance_valsance, affect, total_count, g_count = [0.0, 0.0, 0.0, 0, 0]
	v, d, a = [[], [], []]
	for data_val in db_data:
		# try:
			word_list = []
			if field_name in ['text', 'tags']:
				word_list = data_val[field_name].split()
			else:
				word_list = data_val['caption']['text'].split()
			for words in data_val[field_name].split():
				word = words.lower()
				word = word.translate(string.punctuation)
				total_count = total_count + 1
				if word in wkb_words:
					valence = valence + float(wkb_words[word]['valence'])
					dominance = dominance + float(wkb_words[word]['dominance'])
					affect = affect + float(wkb_words[word]['affect'])
					db_words[word]['count'] = db_words[word]['count'] + 1
					db_words[word]['valence'] = float(wkb_words[word]['valence'])
					db_words[word]['dominance'] = float(wkb_words[word]['dominance'])
					db_words[word]['affect'] = float(wkb_words[word]['affect'])
					v.append({'val': float(wkb_words[word]['valence'])})
					d.append({'val': float(wkb_words[word]['dominance'])})
					a.append({'val': float(wkb_words[word]['affect'])})
					g_count = g_count + 1
		# except:
		# 	pass
	for lv, name in [[v,'valence'],[d,'dominance'], [a,'affect']]:
		ranges = np.linspace(min(vs['val'] for vs in lv), max(vs['val'] for vs in lv), 21)
		data = pd.DataFrame(lv, columns=['val'])
		data = data.groupby(pd.cut(data.val, ranges)).count()
		data.plot(kind='bar', legend=True, figsize=(15,10), fontsize=12, alpha=0.75, rot=65)
		plt.xlabel(name)
		plt.ylabel('Count')
		# plt.savefig('%s_%s_%s.png' % (db_name, name, datetime.now().strftime("%Y_%m_%d_%H_%M_%S")))
		plt.show()

	# pd.DataFrame(d, columns=['sentiment'])
	# pd.DataFrame(a, columns=['sentiment'])

	print total_count
	print g_count
	print valence/g_count
	print dominance/g_count
	print affect/g_count

# get_wkb_data()

def show_wkb_bar_graphs(db_name='twitter_posts', query={}):
	db_data = list(getattr(sys.modules[__name__], 'db_%s' % db_name).find(query, {'arousal': 1, 'dominance': 1, 'valence': 1}))
	data = pd.DataFrame(db_data, columns=['valence', 'arousal', 'dominance'])
	data_bak=data
	min_val, max_val = data.min().min(), data.max().max()
	ranges = np.linspace(min_val, max_val, 21)
	data1 = data.groupby(pd.cut(data['valence'], ranges)).count()[['valence']]
	data2 = data.groupby(pd.cut(data['arousal'], ranges)).count()[['arousal']]
	data3 = data.groupby(pd.cut(data['dominance'], ranges)).count()[['dominance']]
	data = pd.concat([data1, data2, data3], axis=1)
	print db_name + '_wkb_var'
	print data.corr()
	data.plot(kind='bar', legend=True, figsize=(15,10), fontsize=12, alpha=0.75, rot=65)
	plt.xlabel('WKB variables')
	plt.ylabel('Count')
	plt.tight_layout()
	plt.savefig('%s_without_replies_%s_%s.png' % (db_name, 'WKB_variables', datetime.now().strftime("%Y_%m_%d_%H_%M_%S")))
	# plt.show()
	# print data1.columns
	# print data1
	# pd.merge(data1, data2, on='')
	# print data
	print st.t.interval(0.95, len(data_bak)-1, loc=data.corr(), scale=st.sem(data_bak))
	print np.mean(data_bak)
	print st.t.interval(0.95, len(data_bak)-1, loc=np.mean(data_bak), scale=st.sem(data_bak))
	print data_bak.sum()/data_bak.count()


# show_wkb_bar_graphs(query={'wkb_sentiment_analysis_flag': True})
# show_wkb_bar_graphs(db_name='instagram_posts', query={'wkb_sentiment_analysis_flag': True})
# show_wkb_bar_graphs(db_name='instagram_comments', query={'wkb_sentiment_analysis_flag': True})
# show_wkb_bar_graphs(query={'in_reply_to_status_id':{'$ne':None}, 'wkb_sentiment_analysis_flag': True})
# show_wkb_bar_graphs(query={'in_reply_to_status_id':None, 'wkb_sentiment_analysis_flag': True})

def show_sentistrength_bar_graphs(db_name='twitter_posts', query={'sentstrength_negative_sentiment':{'$lt':-1},'sentstrength_positive_sentiment':{'$gt':1}}):
	db_data = list(getattr(sys.modules[__name__], 'db_%s' % db_name).find(query, {'sentstrength_negative_sentiment':1, 'sentstrength_positive_sentiment':1}))
	print 'done'
	for sentiment in ['positive', 'negative']:
		data = pd.DataFrame(db_data, columns=['sentstrength_%s_sentiment' % (sentiment)])
		min_val, max_val = data.min().min(), data.max().max()
		ranges = np.linspace(2, 6, 5).tolist()
		if min_val < 0:
			ranges = np.linspace(-5, -1, 5).tolist()
		data_bak = data
		data = data.groupby(pd.cut(data['sentstrength_%s_sentiment' % (sentiment)], ranges, right=False, include_lowest=True, labels=ranges[:-1])).count()
		# print data
		# print data.sum()
		# print data.count()
		data.plot(kind='bar', legend=True, figsize=(15,10), fontsize=12, alpha=0.75, rot=65)
		xlabel = 'Sentistrength %s sentiment' % (sentiment)
		plt.xlabel(xlabel)
		plt.ylabel('Count')
		plt.tight_layout()
		plt.savefig('%s_without_replies_%s_%s.png' % (db_name, ('_').join(xlabel.split()), datetime.now().strftime("%Y_%m_%d_%H_%M_%S")))
		# plt.clf()
		# # plt.show()
		# # print data1.columns
		# # print data1
		# # pd.merge(data1, data2, on='')
		# # print data
		print db_name + '_sentistrength'
		print st.t.interval(0.95, len(data_bak)-1, loc=np.mean(data_bak), scale=st.sem(data_bak))
		print data_bak.sum()/data_bak.count()

# show_sentistrength_bar_graphs()
# show_sentistrength_bar_graphs(db_name='instagram_posts')
# show_sentistrength_bar_graphs(db_name='instagram_comments')
# show_sentistrength_bar_graphs(query={'sentstrength_negative_sentiment':{'$lt':-1},'sentstrength_positive_sentiment':{'$gt':1},'in_reply_to_status_id':{'$ne':None}})
# show_sentistrength_bar_graphs(query={'in_reply_to_status_id':{'$ne':None}})
# show_sentistrength_bar_graphs(query={'in_reply_to_status_id':None})

def get_comment_distribution():
	comments = map(lambda x: x['_id'], db_instagram_comments.aggregate([{ '$group' : { '_id' : "$instagram_post_id", 'count': { '$sum': 1 } } }, { '$match': { 'count': { '$gte': 5 }, 'count': { '$lte': 10 } } } ])["result"])
	# print comments
	# db_data = list(getattr(sys.modules[__name__], 'db_twitter_posts').find({'wkb_sentiment_analysis_flag': True}, {'arousal': 1, 'dominance': 1, 'valence': 1}).limit(10))
	# print db_data
	# datas = pd.DataFrame(db_data)[['valence','arousal','dominance']]
	# print datas
	# print st.t.interval(0.95, len(datas)-1, loc=np.mean(datas), scale=st.sem(datas))
	# y = list(getattr(sys.modules[__name__], 'db_twitter_posts' % db_name).find(query, {'sentstrength_negative_sentiment':1, 'sentstrength_positive_sentiment':1}).limit(10))

	# comments=["1322173195872159843_183931673"]
	results = db_instagram_comments.find({"instagram_post_id": {'$in': comments},"wkb_sentiment_analysis_flag":True},{"valence":1,"dominance":1,"arousal":1,"instagram_post_id":1,"created_time":1}).sort([("instagram_post_id",1),("created_time",1)])
	# print results
	counts = [[0] for x in [0] * 11]
	valence_vals = [[0] for x in [0] * 11]
	dominance_vals = [[0] for x in [0] * 11]
	arousal_vals = [[0] for x in [0] * 11]
	valence_c = [[0] for x in [0] * 11]
	arousal_c = [[0] for x in [0] * 11]
	dominance_c = [[0] for x in [0] * 11]
	valence_vals[1].append(results[0]["valence"])
	dominance_vals[1].append(results[0]["dominance"])
	arousal_vals[1].append(results[0]["arousal"])
	idx=2
	common=results[0]["instagram_post_id"]
	for result in results[1:]:
		if(result["instagram_post_id"]!=common):
			idx=1
			common=result["instagram_post_id"]
		try:
			valence_vals[idx].append(result["valence"])
			dominance_vals[idx].append(result["dominance"])
			arousal_vals[idx].append(result["arousal"])
			counts[idx].append(1)
		except:
			pass
		idx = idx+1
	for i in range(11):
		# print i
		dataa = pd.DataFrame(arousal_vals[i])
		datad = pd.DataFrame(dominance_vals[i])
		data = pd.DataFrame(valence_vals[i])
		# print data
		# print data[[1]]
		# print len(data[[1]])
		# print np.mean(data[[1]])
		# print st.sem(data[[1]])
		m=st.t.interval(0.95, len(data)-1, loc=np.mean(data), scale=st.sem(data))
		print m[1]-m[0]
		valence_c[i] = float(m[1] - m[0])
		m=st.t.interval(0.95, len(datad)-1, loc=np.mean(datad), scale=st.sem(datad))
		print m[1]-m[0]
		dominance_c[i] = float(m[1] - m[0])
		m=st.t.interval(0.95, len(dataa)-1, loc=np.mean(dataa), scale=st.sem(dataa))
		print m[1]-m[0]
		arousal_c[i] = float(m[1] - m[0])

		# if(counts[i]==0):
		# 	continue

		# valence_vals[i]=valence_vals[i]/float(counts[i])
		# dominance_vals[i]=dominance_vals[i]/float(counts[i])
		# arousal_vals[i]=arousal_vals[i]/float(counts[i])
	# valence_vals = {str(idx)+'a': val for idx,val in enumerate(valence_vals)}
	# print valence_vals
	# data = pd.DataFrame(valence_vals[1])
	# print data
	# print data[[1]]
	# print len(data[[1]])
	# print np.mean(data[[1]])
	# print st.sem(data[[1]])
	# m=st.t.interval(0.95, len(data)-1, loc=np.mean(data), scale=st.sem(data))
	# print m

	# print valence_c
	y = [sum(r)/len(r) for r in valence_vals]
	x = [sum(r)/len(r) for r in dominance_vals]
	z = [sum(r)/len(r) for r in arousal_vals]
	data = pd.DataFrame({'Valence': y, 'Dominance': x, 'Arousal': z})
	ax=data.plot(kind='bar', legend=True, figsize=(15,10), fontsize=12, alpha=0.75, rot=65, use_index=True, yerr=[valence_c, dominance_c, arousal_c])
	# data.index = range(1,len(data)+1)
	for p in ax.patches:
		ax.annotate(np.round(p.get_height(),decimals=2), (p.get_x()+p.get_width()/2., p.get_height()), ha='center', va='center', xytext=(0, 10), textcoords='offset points')
	plt.xlabel('Comment #')
	plt.ylabel('Values')
	plt.tight_layout()
	# plt.show()
	plt.savefig('WKB Parameters for comments_nnn.png')


# get_comment_distribution()

def show_different_wkb():
	data = pd.DataFrame({'WKB Parameters': ['Valence', 'Arousal', 'Dominance'], 'Twitter': [6.001096, 4.148224, 5.613052], 'Twitter Replies': [5.846119, 4.140196,  5.652870], 'Twitter Without Replies':[6.002102, 4.148276, 5.612794], 'Instagram Posts':[6.327977, 4.311188, 5.795368], 'Instagram Comments':[6.537544, 4.352565, 5.970616], 'Twitter_e': [6.00577157-5.9964204,  4.15210708-4.14434146,  5.61674634-5.60935826], 'Twitter Replies_e':[ 5.91994591-5.77229298,  4.18920313-4.09118943,  5.70031806-5.60542111],'Twitter Without Replies_e':[6.00678282-5.99742078,4.15217148-4.14438127,5.61649914-5.60908863], 'Instagram Posts_e':[ 6.33120603-6.32474856,  4.31363608-4.30874006,  5.79741469-5.79332102], 'Instagram Comments_e':[ 6.54165495-6.53343367,  4.35552142-4.3496082,  5.97308976-5.96814273]})
	data = data.set_index(['WKB Parameters'])
	data[['Twitter','Twitter Replies','Twitter Without Replies','Instagram Posts','Instagram Comments']].plot(kind='bar', legend=True, figsize=(15,10), fontsize=12, alpha=0.75, rot=65, yerr=data[['Twitter_e','Twitter Replies_e','Twitter Without Replies_e','Instagram Posts_e','Instagram Comments_e']].values.T)
	# data.set_xticklabels(['Twitter', 'Instagram Posts', 'Instagram Comments'])
	# plt.legend(handles=['Twitter', 'Instagram Posts', 'Instagram Comments'])
	plt.xlabel('WKB Parameters')
	plt.ylabel('Values')
	plt.tight_layout()
	plt.savefig('WKB Parameters with CI_n.png')

	# plt.show()

# show_different_wkb()

def show_different_correlations():
	data = pd.DataFrame({'WKB Parameters': ['V/A', 'A/D', 'D/V'], 'Twitter': [-0.264976,-0.163940, 0.820971], 'Twitter Replies': [-0.239419, -0.154719,  0.885555],'Twitter Without Replies':[-0.265455,-0.164285,0.820371], 'Instagram Posts':[-0.330027, -0.130260, 0.651406], 'Instagram Comments':[-0.337782, -0.089629, 0.584920],'Twitter_e': [-0.26109328+0.2688589,  -0.16024636+0.16763444, 0.824665-0.81727691], 'Twitter Replies_e':[-0.19041186+0.28842556,-0.1072709+0.20216784,0.93300318-0.83810623], 'Twitter Without Replies_e':[-0.26155979+0.26935,-0.16057983+0.16799034,0.82407587-0.81666536],'Instagram Posts_e':[-0.32757868+0.3324747,-0.12821304+0.13230671,0.65345239-0.64935873], 'Instagram Comments_e':[-0.33482495+0.34073817,-0.08715586+0.09210289,0.58739306-0.58244603]})
	data = data.set_index(['WKB Parameters'])
	data[['Twitter','Twitter Replies','Twitter Without Replies','Instagram Posts','Instagram Comments']].plot(kind='bar', legend=True, figsize=(15,10), fontsize=12, alpha=0.75, rot=65, yerr=data[['Twitter_e','Twitter Replies_e','Twitter Without Replies_e','Instagram Posts_e','Instagram Comments_e']].values.T)
	# data.set_xticklabels(['Twitter', 'Instagram Posts', 'Instagram Comments'])
	# plt.legend(handles=['Twitter', 'Instagram Posts', 'Instagram Comments'])
	plt.xlabel('WKB Parameters')
	plt.ylabel('Values')
	plt.tight_layout()
	plt.savefig('WKB Correlations with CI_n.png')

# show_different_correlations()


def show_different_sentistrength():
	data = pd.DataFrame({'WKB Parameters': ['Positive Without Ones', 'Negative Without Ones'], 'Twitter': [2.393266,-2.556718], 'Twitter Replies': [2.350649,-2.792208], 'Instagram Posts':[2.611311,-2.621237], 'Instagram Comments':[2.373689,-2.451902],'Twitter_e': [2.41318984-2.37334171,-2.53046564+2.58297012], 'Twitter Replies_e':[2.47146208-2.22983662,-2.61056414+2.97385144], 'Instagram Posts_e':[2.62062614-2.60199603,-2.60959176+2.63288206], 'Instagram Comments_e':[2.38248918-2.3648895,-2.44095085+2.4628531]})
	data = data.set_index(['WKB Parameters'])
	data[['Twitter','Twitter Replies','Instagram Posts','Instagram Comments']].plot(kind='bar', legend=True, figsize=(15,10), fontsize=12, alpha=0.75, rot=65, yerr=data[['Twitter_e','Twitter Replies_e','Instagram Posts_e','Instagram Comments_e']].values.T)
	plt.xlabel('SentiStrength')
	plt.ylabel('Values')
	plt.tight_layout()
	plt.savefig('SentiStrength Correlations Various Measures with CI.png')
# show_different_sentistrength()

def weather_emotion(db_name='twitter_posts', query={'wkb_sentiment_analysis_flag': True}):
	data = pd.DataFrame(list(getattr(sys.modules[__name__], 'db_%s' % db_name).find({'wkb_sentiment_analysis_flag': True}, {'timestamp_ms': 1, 'arousal': 1, 'dominance': 1, 'valence': 1, 'created_time': 1}).limit(50000)))
	# print data['timestamp_ms'].astype(int)
	if(db_name=='twitter_posts'):
		data['PDT'] = pd.to_datetime(data['timestamp_ms'].astype(int), unit='ms').dt.tz_localize('UTC').dt.tz_convert('America/Los_Angeles').dt.date
	else:
		data['PDT'] = pd.to_datetime(data['created_time'].astype(int), unit='s').dt.tz_localize('UTC').dt.tz_convert('America/Los_Angeles').dt.date
	# print data
	# print data
	x = data.groupby('PDT', as_index=False)
	x = x.aggregate(np.mean)
	x['PDT'] = x['PDT'].astype('str')
	# x = x.to_frame()
	temp =  pd.read_csv('convertcsv.csv', parse_dates=['PDT'])
	temp['PDT'] = temp['PDT'].astype('str')
	# print x.dtypes
	s = pd.merge(temp,x,on='PDT')
	var = ['Max TemperatureF', 'Mean TemperatureF', 'Min TemperatureF', ' CloudCover']
	for v in var:
		s.sort(v).plot(x=v, y='valence')
		nn = s[[v,'valence']]
		print nn
		# p = st.t.interval(0.95, len(nn)-1, loc=nn.corr(), scale=st.sem(nn))
		# print var
		# print nn.corr()
		# print p
		# plt.show()
		# plt.figure()
		nn.boxplot(by=v)
		# nn.plot()
		plt.xlabel(v)
		plt.ylabel('Valence Values')
		plt.tight_layout()
		# plt.savefig('%s Valence Correlation Values vs %s' % (db_name, v))
		plt.show()
	# print s
	# print data['PDT']
	# print temp['PDT']
	# print m
	# print m['timestamp_ms'].tz_convert(pytz.timezone('America/Los_Angeles'))
	# print pd.timestamp_ms
	# print data

# weather_emotion()
# weather_emotion(db_name='instagram_posts')
# weather_emotion(db_name='instagram_comments')


def show_weather_correlations():
	data = pd.DataFrame({'Weather Parameters': ['Max TemperatureF', 'Mean TemperatureF', 'Min TemperatureF', ' CloudCover'], 'Twitter': [0.229454, 0.264224, 0.185769, -0.030361], 'Instagram Posts':[-0.214036, -0.191655, -0.110391, -0.077949], 'Instagram Comments':[-0.101864, -0.096319, -0.036119, -0.06178]})
	data = data.set_index(['Weather Parameters'])
	ax = data[['Twitter', 'Instagram Posts','Instagram Comments']].plot(kind='bar', legend=True, figsize=(15,10), fontsize=12, alpha=0.75, rot=65)
	for p in ax.patches:
		ax.annotate(np.round(p.get_height(),decimals=2), (p.get_x()+p.get_width()/2., p.get_height()), ha='center', va='center', xytext=(0, 10), textcoords='offset points')
	plt.xlabel('Weather Parameters')
	plt.ylabel('Valence')
	plt.tight_layout()
	plt.savefig('Weather Correlations with Valence.png')
# show_weather_correlations()


def LAWithOthers(db_name='twitter_posts', query={'wkb_sentiment_analysis_flag': True}):
	# print data['timestamp_ms'].astype(int)
	if(db_name=='twitter_posts'):
		data = pd.DataFrame(list(getattr(sys.modules[__name__], 'db_%s' % db_name).find({'wkb_sentiment_analysis_flag': True, 'coordinates':{'$ne':None}, 'coordinates.coordinates':{'$not': {'$geoWithin': {'$center': [ [ -118.481569383702, 34.0231837184805 ], (float(5.0))/111.12 ] } }} }, {'timestamp_ms': 1, 'arousal': 1, 'dominance': 1, 'valence': 1, 'created_time': 1, 'sentstrength_negative_sentiment': 1, 'sentstrength_positive_sentiment':1})))

		data['PDT'] = pd.to_datetime(data['timestamp_ms'].astype(int), unit='ms').dt.tz_localize('UTC').dt.tz_convert('America/Los_Angeles').dt.date
	else:
		data = pd.DataFrame(list(getattr(sys.modules[__name__], 'db_%s' % db_name).find({'wkb_sentiment_analysis_flag': True, 'coordinates':{'$ne':None}, 'coordinates.coordinates':{'$not': {'$geoWithin': {'$center': [ [ -118.481569383702, 34.0231837184805 ], (float(5.0))/111.12 ] } }} }, {'timestamp_ms': 1, 'arousal': 1, 'dominance': 1, 'valence': 1, 'created_time': 1, 'sentstrength_negative_sentiment': 1, 'sentstrength_positive_sentiment':1})))

		data['PDT'] = pd.to_datetime(data['created_time'].astype(int), unit='s').dt.tz_localize('UTC').dt.tz_convert('America/Los_Angeles').dt.date
	# print data
	# print data
	y = data.groupby('PDT', as_index=False)

	for typeagg in ['mean', 'count']:
		x = y.aggregate(typeagg)
		# x = x.agg(['mean','count'])
		# print x[['count']]
		x['PDT'] = x['PDT'].astype('str')
		# x = x.to_frame()

		# for csv in ['SantaMonicaWeather']:
		for csv in ['SantaMonicaWeather', 'LAWeather']:
			temp =  pd.read_csv('%s.csv' % (csv), parse_dates=['PDT'])
			temp['PDT'] = temp['PDT'].astype('str')
			# print x.dtypes
			s = pd.merge(temp,x,on='PDT')
			var = ['Max TemperatureF', 'Mean TemperatureF', 'Min TemperatureF', ' CloudCover']
			for v in var:
				# print s
				s.sort(v)#.plot(x=v, y='valence')
				if(typeagg=='mean'):
					for plot in ['valence', 'arousal']:
					# for plot in ['valence', 'arousal', 'dominance', 'sentstrength_positive_sentiment', 'sentstrength_negative_sentiment']:
						nn = s[[v, plot]]
						# print nn
						# p = st.t.interval(0.95, len(nn)-1, loc=nn.corr(), scale=st.sem(nn))
						# print var
						# print nn.corr()
						# print p
						# plt.show()
						# plt.figure()
						# nn.boxplot(by=v)
						plt.figure()
						ax = sns.regplot(x=v, y=plot, data=nn, ci=95)
						# nn.plot()
						plt.xlabel(v)
						plt.ylabel('%s %s Values' % (csv, plot))
						plt.tight_layout()
						plt.savefig('%s %s Values vs %s for LA vs %s_glm' % (db_name, plot, v, csv))
						# plt.show()
				else:
					for plot in ['valence']:
						nn = s[[v, plot]]
						# print nn
						# p = st.t.interval(0.95, len(nn)-1, loc=nn.corr(), scale=st.sem(nn))
						# print var
						# print nn.corr()
						# print p
						# plt.show()
						# plt.figure()
						# nn.boxplot(by=v)
						plt.figure()
						ax = sns.regplot(x=v, y=plot, data=nn, ci=95)
						# nn.plot()
						plt.xlabel(v)
						plt.ylabel('%s %s Values' % (csv, 'count'))
						plt.tight_layout()
						plt.savefig('%s Count vs %s for LA vs %s_glm' % (db_name, v, csv))
						# plt.show()
			# print s
			# print data['PDT']
			# print temp['PDT']
			# print m
			# print m['timestamp_ms'].tz_convert(pytz.timezone('America/Los_Angeles'))
			# print pd.timestamp_ms
			# print data

# LAWithOthers()
# LAWithOthers(db_name='instagram_posts')
# LAWithOthers(db_name='instagram_comments')

print 'done'

def SMWithOthers(db_name='twitter_posts', query={'wkb_sentiment_analysis_flag': True}):
	# print data['timestamp_ms'].astype(int)
	if(db_name=='twitter_posts'):
		data = pd.DataFrame(list(getattr(sys.modules[__name__], 'db_%s' % db_name).find({'wkb_sentiment_analysis_flag': True, 'coordinates':{'$ne':None}, 'coordinates.coordinates': {'$geoWithin': {'$center': [ [ -118.481569383702, 34.0231837184805 ], (float(5.0))/111.12 ] } } }, {'timestamp_ms': 1, 'arousal': 1, 'dominance': 1, 'valence': 1, 'created_time': 1, 'sentstrength_negative_sentiment': 1, 'sentstrength_positive_sentiment':1})))

		data['PDT'] = pd.to_datetime(data['timestamp_ms'].astype(int), unit='ms').dt.tz_localize('UTC').dt.tz_convert('America/Los_Angeles').dt.date
	else:
		data = pd.DataFrame(list(getattr(sys.modules[__name__], 'db_%s' % db_name).find({'wkb_sentiment_analysis_flag': True, 'coordinates':{'$ne':None}, 'coordinates.coordinates': {'$geoWithin': {'$center': [ [ -118.481569383702, 34.0231837184805 ], (float(5.0))/111.12 ] } } }, {'timestamp_ms': 1, 'arousal': 1, 'dominance': 1, 'valence': 1, 'created_time': 1, 'sentstrength_negative_sentiment': 1, 'sentstrength_positive_sentiment':1})))

		data['PDT'] = pd.to_datetime(data['created_time'].astype(int), unit='s').dt.tz_localize('UTC').dt.tz_convert('America/Los_Angeles').dt.date
	# print data
	# print data
	y = data.groupby('PDT', as_index=False)

	for typeagg in ['mean', 'count']:
		x = y.aggregate(typeagg)
		# x = x.agg(['mean','count'])
		# print x[['count']]
		x['PDT'] = x['PDT'].astype('str')
		# x = x.to_frame()

		# for csv in ['SantaMonicaWeather']:
		for csv in ['SantaMonicaWeather', 'LAWeather']:
			temp =  pd.read_csv('%s.csv' % (csv), parse_dates=['PDT'])
			temp['PDT'] = temp['PDT'].astype('str')
			# print x.dtypes
			s = pd.merge(temp,x,on='PDT')
			var = ['Max TemperatureF', 'Mean TemperatureF', 'Min TemperatureF', ' CloudCover']
			for v in var:
				# print s
				s.sort(v)#.plot(x=v, y='valence')
				if(typeagg=='mean'):
					for plot in ['valence', 'arousal', 'dominance']:
					# for plot in ['valence', 'arousal', 'dominance', 'sentstrength_positive_sentiment', 'sentstrength_negative_sentiment']:
						nn = s[[v, plot]]
						# print nn
						# p = st.t.interval(0.95, len(nn)-1, loc=nn.corr(), scale=st.sem(nn))
						# print var
						# print nn.corr()
						# print p
						# plt.show()
						# plt.figure()
						# nn.boxplot(by=v)
						plt.figure()
						ax = sns.regplot(x=v, y=plot, data=nn, ci=95)
						# nn.plot()
						plt.xlabel(v)
						plt.ylabel('%s %s Values' % (csv, plot))
						plt.tight_layout()
						plt.savefig('%s %s Values vs %s for SM vs %s_glm' % (db_name, plot, v, csv))
						# plt.show()
				else:
					for plot in ['valence']:
						nn = s[[v, plot]]
						# print nn
						# p = st.t.interval(0.95, len(nn)-1, loc=nn.corr(), scale=st.sem(nn))
						# print var
						# print nn.corr()
						# print p
						# plt.show()
						# plt.figure()
						# nn.boxplot(by=v)
						plt.figure()
						ax = sns.regplot(x=v, y=plot, data=nn, ci=95)
						# nn.plot()
						plt.xlabel(v)
						plt.ylabel('%s %s Values' % (csv, 'count'))
						plt.tight_layout()
						plt.savefig('%s Count vs %s for SM vs %s_glm' % (db_name, v, csv))
						# plt.show()
			# print s
			# print data['PDT']
			# print temp['PDT']
			# print m
			# print m['timestamp_ms'].tz_convert(pytz.timezone('America/Los_Angeles'))
			# print pd.timestamp_ms
			# print data

# SMWithOthers()
# SMWithOthers(db_name='instagram_posts')
# SMWithOthers(db_name='instagram_comments')

def r2(x, y):
	# print st.pearsonr(x, y)
	return st.pearsonr(x, y)[1]

def plot_count_crimes(db_name='twitter_posts', tract_flag=False):
	tract_list = [1]
	if tract_flag:
		tract_list = [273100,701201,701202,701302,701304,701402,701501,701502,701601,701602,701701,701702,701801,701802,701902,702002,702102,702201,702202,702300]
	for tract_no in tract_list:
		find_hash = {'tract_found_flag': True}
		if tract_flag:
			find_hash = {'tract_no': '%s' % (tract_no)}		
		if(db_name=='twitter_posts'):
			data = pd.DataFrame(list(getattr(sys.modules[__name__], 'db_%s' % db_name).find(find_hash, {'timestamp_ms': 1, 'created_time': 1})))#, 'arousal': 1, 'dominance': 1, 'valence': 1, 'created_time': 1, 'sentstrength_negative_sentiment': 1, 'sentstrength_positive_sentiment':1})))
			try:
				data['Date Occurred'] = pd.to_datetime(data['timestamp_ms'].astype(int), unit='ms').dt.tz_localize('UTC').dt.tz_convert('America/Los_Angeles').dt.date
			except:
				continue
		else:
			data = pd.DataFrame(list(getattr(sys.modules[__name__], 'db_%s' % db_name).find(find_hash, {'timestamp_ms': 1, 'created_time': 1})))#, 'arousal': 1, 'dominance': 1, 'valence': 1, 'created_time': 1, 'sentstrength_negative_sentiment': 1, 'sentstrength_positive_sentiment':1})))

			try:
				data['Date Occurred'] = pd.to_datetime(data['created_time'].astype(int), unit='s').dt.tz_localize('UTC').dt.tz_convert('America/Los_Angeles').dt.date
			except:
				continue
		# print data
		y = data.groupby('Date Occurred', as_index=False)
		for typeagg in ['count']:
			x = y.count()#.reset_index("count")
			x.drop(x[x['_id'] < (x['_id'].mean() - 4*x.std())['_id']].index, inplace=True)
			# print x
			# x = y.aggregate(typeagg)
			# x = x.agg(['mean','count'])
			# print x[['count']]
			x['Date Occurred'] = x['Date Occurred'].astype('str')
			for csv in ['Police_Incidents']:
			# for csv in ['SantaMonicaWeather', 'LAWeather']:
				temp =  pd.read_csv('%s.csv' % (csv), parse_dates=['Date Occurred'])
				y = temp.groupby('Date Occurred', as_index=False)
				xx = y.aggregate(typeagg)
				xx['Date Occurred'] = xx['Date Occurred'].astype('str')
				# print xx
				# print x.dtypes
				s = pd.merge(xx,x,on='Date Occurred')
				nn = s[['UCR', '_id']]
				# print nn
				ax = sns.regplot(x="UCR", y="_id", data=nn, ci=95)
				p_val = r2(nn['UCR'], nn['_id'])
				if p_val <= 0.05:
					text(0.1, 0.95, 'p-value: %s' % (p_val), horizontalalignment='center', verticalalignment='center', transform = ax.transAxes)

					plt.legend()

					if tract_flag:
						plt.savefig('Tract %s, %s count on a day vs %s for SM' % (tract_no, db_name, 'Crimes count'))
					else:					
						plt.savefig('%s count on a day vs %s for SM sig' % (db_name, 'Crimes count'))			
					plt.xlabel('Crimes count')
					plt.ylabel('%s post count' % db_name)
					plt.savefig('%s post count vs %s for SM sig' % (db_name, 'Crimes count'))
				plt.gcf().clear()						
				# plt.show()
# plot_count_crimes(tract_flag=True)
# plot_count_crimes(db_name='instagram_posts', tract_flag=True)

def mask(df, f):
	return df[f(df)]


# tract_list = [273100,701201,701202,701302,701304,701402,701501,701502,701601,701602,701701,701702,701801,701802,701902,702002,702102,702201,702202,702300]

def plot_crime_stats(db_name='twitter_posts', query={'wkb_sentiment_analysis_flag': True}, tract_flag=False):
	tract_list = [1]
	if tract_flag:
		tract_list = [273100,701201,701202,701302,701304,701402,701501,701502,701601,701602,701701,701702,701801,701802,701902,702002,702102,702201,702202,702300]
	for tract_no in tract_list:
		find_hash = {'tract_found_flag': True}
		if tract_flag:
			find_hash = {'tract_no': '%s' % (tract_no)}	
		if(db_name=='twitter_posts'):
			data = pd.DataFrame(list(getattr(sys.modules[__name__], 'db_%s' % db_name).find(find_hash, {'timestamp_ms': 1, 'created_time': 1, 'arousal': 1, 'valence': 1})))#, 'created_time': 1, 'sentstrength_negative_sentiment': 1, 'sentstrength_positive_sentiment':1})))
			# data = pd.DataFrame(list(getattr(sys.modules[__name__], 'db_%s' % db_name).find({'wkb_sentiment_analysis_flag': True, 'coordinates':{'$ne':None}, 'coordinates.coordinates': {'$geoWithin': {'$center': [ [ -118.481569383702, 34.0231837184805 ], (float(5.0))/111.12 ] } } }, {'timestamp_ms': 1, 'created_time': 1, 'arousal': 1, 'valence': 1})))#, 'created_time': 1, 'sentstrength_negative_sentiment': 1, 'sentstrength_positive_sentiment':1})))

			try:
				data['Date Occurred'] = pd.to_datetime(data['timestamp_ms'].astype(int), unit='ms').dt.tz_localize('UTC').dt.tz_convert('America/Los_Angeles').dt.date
			except:
				continue
		else:
			data = pd.DataFrame(list(getattr(sys.modules[__name__], 'db_%s' % db_name).find(find_hash, {'timestamp_ms': 1, 'created_time': 1, 'arousal': 1, 'valence': 1})))#, 'created_time': 1, 'sentstrength_negative_sentiment': 1, 'sentstrength_positive_sentiment':1})))

			try:
				data['Date Occurred'] = pd.to_datetime(data['created_time'].astype(int), unit='s').dt.tz_localize('UTC').dt.tz_convert('America/Los_Angeles').dt.date
			except:
				continue
		# print data
		y = data.groupby('Date Occurred', as_index=False)
		# z = y.aggregate('count')
		# print y.aggregate('count')
		# print y.aggregate('count')['_id'].mean()
		# print (y.aggregate('count')['_id'].mean() - 1*y.aggregate('count').std())['_id']
		# z.drop(z[z['_id'] < (y.aggregate('count')['_id'].mean() - 1*y.aggregate('count').std())['_id']].index, inplace=True)
		# print z
		# print 5*y.aggregate('count').std()
		# print y.std()
		for typeagg in ['mean']:
			# x = y.mean()#.reset_index("count")
			# print x
			x = y.aggregate(typeagg)
			x.drop(x[x['valence'] < (x['valence'].mean() - 4*x.std()[['valence']])['valence']].index, inplace=True)
			x.drop(x[x['arousal'] < (x['arousal'].mean() - 4*x.std()[['arousal']])['arousal']].index, inplace=True)

			# x = x.agg(['mean','count'])
			# print x[['count']]
			x['Date Occurred'] = x['Date Occurred'].astype('str')
			# print x
			# print '-------------'
			for csv in ['Police_Incidents']:
			# for csv in ['SantaMonicaWeather', 'LAWeather']:
				temp2 =  pd.read_csv('%s.csv' % (csv), parse_dates=['Date Occurred'])
				temp = temp2
				# print temp
				# temp = temp2.mask(lambda x: x['Gang Related'])
					# if(temp['Gang Related'] or temp['Gang Related']=='TRUE'):

				y = temp.groupby('Date Occurred', as_index=False)
				# xx = y.aggregate(typeagg)
				xx = y.aggregate('count')
				xx['Date Occurred'] = xx['Date Occurred'].astype('str')
				# print xx
				# print x.dtypes
				s = pd.merge(xx,x,on='Date Occurred')
				# print '-------------'
				# print s
				# for v in ['valence', 'arousal']:
				for v in ['arousal', 'valence']:
					# plt.figure()
					nn = s[[v, 'UCR']]
					# print '-------------'
					# print nn
					# print nn
					ax = sns.regplot(x="UCR", y=v, data=nn, ci=95, label='%s Values' % v.capitalize())
					p_val = r2(nn['UCR'], nn[v])
					if p_val <= 0.05:
						text(0.1, 0.95, 'p-value: %s' % (p_val), horizontalalignment='center', verticalalignment='center', transform = ax.transAxes)
						plt.xlabel('Crimes count on a day')
						plt.legend()
						plt.ylabel('%s_%s ' % (db_name, v))
						plt.tight_layout()
						if tract_flag:
							plt.savefig('Tract %s, %s_%s count on a day vs %s for SM sig' % (tract_no, db_name, v.capitalize(), 'Crimes count'))
						else:					
							plt.savefig('%s_%s count on a day vs %s for SM sig' % (db_name, v.capitalize(), 'Crimes count'))
						# plt.savefig('%s_%s Count vs %s for SM_gang_related' % (db_name, v, 'Crimes count'))
						# plt.show()
					plt.gcf().clear()						
# plot_crime_stats(tract_flag=True)
# plot_crime_stats(db_name="instagram_posts", tract_flag=True)

def crosscorr(datax, datay, lag=0):
	shifted_data = datay.shift(lag)
	shifted_data.dropna(inplace=True)
	return datax.corr(shifted_data)

def duplicate_columns(frame):
    groups = frame.columns.to_series().groupby(frame.dtypes).groups
    dups = []
    for t, v in groups.items():
        dcols = frame[v].to_dict(orient="list")

        vs = dcols.values()
        ks = dcols.keys()
        lvs = len(vs)

        for i in range(lvs):
            for j in range(i+1,lvs):
                if vs[i] == vs[j]: 
                    dups.append(ks[i])
                    break

    return dups      

def strip_non_ascii(string):
	''' Returns the string without non ASCII characters'''
	stripped = (c for c in string if 0 < ord(c) < 127)
	return ''.join(stripped)    


from itertools import cycle
fig, ax = plt.subplots()
line_styles = cycle(['-','-','-', '--', '-.', ':'])#, 'o', 'v', '^', '<', '>',
		   # '1', '2', '3', '4', 's', 'p', '*', 'h', 'H', '+', 'x', 'D', 'd', '|', '_'])
colors = cycle(matplotlib.rcParams['axes.color_cycle'])

def crosscorrelation_plot(series1, series2, series1_n, series2_n, ax=None, **kwds):
	"""Autocorrelation plot for time series.
	Parameters:
	-----------
	series: Time series
	ax: Matplotlib axis object, optional
	kwds : keywords
		Options to pass to matplotlib plotting method
	Returns:
	-----------
	ax: Matplotlib axis object
	"""
	# import matplotlib.pyplot as plt
	n = len(series1)
	data1 = np.asarray(series1)
	data2 = np.asarray(series2)
	n = 10
	if ax is None:
		ax = plt.gca(xlim=(0, n), ylim=(-1.0, 1.0))
		ax.set_xlabel("Lag")
		ax.set_ylabel("Crosscorrelation wrt %s" % series1_n)
	# mean = np.mean(data)
	# c0 = np.sum((data - mean) ** 2) / float(n)

	def r(h):
		# print crosscorr(series1, series2, lag=h)
		return crosscorr(series1, series2, lag=h)
	# 	return ((data[:n - h] - mean) *
	# 			(data[h:] - mean)).sum() / float(n) / c0
	def pval(h):
		# print series1
		# print data2
		return pd.ols(y=series1, x=series2.shift(h), intercept=True).f_stat['p-value']

	x = np.arange(n-1)
	y = lmap(r, x)
	z = lmap(pval, x)
	# z95 = 1.959963984540054
	# z99 = 2.5758293035489004
	# ax.axhline(y=z99 / np.sqrt(n), linestyle='--', color='grey')
	# ax.axhline(y=z95 / np.sqrt(n), color='grey')
	# ax.axhline(y=0.0, color='black')
	# # ax.axhline(y=-z95 / np.sqrt(n), color='grey')
	# # ax.axhline(y=-z99 / np.sqrt(n), linestyle='--', color='grey')
	# import matplotlib.ticker as plticker

	# loc = plticker.MultipleLocator(base=3.0) # this locator puts ticks at regular intervals
	# ax.xaxis.set_major_locator(loc)	
	# # ax.set_xlim([0,15])
	# # ax.grid(True)
	# ax.plot(x, y, **kwds)
	# if 'label' in kwds:
	# 	ax.legend()
	# ax.grid()
	# return ax
	# print y
	# print z
	cl = colors.next()
	plt.plot(x, y, color =cl, linestyle=line_styles.next(), label=series2_n, linewidth=2.0)#, color='#CC4F1B')#, interpolate=False)
	# print z
	# print y[0]
	# print list(np.array(y)+np.array(z))
	plt.errorbar(x=x, y=y, yerr=z)#, interpolate=False)
	# plt.fill_between(x, list(np.array(y)-np.array(z)), list(np.array(y)+np.array(z)), alpha=0.05, color=cl)#, edgecolor='#CC4F1B', facecolor='#FF9848')
	for i in range(n-1):
	    plt.annotate('%.2f|p-val: %.2f' % (y[i], z[i]), xy=(x[i]-0.2, y[i]+0.05), textcoords='data', color=cl, weight='bold') # <--	
	plt.legend()
	# plt.show()
	return ax



def plot_time_crime_social_data(db_name="twitter_posts", tract_flag=False, top_crime_flag=False):
	tract_list = [1]
	if tract_flag:
		tract_list = [273100,701201,701202,701302,701304,701402,701501,701502,701601,701602,701701,701702,701801,701802,701902,702002,702102,702201,702202,702300]
	for tract_no in tract_list:
		find_hash = {'tract_found_flag': True}
		if tract_flag:
			find_hash = {'tract_no': '%s' % (tract_no)}
		if(db_name=='twitter_posts'):
			data = pd.DataFrame(list(getattr(sys.modules[__name__], 'db_%s' % db_name).find(find_hash, {'timestamp_ms': 1, 'created_time': 1, 'arousal': 1, 'valence': 1})))#, 'created_time': 1, 'sentstrength_negative_sentiment': 1, 'sentstrength_positive_sentiment':1})))

			try:
				data['Date Occurred'] = pd.to_datetime(data['timestamp_ms'].astype(int), unit='ms').dt.tz_localize('UTC').dt.tz_convert('America/Los_Angeles').dt.date
			except:
				continue
		else:
			data = pd.DataFrame(list(getattr(sys.modules[__name__], 'db_%s' % db_name).find(find_hash, {'timestamp_ms': 1, 'created_time': 1, 'arousal': 1, 'valence': 1}).limit(5000)))#, 'created_time': 1, 'sentstrength_negative_sentiment': 1, 'sentstrength_positive_sentiment':1})))
			try:
				data['Date Occurred'] = pd.to_datetime(data['created_time'].astype(int), unit='s').dt.tz_localize('UTC').dt.tz_convert('America/Los_Angeles').dt.date	
			except:
				continue
		
		social_media_grouping = data.groupby('Date Occurred', as_index=False)
		
		social_media_count = social_media_grouping.aggregate('count')
		social_media_count.drop(social_media_count[social_media_count['_id'] <= max(0, (social_media_count['_id'].mean() - 4*social_media_count.std())['_id'])].index, inplace=True)
		social_media_count.drop('valence',inplace=True,axis=1)
		social_media_count.drop('arousal',inplace=True,axis=1)
		
		emotion_value_grouping = social_media_grouping.aggregate('mean')
		emotion_value_grouping.drop(emotion_value_grouping[emotion_value_grouping['valence'] < (emotion_value_grouping['valence'].mean() - 4*emotion_value_grouping.std())['valence']].index, inplace=True)
		emotion_value_grouping.drop(emotion_value_grouping[emotion_value_grouping['arousal'] < (emotion_value_grouping['arousal'].mean() - 4*emotion_value_grouping.std())['arousal']].index, inplace=True)
		# emotion_value_grouping.drop('_id',inplace=True,axis=1)

		police_incidents_csv =  pd.read_csv('%s.csv' % ('Police_Incidents'), parse_dates=['Date Occurred'])
		gang_related_csv = police_incidents_csv[police_incidents_csv['Gang Related'] == True]
		if top_crime_flag:
			pid_list = [640, 450, 2300, 1100, 660, 1400, 690, 670, 630, 2606]
			police_incidents_csv = police_incidents_csv[police_incidents_csv.UCR.isin(pid_list)]
		crime_data_grouping = police_incidents_csv.groupby('Date Occurred', as_index=False)
		crime_data_count = crime_data_grouping.aggregate('count')
		gang_data_grouping = gang_related_csv.groupby('Date Occurred', as_index=False)
		gang_data_count = gang_data_grouping.aggregate('count')

		social_media_count['Date'] = social_media_count['Date Occurred'].astype('str')
		emotion_value_grouping['Date'] = emotion_value_grouping['Date Occurred'].astype('str')
		crime_data_count['Date'] = crime_data_count['Date Occurred'].astype('str')
		gang_data_count['Date'] = gang_data_count['Date Occurred'].astype('str')
		# social_media_count.reset_index(inplace=True)
		# emotion_value_grouping.reset_index(inplace=True)
		# crime_data_count.reset_index(inplace=True)
		# gang_data_count.reset_index(inplace=True)

		crime_social_emotion_merge = pd.merge(social_media_count,emotion_value_grouping,on='Date')
		# crime_social_emotion_merge.reset_index(inplace=True)
		crime_social_emotion_merge = pd.merge(crime_social_emotion_merge,crime_data_count,on='Date')
		# crime_social_emotion_merge.reset_index(inplace=True)
		# print crime_social_emotion_merge.columns
		# print crime_social_emotion_merge.index
		# cols_to_use = gang_data_count.columns - crime_social_emotion_merge.columns
		crime_social_emotion_merge = pd.merge(crime_social_emotion_merge, gang_data_count,left_index=True, right_index=True, how='outer', suffixes=('', '_y'))
		crime_social_emotion_merge.columns = [strip_non_ascii(x) for x in crime_social_emotion_merge.columns]
		# print [i for i in crime_social_emotion_merge.columns]
		_, i = np.unique(crime_social_emotion_merge.columns, return_index=True)
		crime_social_emotion_merge = crime_social_emotion_merge.iloc[:, i]
		# dups = duplicate_columns(crime_social_emotion_merge)
		# crime_social_emotion_merge = crime_social_emotion_merge.drop(dups, axis=1)
		# print crime_social_emotion_merge.columns
		# print crime_social_emotion_merge.index
		# print crime_social_emotion_merge[crime_social_emotion_merge.index.duplicated()]

		crime_social_emotion_merge.reset_index(inplace=True)
		# print crime_social_emotion_merge.columns
		# print crime_social_emotion_merge.index
		crime_social_emotion_merge.set_index('Date Occurred', inplace=True)
		#.interpolate(method='spline', order=3)
		# print crime_social_emotion_merge.rolling(window=3, min_periods=1).mean().interpolate(method='cubic').reset_index()
		# crime_social_emotion_merge = crime_social_emotion_merge.resample('3d').mean().rolling(window=3, min_periods=1).mean().interpolate(method='spline', order=3).reset_index()
		# print crime_social_emotion_merge
		# print crime_social_emotion_merge.rolling(window=3, min_periods=1).mean()
		# crime_social_emotion_merge = crime_social_emotion_merge.resample('7d').sum().reset_index()
		crime_social_emotion_merge = crime_social_emotion_merge.rolling(window=1, min_periods=1).mean().reset_index()
		crime_social_emotion_merge.drop(crime_social_emotion_merge[crime_social_emotion_merge['_id'] < (crime_social_emotion_merge['_id'].mean() - 2*crime_social_emotion_merge.std())['_id']].index, inplace=True)
		crime_social_emotion_merge.dropna(inplace=True)
		# print crime_social_emotion_merge
		# fig, ax = plt.subplots()

		# # Twin the x-axis twice to make independent y-axes.
		# axes = [ax, ax.twinx()]

		# # Make some space on the right side for the extra y-axis.
		# fig.subplots_adjust(right=0.75)

		# # Move the last y-axis spine over to the right by 20% of the width of the axes
		# axes[-1].spines['right'].set_position(('axes', 1.2))

		# # To make the border of the right-most axis visible, we need to turn the frame
		# # on. This hides the other plots, however, so we need to turn its fill off.
		# axes[-1].set_frame_on(True)
		# axes[-1].patch.set_visible(False)

		# print crime_social_emotion_merge.columns
		crime_social_emotion_merge = crime_social_emotion_merge[['Date Occurred', 'UCR', '_id', 'valence', 'arousal', 'Gang Related_y']]
		crime_social_emotion_merge =crime_social_emotion_merge.rename(columns={"UCR": "Crime Count", "_id": "Posts Count", "Gang Related_y": "Gang Crimes"})
		crime_social_emotion_merge.set_index(['Date Occurred'], inplace=True)
		ys = [['Crime Count'], ['Gang Crimes'], ['Posts Count'], ['valence'], ['arousal']]

		from itertools import cycle
		fig, ax = plt.subplots()

		axes = [ax]
		for y in ys[1:]:
			# Twin the x-axis twice to make independent y-axes.
			axes.append(ax.twinx())

		extra_ys =  len(axes[2:])

		# Make some space on the right side for the extra y-axes.
		if extra_ys>0:
			temp = 0.85
			if extra_ys<=2:
				temp = 0.75
			elif extra_ys<=6:
				temp = 0.6
			if extra_ys>10:
				print 'you are being ridiculous'
			fig.subplots_adjust(right=temp)
			right_additive = (0.98-temp)/float(extra_ys)
		# Move the last y-axis spine over to the right by x% of the width of the axes
		i = 1.
		for ax in axes[2:]:
			ax.spines['right'].set_position(('axes', 1.+right_additive*i))
			ax.set_frame_on(True)
			ax.patch.set_visible(False)
			ax.yaxis.set_major_formatter(matplotlib.ticker.OldScalarFormatter())
			i +=1.
		# To make the border of the right-most axis visible, we need to turn the frame
		# on. This hides the other plots, however, so we need to turn its fill off.

		cols = []
		lines = []
		line_styles = cycle(['-','-','-', '--', '-.', ':', '.', ',', 'o', 'v', '^', '<', '>',
				   '1', '2', '3', '4', 's', 'p', '*', 'h', 'H', '+', 'x', 'D', 'd', '|', '_'])
		colors = cycle(matplotlib.rcParams['axes.color_cycle'])
		for ax,y in zip(axes,ys):
			ls=line_styles.next()
			if len(y)==1:
				col = y[0]
				cols.append(col)
				color = colors.next()
				lines.append(ax.plot(crime_social_emotion_merge[col],linestyle =ls,label = col,color=color))
				ax.set_ylabel(col,color=color)
				ax.tick_params(axis='y', colors=color)
				ax.spines['right'].set_color(color)
			else:
				for col in y:
					color = colors.next()
					lines.append(ax.plot(crime_social_emotion_merge[col],linestyle =ls,label = col,color=color))
					cols.append(col)
				ax.set_ylabel(', '.join(y))
				ax.tick_params(axis='y')
		axes[0].set_xlabel(crime_social_emotion_merge.index.name)
		lns = lines[0]
		for l in lines[1:]:
			lns +=l
		labs = [l.get_label() for l in lns]
		axes[0].legend(lns, labs, loc=0)
		# for idx, y in enumerate(ys):
			# print crime_social_emotion_merge[['Crime Count']]
			# print crime_social_emotion_merge[y]
			# print '----BEGIN----'
			# print y[0]
			# plot_acf(crime_social_emotion_merge[y], use_vlines = True, alpha = 0.05)#, unbiased = True)
			# plt.savefig('%s 1 day AutoCorrelations %s v %s TopCrimes Gang' % (db_name, y[0], y[0]))
			# plt.show()
			# plt.clf()
			# ax=None
			# for idx_corr, corr_y in enumerate(ys):
			# 	# print '--Var--'
			# 	# print '%s vs %s' % (y[0], corr_y[0])
			# 	# lag_auto_correlations = [crosscorr(crime_social_emotion_merge[y[0]], crime_social_emotion_merge[y[0]], i) for i in range(1, 7)]				
			# 	# print max(lag_auto_correlations)
			# 	# print lag_auto_correlations.index(max(lag_auto_correlations)) + 1
			# 	lag_auto_correlations = []
			# 	start_val = 0
			# 	if idx_corr == idx:
			# 		start_val = 1
			# 	for i in range(start_val, 7):
			# 		crime_social_emotion_merge_copy = crime_social_emotion_merge.copy(deep=True)
			# 		crime_social_emotion_merge_copy['y_%s_%s' % (idx, idx_corr)] = crime_social_emotion_merge_copy[corr_y].shift(i)
			# 		crime_social_emotion_merge_copy.dropna(inplace=True)
			# 		# print crime_social_emotion_merge_copy
			# 		# shifted_data.dropna(inplace=True)
			# 		# r = pd.DataFrame([crime_social_emotion_merge_copy['Crime Count'], shifted_data])
			# 		# r.dropna(inplace=True)
			# 		# lag_auto_correlations.append(st.pearsonr(crime_social_emotion_merge_copy[y], crime_social_emotion_merge_copy[['y_%s_%s' % (idx, idx_corr)]]))
			# 	# print st.pearsonr(crime_social_emotion_merge_copy[y], crime_social_emotion_merge_copy[y].shift(1))
			# 	# print lag_auto_correlations
			# 	# print '--Max Correlation--'
			# 	# max_corr_idx = [abs(x[0]) for x in lag_auto_correlations].index(max([abs(x[0]) for x in lag_auto_correlations]))
			# 	# print lag_auto_correlations[max_corr_idx]
			# 	# print 'Lag: %s' % (max_corr_idx + start_val)
			# 	# print '\n'
			# 	# print '--Min P-Value--'
			# 	# min_pval_idx = [x[1] for x in lag_auto_correlations].index(min([x[1] for x in lag_auto_correlations]))
			# 	# print lag_auto_correlations[min_pval_idx]
			# 	# print 'Lag: %s' % (min_pval_idx + start_val)
			# 	ax=crosscorrelation_plot(crime_social_emotion_merge_copy[y[0]], crime_social_emotion_merge_copy[corr_y[0]], y[0], corr_y[0])
			# 	# plt.savefig('%s 1 day Correlations %s v %s TopCrimes Gang' % (db_name, y[0], corr_y[0]))
			# 	# plt.clf()
			# plt.savefig('%s 1 day Correlations %s TopCrimes Gang' % (db_name, y[0]))
			# plt.show()	
			# print '-----END-----'
			# p_val = st.pearsonr(crime_social_emotion_merge[['Gang Crimes']], crime_social_emotion_merge[y])			
			# text(0.3, 0.95-idx*0.05, 'pval gang|%s: %s' % (y[0], p_val), horizontalalignment='center', verticalalignment='center', transform = ax.transAxes)

		# ax.plot(crime_social_emotion_merge['Date Occurred'], crime_social_emotion_merge['UCR'])
		# ax.plot(crime_social_emotion_merge['Date Occurred'], crime_social_emotion_merge['_id'])
		# ax.plot(crime_social_emotion_merge['Date Occurred'], crime_social_emotion_merge['valence'])
		# ax.tick_params(axis='y')
		# ax.plot(crime_social_emotion_merge['Date Occurred'], crime_social_emotion_merge['arousal'])
		
		# fig.tight_layout()
		if tract_flag:
			plt.savefig('Tract %s, %s Time Series of Crime, Social Media Count and Sentiment Variables for SM CI TopCrimes Gang' % (tract_no, db_name))
		else:
			plt.savefig('%s Time Series of Crime, Social Media Count and Sentiment Variables for SM CI TopCrimes Gang' % (db_name))
		# plt.show()

		# crosscorrelation_plot(crime_social_emotion_merge['arousal'], crime_social_emotion_merge['Crime Count'])
		# xcorr(crime_social_emotion_merge['arousal'].values, crime_social_emotion_merge['valence'].values, usevlines=True, maxlags=50)
		# plot_acf(crime_social_emotion_merge[['valence']], use_vlines = True, alpha = 0.05)#, unbiased = True)
		# plt.show()
# plot_time_crime_social_data(top_crime_flag=True)#, tract_flag=True)
plot_time_crime_social_data(db_name='instagram_posts', top_crime_flag=True)#, tract_flag=True)

def findPopularCrimes():
	# police_incidents_csv =  pd.read_csv('%s.csv' % ('Police_Incidents'), parse_dates=['Date Occurred'])
	# police_incidents_csv.rename(columns={"Incident Number": "IN"}, inplace=True)
	# # print list(police_incidents_csv.columns.values)
	# crime_data_grouping = police_incidents_csv.groupby('UCR', as_index=False)
	# # print crime_data_grouping.columns
	# crime_data_count = crime_data_grouping.aggregate('count')
	# print list(crime_data_count.sort_values('Date Occurred', ascending=[False])[:10]['UCR Description'])
	pid_list = [640, 450, 2300, 1100, 660, 1400, 690, 670, 630, 2606]
	police_incidents_csv =  pd.read_csv('%s.csv' % ('Police_Incidents'), parse_dates=['Date Occurred'])
	print police_incidents_csv[police_incidents_csv.UCR.isin(pid_list)][['UCR Description', 'UCR']].drop_duplicates().groupby('UCR').head()
# findPopularCrimes()
