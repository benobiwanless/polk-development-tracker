const cities = [
  "Auburndale","Bartow","Davenport","Dundee","Eagle Lake","Fort Meade",
  "Frostproof","Haines City","Highland Park","Hillcrest Heights","Lake Alfred",
  "Lake Hamilton","Lakeland","Lake Wales","Mulberry","Polk City","Winter Haven",
  "Polk County","Unincorporated"
];

const categories = ["Housing","Restaurant","Retail","Hotel","Infrastructure","Commercial","Community","Development"];
const statuses = ["Approved","Coming Soon","Under Construction","Grand Opening","Update"];

function categoryPlaceholder(category="Development"){
  const labels = {
    Housing:"Housing Development",
    Restaurant:"Restaurant Opening",
    Retail:"Retail Project",
    Hotel:"Hotel Development",
    Infrastructure:"Infrastructure Update",
    Commercial:"Commercial Project",
    Community:"Community Project",
    Development:"Polk Development"
  };
  const title = labels[category] || labels.Development;
  const svg = `<svg xmlns='http://www.w3.org/2000/svg' width='900' height='520'>
  <defs><linearGradient id='g' x1='0' x2='1'><stop stop-color='#d8ecff'/><stop offset='1' stop-color='#f3fbff'/></linearGradient></defs>
  <rect width='100%' height='100%' fill='url(#g)'/>
  <circle cx='120' cy='105' r='62' fill='#8ee26f' opacity='.75'/>
  <rect x='0' y='380' width='900' height='140' fill='#c7e7fb'/>
  <path d='M0 420 C160 360 260 455 420 395 C590 330 690 430 900 360 L900 520 L0 520 Z' fill='#0c4e93' opacity='.22'/>
  <text x='50%' y='46%' text-anchor='middle' font-family='Arial' font-size='36' fill='#061b3a' font-weight='800'>${title}</text>
  <text x='50%' y='57%' text-anchor='middle' font-family='Arial' font-size='20' fill='#3c526d' font-weight='700'>Polk County Florida</text>
  </svg>`;
  return "data:image/svg+xml;utf8," + encodeURIComponent(svg);
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
