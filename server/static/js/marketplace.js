// CampusGrid — Marketplace Filters & Client Interactivity
document.addEventListener('DOMContentLoaded', () => {
  // Auto-submit filter form on select change
  const filterForm = document.querySelector('#filter-form');
  if (filterForm) {
    const autoInputs = filterForm.querySelectorAll('select, input[type="radio"]');
    autoInputs.forEach(input => {
      input.addEventListener('change', () => filterForm.submit());
    });
  }
});
