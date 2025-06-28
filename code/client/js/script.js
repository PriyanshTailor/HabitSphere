
  window.addEventListener('DOMContentLoaded', () => {
    const links = document.querySelectorAll('.sidebar .nav a');
    const currentPage = window.location.pathname.split('/').pop().toLowerCase();

    links.forEach(link => {
      const linkPage = link.getAttribute('href').split('/').pop().toLowerCase();
      if (linkPage === currentPage) {
        link.classList.add('active');
      }
    });
  });
