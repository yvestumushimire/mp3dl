"""
Contains utility functions for the new_music_dl package.

"""
import os

import requests
from dotenv import load_dotenv
import wget
import pafy


from new_music_dl.const import BASE_DIR

load_dotenv()


def download_image(
    url: str,
    filename: str,
) -> str:
    """
    Downloads an image from the internet.

    Returns:
        str: The path to the downloaded image.

    """
    # Download the image
    wget.download(url, f"media/{filename}.jpg")
    return f"media/{filename}.jpg"


def get_spotify_access_token():
    """
    Gets the Spotify access token.

    Returns:
        str: The Spotify access token.

    """
    # Get the Spotify access token
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(os.getenv("SPOTIFY_CLIENT_ID"), os.getenv("SPOTIFY_CLIENT_SECRET")),
    )

    # Get the access token
    access_token = response.json()["access_token"]

    return access_token


def get_new_releases_albums():
    """
    Gets the new releases albums from the Spotify API.

    Returns:
        list: A list of the new releases albums.

    """
    # Get the Spotify access token
    access_token = get_spotify_access_token()

    # Get the new releases albums
    response = requests.get(
        "https://api.spotify.com/v1/browse/new-releases",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    albums = response.json()["albums"]["items"]

    return albums


def get_album_details(url: str):
    """
    Gets the tracks from an album from the Spotify API.

    Args:
        url (str): The Spotify album url.

    Returns:
        list: A list of the album tracks.

    """
    # Get the Spotify access token
    access_token = get_spotify_access_token()

    # Get the album tracks
    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    return response.json()


def search_video(query: str):
    """
    Searches for a video on YouTube.

    Returns:
        str: The YouTube video url.

    """
    # Get the YouTube search results
    response = requests.get(
        "https://www.googleapis.com/youtube/v3/search",
        params={
            "key": os.getenv("YOUTUBE_API_KEY"),
            "part": "snippet",
            "maxResults": 1,
            "q": query,
            "type": "video",
        },
    )

    # Get the video url
    if response.json()["items"]:
        video_url = response.json()["items"][0]["id"]["videoId"]
    else:
        print("No video found change key?")
        video_url = None

    return video_url


def download_convert(video_id, cover_url, album_name, artist_name, track_name):
    # Download the video
    path_name = (
        f"{track_name}_{album_name}_{artist_name}".replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
    )
    clean_album_name = album_name.replace("(", "").replace(")", "")
    MP3FINAL = f"media/{path_name}.mp3"
    pafy.set_api_key(os.getenv("YOUTUBE_API_KEY"))
    video = pafy.new(f"https://www.youtube.com/watch?v={video_id}")
    bestaudio = video.getbestaudio(preftype="m4a")
    BESTFILE = f"media/{path_name}.{bestaudio.extension}"
    MP3FILE = f"media/{path_name}_del.mp3"
    cover_image = clean_album_name.replace(" ", "_")
    if os.path.isfile(cover_image):
        print("File already exists, skipping")
    else:
        download_image(url=cover_url, filename=cover_image)
    bestaudio.download(BESTFILE)
    print("+++++=======================Done")
    cover_image_path = f"media/{cover_image}.jpg"
    os.system(
        f'ffmpeg -i {BESTFILE} -vn -ab 128k -ar 44100 -metadata album="{clean_album_name}" -metadata artist="{artist_name}" -y {MP3FILE}'
    )
    os.system(
        f"ffmpeg -i {MP3FILE} -i {cover_image_path} -map 0:0 -map 1:0 -c copy -id3v2_version 3 -metadata:s:v title='Album cover' -metadata:s:v comment='Cover (front)' -y {MP3FINAL}"
    )
    os.remove(BESTFILE)
    os.remove(MP3FILE)
