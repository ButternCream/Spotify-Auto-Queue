# **********************************************************************************
# Spotify_Handle V0.01
# By:Ben Bellerose
# Description: This program handles all spotify interaction for the application.
# Reference: https://github.com/drshrey/spotify-flask-auth-example
# **********************************************************************************
# Modified from the original version above!

import json
import requests
import base64
import urllib
from flask import request
import logging
from utils import Utils
logger = logging.getLogger("Queue_Bot")

data = Utils.load_settings()

# Client Keys
CLIENT_ID = data['spotify']['CLIENT_ID']
CLIENT_SECRET = data['spotify']['CLIENT_SECRET']
history = data['history']['enabled']
playlist_id = data['history']['playlist_id']

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# Server-side Parameters
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 8080
REDIRECT_URI = "{}:{}/callback/q".format(CLIENT_SIDE_URL, PORT)
SCOPE = "user-modify-playback-state playlist-modify-public playlist-modify-private user-read-currently-playing"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()
refresh_token = None
authorization_header = None

# Authorization of application with spotify


def app_Authorization():
  auth_query_parameters = {
      "response_type": "code",
      "redirect_uri": REDIRECT_URI,
      "scope": SCOPE,
      "client_id": CLIENT_ID
  }
  url_args = "&".join(["{}={}".format(key, val)
                       for key, val in auth_query_parameters.items()])
  auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
  return auth_url


def user_Authorization():
  global refresh_token, authorization_header
  auth_token = request.args['code']
  code_payload = {
      "grant_type": "authorization_code",
      "code": str(auth_token),
      "redirect_uri": REDIRECT_URI
  }
  base64encoded = base64.b64encode("{}:{}".format(
      CLIENT_ID, CLIENT_SECRET).encode('utf-8'))
  headers = {"Authorization": "Basic {}".format(
      base64encoded.decode('utf-8'))}
  post_request = requests.post(
      SPOTIFY_TOKEN_URL, data=code_payload, headers=headers)

  # Tokens are Returned to Application
  response_data = json.loads(post_request.text)
  access_token = response_data["access_token"]
  refresh_token = response_data["refresh_token"]
  token_type = response_data["token_type"]
  expires_in = response_data["expires_in"]

  # Use the access token to access Spotify API
  authorization_header = {
      "Authorization": "Bearer {}".format(access_token)}
  return authorization_header


def refresh():
  code_payload = {
      "grant_type": "refresh_token",
      "refresh_token": str(refresh_token)
  }
  base64encoded = base64.b64encode("{}:{}".format(
      CLIENT_ID, CLIENT_SECRET).encode('utf-8'))
  headers = {"Authorization": "Basic {}".format(
      base64encoded.decode('utf-8'))}
  post_request = requests.post(
      SPOTIFY_TOKEN_URL, data=code_payload, headers=headers)

  logger.info(post_request.text)

  # Tokens are Returned to Application
  response_data = json.loads(post_request.text)
  access_token = response_data["access_token"]
  token_type = response_data["token_type"]
  expires_in = response_data["expires_in"]

  authorization_header = {
      "Authorization": "Bearer {}".format(access_token)}
  return authorization_header


def add_song_to_queue(uri):
  url = 'https://api.spotify.com/v1/me/player/queue?uri={id}'.format(id=uri)
  result = process_request(url, 'post')
  logger.debug(result.text)
  if result.status_code == 204:
    global history
    if history:
      add_to_history(uri)
    track_req = get_track_info(uri)
    json_obj = track_req.json()
    artists = ', '.join(artists['name']
                        for artists in json_obj['artists'])
    song_name = json_obj['name']
    data = {
        'song': song_name,
        'artists': artists,
        'uri': uri
    }
    return data
  return


def add_to_history(uri):
  global playlist_id
  url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks?uris={uri}'
  result = process_request(url, 'post')
  logger.debug(result.text)
  return result


def get_track_info(uri):
  url = 'https://api.spotify.com/v1/tracks/{id}'
  id = uri.split(':')[-1]
  return process_request(url.format(id=id), 'get')


def get_song_and_artist(uri):
  track_req = get_track_info(uri)
  json_obj = track_req.json()
  logger.debug(json_obj)
  artists = ', '.join(artists['name']
                      for artists in json_obj['artists'])
  song_name = json_obj['name']
  logger.debug('here')
  return song_name, artists


def get_current_song():
  url = 'https://api.spotify.com/v1/me/player/currently-playing'
  response = process_request(url, 'get')
  if response.status_code == 200:
    try:
      response_json = response.json()
      song_title = response_json['item']['name']
      artists_json = response_json['item']['artists']
      artists = ', '.join(artists['name']
                          for artists in artists_json)
      logger.debug(f'Found {song_title} by {artists}')
      return song_title, artists
    except Exception as e:
      logger.debug(str(e))
  else:
    logger.debug(response)

  return None


def process_request(url, request_type):
  global authorization_header
  logger.info('Processing {} request {}'.format(request_type, url))
  if request_type == 'post':
    spotify_request = requests.post
  elif request_type == 'get':
    spotify_request = requests.get
  else:
    spotify_request = requests.put
  result = spotify_request(url, headers=authorization_header)
  return result


def refresh_wrapper():
  global authorization_header
  logger.info("REFRESHING AUTH")
  authorization_header = refresh()
  logger.debug("New Auth Header")
  logger.debug(authorization_header)
  logger.debug('\n\n')
