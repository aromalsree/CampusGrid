// CampusGrid — Responsive Navigation & Dropdown Management
document.addEventListener('DOMContentLoaded', () => {
  // 1. Mobile Menu Drawer
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

  // 2. User Profile Dropdown Toggle
  const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
  
  dropdownToggles.forEach(toggle => {
    toggle.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      const dropdown = toggle.closest('.user-dropdown');
      if (!dropdown) return;
      
      const isOpen = dropdown.classList.contains('open');

      // Close other open dropdowns
      document.querySelectorAll('.user-dropdown.open').forEach(d => {
        if (d !== dropdown) {
          d.classList.remove('open');
          const t = d.querySelector('.dropdown-toggle');
          if (t) t.setAttribute('aria-expanded', 'false');
        }
      });

      // Toggle current dropdown
      dropdown.classList.toggle('open', !isOpen);
      toggle.setAttribute('aria-expanded', String(!isOpen));
    });
  });

  // Close dropdown when clicking outside
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.user-dropdown')) {
      document.querySelectorAll('.user-dropdown.open').forEach(dropdown => {
        dropdown.classList.remove('open');
        const toggle = dropdown.querySelector('.dropdown-toggle');
        if (toggle) toggle.setAttribute('aria-expanded', 'false');
      });
    }
  });

  // Close dropdown on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      document.querySelectorAll('.user-dropdown.open').forEach(dropdown => {
        dropdown.classList.remove('open');
        const toggle = dropdown.querySelector('.dropdown-toggle');
        if (toggle) toggle.setAttribute('aria-expanded', 'false');
      });
    }
  });
});

