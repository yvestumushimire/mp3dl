import click
import os

from new_music_dl.utils import (
    download_convert,
    get_album_details,
    get_new_releases_albums,
    get_plalist_tracks,
    search_video,
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
        for track in album_details["tracks"]["items"]:
            track_artists = ", ".join(a["name"] for a in album_details["artists"])
            track_name = track["name"]
            path_name = (
                f"{track_name}_{album_details['name']}_{track_artists}".replace(
                    " ", "_"
                )
                .replace("(", "")
                .replace(")", "")
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
                            )
                        except Exception as e:
                            print(f"======>{e}g")
                except Exception as e:
                    print(f"Error: {e}")
                    continue


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
    for item in tracks_list:
        track_artists = ", ".join(a["name"] for a in item["track"]["artists"])
        track_name = item["track"]["name"]
        album = item["track"]["album"]
        path_name = (
            f"{track_name}_{album['name']}_{track_artists}".replace(" ", "_")
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
                continue
