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


ARTIST_ID = 26835  # Bahram on Genius

def get_song_paths(page=1):
    url = f"{BASE}/api/artists/{ARTIST_ID}/songs?per_page=50&page={page}&sort=title"
    r = requests.get(url, headers=HEADERS, timeout=15)
    d = r.json()
    songs = d.get("response", {}).get("songs", [])
    next_page = d.get("response", {}).get("next_page")
    pairs = [(s["path"], s["title"]) for s in songs if s.get("path") and s.get("title")]
    return pairs, next_page


def get_song_data(path, title):
    url = BASE + path
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
    except Exception as e:
        print(f"  Error fetching {path}: {e}")
        return None, {}

    # Extract media links from embedded JSON
    links = {}
    data = parse_preloaded(r.text)
    if data:
        songs_ent = data.get("entities", {}).get("songs", {})
        if songs_ent:
            s = next(iter(songs_ent.values()))
            if s.get("youtubeUrl"):
                links["youtube"] = s["youtubeUrl"]
            if s.get("soundcloudUrl"):
                links["soundcloud"] = s["soundcloudUrl"]
            if s.get("spotifyUuid"):
                links["spotify"] = f"https://open.spotify.com/track/{s['spotifyUuid']}"

    soup = BeautifulSoup(r.text, "html.parser")
    containers = soup.find_all("div", attrs={"data-lyrics-container": "true"})
    if not containers:
        return None, links
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
            lines.append(chunk)
    if lines and ("Lyrics" in lines[0] or "Contributors" in lines[0]):
        lines = lines[1:]
    return (lines if len(lines) >= 5 else None), links


# Collect all song paths
print("Fetching song list...")
all_songs_meta = []
page = 1
while True:
    songs_on_page, next_page = get_song_paths(page)
    all_songs_meta.extend(songs_on_page)
    print(f"  Page {page}: {len(songs_on_page)} songs (total: {len(all_songs_meta)})")
    if not songs_on_page or not next_page:
        break
    page = next_page
    time.sleep(0.5)

print(f"\nTotal songs found: {len(all_songs_meta)}")
print("Fetching lyrics...\n")

songs = []
for i, (path, title) in enumerate(all_songs_meta, 1):
    print(f"[{i}/{len(all_songs_meta)}] {title}")
    lyrics, links = get_song_data(path, title)
    if lyrics:
        entry = {"song": title, "lyrics": lyrics}
        if links:
            entry["links"] = links
        songs.append(entry)
        link_str = " ".join(links.keys()) if links else "no links"
        print(f"  ✓ {len(lyrics)} lines [{link_str}]")
    else:
        print(f"  ✗ skipped (no lyrics or too short)")
    time.sleep(0.6)

import os
out_path = os.path.join(os.path.dirname(__file__), "..", "data", "lyrics.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(songs, f, ensure_ascii=False, indent=2)

print(f"\nDone — {len(songs)} songs saved to data/lyrics.json")
