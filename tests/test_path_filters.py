import pytest
from unittest.mock import AsyncMock
from services.file_service import list_files, search_files

# Mock the Pyrogram Client
class MockMessage:
    def __init__(self, id, document=None, video=None, photo=None, audio=None, date=None, empty=False, service=False):
        self.id = id
        self.document = document
        self.video = video
        self.photo = photo
        self.audio = audio
        self.date = date
        self.empty = empty
        self.service = service
        self.caption = ""

class MockClient:
    def __init__(self, messages, metadata_map):
        self.messages = messages
        self.metadata_map = metadata_map

    async def get_chat_history(self, chat_id):
        for m in self.messages:
            yield m

@pytest.fixture
def mock_parser(monkeypatch):
    import utils.parser as parser
    original = parser.extract_message_metadata

    # We'll use a mocked metadata map in the test
    # instead of extracting from actual messages, to test the filter logic easily
    pass

@pytest.mark.asyncio
async def test_list_files_with_path(monkeypatch):
    import services.file_service as fs

    mock_meta = {
        1: {"id": 1, "name": "naruto_ep1.mp4", "path": "/anime/naruto/", "date": "2023-01-01", "size": "100MB", "raw_size": 1000},
        2: {"id": 2, "name": "bleach_ep1.mp4", "path": "/anime/bleach/", "date": "2023-01-01", "size": "100MB", "raw_size": 1000},
        3: {"id": 3, "name": "matrix.mp4", "path": "/movies/", "date": "2023-01-01", "size": "100MB", "raw_size": 1000},
        4: {"id": 4, "name": "no_path.mp4", "date": "2023-01-01", "size": "100MB", "raw_size": 1000}, # should default to "/"
    }

    def mock_extract(msg):
        return mock_meta.get(msg.id)

    monkeypatch.setattr(fs, "extract_message_metadata", mock_extract)

    client = MockClient([MockMessage(1), MockMessage(2), MockMessage(3), MockMessage(4)], mock_meta)

    # Test path: /anime/
    res = await list_files(client, path="/anime/")
    assert len(res) == 2
    assert set(r["id"] for r in res) == {1, 2}

    # Test strict prefix: /anime/
    res = await list_files(client, path="/anime/naru") # Should normalize to /anime/naru/ and match nothing if naruto is a folder
    # Actually normalize_path("anime/naru") -> "/anime/naru/"
    # "/anime/naruto/".startswith("/anime/naru/") is False
    assert len(res) == 0

    # Test root path
    res = await list_files(client, path="/")
    assert len(res) == 4

    # Test backward compatibility (no path metadata defaults to "/")
    res = await list_files(client, path="/movies/")
    assert len(res) == 1
    assert res[0]["id"] == 3

@pytest.mark.asyncio
async def test_search_files_with_path(monkeypatch):
    import services.file_service as fs

    mock_meta = {
        1: {"id": 1, "name": "naruto_ep1.mp4", "path": "/anime/naruto/", "date": "2023-01-01", "size": "100MB", "raw_size": 1000},
        2: {"id": 2, "name": "bleach_ep1.mp4", "path": "/anime/bleach/", "date": "2023-01-01", "size": "100MB", "raw_size": 1000},
        3: {"id": 3, "name": "naruto_movie.mp4", "path": "/movies/anime/", "date": "2023-01-01", "size": "100MB", "raw_size": 1000},
    }

    def mock_extract(msg):
        return mock_meta.get(msg.id)

    monkeypatch.setattr(fs, "extract_message_metadata", mock_extract)

    client = MockClient([MockMessage(1), MockMessage(2), MockMessage(3)], mock_meta)

    # Search for "naruto" in path "/anime/"
    res = await search_files(client, query="naruto", path="/anime/")
    assert len(res) == 1
    assert res[0]["id"] == 1

    # Search for "naruto" in path "/movies/"
    res = await search_files(client, query="naruto", path="/movies/")
    assert len(res) == 1
    assert res[0]["id"] == 3
