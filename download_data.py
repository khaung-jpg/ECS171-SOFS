import os, json, urllib.request

API = "https://api.github.com/repos/StackExchange/Survey/contents/packages/archive"
MEDIA = "https://media.githubusercontent.com/media/StackExchange/Survey/main/packages/archive"

def is_pointer(path):
    if not os.path.exists(path) or os.path.getsize(path) > 1024:
        return False
    with open(path, "rb") as fh:
        return fh.read(40).startswith(b"version https://git-lfs")

for y in range(2011, 2027):
    folder = f"data/{y}"
    os.makedirs(folder, exist_ok=True)
    try:
        info = json.loads(urllib.request.urlopen(f"{API}/{y}").read())
    except Exception as e:
        print(f"Skipping {y}: {e}")
        continue
    for f in info:
        if not f["name"].endswith((".csv", ".pdf")):
            continue
        dest = f"{folder}/{f['name']}"
        if os.path.exists(dest) and not is_pointer(dest):
            continue  # already have the real file
        print(f"Downloading {y}/{f['name']}...")
        urllib.request.urlretrieve(f"{MEDIA}/{y}/{f['name']}", dest)
print("Done.")