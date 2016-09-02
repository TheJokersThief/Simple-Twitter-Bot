#!/usr/bin/env python
# -*- coding: utf-8 -*-

from HackerNews import HackerNews
from Reddit import Reddit
from RSS import RSS

# CONSTANTS
RETRIES = 10 			# Number of retries on URL failure
WAIT_TIME = 20 * 60 	# Time to wait between posting (in seconds)

news = HackerNews( WAIT_TIME )
news.tweet_stories( 5 )

reddit = Reddit( WAIT_TIME )
reddit.tweet_stories( 3 )

rss = RSS( WAIT_TIME )
rss.tweet_stories( 2 )
