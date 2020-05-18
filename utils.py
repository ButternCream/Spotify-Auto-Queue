import os
import logging
import json
import datetime
import time


class Utils(object):

  def init_logs():
    logger = logging.getLogger("Queue_Bot")
    logger.setLevel(logging.DEBUG)
    date = str(datetime.datetime.strftime(
        datetime.datetime.now(), '%Y%m%d_%H_%M_%f')).replace(' ', '_')
    log_path = 'logs\\{}.log'.format(date)
    logging.basicConfig(
        format='%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  \
          %(message)s',
        handlers=[
            logging.FileHandler(
                log_path, mode='w'),
            logging.StreamHandler()
        ],

        # level=logging.DEBUG
    )
    if not os.path.isdir('logs'):
      logger.info(
          'Logs directory does not exist. Creating logs directory')
      os.mkdir('logs')
    else:
      # 3 days ago in sec
      time_in_sec = time.time() - (3 * 24 * 60 * 60)
      logs_dir = os.path.join(os.getcwd(), 'logs/')
      for f in os.listdir(logs_dir):
        file_path = os.path.join(logs_dir, f)
        stat = os.stat(file_path)
        if stat.st_mtime <= time_in_sec:
          logger.info(f"{f} is older than 3 days. Removing...")
          os.remove(file_path)
    return logger

  def load_settings():
    logger = logging.getLogger("Queue_Bot")
    try:
      assert os.path.isfile('settings.json')
    except AssertionError as e:
      logger.info('settings.json not found')
      raise e

    with open('settings.json', 'r') as f:
      try:
        data = json.load(f)
        logger.info(data)
        return data
      except Exception as e:
        logger.error(f"Error parsing JSON: {e}")
        exit(1)


class Constants:
  HTML = '''<!DOCTYPE html>
  <html lang="en">
  <head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css" integrity="sha384-9aIt2nRpC12Uk9gS9baDl411NQApFmC26EwAOH8WgZl5MYYxFfc+NcPb1dKGj7Sk" crossorigin="anonymous">
  <title>Auto Queue</title>
  <style>
    @import url('https://fonts.googleapis.com/css?family=Roboto:300,400');
    body{
      font-family: Roboto;
      background-color: #212529;
      color: white;
      position:fixed;
      top:0;
      bottom:0;
      left:0;
      right:0;
    }
    img{
      padding: 3px;
    }
  </style>
  </head>
  <body>
  <div class="jumbotron bg-dark">
    <h1 class="display-4">Profile</h1>
    {% if user_info %}
      <p class="lead">Authentication was successful. You can close this page</p>
      <hr class="my-2">
      <img src="{{user_info['images'][0]['url']}}" class="rounded-circle border-dark"/>
      <hr class="my-2">
      <p class="lead"> <b>Name</b>: {{user_info['display_name']}} </p>
      <p class="lead"> <b>User ID</b>: {{user_info['id']}} </p>
      <p class="lead"> <b>URI</b>: {{user_info['uri']}} </p>
      <p class="lead"> <b>Link</b>: {{user_info['external_urls']['spotify']}} </p>
      <p class="lead"> <b>Followers</b>: {{user_info['followers']['total']}} </p>
    {% else %}
      <p class="lead">There was an error getting your profile</p>
    {% endif %}
    </div>
    <!-- Footer -->
  <footer class="page-footer font-small blue">

    <!-- Copyright -->
     <div class="footer-copyright text-center py-2">Spotify Queue Bot by ButterandCream
    </div>
    <div class="footer-copyright text-center py-3">Modified Template From
      <a href="https://github.com/drshrey/spotify-flask-auth-example"> Here</a>
    </div>
    <!-- Copyright -->

  </footer>
  <!-- Footer -->
  </body>
  </html>
  '''
