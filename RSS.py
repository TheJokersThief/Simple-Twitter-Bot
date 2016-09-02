import sys
import inspect, os
import time
import datetime
import json
import ConfigParser
import HTMLParser
import feedparser
from random import randint


from Functions import Functions
from Tweet import Tweet

# Fetch posts from reddit and tweet them
class RSS:
 CONFIG = ConfigParser.RawConfigParser()
 SECTION = 'rss'

 def __init__( self, wait_time ):
  self.WAIT_TIME = wait_time
  self.FUNCTIONS = Functions( self.SECTION +'.db' )
  self.TWEET = Tweet()
  self.full_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
  
  with open(self.full_path + '/settings.json') as data_file:    
    self.RSS_URLS = json.load(data_file)[self.SECTION]["urls"]

 def tweet_stories( self, story_count ):
  for url in self.RSS_URLS:
   # For each URL defined in the config, get the JSON data 
   print "Getting data from " + str( url ) + "\n"
   data = feedparser.parse( url )
  
   if( data == False ):
    # If it returns no data, continue onto the next URL
    continue

   print "Got data \n"

   # Posts are "children" of the main request
   children = data['entries']

   counter = 0
   for post in children:
    postid = data['feed']['title'] + "_" + str(post['id'])
    if( counter >= story_count ):
     # Only use a certain number of posts
     break

    counter += 1

    if( self.FUNCTIONS.seen( postid ) ):
     # If a post has been posted already, move to the next one and reset the counter
     counter -= 1
     continue

    url = post['link']
    title = post['title'].encode('utf-8')
    
    self.TWEET.tweet( title, url, False )

    self.FUNCTIONS.write_to_seen(postid)
    time.sleep( randint( 0, self.WAIT_TIME ) )
