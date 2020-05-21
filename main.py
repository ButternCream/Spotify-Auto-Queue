# **********************************************************************************
# Spotify Queue Bot V1.08
# By: ButterandCream
# Description: This bot allows songs to be queued in spotify via twitch chat
# **********************************************************************************


from flask import Flask, render_template_string, redirect
import spotify
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

     context: message context from twitch
  '''
  global bot_enabled, log_reward_id
  # Log reward id if option is enabled
  if log_reward_id and 'custom-reward-id' in context.event.keys():
    logger.info("Custom Reward ID: {}".format(
        context.event['custom-reward-id']))
    logger.info("Message: {}".format(context.event['message']))

  # Get the current song playing
  if context.event['message'] == '!song':
    title, artists = spotify.get_current_song()
    song = song_response.format(name=title, artists=artists)
    context.bot.send_message(song)

  # Get the custom reward id if exists
  if context.event.get('custom-reward-id', 0) == reward_id:
    logger.info(f"Found matching reward id {reward_id}")
    song_link = context.event['message']
    uri = re.search(r'\w{22}', song_link.rstrip().strip())
    # Check for valid URI / URL
    if uri:
      uri = uri.group()
      song, artists = spotify.get_song_and_artist(uri)
      username = context.event['display-name']

      # Check if song is banned
      if any(uri in s for s in banned_songs):
        context.bot.send_message(ban_message)

      elif 'track' in song_link:
        # Refresh the spotify auth and add song to queue
        spotify.refresh()
        data = spotify.add_song_to_queue(f'spotify:track:{uri}')
        if data:
          logger.debug(data)
          logger.info(
              f'{username} successfuly added song \'{song} by {artists}\'')
          if bot_enabled:
            context.bot.send_message(bot_response.format(
                user=username,
                song=song,
                artists=artists)
            )


app = Flask(__name__)


@app.route("/")
def index():
  # Authorization
  auth_url = spotify.app_Authorization()
  return redirect(auth_url)


@app.route("/callback/q")
def callback():
  spotify.user_Authorization()
  logger.debug(f"Initial Auth Header {spotify.authorization_header}")
  user_info_request = spotify.process_request(
      'https://api.spotify.com/v1/me', 'get')
  if user_info_request.status_code == 200:
    user_info = user_info_request.json()
    logger.debug(user_info)
  else:
    user_info = None

  return render_template_string(Constants.HTML,
                                user_info=user_info)


def main():
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
  banned_songs = data['banned']
  ban_message = data['ban_message']

  logger.info('Connecting to channels {}'.format(channels))
  threading.Thread(target=main).start()
  app.run('127.0.0.1', port=8080, debug=False)
