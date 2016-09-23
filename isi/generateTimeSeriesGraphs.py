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
# from statsmodels.tsa.stattools import adfuller
import json
from wordcloud import WordCloud, STOPWORDS
from bson.code import Code
from matplotlib.pylab import rcParams
from collections import defaultdict
import csv
import string
import matplotlib
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

def create_word_cloud(json_file, field_name='text', query={}):
	stop_words = ['https', 'co', "rt", "amp", "able" , "about" , "above" , "abroad" , "according" , "accordingly" , "across" , "actually" , "adj" , "after" , "afterwards" , "again" , "against" , "ago" , "ahead" , "ain't" , "all" , "allow" , "allows" , "almost" , "alone" , "along" , "alongside" , "already" , "also" , "although" , "always" , "am" , "amid" , "amidst" , "among" , "amongst" , "an" , "and" , "another" , "any" , "anybody" , "anyhow" , "anyone" , "anything" , "anyway" , "anyways" , "anywhere" , "apart" , "appear" , "appreciate" , "appropriate" , "are" , "aren't" , "around" , "as" , "a's" , "aside" , "ask" , "asking" , "associated" , "at" , "available" , "away" , "awfully" , "back" , "backward" , "backwards" , "be" , "became" , "because" , "become" , "becomes" , "becoming" , "been" , "before" , "beforehand" , "begin" , "behind" , "being" , "believe" , "below" , "beside" , "besides" , "best" , "better" , "between" , "beyond" , "both" , "brief" , "but" , "by" , "came" , "can" , "cannot" , "cant" , "can't" , "caption" , "cause" , "causes" , "certain" , "certainly" , "changes" , "clearly" , "c'mon" , "co" , "co." , "com" , "come" , "comes" , "concerning" , "consequently" , "consider" , "considering" , "contain" , "containing" , "contains" , "corresponding" , "could" , "couldn't" , "course" , "c's" , "currently" , "dare" , "daren't" , "definitely" , "described" , "despite" , "did" , "didn't" , "different" , "directly" , "do" , "does" , "doesn't" , "doing" , "done" , "don't" , "down" , "downwards" , "during" , "each" , "edu" , "eg" , "eight" , "eighty" , "either" , "else" , "elsewhere" , "end" , "ending" , "enough" , "entirely" , "especially" , "et" , "etc" , "even" , "ever" , "evermore" , "every" , "everybody" , "everyone" , "everything" , "everywhere" , "ex" , "exactly" , "example" , "except" , "fairly" , "far" , "farther" , "few" , "fewer" , "fifth" , "first" , "five" , "followed" , "following" , "follows" , "for" , "forever" , "former" , "formerly" , "forth" , "forward" , "found" , "four" , "from" , "further" , "furthermore" , "get" , "gets" , "getting" , "given" , "gives" , "go" , "goes" , "going" , "gone" , "got" , "gotten" , "greetings" , "had" , "hadn't" , "half" , "happens" , "hardly" , "has" , "hasn't" , "have" , "haven't" , "having" , "he" , "he'd" , "he'll" , "hello" , "help" , "hence" , "her" , "here" , "hereafter" , "hereby" , "herein" , "here's" , "hereupon" , "hers" , "herself" , "he's" , "hi" , "him" , "himself" , "his" , "hither" , "hopefully" , "how" , "howbeit" , "however" , "hundred" , "i'd" , "ie" , "if" , "ignored" , "i'll" , "i'm" , "immediate" , "in" , "inasmuch" , "inc" , "inc." , "indeed" , "indicate" , "indicated" , "indicates" , "inner" , "inside" , "insofar" , "instead" , "into" , "inward" , "is" , "isn't" , "it" , "it'd" , "it'll" , "its" , "it's" , "itself" , "i've" , "just" , "k" , "keep" , "keeps" , "kept" , "know" , "known" , "knows" , "last" , "lately" , "later" , "latter" , "latterly" , "least" , "less" , "lest" , "let" , "let's" , "like" , "liked" , "likely" , "likewise" , "little" , "look" , "looking" , "looks" , "low" , "lower" , "ltd" , "made" , "mainly" , "make" , "makes" , "many" , "may" , "maybe" , "mayn't" , "me" , "mean" , "meantime" , "meanwhile" , "merely" , "might" , "mightn't" , "mine" , "minus" , "miss" , "more" , "moreover" , "most" , "mostly" , "mr" , "mrs" , "much" , "must" , "mustn't" , "my" , "myself" , "name" , "namely" , "nd" , "near" , "nearly" , "necessary" , "need" , "needn't" , "needs" , "neither" , "never" , "neverf" , "neverless" , "nevertheless" , "new" , "next" , "nine" , "ninety" , "no" , "nobody" , "non" , "none" , "nonetheless" , "noone" , "no-one" , "nor" , "normally" , "not" , "nothing" , "notwithstanding" , "novel" , "now" , "nowhere" , "obviously" , "of" , "off" , "often" , "oh" , "ok" , "okay" , "old" , "on" , "once" , "one" , "ones" , "one's" , "only" , "onto" , "opposite" , "or" , "other" , "others" , "otherwise" , "ought" , "oughtn't" , "our" , "ours" , "ourselves" , "out" , "outside" , "over" , "overall" , "own" , "particular" , "particularly" , "past" , "per" , "perhaps" , "placed" , "please" , "plus" , "possible" , "presumably" , "probably" , "provided" , "provides" , "que" , "quite" , "qv" , "rather" , "rd" , "re" , "really" , "reasonably" , "recent" , "recently" , "regarding" , "regardless" , "regards" , "relatively" , "respectively" , "right" , "round" , "said" , "same" , "saw" , "say" , "saying" , "says" , "second" , "secondly" , "see" , "seeing" , "seem" , "seemed" , "seeming" , "seems" , "seen" , "self" , "selves" , "sensible" , "sent" , "serious" , "seriously" , "seven" , "several" , "shall" , "shan't" , "she" , "she'd" , "she'll" , "she's" , "should" , "shouldn't" , "since" , "six" , "so" , "some" , "somebody" , "someday" , "somehow" , "someone" , "something" , "sometime" , "sometimes" , "somewhat" , "somewhere" , "soon" , "sorry" , "specified" , "specify" , "specifying" , "still" , "sub" , "such" , "sup" , "sure" , "take" , "taken" , "taking" , "tell" , "tends" , "th" , "than" , "thank" , "thanks" , "thanx" , "that" , "that'll" , "thats" , "that's" , "that've" , "the" , "their" , "theirs" , "them" , "themselves" , "then" , "thence" , "there" , "thereafter" , "thereby" , "there'd" , "therefore" , "therein" , "there'll" , "there're" , "theres" , "there's" , "thereupon" , "there've" , "these" , "they" , "they'd" , "they'll" , "they're" , "they've" , "thing" , "things" , "think" , "third" , "thirty" , "this" , "thorough" , "thoroughly" , "those" , "though" , "three" , "through" , "throughout" , "thru" , "thus" , "till" , "to" , "together" , "too" , "took" , "toward" , "towards" , "tried" , "tries" , "truly" , "try" , "trying" , "t's" , "twice" , "two" , "un" , "under" , "underneath" , "undoing" , "unfortunately" , "unless" , "unlike" , "unlikely" , "until" , "unto" , "up" , "upon" , "upwards" , "us" , "use" , "used" , "useful" , "uses" , "using" , "usually" , "v" , "value" , "various" , "versus" , "very" , "via" , "viz" , "vs" , "want" , "wants" , "was" , "wasn't" , "way" , "we" , "we'd" , "welcome" , "well" , "we'll" , "went" , "were" , "we're" , "weren't" , "we've" , "what" , "whatever" , "what'll" , "what's" , "what've" , "when" , "whence" , "whenever" , "where" , "whereafter" , "whereas" , "whereby" , "wherein" , "where's" , "whereupon" , "wherever" , "whether" , "which" , "whichever" , "while" , "whilst" , "whither" , "who" , "who'd" , "whoever" , "whole" , "who'll" , "whom" , "whomever" , "who's" , "whose" , "why" , "will" , "willing" , "wish" , "with" , "within" , "without" , "wonder" , "won't" , "would" , "wouldn't" , "yes" , "yet" , "you" , "you'd" , "you'll" , "your" , "you're" , "yours" , "yourself" , "yourselves" , "you've" , "zero"]
	with open(json_file) as data_file:
		data = json.load(data_file)
		text_list = []
		for data_val in data:
			try:
				if field_name in ['text', 'tags']:
					text_list.append(' '.join([word.replace('https', '').replace('co', '') for word in data_val[field_name].split() if word.lower() not in stop_words]))
				else:
					text_list.append(' '.join([word.replace('https', '').replace('co', '') for word in data_val['caption']['text'].split() if word.lower() not in stop_words]))
			except:
				pass
		# print text_list
		# map(lambda x: text_list.append(x[field_name]), data)
		text = ' '.join(text_list)
		wordcloud = WordCloud().generate(text)
		# Open a plot of the generated image.
		plt.imshow(wordcloud)
		plt.axis("off")
		# plt.show()
		# Save the figure
		plt.savefig('%s_word_cloud.png' % (json_file))


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
	valence, dominance, affect, total_count, g_count = [0.0, 0.0, 0.0, 0, 0]
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
	# min_val, max_val = data.min().min(), data.max().max()
	# ranges = np.linspace(min_val, max_val, 21)
	# data1 = data.groupby(pd.cut(data['valence'], ranges)).count()[['valence']]
	# data2 = data.groupby(pd.cut(data['arousal'], ranges)).count()[['arousal']]
	# data3 = data.groupby(pd.cut(data['dominance'], ranges)).count()[['dominance']]
	# data = pd.concat([data1, data2, data3], axis=1)
	# print data.corr()
	# data.plot(kind='bar', legend=True, figsize=(15,10), fontsize=12, alpha=0.75, rot=65)
	# plt.xlabel('WKB variables')
	# plt.ylabel('Count')
	# plt.tight_layout()
	# plt.savefig('%s_%s_%s.png' % (db_name, 'WKB_variables', datetime.now().strftime("%Y_%m_%d_%H_%M_%S")))
	# plt.show()
	# print data1.columns
	# print data1
	# pd.merge(data1, data2, on='')
	# print data
	print data.sum()/data.count()


