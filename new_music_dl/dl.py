import click
import os

from new_music_dl.utils import (
    download_convert,
    get_album_details,
    get_new_releases_albums,
    search_video,
)


@click.command()
@click.option("--size", default=1, type=int, help="album number")
def download(size=1):
    """Download album"""
    new_albums = get_new_releases_albums()
    for album in new_albums:
        album_details = get_album_details(album["href"])
        for track in album_details["tracks"]["items"]:
            track_artists = ", ".join(a["name"] for a in album_details["artists"])
            track_name = track["name"]
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
                        )
                    except Exception as e:
                        print(f"======>{e}g")
            except Exception as e:
                print(f"Error: {e}")
                continue
