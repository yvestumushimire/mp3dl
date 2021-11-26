import click
import os
import concurrent.futures

from new_music_dl.utils import (
    download_convert,
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
