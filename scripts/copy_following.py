import sys
sys.path.append("..")
from Tweet import Tweet

Tweet = Tweet( )

if len( sys.argv ) < 2:
	print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
	print "Please pass the username you want to copy from"
	print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
else:
	Tweet.copyFollowing( sys.argv[1] )