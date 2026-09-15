// CampusGrid — Responsive Navigation & Dropdown Management
document.addEventListener('DOMContentLoaded', () => {
  const toggleBtn = document.querySelector('[data-mobile-menu-toggle]');
  const mobileNav = document.getElementById('cg-mobile-nav');
  const overlay = document.querySelector('[data-mobile-overlay]');

  if (toggleBtn && mobileNav) {
    const toggleMenu = () => {
      const isOpen = mobileNav.classList.toggle('open');
      if (overlay) overlay.classList.toggle('active', isOpen);
      document.body.style.overflow = isOpen ? 'hidden' : '';
    };

    toggleBtn.addEventListener('click', toggleMenu);
    if (overlay) overlay.addEventListener('click', toggleMenu);
  }
});
