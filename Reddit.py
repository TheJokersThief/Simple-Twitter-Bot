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

# Fetch posts from reddit and tweet them
class Reddit:
	CONFIG = ConfigParser.RawConfigParser()
	SECTION = 'reddit'

	"""Initialise Reddit object
	
	wait_time 	=> The time to wait between each post
	"""
	def __init__( self, wait_time ):
		self.WAIT_TIME = wait_time
		self.full_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
  
		with open(self.full_path + '/settings.json') as data_file: 
		    self.REDDIT_URLS = json.load(data_file)[self.SECTION]["urls"]

		self.FUNCTIONS = Functions( self.SECTION +'.db' )
		self.TWEET = Tweet()

	"""Fetch and tweet stories from the source
	
	story_count => Number of stories to post 
	"""
	def tweet_stories( self, story_count ):
		for url in self.REDDIT_URLS:
			# For each URL defined in the config, get the JSON data 
			print "Getting data from " + str( url ) + "\n"
			data = self.FUNCTIONS.get_data( url )
		
			if( data == False ):
				# If it returns no data, continue onto the next URL
				continue

			print "Got data \n"

			# Posts are "children" of the main request
			children = data['data']['children']

			counter = 0
			for post in children:
				postid = post['data']['subreddit'] + "_" + str(post['data']['id'])
				if( counter >= story_count ):
					# Only use a certain number of posts
					break

				counter += 1

				if( self.FUNCTIONS.seen( postid ) ):
					# If a post has been posted already, ignore it and continue to the next 
					continue

				url = post['data']['url']
				title = post['data']['title'].encode('utf-8')
				comment_url = post['data']['permalink']
				
				if "i.reddituploads.com" in url:
					continue
				
				if( url != '' ):
					self.TWEET.tweet( title, url, True )
				else:
					# If the URL is empty, tweet the post's comment URL instead
					self.TWEET.tweet( title, comment_url, True )

				self.FUNCTIONS.write_to_seen(postid)
				time.sleep( randint( 0, self.WAIT_TIME ) )
