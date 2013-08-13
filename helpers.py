#!/usr/bin/env python
# encoding: utf-8

from rdio import Rdio
from credentials import *

# initalize Rdio using tokens/secrets stored in credentials file
rdio = Rdio((RDIO_CONSUMER_KEY, RDIO_CONSUMER_SECRET), 
		    (RDIO_TOKEN, RDIO_TOKEN_SECRET))

# get the keys for all playlists owned by the authenticated user
# returns a list of playlist keys
def getPlaylistKeys():
	playlist_keys = []
	playlists = rdio.call('getPlaylists')['result']['owned']
	for playlist in playlists:
		playlist_keys.append(playlist['key'])
	return playlist_keys

# get all the track keys for a given playlist
# returns a list of track keys
def getPlaylistTracks(playlist_key):
	track_keys = rdio.call('get', {'keys': playlist_key, 'extras': 'trackKeys'}

def main():
	
	#METHODS TO RUN GO HERE
	
if __name__ == '__main__':
	main()