#!/usr/bin/env python
# encoding: utf-8

from rdio import Rdio
from credentials import *
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

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
def find_track(track_dict):
	# not sure the encoding here helps; try deleting it at some point
	if type(track_dict['artist']) == 'unicode':
		track_dict['artist'] = track_dict['artist'].encode('utf8', 'ignore')
	if type(track_dict['title']) == 'unicode':
		track_dict['title'] = track_dict['title'].encode('utf8', 'ignore')
	
	query = track_dict['artist']+' '+track_dict['title']
	
	try:
		search = rdio.call('search', {'query': query, 'types': 'Track'})
	except UnicodeEncodeError, e:
		# get index of problem character
		error_message = str(e)
		m = re.search('(?<=position )..', error_message)
		char_index = int(m.group())
		
		#eliminate trouble character & re-search
		query = query[:char_index] + query[char_index+1:]
		search = rdio.call('search', {'query': query, 'types': 'Track'})
    
	#set how many options to search amongst; never more than 5
	result_count = search['result']['track_count']
	choice_count = 5 if result_count > 5 else result_count #one-line if-else statement!
	
	choices = []
	
	for i in range(0, choice_count):
		choice_string = (search['result']['results'][i]['artist'] + ' ' + 
						 search['result']['results'][i]['name'])
		choices.append(choice_string)
		
	#use seatgeek fuzzywuzzy matching to find best choice
	best_choice = process.extractOne(query, choices)

	#weed out results with low similarity scores
	if (int(best_choice[1]))>89:
	
		index = choices.index(best_choice[0])
		
		#make sure it's streamable
		if search['result']['results'][index]['canStream']:
			
			#get the track key for the best choice
			key = search['result']['results'][index]['key']
			return key
		
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
			track_query = create_track_dict(track)
			if find_track(track_query):
				new_track_key = find_track(track_query)
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