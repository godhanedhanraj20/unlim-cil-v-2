import pytest
from utils.metadata_manager import normalize_path, set_path, get_path, move_path, get_all_folders
import utils.metadata_manager as mm

def test_normalize_path():
    assert normalize_path("") == "/"
    assert normalize_path(None) == "/"
    assert normalize_path("  ") == "/"
    assert normalize_path("/") == "/"
    assert normalize_path("//") == "/"
    assert normalize_path("Anime") == "/anime/"
    assert normalize_path("ANIME/NARUTO") == "/anime/naruto/"
    assert normalize_path("/anime//naruto/") == "/anime/naruto/"
    assert normalize_path(" anime / naruto ") == "/anime/naruto/"

def test_set_and_get_path(monkeypatch, tmp_path):
    metadata_file = tmp_path / "metadata.json"
    monkeypatch.setattr(mm, "METADATA_FILE", str(metadata_file))
    monkeypatch.setattr(mm, "CONFIG_DIR", str(tmp_path))

    assert get_path("123") == "/"

    set_path("123", "Anime/Naruto")
    assert get_path("123") == "/anime/naruto/"

    # Backward compatibility (no path saved)
    import json
    with open(str(metadata_file), "w") as f:
        json.dump({"456": {"tags": ["test"]}}, f)

    assert get_path("456") == "/"

def test_move_path(monkeypatch, tmp_path):
    metadata_file = tmp_path / "metadata.json"
    monkeypatch.setattr(mm, "METADATA_FILE", str(metadata_file))
    monkeypatch.setattr(mm, "CONFIG_DIR", str(tmp_path))

    move_path("123", "/movies/")
    assert get_path("123") == "/movies/"

def test_get_all_folders(monkeypatch, tmp_path):
    metadata_file = tmp_path / "metadata.json"
    monkeypatch.setattr(mm, "METADATA_FILE", str(metadata_file))
    monkeypatch.setattr(mm, "CONFIG_DIR", str(tmp_path))

    set_path("1", "/anime/naruto/season1/")
    set_path("2", "/anime/bleach/")
    set_path("3", "/") # shouldn't add "/" to folders explicitly or if it does it's fine
    set_path("4", "/movies/")

    folders = get_all_folders()
    assert set(folders) == {
        "/anime/",
        "/anime/naruto/",
        "/anime/naruto/season1/",
        "/anime/bleach/",
        "/movies/"
    }
