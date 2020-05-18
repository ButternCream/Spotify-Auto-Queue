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
