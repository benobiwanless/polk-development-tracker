let allStories = [];
let activeCategory = "All";
let map;
let markers = [];

const categoryIcons = {
  Restaurant: "🍔",
  Retail: "🛍️",
  Housing: "🏡",
  Roads: "🚧",
  Business: "🏢"
};

fetch("data/stories.json")
  .then(res => res.json())
  .then(data => {
    allStories = data;
    buildStats();
    renderStories();
    initMap();
  });

function buildStats(){
  const stats = document.getElementById("stats");
  const total = allStories.length;
  const restaurants = allStories.filter(s => s.category === "Restaurant").length;
  const retail = allStories.filter(s => s.category === "Retail").length;
  const housing = allStories.filter(s => s.category === "Housing").length;

  stats.innerHTML = `
    <div class="stat"><strong>${total}</strong><span>Tracked Projects</span></div>
    <div class="stat"><strong>${restaurants}</strong><span>Restaurants</span></div>
    <div class="stat"><strong>${retail}</strong><span>Retail</span></div>
    <div class="stat"><strong>${housing}</strong><span>Housing</span></div>
  `;
}

function getFilteredStories(){
  const q = document.getElementById("searchInput").value.toLowerCase();
  return allStories.filter(story => {
    const matchesCategory = activeCategory === "All" || story.category === activeCategory;
    const text = `${story.title} ${story.city} ${story.category} ${story.status} ${story.summary}`.toLowerCase();
    return matchesCategory && text.includes(q);
  });
}

function renderStories(){
  const stories = getFilteredStories();
  const grid = document.getElementById("storyGrid");
  const count = document.getElementById("resultCount");
  count.textContent = `${stories.length} result${stories.length === 1 ? "" : "s"}`;

  grid.innerHTML = stories.map(story => `
    <article class="card">
      <span class="tag">${categoryIcons[story.category] || "📍"} ${story.category}</span>
      <h3>${story.title}</h3>
      <p class="meta">📍 ${story.city}</p>
      <p>${story.summary}</p>
      <p class="status">Status: <strong>${story.status}</strong></p>
      <a class="source" href="${story.source}" target="_blank">Source →</a>
    </article>
  `).join("");

  updateMapMarkers(stories);
}

document.getElementById("searchInput").addEventListener("input", renderStories);

document.querySelectorAll("[data-category]").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll("[data-category]").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    activeCategory = btn.dataset.category;
    renderStories();
  });
});

function initMap(){
  map = L.map("developmentMap").setView([28.0395, -81.7887], 10);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap"
  }).addTo(map);
  updateMapMarkers(allStories);
}

function updateMapMarkers(stories){
  if(!map) return;
  markers.forEach(marker => map.removeLayer(marker));
  markers = stories.map(story => {
    return L.marker([story.lat, story.lng])
      .addTo(map)
      .bindPopup(`<strong>${story.title}</strong><br>${story.city}<br>${story.category} • ${story.status}`);
  });
}
