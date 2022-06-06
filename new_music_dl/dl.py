import json
import requests
import click
import os
import concurrent.futures

from new_music_dl.utils import (
    download_convert,
    download_video,
    get_album_details,
    get_new_releases_albums,
    get_plalist_tracks,
    search_video,
    download_song,
    download_playlist_song,
)


@click.group()
def cli():
    """
    Download albums from new releases
    """
    pass


@cli.command()
@click.option("-o", "--offset", default=0, type=int, help="Strating position")
@click.option(
    "-l", "--limit", default=50, type=int, help="Number of albums to download"
)
@click.option("-c", "--country", default="US", type=str, help="Country code eg: RW")
def newmusicfriday(offset: int, limit: int, country: str):
    """Download album"""
    new_albums = get_new_releases_albums(offset, limit, country)
    for album in new_albums:
        album_details = get_album_details(album["href"])
        args_song = (
            (album_details, track) for track in album_details["tracks"]["items"]
        )
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(lambda f: download_song(*f), args_song)


@cli.command()
@click.option(
    "-p",
    "--playlist_id",
    default="37i9dQZEVXcWgB7lGHApVn",
    type=str,
    help="Playlist ID",
)
def playlist(playlist_id: str):
    """Download playlist"""
    tracks_list = get_plalist_tracks(playlist_id)
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(download_playlist_song, tracks_list)


@cli.command()
@click.option("-a", "--album", type=str, help="Album ID")
def album(album: str):
    """
    Download album

    """
    url = f"https://api.spotify.com/v1/albums/{album}"
    album_details = get_album_details(url)
    args_song = ((album_details, track) for track in album_details["tracks"]["items"])
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(lambda f: download_song(*f), args_song)


@cli.command()
@click.option("-a", "--album", type=str, help="Album ID")
def post_album(album: str):
    url = f"https://api.spotify.com/v1/albums/{album}"
    ad = get_album_details(url)
    album_name = ad["name"]
    credits_copyright = ", ".join(x["text"] for x in ad["copyrights"])
    album_cover_hd = ad["images"][0]["url"]
    album_cover_md = ad["images"][1]["url"]
    album_cover_sm = ad["images"][2]["url"]
    label = ad["label"]
    album_popularity = ad["popularity"]
    release_date = ad["release_date"]
    for at in ad["tracks"]["items"]:
        track_artists = ", ".join(a["name"] for a in at["artists"])
        track_name = at["name"]
        track_title = "{umuhanzi} - {indirimbo}".format(
            umuhanzi=track_artists, indirimbo=track_name
        )
        final_title = track_title + " Mp3 Download"
        data = json.dumps(
            {
                "name": final_title,
                "song_id": at["id"],
                "artists": track_artists,
                "release_date": release_date,
                "popularity": album_popularity,
                "album_cover_hd": album_cover_hd,
                "album_cover_md": album_cover_md,
                "album_cover_sm": album_cover_sm,
                "label": label,
                "album_name": album_name,
                "stream_url": "",
                "credits_copyright": credits_copyright,
                "body": "",
                "lyrics": "",
                "is_featured": False,
            }
        )
        res = requests.post(
            "http://localhost:8000/core/music_api",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjQxNzQ3NDk4LCJpYXQiOjE2NDE3NDcxOTgsImp0aSI6ImU1YTY1Mjc0MTM5NDRiMDliNGQ4MzQwM2MwYWE4ZWE3IiwidXNlcl9pZCI6MX0.d65yEZPBaeXskrWs5SU8IYRLuKbilmD3NNLWg4eXICM",
            },
        )
        print(res.status_code)


@cli.command()
@click.option("-v", "--video", type=str, help="playlist id")
def video(video: str):
    songs_list = get_plalist_tracks(video)

    # download video from playlist songs
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(download_video, songs_list)

