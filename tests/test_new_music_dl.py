from new_music_dl.utils import get_new_releases_albums, get_spotify_access_token


def test_access_token():
    assert get_spotify_access_token() is not None


def test_access_token_type():
    assert type(get_spotify_access_token()) is str


def test_get_new_releases_albums():
    assert get_new_releases_albums() is not None


def test_get_new_releases_albums_type():
    assert type(get_new_releases_albums()) is list
