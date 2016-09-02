import sys
import inspect, os
import json
import ConfigParser
import twitter
import time
import datetime
from dateutil import parser
from random import randint

import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

class Tweet:
    CONFIG = ConfigParser.RawConfigParser()
    SECTION = 'twitter'

    def __init__( self ):
        self.chars = 0
        self.full_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

        with open(self.full_path + '/settings.json') as data_file:
            self.settings = json.load(data_file)[self.SECTION]

        self.my_consumer_key = self.settings['twitter_consumer_key']
        self.my_consumer_secret = self.settings['twitter_consumer_secret']
        self.my_access_token_key = self.settings['twitter_access_token_key']
        self.my_access_token_secret = self.settings['twitter_access_token_secret']

    def check_last_tweet( self ):
        if( self.settings['disable_if_posted_recently'] ):
            try:
                api = twitter.Api(consumer_key = self.my_consumer_key,
                                    consumer_secret = self.my_consumer_secret,
                                    access_token_key = self.my_access_token_key,
                                    access_token_secret = self.my_access_token_secret)

                timeline = api.GetUserTimeline('thejokersthief')

                last_tweet_datetime = parser.parse( timeline[0].created_at )
                return (datetime.datetime.now() - last_tweet_datetime.replace(tzinfo=None)
                            ) > datetime.timedelta( hours = self.settings['disable_time_hours'] )
                
            except Exception as e:
                print "{0}".format(e)
                print "Posting to Twitter failed!"
        else:
            return true

    def tweet( self, title, url, include_quotes ):
        # calculate the chars needed (without title)
        # twitter shortens URLs at 22 (http) or 23 (https) chars
        self.chars = 4  # 2 spaces + 2 braces
        if ( url[0:8] == 'https://' ):
                if len( url ) < 23:
                        self.chars += len( url )
                else:
                        self.chars += 23
        elif ( url[0:7] == 'http://' ):
                if len( url ) < 22:
                        self.chars += len( url )
                else:
                        self.chars += 22
        elif ( url == '' ):  # it's a story on HN
                self.chars -= 3  # no space + braces for comment link
        else:
                print "Unknown URL schema: {0}".format( url )
                sys.exit(1)

        self.chars += 23  # comment url

        # cut title if too long
        if (self.chars + len(title) > 140):
                title = "{0} ...".format(title[0:140 - self.chars - 4])

        if( include_quotes ):
                t = "\"{0}\" {1}".format(title, url)
        else:
                #t = "{0} {1} ({2})".format(title, url, comment_url)
                t = "{0} {1}".format(title, url)

        isImage = False
        if( url[-4:] == ".png" or url[-4:] == ".jpg" ):
            extension = url[-3:]
            isImage = True
        elif( url[-5:] == ".jpeg" ):
            extension = "jpeg"
            isImage = True

        # Tweet it
        try:
            api = twitter.Api(consumer_key = self.my_consumer_key,
                              consumer_secret = self.my_consumer_secret,
                              access_token_key = self.my_access_token_key,
                              access_token_secret = self.my_access_token_secret)

            if( isImage ):
                api.PostMedia(title, url)
            else:
                api.PostUpdate(t)
            print "Twitter Post succeeeded: " + str( t )
        except Exception as e:
            print "{0}".format(e)
            print "Posting to Twitter failed!"

    def copyFollowers( self, screen_name ):
        try:
            api = twitter.Api(consumer_key = self.my_consumer_key,
                              consumer_secret = self.my_consumer_secret,
                              access_token_key = self.my_access_token_key,
                              access_token_secret = self.my_access_token_secret)

            for user in api.GetFollowers( screen_name = screen_name ):
                api.CreateFriendship( screen_name = user.screen_name )
        except Exception as e:
            print "{0}".format(e)
            print "Posting to Twitter failed!"

    def copyFollowing( self, screen_name ):
        # try:
            api = twitter.Api(consumer_key = self.my_consumer_key,
                              consumer_secret = self.my_consumer_secret,
                              access_token_key = self.my_access_token_key,
                              access_token_secret = self.my_access_token_secret)

            for user in api.GetFriends( screen_name = screen_name ):
                api.CreateFriendship( screen_name = user.screen_name )
        # except Exception as e:
        #     print "{0}".format(e)
        #     print "Posting to Twitter failed!"

    def getFriends( self, screen_name = 'TheJokersThief', cursor = -1 ):
        api = twitter.Api(consumer_key = self.my_consumer_key,
                          consumer_secret = self.my_consumer_secret,
                          access_token_key = self.my_access_token_key,
                          access_token_secret = self.my_access_token_secret)
        all_friends = []

        if( screen_name != 'TheJokersThief' ):
            target = open(self.full_path + '/'+ screen_name +'.json', 'a')
        else:
            target = open(self.full_path + '/list_of_friends.json', 'a')

        try:
            counter = 0
            print cursor

            for user in api.GetFriends( screen_name = screen_name, cursor = cursor, count = (cursor + 200 ) ):
                all_friends.append( user.screen_name )
                counter += 1

            cursor += 200

            if counter >= 199:
                self.getFriends( screen_name, cursor )
        except Exception, e:
            print e
            now = datetime.datetime.now()
            time.sleep( ( 16 - ( now.minute % 15 )) * 60 )
            self.getFriends( screen_name, cursor )

        print "Writing to file"
        target.write( json.dumps( all_friends ) )
        target.close()


    def removeNonFollowers( self ):
        api = twitter.Api(consumer_key = self.my_consumer_key,
                          consumer_secret = self.my_consumer_secret,
                          access_token_key = self.my_access_token_key,
                          access_token_secret = self.my_access_token_secret)

        print "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"

        with open(self.full_path + '/list_of_friends.json') as data_file:
            all_friends = json.load( data_file )

        rate_counter = 0;

        print "Checking friendship status"
        for friend in all_friends:
            print rate_counter 
            if( rate_counter >= 160 ):
                print "Waiting to bypass rate limit"
                rate_counter = 0
                # Sleep to avoid rate limiting
                time.sleep( 15 * 60 )

            print friend
            # LookupFriendship is always one count
            rate_counter += 1
            try:
                followed_by = api.LookupFriendship( screen_name = friend ).followed_by
            except Exception, e:
                print "Deleting " + friend
                # DestroyFriendship is an additional count
                api.DestroyFriendship( screen_name = friend )
                rate_counter += 1

    def chunks(self, l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i+n]
