async function loadComponent(selector, file) {
  const container = document.querySelector(selector);
  if (!container) return;

  try {
    const res = await fetch(file);
    const html = await res.text();
    container.innerHTML = html;

    // If loading sidebar, fetch user info
    if (file.includes('sidebar.html')) {
      try {
        const userRes = await fetch('/get_user_info');
        const data = await userRes.json();

        // Update sidebar name
        const nameElem = document.getElementById('sidebar-fullname');
        if (nameElem) {
          nameElem.textContent = data.fullname || 'User';
        }

        // Update sidebar profile picture
        const imgElem = document.getElementById('sidebar-profile-pic');
        if (imgElem) {
          if (data.profile_pic_url) {
            // Cache bust so updated image shows immediately
            imgElem.src = data.profile_pic_url + '?t=' + new Date().getTime();
          } else {
            imgElem.src = '/images/defaultuser.jpg';
          }
        }
      } catch (err) {
        console.error('Error fetching user info:', err);
      }
    }
  } catch (err) {
    console.error(`Error loading component: ${file}`, err);
    container.innerHTML = `<p style="color:red">Error loading component: ${file}</p>`;
  }
}
