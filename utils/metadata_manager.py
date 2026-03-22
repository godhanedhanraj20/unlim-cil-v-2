import os
import json

CONFIG_DIR = os.path.expanduser("~/.tsg-cli")
METADATA_FILE = os.path.join(CONFIG_DIR, "metadata.json")

def ensure_config_dir():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

def load_metadata() -> dict:
    ensure_config_dir()
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_metadata(data: dict):
    ensure_config_dir()
    with open(METADATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_tag(file_id: str, tag: str):
    data = load_metadata()
    if file_id not in data:
        data[file_id] = {"tags": []}
        
    tags = data[file_id].get("tags", [])
    if tag not in tags:
        tags.append(tag)
        data[file_id]["tags"] = tags
        save_metadata(data)

def remove_tag(file_id: str, tag: str):
    data = load_metadata()
    if file_id in data:
        tags = data[file_id].get("tags", [])
        if tag in tags:
            tags.remove(tag)
            data[file_id]["tags"] = tags
            save_metadata(data)

def get_tags(file_id: str) -> list:
    data = load_metadata()
    if file_id in data:
        return data[file_id].get("tags", [])
    return []

def set_custom_name(file_id: str, name: str):
    data = load_metadata()
    entry = data.setdefault(file_id, {})
    entry["custom_name"] = name
    save_metadata(data)

def get_custom_name(file_id: str):
    data = load_metadata()
    return data.get(file_id, {}).get("custom_name")

def remove_custom_name(file_id: str):
    data = load_metadata()
    if file_id in data and "custom_name" in data[file_id]:
        del data[file_id]["custom_name"]
        save_metadata(data)

def normalize_path(path: str) -> str:
    """
    Normalizes a virtual folder path.
    - Trims spaces and converts to lowercase
    - Ensures leading and trailing '/'
    - Collapses duplicate slashes
    - Treats empty, None, or whitespace as '/'
    """
    if not path or not str(path).strip():
        return "/"

    path = str(path).strip().lower()

    parts = [p.strip() for p in path.split("/") if p.strip()]
    if not parts:
        return "/"

    return "/" + "/".join(parts) + "/"

def set_path(file_id: str, path: str):
    data = load_metadata()
    entry = data.setdefault(file_id, {})
    entry["path"] = normalize_path(path)
    save_metadata(data)

def get_path(file_id: str) -> str:
    data = load_metadata()
    return normalize_path(data.get(file_id, {}).get("path"))

def move_path(file_id: str, new_path: str):
    set_path(file_id, new_path)

def get_all_folders() -> list:
    data = load_metadata()
    folders = set()

    for entry in data.values():
        path = normalize_path(entry.get("path"))
        if path == "/":
            continue

        parts = [p for p in path.split("/") if p]
        current_path = ""
        for part in parts:
            current_path += f"/{part}"
            folders.add(current_path + "/")

    return sorted(list(folders))
