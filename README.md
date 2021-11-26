
# Music(MP3) Download

This script download music from youtube and convert it to mp3 format.
It also add metadata such as album cover, artist, album name, year, title and more to the mp3 file from spotify.

## Features 🤯

* *Download full album*: you can pass spotify album id and it will download all songs from the album.
* *Download single song*: you can pass spotify song_id and it will download the song.
* *Download playlist*: you can pass spotify playlist id url and it will download all songs from the playlist.

## Requirements 🧰

* [FFMPEG](https://ffmpeg.org/)
* [Spotify for developers (CLient ID and Client Secret)](https://developer.spotify.com/my-applications/#!/applications)
* [Google apikey (youtube-data-api)](https://developers.google.com/youtube/v3/getting-started)
* [Python 3.8](https://www.python.org/downloads/)
* [Poetry](https://poetry.eustace.io/)

## Installation 🚀

* Clone this repository
* Navigate to the directory of this repository
* and run the following command:
  * `poetry shell`
  * `poetry install`
* Copy `.env.example` contents to `.env` file and enter your credentials

## USAGE 🥰

### Help

run `poetry run mp3dl --help` for more info

### Download new music releases (every friday):

run `poetry run mp3l newmusicfriday` to download new music releases every friday from spotify
you can also use `-c` to specify the country code

### Download Plalist

`poetry run mp3dl -p playlist_id` to download all songs from a playlist. you will need a playlist_id from spotify playlist url.

### Download Album

`poetry run mp3dl -a album_id` to download all songs from an album. you will need an album_id from spotify album url.

## Disclaimer 🤔

    This script is provided "as is" without any warranty.
    Use it at your own risk.
