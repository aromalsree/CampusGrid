// CampusGrid — Global Client Script
document.addEventListener('DOMContentLoaded', () => {
  // Auto dismiss alerts after 6 seconds
  const alerts = document.querySelectorAll('.cg-alert');
  alerts.forEach(alert => {
    const closeBtn = alert.querySelector('.cg-alert-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 250);
      });
    }
  });

  // Sticky header scroll behavior
  const header = document.querySelector('.cg-header');
  if (header) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 20) {
        header.classList.add('scrolled');
      } else {
        header.classList.remove('scrolled');
      }
    }, { passive: true });
  }
});
