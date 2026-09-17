// CampusGrid — Global Client Experience Engine
(() => {
  document.addEventListener('DOMContentLoaded', () => {
    // 1. Toast Notification Manager
    const setupAlertDismiss = (el) => {
      const closeBtn = el.querySelector('.cg-toast-close, .cg-alert-close');
      const dismiss = () => {
        el.style.opacity = '0';
        el.style.transform = 'translateX(20px)';
        setTimeout(() => el.remove(), 250);
      };
      if (closeBtn) closeBtn.addEventListener('click', dismiss);
      setTimeout(dismiss, 5000);
    };

    document.querySelectorAll('.cg-toast, .cg-alert').forEach(setupAlertDismiss);

    // Global Toast Trigger helper
    window.showToast = (message, type = 'success') => {
      let container = document.querySelector('#cg-toast-container');
      if (!container) {
        container = document.createElement('div');
        container.id = 'cg-toast-container';
        document.body.appendChild(container);
      }
      const toast = document.createElement('div');
      toast.className = `cg-toast cg-toast--${type}`;
      toast.setAttribute('role', 'alert');
      toast.innerHTML = `
        <div style="display:flex;align-items:center;gap:0.5rem;">
          <span>${message}</span>
        </div>
        <button type="button" class="cg-toast-close" aria-label="Dismiss">&times;</button>
      `;
      container.appendChild(toast);
      setupAlertDismiss(toast);
    };

    // 3. Sticky header scroll behavior
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

    // 4. Scroll Reveal with IntersectionObserver
    if ('IntersectionObserver' in window) {
      const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('in-view');
            revealObserver.unobserve(entry.target);
          }
        });
      }, { threshold: 0.1 });

      document.querySelectorAll('.scroll-reveal').forEach(el => revealObserver.observe(el));
    } else {
      document.querySelectorAll('.scroll-reveal').forEach(el => el.classList.add('in-view'));
    }

    // 5. Wishlist toggle micro-interaction
    document.querySelectorAll('.cg-wishlist-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        btn.classList.toggle('active');
        const isActive = btn.classList.contains('active');
        window.showToast(isActive ? 'Saved to wishlist!' : 'Removed from wishlist', isActive ? 'success' : 'info');
      });
    });
  });
})();
