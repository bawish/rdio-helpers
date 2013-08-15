#!/usr/bin/env python
# encoding: utf-8

from rdio import Rdio
from credentials import *

rdio = Rdio((RDIO_CONSUMER_KEY, RDIO_CONSUMER_SECRET), 
		    (RDIO_TOKEN, RDIO_TOKEN_SECRET))

# initalize Rdio using tokens/secrets stored in credentials file
def initialize_rdio():	
	rdio = Rdio((RDIO_CONSUMER_KEY, RDIO_CONSUMER_SECRET), 
			    (RDIO_TOKEN, RDIO_TOKEN_SECRET))
	return rdio

# get the keys for all playlists owned by the authenticated user
# returns a list of playlist keys
def get_playlist_keys():
	playlist_keys = []
	playlists = rdio.call('getPlaylists')['result']['owned']
	for playlist in playlists:
		playlist_keys.append(playlist['key'])
	return playlist_keys

# get all the track keys for a given playlist
# returns a list of track keys
def get_playlist_tracks(playlist_key):
	track_keys = (rdio.call('get', {'keys': playlist_key, 
									'extras': 'trackKeys'})
				  ['result'][playlist_key]['trackKeys'])
	return track_keys

#returns boolean true if a track is still available; key should be a string	
def is_available(key):
	track_info = rdio.call('get', {'keys' : key})
	availability = track_info['result'][key]['canStream']
	return availability
	
# accepts dict with 'artist' and 'title'; searches rdio for matching track
# returns track key
# BETTER WAY TO DO ERROR HANDLING? SIMILARITY SCORES?
def find_track(track):
    query = track['artist']+' '+track['title']
    search = rdio.call('search', {'query': query, 'types': 'Track'})
    search = search['result']['results'] #gets rid of extraneous matter from search query return
    for result in search:
        if re.search(track['artist'],result['artist'],flags=re.IGNORECASE) != None:
            if re.search(track['title'],result['name'],flags=re.IGNORECASE) != None:
                if result['canStream']:
                    return result['key']

# looks for any dead (unavailable) tracks, attempts to replace them
# requires playlist key
def refresh_playlist(playlist_key):