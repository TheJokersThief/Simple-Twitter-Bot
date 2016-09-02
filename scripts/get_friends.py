import sys
sys.path.append("..")
from Tweet import Tweet

Tweet = Tweet( )

if len( sys.argv ) < 2:
	Tweet.getFriends( )
else:
	Tweet.getFriends( sys.argv[1] )