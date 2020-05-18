# **********************************************************************************
# Spotify Queue Bot V1.08
# By: ButterandCream
# Description: This bot allows songs to be queued in spotify via twitch chat
# **********************************************************************************


from flask import Flask, render_template_string, redirect
from spotify import app_Authorization, user_Authorization, refresh
import requests
import webbrowser
import re
import threading
import json
import os
import time
# Custom Classes / Files
from irc_bot import Bot
from utils import Utils, Constants


def new_message(context):
  '''Handler for new twitch chat messages

     context: JSON from twitch with details pertaining to the message sent
  '''
  global bot_enabled, log_reward_id, bot
  # Log reward id if option is enabled
  if log_reward_id and 'custom-reward-id' in context.keys():
    logger.info("Custom Reward ID: {}".format(context['custom-reward-id']))
    logger.info("Message: {}".format(context['message']))

  # Get the current song playing
  if context['message'] == '!song':
    title, artists = get_current_song()
    song = song_response.format(name=title, artists=artists)
    bot.send_message(song)

  # Get the custom reward id if exists
  if context.get('custom-reward-id', 0) == reward_id:
    logger.info(f"Found matching reward id {reward_id}")
    song_link = context['message']
    uri = re.search(r'\w{22}', song_link.rstrip().strip())
    # Check for valid URI / URL
    if uri:
      uri = uri.group()
      song, artists = get_song_and_artist(uri)
      username = context['display-name']

      # Check if song is banned
      if any(uri in s for s in banned_songs):
        bot.send_message(ban_message)

      elif 'track' in song_link:
        # Refresh the spotify auth and add song to queue
        refresh_wrapper()
        data = add_song_to_queue(f'spotify:track:{uri}')
        if data:
          logger.debug(data)
          logger.info(
              f'{username} successfuly added song \'{song} by {artists}\'')
          if bot_enabled:
            bot.send_message(bot_response.format(
                user=username,
                song=song,
                artists=artists)
            )


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
  url = '	https://api.spotify.com/v1/me/player/currently-playing'
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


app = Flask(__name__)
authorization_header = None
bot = None


@app.route("/")
def index():
  # Authorization
  auth_url = app_Authorization()
  return redirect(auth_url)


@app.route("/callback/q")
def callback():
  global authorization_header
  authorization_header = user_Authorization()
  logger.debug(f"Initial Auth Header {authorization_header}")
  user_info_request = process_request('https://api.spotify.com/v1/me', 'get')
  if user_info_request.status_code == 200:
    user_info = user_info_request.json()
    logger.debug(user_info)
  else:
    user_info = None

  return render_template_string(Constants.HTML,
                                user_info=user_info)


def main():
  global bot
  if auto_launch_browser:
    webbrowser.open('http://127.0.0.1:8080')
  else:
    logger.info("To authenticate go to http://127.0.0.1:8080")
  logger.info('Waiting for requests...')
  bot = Bot(bot_name, client_id, oauth, channels[0])
  bot.add_handler(new_message)
  bot.start()


if __name__ == "__main__":

  logger = Utils.init_logs()

  logger.info('Starting app')

  data = Utils.load_settings()

  channels = data['channels']
  reward_id = data['reward-id']
  client_id = data['bot']['client_id']
  oauth = data['bot']['oauth']
  bot_name = data['bot']['name']
  bot_response = data['bot']['response']
  song_response = data['bot']['current_song_response']
  bot_enabled = data['bot']['enabled']
  log_reward_id = data['log_custom_reward_ids']
  auto_launch_browser = data['auto_launch_browser']
  history = data['history']['enabled']
  playlist_id = data['history']['playlist_id']
  banned_songs = data['banned']
  ban_message = data['ban_message']

  logger.info('Connecting to channels {}'.format(channels))
  threading.Thread(target=main).start()
  app.run('127.0.0.1', port=8080, debug=False)
