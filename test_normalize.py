def normalize_path(path: str) -> str:
    if not path or not str(path).strip():
        return "/"

    path = str(path).strip().lower()

    # collapse consecutive slashes
    parts = [p.strip() for p in path.split("/") if p.strip()]

    if not parts:
        return "/"

    return "/" + "/".join(parts) + "/"

assert normalize_path(None) == "/"
assert normalize_path("") == "/"
assert normalize_path(" ") == "/"
assert normalize_path("/") == "/"
assert normalize_path("//") == "/"
assert normalize_path("anime/naruto") == "/anime/naruto/"
assert normalize_path("/Anime//Naruto") == "/anime/naruto/"
assert normalize_path(" anime / naruto ") == "/anime/naruto/"
print("All passed")
