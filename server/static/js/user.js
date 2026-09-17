// CampusGrid — User & Auth Form Enhancements
document.addEventListener('DOMContentLoaded', () => {
  // 1. Academic Email Detection
  const emailInput = document.querySelector('#id_email, input[name="email"]');
  const badgeHint = document.querySelector('#edu-detected-badge');

  if (emailInput && badgeHint) {
    emailInput.addEventListener('input', (e) => {
      const val = e.target.value.toLowerCase().trim();
      const isEdu = /\.(edu|ac\.in|edu\.in|college\.edu|institute\.ac)$/i.test(val) || /\.ac\.[a-z]{2}$/i.test(val);
      badgeHint.style.display = isEdu ? 'inline-flex' : 'none';
    });
  }

  // 2. Password Visibility Toggle
  document.querySelectorAll('.pwd-toggle-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const inputWrap = btn.closest('.input-with-toggle');
      if (!inputWrap) return;
      const input = inputWrap.querySelector('input');
      if (!input) return;
      const isHidden = input.type === 'password';
      input.type = isHidden ? 'text' : 'password';
      const iconShow = btn.querySelector('.pwd-icon-show');
      const iconHide = btn.querySelector('.pwd-icon-hide');
      if (iconShow) iconShow.style.display = isHidden ? 'none' : 'block';
      if (iconHide) iconHide.style.display = isHidden ? 'block' : 'none';
    });
  });

  // 3. Form Submit Loading State
  const authForm = document.querySelector('#login-form, #register-form');
  if (authForm) {
    authForm.addEventListener('submit', () => {
      const submitBtn = authForm.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.style.opacity = '0.7';
        submitBtn.innerHTML = 'Connecting to CampusGrid...';
      }
    });
  }
});
