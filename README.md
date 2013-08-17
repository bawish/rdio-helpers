A set of methods built on top of the rdio-simple library for Python that make interacting with the Rdio API even, well, simpler (and convenient).

Store your credentials in a separate file called credentials.py. These should include:

1. RDIO_CONSUMER_KEY
2. RDIO_CONSUMER_SECRET
3. RDIO_TOKEN
4. RDIO_TOKEN_SECRET

The methods are, in order of descending awesomeness:

*refresh_playlist*: Often times certain new tracks go "dead". This especially happens when an artist releases an EP and then a full-length--the EP tracks sometimes become unavailable. This method accepts a playlist key and then "refreshes" the playlist, finding dead tracks and replacing them with the "live" versions of the same song (and in the same order).

*find_track*: accepts a dictionary in the form of {'artist': ARTIST, 'title': TITLE} and then searches Rdio for that track. Returns a track key if found.

*get_playlist_tracks*: returns all the track keys for a given playlist

*get_playlist_keys*: returns the keys of all playlists for a given user

*initialize_rdio*: just an easy way to initialize the Rdio object without have to type your credentials over and over