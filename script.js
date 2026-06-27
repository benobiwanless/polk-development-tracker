fetch('data/stories.json').then(r=>r.json()).then(data=>{
const c=document.getElementById('stories');
const s=document.getElementById('search');
function render(list){
c.innerHTML='';
list.forEach(x=>c.innerHTML+=`<div class="card"><small>${x.category}</small><h3>${x.title}</h3><p><b>${x.city}</b></p><p>${x.summary}</p></div>`);
}
render(data);
s.oninput=()=>render(data.filter(x=>(x.title+x.city+x.category).toLowerCase().includes(s.value.toLowerCase())));
});