# show_wkb_bar_graphs(query={'wkb_sentiment_analysis_flag': True})
# show_wkb_bar_graphs(db_name='instagram_posts', query={'wkb_sentiment_analysis_flag': True})
# show_wkb_bar_graphs(db_name='instagram_comments', query={'wkb_sentiment_analysis_flag': True})

def show_sentistrength_bar_graphs(db_name='twitter_posts', query={'sentstrength_negative_sentiment':{'$ne':None}}):
	db_data = list(getattr(sys.modules[__name__], 'db_%s' % db_name).find(query, {'sentstrength_negative_sentiment':1, 'sentstrength_positive_sentiment':1}))
	print 'done'
	for sentiment in ['positive', 'negative']:
		data = pd.DataFrame(db_data, columns=['sentstrength_%s_sentiment' % (sentiment)])
		# min_val, max_val = data.min().min(), data.max().max()
		# ranges = np.linspace(1, 5, 5)
		# if min_val < 0:
		# 	ranges = np.linspace(-5, -1, 5)
		# data = data.groupby(pd.cut(data['sentstrength_%s_sentiment' % (sentiment)], ranges)).count()
		# data.plot(kind='bar', legend=True, figsize=(15,10), fontsize=12, alpha=0.75, rot=65)
		# xlabel = 'Sentistrength %s sentiment' % (sentiment)
		# plt.xlabel(xlabel)
		# plt.ylabel('Count')
		# plt.tight_layout()
		# plt.savefig('%s_%s_%s.png' % (db_name, ('_').join(xlabel.split()), datetime.now().strftime("%Y_%m_%d_%H_%M_%S")))
		# plt.clf()
		# # plt.show()
		# # print data1.columns
		# # print data1
		# # pd.merge(data1, data2, on='')
		# # print data
		print data.sum()/data.count()

