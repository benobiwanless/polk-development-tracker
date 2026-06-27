let allProjects=[];let activeCategory="All";let map;let markers=[];
const icons={Restaurant:"🍔",Retail:"🛍️",Housing:"🏡",Roads:"🚧",Business:"🏢",Entertainment:"🎉"};
document.getElementById("menuBtn")?.addEventListener("click",()=>document.getElementById("navLinks").classList.toggle("open"));
fetch("data/projects.json").then(r=>r.json()).then(data=>{allProjects=data;buildCityFilter();buildStats();renderFeatured();renderSections();renderProjects();initMap();});
function buildCityFilter(){const cities=[...new Set(allProjects.map(s=>s.city))].sort();document.getElementById("cityFilter").innerHTML='<option value="All">All Cities</option>'+cities.map(c=>`<option value="${c}">${c}</option>`).join("");}
function buildStats(){const stats=document.getElementById("stats");const active=allProjects.filter(p=>p.phase==="Active").length;const coming=allProjects.filter(p=>p.phase==="Coming Soon").length;const opened=allProjects.filter(p=>p.phase==="Recently Opened").length;stats.innerHTML=`<div class="stat"><strong>${allProjects.length}</strong><span>Total Projects</span></div><div class="stat"><strong>${active}</strong><span>Active</span></div><div class="stat"><strong>${coming}</strong><span>Coming Soon</span></div><div class="stat"><strong>${opened}</strong><span>Recently Opened</span></div>`;}
function renderFeatured(){const s=allProjects[0];document.getElementById("featured").innerHTML=`<p class="eyebrow">Featured Project</p><h2>${icons[s.category]||"📍"} ${s.title}</h2><p class="meta">📍 ${s.city} • ${s.category} • ${s.status}</p><p>${s.summary}</p><a class="read-more" href="pages/project.html?id=${s.id}">View project →</a>`;}
function card(s,small=false){return `<article class="card"><span class="tag">${icons[s.category]||"📍"} ${s.category}</span><span class="tag phase">${s.phase}</span><h3>${s.title}</h3><p class="meta">📍 ${s.city} • Updated ${s.updated}</p>${small?"":`<p>${s.summary}</p>`}<p class="status">Status: <strong>${s.status}</strong></p><a class="read-more" href="pages/project.html?id=${s.id}">View project →</a></article>`;}
function renderSections(){document.getElementById("comingSoonGrid").innerHTML=allProjects.filter(p=>p.phase==="Coming Soon").slice(0,4).map(p=>card(p,true)).join("");document.getElementById("openedGrid").innerHTML=allProjects.filter(p=>p.phase==="Recently Opened").slice(0,4).map(p=>card(p,true)).join("") || `<p class="meta">No recently opened projects yet.</p>`;}
function filtered(){const q=document.getElementById("searchInput").value.toLowerCase();const city=document.getElementById("cityFilter").value;return allProjects.filter(s=>{const txt=`${s.title} ${s.city} ${s.category} ${s.status} ${s.phase} ${s.summary}`.toLowerCase();return (activeCategory==="All"||s.category===activeCategory)&&(city==="All"||s.city===city)&&txt.includes(q);});}
function renderProjects(){const list=filtered();document.getElementById("resultCount").textContent=`${list.length} result${list.length===1?"":"s"}`;document.getElementById("projectGrid").innerHTML=list.map(s=>card(s)).join("");updateMapMarkers(list);}
document.getElementById("searchInput").addEventListener("input",renderProjects);document.getElementById("cityFilter").addEventListener("change",renderProjects);
document.querySelectorAll("[data-category]").forEach(btn=>btn.addEventListener("click",()=>{document.querySelectorAll("[data-category]").forEach(b=>b.classList.remove("active"));btn.classList.add("active");activeCategory=btn.dataset.category;renderProjects();}));
function initMap(){map=L.map("developmentMap").setView([28.0395,-81.7887],10);L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{attribution:"&copy; OpenStreetMap"}).addTo(map);updateMapMarkers(allProjects);}
function updateMapMarkers(list){if(!map)return;markers.forEach(m=>map.removeLayer(m));markers=list.map(s=>L.marker([s.lat,s.lng]).addTo(map).bindPopup(`<strong>${s.title}</strong><br>${s.city}<br>${s.category} • ${s.status}<br><a href="pages/project.html?id=${s.id}">View project</a>`));}


function renderLiveNews(){
  fetch("data/live-news.json?cache=" + Date.now())
    .then(r=>r.json())
    .then(items=>{
      const grid=document.getElementById("liveNewsGrid");
      if(!grid) return;
      grid.innerHTML=items.slice(0,6).map(item=>`
        <article class="card">
          <span class="tag">Live Source</span>
          <h3>${item.title}</h3>
          <p class="meta">${item.source}${item.date ? " • " + item.date.substring(0,10) : ""}</p>
          <p>${item.summary || ""}</p>
          <a class="read-more" href="${item.url}" target="_blank">Open source →</a>
        </article>
      `).join("");
    })
    .catch(()=>{
      const grid=document.getElementById("liveNewsGrid");
      if(grid) grid.innerHTML='<p class="meta">Live source data has not been generated yet.</p>';
    });

  fetch("data/last-updated.json?cache=" + Date.now())
    .then(r=>r.json())
    .then(info=>{
      const el=document.getElementById("lastUpdated");
      if(el && info.lastUpdatedUtc) el.textContent="Updated " + new Date(info.lastUpdatedUtc).toLocaleString();
    })
    .catch(()=>{});
}
renderLiveNews();


function renderYouTubeHeadlines(){
  fetch("data/youtube-headlines.json?cache=" + Date.now())
    .then(r=>r.json())
    .then(items=>{
      const grid=document.getElementById("youtubeGrid");
      if(!grid) return;
      grid.innerHTML=items.slice(0,8).map(item=>`
        <article class="card">
          <span class="tag">YouTube</span>
          <h3>${item.title}</h3>
          <p class="meta">${item.channel || "YouTube"}${item.publishedAt ? " • " + item.publishedAt.substring(0,10) : ""}</p>
          <p>${item.description || ""}</p>
          <a class="read-more" href="${item.url}" target="_blank">Watch / open →</a>
        </article>
      `).join("");
    })
    .catch(()=>{
      const grid=document.getElementById("youtubeGrid");
      if(grid) grid.innerHTML='<p class="meta">YouTube data has not been generated yet.</p>';
    });
}
renderYouTubeHeadlines();
