let songs = null;

fetch('data/lyrics.json')
  .then(r => r.json())
  .then(data => { songs = data; })
  .catch(() => showError());

document.getElementById('btn').addEventListener('click', () => {
  if (!songs) { showError(); return; }

  const song = songs[Math.floor(Math.random() * songs.length)];
  const lines = song.lyrics;

  // Need at least 2 lines before and 2 after
  const minIdx = 2;
  const maxIdx = lines.length - 3;
  if (maxIdx < minIdx) return; // song too short, retry silently

  const i = minIdx + Math.floor(Math.random() * (maxIdx - minIdx + 1));
  const context = lines.slice(i - 2, i + 3);

  const card = document.getElementById('fortune-card');
  const contextEl = document.getElementById('context-lines');
  const songEl = document.getElementById('song-name');

  contextEl.innerHTML = '';
  context.forEach((line, idx) => {
    const div = document.createElement('div');
    div.className = idx === 2 ? 'line fortune' : 'line';
    div.textContent = line;
    contextEl.appendChild(div);
  });

  songEl.textContent = song.song;

  const mediaEl = document.getElementById('media-links');
  mediaEl.innerHTML = '';
  const links = song.links || {};
  const spotifyUrl = links.spotify ||
    `https://open.spotify.com/search/${encodeURIComponent('Bahram ' + song.song)}`;

  const platforms = [
    { key: 'youtube',    label: 'YouTube',    icon: '▶', href: links.youtube },
    { key: 'spotify',    label: 'Spotify',    icon: '♫', href: spotifyUrl },
    { key: 'soundcloud', label: 'SoundCloud', icon: '☁', href: links.soundcloud },
  ];
  platforms.forEach(({ key, label, icon, href }) => {
    if (!href) return;
    const a = document.createElement('a');
    a.href = href;
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
    a.className = `media-link media-link--${key}`;
    a.innerHTML = `<span class="media-icon">${icon}</span>${label}`;
    mediaEl.appendChild(a);
  });

  const fortuneLine = context[2];
  const shareText = `فال بهرام من:\n«${fortuneLine}»\n— از آهنگ ${song.song}\n\nفال خودت رو بگیر: ${location.href}`;

  document.getElementById('share-twitter').onclick = () => {
    window.open('https://twitter.com/intent/tweet?text=' + encodeURIComponent(shareText), '_blank');
  };
  document.getElementById('share-whatsapp').onclick = () => {
    window.open('https://wa.me/?text=' + encodeURIComponent(shareText), '_blank');
  };
  document.getElementById('share-telegram').onclick = () => {
    window.open('https://t.me/share/url?url=' + encodeURIComponent(location.href) + '&text=' + encodeURIComponent(`فال بهرام من:\n«${fortuneLine}»\n— از آهنگ ${song.song}`), '_blank');
  };
  document.getElementById('share-copy').onclick = () => {
    navigator.clipboard.writeText(shareText).then(() => {
      const btn = document.getElementById('share-copy');
      btn.textContent = 'کپی شد ✓';
      setTimeout(() => { btn.textContent = 'کپی'; }, 2000);
    });
  };

  card.classList.remove('hidden', 'reveal');
  void card.offsetWidth;
  card.classList.add('reveal');
});

function showError() {
  document.getElementById('error').classList.remove('hidden');
}
