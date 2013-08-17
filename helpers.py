#!/usr/bin/env python
# encoding: utf-8

from rdio import Rdio
from credentials import *
import re

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
def find_track(track_dict):
    query = track_dict['artist']+' '+track_dict['title']
    search = rdio.call('search', {'query': query, 'types': 'Track'})
    search = search['result']['results'] #gets rid of extraneous matter from search query return
    for result in search:
        if re.search(track_dict['artist'],result['artist'],flags=re.IGNORECASE) != None:
            if re.search(track_dict['title'],result['name'],flags=re.IGNORECASE) != None:
                if result['canStream']:
                    return result['key']

# creates a dict with 'artist' and 'title' attributes from a track key
def create_track_dict(track_key):
	track_info = rdio.call('get', {'keys': track_key})['result'][track_key]
	track_dict = {'artist': track_info['artist'], 'title': track_info['name']}
	return track_dict

# looks for any dead (unavailable) tracks, attempts to replace them
# requires playlist key
def refresh_playlist(playlist_key):
	tracks = get_playlist_tracks(playlist_key)
	for track in tracks:
		if not is_available(track):
			if find_track(create_track_dict(track)):
				new_track_key = find_track(create_track_dict(track))
				index = tracks.index(track)
				rdio.call('addToPlaylist', {'playlist': playlist_key, 
											'tracks': new_track_key})
				rdio.call('removeFromPlaylist', {'playlist': playlist_key, 
												 'index': index, 'count': 1, 
												 'tracks': track})
				new_track_list = get_playlist_tracks(playlist_key)
				new_track_list.insert(index, new_track_key)
				new_track_list.pop()
				new_track_list_string = ', '.join(new_track_list)
				rdio.call('setPlaylistOrder', {'playlist': playlist_key, 'tracks': new_track_list_string}) 