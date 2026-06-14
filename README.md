# فال بهرام

A Persian fortune-telling site powered by Bahram's rap lyrics. Click the button, get your fate.

**Live site:** https://rezaraki.github.io/fal-bahram/

## How it works

Each click picks a random line from Bahram's discography and shows it as your fortune, along with the two lines before and after it for context, and the song it's from.

## Stack

- Static HTML/CSS/JS — no framework, no server
- Lyrics scraped from Genius (115 songs)
- Hosted on GitHub Pages

## Scraping lyrics yourself

You'll need Python 3.10+ and the dependencies:

```bash
pip install -r scraper/requirements.txt
python scraper/scrape.py
```

This fetches all of Bahram's songs from Genius and writes them to `data/lyrics.json`.

To serve locally:

```bash
python -m http.server 8000
```

Then open `http://localhost:8000`.
