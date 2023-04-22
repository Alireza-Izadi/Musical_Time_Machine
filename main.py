import requests
import spotipy
import os

from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyOAuth

BILLBOARD_URL = "https://www.billboard.com/charts/hot-100/"
SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")

favorite_date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")

#------------------------GETTING BILLBOARD TOP 100 SONGS----------------------------#
response = requests.get(f"{BILLBOARD_URL}{favorite_date}")
top_100_website = response.text


#--------------CRAWLING DATA FROM BILLBOARD WEBSITE USING BEAUTIFULSOUP----------------#
soup = BeautifulSoup(top_100_website, "html.parser")

top_songs = soup.select(selector="li h3")
top_singers = soup.select(selector="#title-of-a-story + span")

songs = []
singers = []

for song in top_songs[1:len(top_songs) - 9]:
    songs.append(song.getText().strip())

for singer in top_singers[1:len(top_singers) - 9]:    
    singers.append(singer.getText().strip())

#--------------------------SPOTIPY----------------------------#
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="http://example.com",
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        show_dialog=True,
        cache_path="token.txt",
    )
)
#---------------------------FINDING SONG URIS-----------------------#
user_id = sp.current_user()["id"]
song_uris = []
year = favorite_date.split("-")[0]

for song in songs:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    print(result)
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")


#---------------------------------MAKING A PLAYLIST IN YOUR SPOTIFY-----------------------------#        
playlist = sp.user_playlist_create(user=user_id, name=f"{favorite_date} Billboard 100", public=False)


sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)

#====================================================================================================#