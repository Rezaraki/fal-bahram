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
  const platforms = [
    { key: 'youtube',    label: 'YouTube',    icon: '▶' },
    { key: 'spotify',    label: 'Spotify',    icon: '♫' },
    { key: 'soundcloud', label: 'SoundCloud', icon: '☁' },
  ];
  platforms.forEach(({ key, label, icon }) => {
    if (!links[key]) return;
    const a = document.createElement('a');
    a.href = links[key];
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
    a.className = `media-link media-link--${key}`;
    a.innerHTML = `<span class="media-icon">${icon}</span>${label}`;
    mediaEl.appendChild(a);
  });

  card.classList.remove('hidden', 'reveal');
  void card.offsetWidth; // force reflow to restart animation
  card.classList.add('reveal');
});

function showError() {
  document.getElementById('error').classList.remove('hidden');
}
