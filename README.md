# Spotify Auto Queue

### A twitch bot framework to add songs to your spotify queue using custom channel rewards
**Note: Requires PREMIUM**

### Spotify Steps
1. Create a client id on the [spotify developers page](https://developer.spotify.com/dashboard/applications)
2. Put the client id and client secret in `settings.json`
3. In the app settings add http://127.0.0.1:8080/callback/q to the redirect URI's. You can change it in `spotify.py`

### Twitch Steps
1. Create a twitch account for your bot
2. Login [here](https://twitchapps.com/tmi/) to get OAUTH
3. [Register your app](https://dev.twitch.tv/dashboard/apps/create) on twitch developers to get client id
4. Put OAUTH and Client Id in `settings.json`
