# Import necessary libraries and modules
import tweepy
import time
import sys
import spotipy
import spotipy.util as util
from tweepy import OAuthHandler
from tweepy import API
from tweepy import Cursor
from datetime import datetime, date, time, timedelta
from collections import Counter

# Import API keys from separate files
from keys import *
from key_spotify import *

# Authenticate Twitter API access
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

# Constants
FILE_NAME = 'last_seen_id.txt'
hashtag = ""  
playlist = ''  
client = tweepy.Client(bearer_token='')  
screen_name = ''  

# Function to add a track to a Spotify playlist
def add_to_playlist(track):
    # Get Spotify token
    token = util.prompt_for_user_token(SPOTIFY_ACCOUNT, SCOPE, SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI)
    try:
        if token:
            # Initialize Spotipy
            sp = spotipy.Spotify(auth=token)
            sp.trace = False
            
            # Get user playlist
            playlist = sp.user_playlist(SPOTIFY_ACCOUNT, SPOTIFY_PLAYLIST)
            tracks = playlist['tracks']
            totalTracks = tracks['total']
            
            # Get ID of latest added track
            if totalTracks > 0:
                latestAdd = tracks['items'][0]
                latestTrackId = latestAdd['track']['id']
            
            # Remove oldest track if playlist is full
            if totalTracks >= 200:
                print("REMOVE")
                sp.user_playlist_remove_all_occurrences_of_tracks(SPOTIFY_ACCOUNT, SPOTIFY_PLAYLIST, [latestTrackId])
            
            # Add track to playlist
            try:
                sp.user_playlist_remove_all_occurrences_of_tracks(SPOTIFY_ACCOUNT, SPOTIFY_PLAYLIST, [track])
                sp.user_playlist_add_tracks(SPOTIFY_ACCOUNT, SPOTIFY_PLAYLIST,[track])
                return True
            except:
                sp.user_playlist_add_tracks(SPOTIFY_ACCOUNT, SPOTIFY_PLAYLIST,[track])
                return True
        else:
            print("Can't get token for", SPOTIFY_ACCOUNT)
            return False
    except:
        print("Can't add track to playlist")
        return False
    
# Function to extract track URI from tweet
def getURI(tweet):
    tweet = str(tweet).split(" ")
    for i in tweet:
        i = i.strip()
        if i.find("https://t.co/") != -1:
            i = i[i.find("https://open.spotify.com/track/"):len(i)]
            tweet = i[31:i.find("?")]
        elif i.find("spotify:track:") != -1:
            i = i[i.find("spotify:track:"):len(i)]
            tweet = i[14:len(i)]                  
    return tweet                                                 
                    

# Function to calculate account age in days
def account_age(item):
    account_created_date = item.created_at
    delta = datetime.utcnow() - account_created_date
    account_age_days = delta.days
    return account_age_days
    
# Function to store the ID of the last seen tweet
def store_last_seen_id(last_seen_id, file_name):
    f_write = open(file_name, 'w')
    f_write.write(str(last_seen_id))
    f_write.close()
    return

# Function to retrieve the ID of the last seen tweet
def retrieve_last_seen_id(file_name):
    f_read = open(file_name, 'r')
    last_seen_id = int(f_read.read().strip())
    f_read.close()
    return last_seen_id

# Function to get tweets from a specific user's timeline
def get_tweets(screen_name):
    tweets = api.user_timeline(user, screen_name, count=200,include_rts = False,tweet_mode = 'extended')
    substring = 'https://t.co/'
    for info in tweets[:3]:
        if substring in info.full_text:
            add_to_playlist(getURI(tweets))
            print(info.full_text)
           
            


while True:
    get_tweets()    
    time.sleep(60)
    