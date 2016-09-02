import sys
import inspect, os
import time
import datetime
import json
import ConfigParser
import HTMLParser
from random import randint

from Functions import Functions
from Tweet import Tweet

class HackerNews:
	CONFIG = ConfigParser.ConfigParser()
	SECTION = 'hacker_news'

	def __init__( self, wait_time ):
		self.WAIT_TIME = wait_time

		self.full_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
  
		with open(self.full_path + '/settings.json') as data_file: 
			self.settings = json.load(data_file)[self.SECTION]

		self.APIURL = self.settings["apiurl"]
		self.TOPSTORIESURL = self.settings["topstoriesurl"]
		self.COMMENT = self.settings["comment"]

		self.FUNCTIONS = Functions( self.SECTION +'.db' )
		self.TWEET = Tweet()

	def tweet_stories( self, story_count ):
		data = {}
		topstories = self.FUNCTIONS.get_data(self.TOPSTORIESURL)
		h = HTMLParser.HTMLParser()
		unseen = [(rank, storyid) for (rank, storyid) in
				  list(enumerate(topstories[ 0:story_count ])) if not self.FUNCTIONS.seen(storyid)]

		for (rank, storyid) in unseen:
			if rank not in data:
				jsonurl = "{0}item/{1}.json".format(self.APIURL, storyid)
				data[rank] = self.FUNCTIONS.get_data(jsonurl)

			title = data[rank]['title'].encode('utf-8')
			title.replace( "Show HN: ", "" )

			if 'url' in data[rank]:
				url = h.unescape(data[rank]['url']).encode('utf-8')
			else:
				url = ''
			
			comment_url = "{0}{1}".format(self.COMMENT, storyid)

			if( url != '' ):
				self.TWEET.tweet( title, url, False )
			else:
				self.TWEET.tweet( title, comment_url, False )

			self.FUNCTIONS.write_to_seen(storyid)
			time.sleep( randint( 0, self.WAIT_TIME ) )
		else:
		   print "No tweets to send " + str( datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y") )
