import re
import json
import time
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
BASE = "https://genius.com"
SECTION_RE = re.compile(r"^\[.*\]$")
META_RE = re.compile(r"^\d+ Contributors")


def parse_preloaded(html):
    idx = html.find("window.__PRELOADED_STATE__ = JSON.parse('")
    if idx == -1:
        return None
    start = idx + len("window.__PRELOADED_STATE__ = JSON.parse('")
    i = start
    while i < len(html):
        if html[i] == "'" and html[i - 1] != "\\":
            break
        i += 1
    raw = html[start:i].replace("\\'", "'")
    decoded = json.loads('"' + raw + '"')
    return json.loads(decoded)


def get_song_paths(page=1):
    url = f"{BASE}/artists/Bahram/songs?page={page}"
    r = requests.get(url, headers=HEADERS, timeout=15)
    data = parse_preloaded(r.text)
    if not data:
        return [], None
    disc = data.get("artistDiscography", {})
    entities = data.get("entities", {}).get("songs", {})
    items = disc.get("items", [])
    paths = [entities[str(item["id"])]["path"] for item in items if str(item["id"]) in entities]
    titles = {str(item["id"]): entities[str(item["id"])]["title"] for item in items if str(item["id"]) in entities}
    next_page = disc.get("nextPage")
    return list(zip(paths, [titles[str(item["id"])] for item in items if str(item["id"]) in entities])), next_page


def get_lyrics(path, title):
    url = BASE + path
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
    except Exception as e:
        print(f"  Error fetching {path}: {e}")
        return None
    soup = BeautifulSoup(r.text, "html.parser")
    containers = soup.find_all("div", attrs={"data-lyrics-container": "true"})
    if not containers:
        return None
    lines = []
    for c in containers:
        for br in c.find_all("br"):
            br.replace_with("\n")
        for chunk in c.get_text().splitlines():
            chunk = chunk.strip()
            if not chunk:
                continue
            if SECTION_RE.match(chunk):
                continue
            if META_RE.match(chunk):
                continue
            # Drop first line if it looks like "N ContributorsTITLE Lyrics..."
            lines.append(chunk)
    # Drop the first line which always contains contributor + title metadata
    if lines and ("Lyrics" in lines[0] or "Contributors" in lines[0]):
        lines = lines[1:]
    return lines if len(lines) >= 5 else None


# Collect all song paths (Genius paginates; stop when we see duplicate IDs)
print("Fetching song list...")
all_songs_meta = []
seen_paths = set()
page = 1
while True:
    songs_on_page, next_page = get_song_paths(page)
    new_songs = [(p, t) for p, t in songs_on_page if p not in seen_paths]
    for p, t in new_songs:
        seen_paths.add(p)
    all_songs_meta.extend(new_songs)
    print(f"  Page {page}: {len(new_songs)} new songs (total: {len(all_songs_meta)})")
    if not new_songs or not next_page or next_page <= page:
        break
    page = next_page
    time.sleep(0.5)

print(f"\nTotal songs found: {len(all_songs_meta)}")
print("Fetching lyrics...\n")

songs = []
for i, (path, title) in enumerate(all_songs_meta, 1):
    print(f"[{i}/{len(all_songs_meta)}] {title}")
    lyrics = get_lyrics(path, title)
    if lyrics:
        songs.append({"song": title, "lyrics": lyrics})
        print(f"  ✓ {len(lyrics)} lines")
    else:
        print(f"  ✗ skipped (no lyrics or too short)")
    time.sleep(0.6)

import os
out_path = os.path.join(os.path.dirname(__file__), "..", "data", "lyrics.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(songs, f, ensure_ascii=False, indent=2)

print(f"\nDone — {len(songs)} songs saved to data/lyrics.json")
