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
    wget.download(url, f"media/covers/{filename}.jpg")
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


def get_new_releases_albums(offset: int = 0, limit: int = 50, country: str = "US"):
    """
    Gets the new releases albums from the Spotify API.

    Returns:
        list: A list of the new releases albums.

    """
    # Get the Spotify access token
    access_token = get_spotify_access_token()

    # Get the new releases albums
    response = requests.get(
        f"https://api.spotify.com/v1/browse/new-releases?offset={offset}&country={country}&limit={limit}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    albums = response.json()["albums"]["items"]

    return albums


def get_plalist_tracks(playlist_id: str) -> list:
    # Get the Spotify access token
    access_token = get_spotify_access_token()

    # Get the playlist tracks
    response = requests.get(
        f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    return response.json()["items"]


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
    try:
        video_url = response.json()["items"][0]["id"]["videoId"]
    except Exception as e:
        print(f"No video found change key? : {e}")
        video_url = None

    return video_url


def download_convert(
    video_id,
    cover_url,
    album_name,
    artist_name,
    track_name,
    track_number,
    total_tracks,
    year,
):
    # Download the video
    path_name = (
        f"{track_name}_{album_name}_{artist_name}".replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
        .replace(".", "")
        .replace("'", "")
    )
    clean_album_name = album_name.replace("(", "").replace(")", "")
    MP3FINAL = f"media/{path_name}.mp3"
    pafy.set_api_key(os.getenv("YOUTUBE_API_KEY"))
    video = pafy.new(f"https://www.youtube.com/watch?v={video_id}")
    bestaudio = video.getbestaudio(preftype="m4a")
    BESTFILE = f"media/{path_name}.{bestaudio.extension}"
    MP3FILE = f"media/{path_name}_del.mp3"
    cover_image = clean_album_name.replace(" ", "_")
    if os.path.isfile(f"media/covers/{cover_image}.jpg"):
        print("File already exists, skipping")
    else:
        download_image(url=cover_url, filename=cover_image)
    bestaudio.download(BESTFILE)
    print("+++++=======================Done")
    cover_image_path = f"media/covers/{cover_image}.jpg"
    os.system(
        f'ffmpeg -i {BESTFILE} -vn -ab 128k -ar 44100 -metadata album="{clean_album_name}" -metadata artist="{artist_name}" -metadata track="{track_number}/{total_tracks}" -metadata title="{track_name}" -metadata date="{year}" -metadata comment="source (https://github.com/yvestumushimire/mp3dl)"  -y {MP3FILE}'
    )
    os.system(
        f"ffmpeg -i {MP3FILE} -i {cover_image_path} -map 0:0 -map 1:0 -c copy -id3v2_version 3 -metadata:s:v comment='...' -y {MP3FINAL}"
    )
    os.remove(BESTFILE)
    os.remove(MP3FILE)