# show_sentistrength_bar_graphs()
# show_sentistrength_bar_graphs(db_name='instagram_posts')
# show_sentistrength_bar_graphs(db_name='instagram_comments')


def show_different_wkb():
	data = pd.DataFrame({'WKB Parameters': ['Valence', 'Arousal', 'dominance'], 'Twitter': [6.001096, 4.148224, 5.613052], 'Instagram Posts':[6.327977, 4.311188, 5.795368], 'Instagram Comments':[6.537544, 4.352565, 5.970616]})
	data = data.set_index(['WKB Parameters'])
	data.plot(kind='bar', legend=True, figsize=(15,10), fontsize=12, alpha=0.75, rot=65)
	# data.set_xticklabels(['Twitter', 'Instagram Posts', 'Instagram Comments'])
	# plt.legend(handles=['Twitter', 'Instagram Posts', 'Instagram Comments'])
	plt.xlabel('WKB Parameters')
	plt.ylabel('Values')
	plt.tight_layout()
	plt.savefig('WKB Parameters.png')

	# plt.show()

show_different_wkb()

def show_different_correlations():
	data = pd.DataFrame({'WKB Parameters': ['V/A', 'A/D', 'D/V'], 'Twitter': [-0.264976,-0.163940, 0.820971], 'Instagram Posts':[-0.330027, -0.130260, 0.651406], 'Instagram Comments':[-0.337782, -0.089629, 0.584920]})
	data = data.set_index(['WKB Parameters'])
	data.plot(kind='bar', legend=True, figsize=(15,10), fontsize=12, alpha=0.75, rot=65)
	# data.set_xticklabels(['Twitter', 'Instagram Posts', 'Instagram Comments'])
	# plt.legend(handles=['Twitter', 'Instagram Posts', 'Instagram Comments'])
	plt.xlabel('WKB Parameters')
	plt.ylabel('Values')
	plt.tight_layout()
	plt.savefig('WKB Correlations.png')

show_different_correlations()


def show_different_sentistrength():
	data = pd.DataFrame({'WKB Parameters': ['Positive', 'Negative'], 'Twitter': [1.428247,-1.088973], 'Instagram Posts':[1.683773, -1.142164], 'Instagram Comments':[1.802289, -1.070709]})
	data = data.set_index(['WKB Parameters'])
	data.plot(kind='bar', legend=True, figsize=(15,10), fontsize=12, alpha=0.75, rot=65)
	plt.xlabel('SentiStrength')
	plt.ylabel('Values')
	plt.tight_layout()
	plt.savefig('SentiStrength Correlations.png')
# show_different_sentistrength()