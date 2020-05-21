from irc.bot import SingleServerIRCBot
import requests

import logging

logger = logging.getLogger("Queue_Bot")


class Context:
  def __init__(self, **kwargs):
    vars(self).update(kwargs)


class Bot(SingleServerIRCBot):
  def __init__(self, name, client_id, oauth, channel):
    self.HOST = "irc.chat.twitch.tv"
    self.PORT = 6667
    self.USERNAME = name.lower()
    self.CLIENT_ID = client_id
    self.TOKEN = oauth
    self.CHANNEL = f"#{channel}"
    self.handler = None

    # Login bot
    url = f"https://api.twitch.tv/kraken/users?login={self.USERNAME}"
    headers = {"Client-ID": self.CLIENT_ID,
               "Accept": "application/vnd.twitchtv.v5+json"}
    logger.info("Logging in twitch bot...")
    resp = requests.get(url, headers=headers).json()
    logger.debug(resp)

    super().__init__(
        [
            (self.HOST, self.PORT, self.TOKEN)
        ], self.USERNAME, self.USERNAME
    )

  def on_welcome(self, cxn, event):
    """Request capabilities on joining the channel
    """
    for req in ("membership", "tags", "commands"):
      cxn.cap("REQ", f":twitch.tv/{req}")
    cxn.join(self.CHANNEL)

  def on_pubmsg(self, cxn, event):
    """Override for public message event handler
    """
    tags = {kvpair["key"]: kvpair["value"] for kvpair in event.tags}
    tags['message'] = event.arguments[0]
    ctx = Context(event=tags, bot=self)
    if self.handler:
      # To generalize have your handler func be (*args, **kwargs)
      self.handler(ctx)

  def send_message(self, message):
    """Send a message
    """
    self.connection.privmsg(self.CHANNEL, message)

  def add_handler(self, handler):
    """A wrapper for incoming message handling
    """
    self.handler = handler
