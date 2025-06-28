async function loadComponent(selector, file) {
  const container = document.querySelector(selector);
  if (!container) return;

  try {
    const res = await fetch(file);
    const html = await res.text();
    container.innerHTML = html;
  } catch (err) {
    console.error(`Error loading component: ${file}`, err);
    container.innerHTML = `<p style="color:red">Error loading component: ${file}</p>`;
  }
}
