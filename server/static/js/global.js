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
// 5. Wishlist toggle micro-interaction (AJAX-Enabled)
    document.querySelectorAll('.cg-wishlist-btn').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        e.preventDefault();
        e.stopPropagation();

        const form = btn.closest('form');
        const url = form ? form.action : btn.getAttribute('href');
        
        // Grab CSRF token safely
        const csrfInput = form ? form.querySelector('[name=csrfmiddlewaretoken]') : null;
        const csrfToken = csrfInput ? csrfInput.value : getCookie('csrftoken');

        if (!url) return;

        try {
          const response = await fetch(url, {
            method: 'POST',
            headers: {
              'X-Requested-With': 'XMLHttpRequest',
              'X-CSRFToken': csrfToken,
              'Content-Type': 'application/json',
            },
          });

          // Redirect to login if user is unauthenticated
          if (response.status === 401 || response.redirected) {
            window.location.href = '/accounts/login/';
            return;
          }

          // Safely check if Django returned JSON
          const contentType = response.headers.get('content-type');
          if (!contentType || !contentType.includes('application/json')) {
            const textResponse = await response.text();
            console.error('Expected JSON, but received HTML response:', textResponse);
            window.showToast('Server error. Please try again.', 'danger');
            return;
          }

          const data = await response.json();

          if (data && data.status === 'success') {
            const svgIcon = btn.querySelector('svg');

            if (data.in_wishlist) {
              btn.classList.add('active');
              if (svgIcon) svgIcon.setAttribute('fill', 'currentColor');
            } else {
              btn.classList.remove('active');
              if (svgIcon) svgIcon.setAttribute('fill', 'none');
            }

            window.showToast(data.message, data.in_wishlist ? 'success' : 'info');
          }
        } catch (error) {
          console.error('Wishlist AJAX Error:', error);
        }
      });
    });
    
  });
})();
