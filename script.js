let allStories = [];
let activeCategory = "All";

fetch("data/news.json")
  .then(response => response.json())
  .then(data => {
    allStories = data;
    renderStories();
  });

document.querySelectorAll("[data-category]").forEach(button => {
  button.addEventListener("click", () => {
    document.querySelectorAll("[data-category]").forEach(btn => btn.classList.remove("active"));
    button.classList.add("active");
    activeCategory = button.dataset.category;
    renderStories();
  });
});

function renderStories() {
  const grid = document.getElementById("newsGrid");

  const stories = activeCategory === "All"
    ? allStories
    : allStories.filter(story => story.category === activeCategory);

  grid.innerHTML = stories.map(story => `
    <article class="news-card">
      <div class="news-image">
        <img src="${story.image}" alt="${story.title}">
        <span class="badge ${story.category}">${story.category}</span>
      </div>
      <div class="news-content">
        <h2>${story.title}</h2>
        <p>${story.summary}</p>
        <div class="meta">
          <span>📍 ${story.city}</span>
          <span>|</span>
          <span>${story.date}</span>
        </div>
        <a class="read-more" href="${story.link}" target="_blank" rel="noopener">Read More →</a>
      </div>
    </article>
  `).join("");
}
