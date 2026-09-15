// CampusGrid — User & Auth Form Enhancements
document.addEventListener('DOMContentLoaded', () => {
  const emailInput = document.querySelector('#id_email, input[name="email"]');
  const badgeHint = document.querySelector('#edu-detected-badge');

  if (emailInput && badgeHint) {
    emailInput.addEventListener('input', (e) => {
      const val = e.target.value.toLowerCase().trim();
      const isEdu = val.endsWith('.edu') || val.includes('.edu.') || val.endsWith('.ac.in');
      badgeHint.style.display = isEdu ? 'inline-flex' : 'none';
    });
  }
});
