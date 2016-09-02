import time
import json
import urllib2

from random import randint

class Functions:
	RETRIES = 10 			# Number of retries on URL failure
	SLEEP_TIME = 2 * 60 	# Time to wait between retries

	def __init__(self, seen_db_name):
		self.SEENDB = seen_db_name

	def seen( self, myid ):
		try:
			with open(  self.SEENDB, 'r' ) as f:
				if(  str( myid ).encode('utf-8') in [ x.strip() for x in f.readlines() ] ):
					return 1
				else:
					return 0
		except Exception as e:
			return 0

	def write_to_seen( self, myid ):
		with open( self.SEENDB, 'a' ) as f:
			f.write( str( myid ) )
			f.write( '\n' )


	def get_data( self, url ):
		i = 1
		errormsg = ''
		data = None

		while( i < self.RETRIES+1 and not data ):
			print str( i ) + ": Getting data..."
			try:
				opener = urllib2.build_opener(  )
				opener.addheaders = [( 'User-agent', 'UCC Netsoc Twitter Poster' )]
				data = json.load( opener.open( url ) )
			except Exception as e:
				errormsg = errormsg + "Run {0}: {1}\n".format( i, e )
				time.sleep(  randint(  0, self.SLEEP_TIME ) )
				i += 1

		if data:
			return data
		else:
			print errormsg
			print "API call {0} failed!".format( url )
			return False
