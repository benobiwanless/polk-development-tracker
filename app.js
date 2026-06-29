const cities = [
  "Auburndale","Bartow","Davenport","Dundee","Eagle Lake","Fort Meade",
  "Frostproof","Haines City","Highland Park","Hillcrest Heights","Lake Alfred",
  "Lake Hamilton","Lakeland","Lake Wales","Mulberry","Polk City","Winter Haven",
  "Polk County","Unincorporated"
];

const categories = ["Housing","Restaurant","Retail","Hotel","Infrastructure","Commercial","Community","Development"];
const statuses = ["Approved","Coming Soon","Under Construction","Grand Opening","Update"];

const placeholder = "data:image/svg+xml;utf8," + encodeURIComponent(`
<svg xmlns='http://www.w3.org/2000/svg' width='900' height='520'>
<defs><linearGradient id='g' x1='0' x2='1'><stop stop-color='#d8ecff'/><stop offset='1' stop-color='#eef8ff'/></linearGradient></defs>
<rect width='100%' height='100%' fill='url(#g)'/>
<text x='50%' y='48%' text-anchor='middle' font-family='Arial' font-size='34' fill='#061b3a' font-weight='700'>Polk Development Tracker</text>
<text x='50%' y='58%' text-anchor='middle' font-family='Arial' font-size='20' fill='#447'>Live Development Update</text>
</svg>`);

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
  return item.image && item.image.trim() ? item.image : placeholder;
}
function linkFor(item){
  return item.link ? `<a class="btn" href="${esc(item.link)}" target="_blank" rel="noopener">Read More →</a>` : "";
}

function renderFeatured(items){
  const featured = items.find(i => i.featured) || items[0];
  const el = document.getElementById("featured");
  if(!featured){ el.innerHTML = ""; return; }
  el.innerHTML = `
    <div class="section-header"><h2>Featured Project</h2></div>
    <article class="featured-card">
      <img src="${esc(imageFor(featured))}" alt="">
      <div>
        <div class="badges">${badge(featured.status || "Update","status")}${badge(featured.category || "Development","category")}</div>
        <h3>${esc(featured.title)}</h3>
        <p class="meta">📍 ${esc(featured.city || "Polk County")} • ${esc(featured.date || "")} • ${esc(featured.source || "Live source")}</p>
        <p class="summary">${esc(featured.summary || "")}</p>
        ${linkFor(featured)}
      </div>
    </article>`;
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

  renderFeatured(items);
  renderCards(items);
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
    applyFilters();
  }catch(e){
    document.getElementById("newsGrid").innerHTML = "<p>Unable to load live news feed.</p>";
    console.error(e);
  }
}
init();
