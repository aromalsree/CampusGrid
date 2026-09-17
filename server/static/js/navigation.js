// CampusGrid — Responsive Navigation & Dropdown Management
document.addEventListener('DOMContentLoaded', () => {
  const toggleButtons = document.querySelectorAll('[data-mobile-menu-toggle]');
  const mobileNav = document.getElementById('cg-mobile-nav');
  const overlay = document.querySelector('[data-mobile-overlay]');

  if (mobileNav && toggleButtons.length > 0) {
    const toggleMenu = () => {
      const isOpen = mobileNav.classList.toggle('open');
      if (overlay) overlay.classList.toggle('active', isOpen);
      document.body.style.overflow = isOpen ? 'hidden' : '';
    };

    toggleButtons.forEach(btn => btn.addEventListener('click', toggleMenu));
    if (overlay) overlay.addEventListener('click', toggleMenu);
  }
});
