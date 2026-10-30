import os, urllib.request

BASE = "https://github.com/StackExchange/Survey/raw/main/packages/archive"

for y in range(2011, 2027):
    folder = f"data/{y}"
    os.makedirs(folder, exist_ok=True)

    # Ask GitHub what's in this year's folder
    files = (urllib.request.urlopen(
        f"https://api.github.com/repos/StackExchange/Survey/contents/packages/archive/{y}"
    ).read().decode())

    # Parse JSON manually to get filenames
    import json
    info = json.loads(files)

    for f in info:
        if f['name'].endswith(('.csv', '.pdf')):
            url = f['download_url']
            dest = f"{folder}/{f['name']}"
            if not os.path.exists(dest):
                print(f"Downloading {y}/{f['name']}...")
                urllib.request.urlretrieve(url, dest)

print("Done.")