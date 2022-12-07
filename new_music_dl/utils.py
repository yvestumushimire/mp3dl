"""
Contains utility functions for the new_music_dl package.

"""
import os

import requests
from dotenv import load_dotenv
import wget
import pafy
from pytube import YouTube, Search
from concurrent.futures import ThreadPoolExecutor



from new_music_dl.const import BASE_DIR

load_dotenv()


def download_image(url: str, filename: str,) -> str:
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
    response = requests.get(url, headers={"Authorization": f"Bearer {access_token}"},)

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


def download_video(video_id, path_name, track_name, artist_name):
    path_name = (
        f"{track_name}_{artist_name}".replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
        .replace(".", "")
        .replace("'", "")
    )
    # pafy.set_api_key(os.getenv("YOUTUBE_API_KEY"))
    print(f"Downloading {track_name}")
    # video = YouTube(f"https://www.youtube.com/watch?v={video_id}")
    print("....")
    if os.path.isfile(f"media/{path_name}.mp4"):
        print(f"{track_name} already downloaded")
        return
    video_id.streams.filter(progressive=True).get_highest_resolution().download(
        output_path="media", filename=f"{path_name}.mp4"
    )


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
        f"{track_name}_{artist_name}".replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
        .replace(".", "")
        .replace("'", "")
    )
    clean_album_name = (
        album_name.replace("(", "")
        .replace(")", "")
        .replace(".", "")
        .replace("'", "")
        .replace("&", "and")
    )
    MP3FINAL = f"media/{path_name}.mp3"
    pafy.set_api_key(os.getenv("YOUTUBE_API_KEY"))
    video = YouTube(f"https://www.youtube.com/watch?v={video_id}")
    bestaudio = (
        video.streams.filter(only_audio=True)
        .first()
        .download(output_path="media", filename=f"{path_name}_og.mp3")
    )
    BESTFILE = f"media/{path_name}_og.mp3"
    MP3FILE = f"media/{path_name}_del.mp3"
    cover_image = clean_album_name.replace(" ", "_")
    other_cover = "media/covers/promo.png"
    if os.path.isfile(f"media/covers/{cover_image}.jpg"):
        print("cover already exists, skipping")
    else:
        download_image(url=cover_url, filename=cover_image)
    with ThreadPoolExecutor(max_workers=10) as pool:
        try:
            pool.submit(bestaudio.download(BESTFILE))
        except Exception as e:
            print(f"Error downloading {BESTFILE}: {e}")
    print("+++++=======================Done")
    cover_image_path = f"media/covers/{cover_image}.jpg"
    os.system(
        f'ffmpeg -i {BESTFILE} -vn -ab 128k -ar 44100 -metadata album="{clean_album_name}" -metadata artist="{artist_name}" -metadata track="{track_number}/{total_tracks}" -metadata title="{track_name}" -metadata date="{year}" -metadata comment="source (https://github.com/yvestumushimire/mp3dl)"  -y {MP3FILE}'
    )
    os.system(
        f"ffmpeg -i {MP3FILE} -i {other_cover} -map 0:0 -map 1:0 -c copy -id3v2_version 3 -metadata:s:v comment='...' -y {MP3FINAL}"
    )
    os.remove(BESTFILE)
    os.remove(MP3FILE)
    # cloudinary.uploader.upload(MP3FINAL, resource_type="audio")


def download_song(album_details, track):
    track_artists = ", ".join(a["name"] for a in album_details["artists"])
    track_name = track["name"]
    path_name = (
        f"{track_name}_{track_artists}".replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
        .replace(".", "")
        .replace("'", "")
    )
    if os.path.isfile(f"media/{path_name}.mp3"):
        print("File already exists, skipping")
    else:
        try:
            video_url = search_video(f"{track_artists} - {track_name}")
            if video_url is not None:
                try:
                    download_convert(
                        video_id=video_url,
                        cover_url=album_details["images"][0]["url"],
                        album_name=album_details["name"],
                        artist_name=track_artists,
                        track_name=track_name,
                        track_number=track["track_number"],
                        total_tracks=album_details["tracks"]["total"],
                        year=album_details["release_date"].split("-")[0],
                    )
                except Exception as e:
                    print(f"======>{e}g")
        except Exception as e:
            print(f"Error: {e}")


def download_playlist_song(item):
    track_artists = ", ".join(a["name"] for a in item["track"]["artists"])
    track_name = item["track"]["name"]
    album = item["track"]["album"]
    path_name = (
        f"{track_name}_{track_artists}".replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
        .replace(".", "")
        .replace("'", "")
    )
    if os.path.isfile(f"media/{path_name}.mp4"):
        print("File already exists, skipping")
    else:
        try:
            s = Search(f"{track_artists} - {track_name}")
            if len(s.results) > 0:
                video_url = s.results[0]
            else:
                video_url = None
            if video_url is not None:
                try:
                    download_video(
                        video_id=video_url,
                        artist_name=track_artists,
                        track_name=track_name,
                        path_name=path_name,
                    )
                except Exception as e:
                    print(f"======>{e}g")
        except Exception as e:
            print(f"Error: {e}")


def download_playlist_video(item):
    track_artists = ", ".join(a["name"] for a in item["track"]["artists"])
    track_name = item["track"]["name"]
    album = item["track"]["album"]
    path_name = (
        f"{track_name}_{track_artists}".replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
        .replace(".", "")
        .replace("'", "")
    )
    if os.path.isfile(f"media/{path_name}.mp3"):
        print("File already exists, skipping")
    else:
        try:
            video_url = search_video(f"{track_artists} - {track_name}")
            if video_url is not None:
                try:
                    download_convert(
                        video_id=video_url,
                        cover_url=album["images"][0]["url"],
                        album_name=album["name"],
                        artist_name=track_artists,
                        track_name=track_name,
                        track_number=item["track"]["track_number"],
                        total_tracks=album["total_tracks"],
                        year=album["release_date"].split("-")[0],
                    )
                except Exception as e:
                    print(f"======>{e}g")
        except Exception as e:
            print(f"Error: {e}")
