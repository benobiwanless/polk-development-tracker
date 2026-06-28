const state = { items: [], filtered: [] };

const cardsEl = document.getElementById('cards');
const statsEl = document.getElementById('stats');
const updatedEl = document.getElementById('updated');
const countLabel = document.getElementById('countLabel');
const searchEl = document.getElementById('search');
const categoryEl = document.getElementById('categoryFilter');
const cityEl = document.getElementById('cityFilter');

function cleanCity(location = '') {
  return location.replace(', FL', '').replace('Florida', '').trim() || 'Polk County';
}

function normalizeCategory(category = 'Development') {
  return category || 'Development';
}

function isFresh(dateText = '') {
  return /today|recent|new|2026|2025/i.test(dateText);
}

function renderStats(items) {
  const cats = ['Housing','Restaurants','Retail','Hotels','Infrastructure','Development'];
  statsEl.innerHTML = cats.map(cat => {
    const count = items.filter(i => normalizeCategory(i.category) === cat).length;
    return `<article><strong>${count}</strong><span>${cat}</span></article>`;
  }).join('');
}

function renderCityOptions(items) {
  const cities = [...new Set(items.map(i => cleanCity(i.location)))].sort();
  cityEl.innerHTML = '<option value="all">All cities</option>' + cities.map(city => `<option>${city}</option>`).join('');
}

function cardTemplate(item, index) {
  const category = normalizeCategory(item.category);
  const city = cleanCity(item.location);
  const image = item.image || 'assets/sample-layout.png';
  const href = item.url || '#';
  const featured = index === 0 ? ' featured' : '';
  const fresh = isFresh(item.date) ? ' • New' : '';
  return `
    <article class="card${featured}">
      <a class="thumb" href="${href}" style="background-image:url('${image}')" aria-label="Read ${item.title}">
        <span class="badge">${category}</span>
      </a>
      <div class="card-body">
        <div class="meta">${city} • ${item.source || 'Source'} • ${item.date || 'Recent'}${fresh}</div>
        <h3>${item.title}</h3>
        <p>${item.summary || ''}</p>
        <a class="read" href="${href}">Read more →</a>
      </div>
    </article>`;
}

function applyFilters() {
  const query = searchEl.value.trim().toLowerCase();
  const category = categoryEl.value;
  const city = cityEl.value;

  state.filtered = state.items.filter(item => {
    const haystack = `${item.title} ${item.summary} ${item.category} ${item.location} ${item.source}`.toLowerCase();
    const itemCity = cleanCity(item.location);
    return (!query || haystack.includes(query)) &&
      (category === 'all' || normalizeCategory(item.category) === category) &&
      (city === 'all' || itemCity === city);
  });

  countLabel.textContent = `${state.filtered.length} update${state.filtered.length === 1 ? '' : 's'} shown`;
  cardsEl.innerHTML = state.filtered.length
    ? state.filtered.map(cardTemplate).join('')
    : '<p class="empty">No updates match those filters.</p>';
}

async function loadNews() {
  try {
    const response = await fetch('data/news.json', { cache: 'no-store' });
    const data = await response.json();
    state.items = Array.isArray(data.items) ? data.items : [];
    updatedEl.textContent = `Last updated: ${data.updated_at || 'Starter data'}`;
    renderStats(state.items);
    renderCityOptions(state.items);
    applyFilters();
  } catch (error) {
    cardsEl.innerHTML = '<p class="empty">Could not load news data. Check that data/news.json was uploaded.</p>';
    updatedEl.textContent = 'Last updated: unavailable';
  }
}

searchEl.addEventListener('input', applyFilters);
categoryEl.addEventListener('change', applyFilters);
cityEl.addEventListener('change', applyFilters);

loadNews();
