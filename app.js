const cities = [
  "Auburndale","Bartow","Davenport","Dundee","Eagle Lake","Fort Meade",
  "Frostproof","Haines City","Highland Park","Hillcrest Heights","Lake Alfred",
  "Lake Hamilton","Lakeland","Lake Wales","Mulberry","Polk City","Winter Haven",
  "Polk County","Unincorporated"
];

const categories = ["Housing","Restaurant","Retail","Hotel","Infrastructure","Commercial","Community","Development"];
const statuses = ["Approved","Coming Soon","Under Construction","Grand Opening","Update"];

function categoryPlaceholder(category="Development"){
  const map = {
    Housing:"assets/category/housing.svg",
    Restaurant:"assets/category/restaurant.svg",
    Retail:"assets/category/retail.svg",
    Hotel:"assets/category/hotel.svg",
    Infrastructure:"assets/category/infrastructure.svg",
    Commercial:"assets/category/commercial.svg",
    Community:"assets/category/community.svg",
    Development:"assets/category/development.svg"
  };
  return map[category] || map.Development;
}
let allItems = [];

function esc(str=""){
  return String(str).replace(/[&<>"']/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[s]));
}
function slug(str=""){
  return String(str).replace(/\s+/g,"-").replace(/[^a-zA-Z0-9-]/g,"");
}
function badge(text, type){
  return `<span class="badge ${type}-${slug(text)}">${esc(text)}</span>`;
}
function imageFor(item){
  return item.image && item.image.trim() ? item.image : categoryPlaceholder(item.category);
}
function linkFor(item){
  return item.link ? `<a class="btn" href="${esc(item.link)}" target="_blank" rel="noopener">Read More →</a>` : "";
}

function renderCards(items){
  const grid = document.getElementById("newsGrid");
  grid.innerHTML = items.map(item => `
    <article class="news-card">
      <img src="${esc(imageFor(item))}" alt="">
      <div class="news-card-body">
        <div class="badges">${badge(item.status || "Update","status")}${badge(item.category || "Development","category")}</div>
        <h3>${esc(item.title)}</h3>
        <p class="meta">📍 ${esc(item.city || "Polk County")} • ${esc(item.date || "")}</p>
        <p class="summary">${esc(item.summary || "")}</p>
        ${linkFor(item)}
      </div>
    </article>`).join("");
}

function fillSelect(id, values){
  const select = document.getElementById(id);
  values.forEach(v => {
    const opt = document.createElement("option");
    opt.value = v;
    opt.textContent = v;
    select.appendChild(opt);
  });
}

function applyFilters(){
  const city = document.getElementById("cityFilter").value;
  const category = document.getElementById("categoryFilter").value;
  const status = document.getElementById("statusFilter").value;
  const sort = document.getElementById("sortFilter").value;

  let items = [...allItems];
  if(city) items = items.filter(i => (i.city || "").toLowerCase() === city.toLowerCase());
  if(category) items = items.filter(i => (i.category || "").toLowerCase() === category.toLowerCase());
  if(status) items = items.filter(i => (i.status || "").toLowerCase() === status.toLowerCase());

  if(sort === "city") items.sort((a,b)=>(a.city||"").localeCompare(b.city||""));
  if(sort === "category") items.sort((a,b)=>(a.category||"").localeCompare(b.category||""));

  renderCards(items);
}


function updateTicker(items){
  const ticker = document.getElementById("tickerText");
  if(!ticker) return;
  const headlines = items.slice(0, 8).map(i => {
    const city = i.city || "Polk County";
    const status = i.status || "Update";
    return `${status}: ${i.title} (${city})`;
  });
  if(!headlines.length){
    ticker.textContent = "No live development updates found yet.";
    return;
  }
  let index = 0;
  ticker.textContent = headlines[index];
  setInterval(() => {
    index = (index + 1) % headlines.length;
    ticker.textContent = headlines[index];
  }, 5500);
}

async function init(){
  fillSelect("cityFilter", cities);
  fillSelect("categoryFilter", categories);
  fillSelect("statusFilter", statuses);

  ["cityFilter","categoryFilter","statusFilter","sortFilter"].forEach(id => {
    document.getElementById(id).addEventListener("change", applyFilters);
  });

  try{
    const res = await fetch("data/news.json?cb=" + Date.now());
    const data = await res.json();
    allItems = data.items || [];
    document.getElementById("lastUpdated").textContent = data.last_updated ? `Last updated: ${data.last_updated}` : "";
    updateTicker(allItems);
    applyFilters();
  }catch(e){
    document.getElementById("newsGrid").innerHTML = "<p>Unable to load live news feed.</p>";
    console.error(e);
  }
}
init();
