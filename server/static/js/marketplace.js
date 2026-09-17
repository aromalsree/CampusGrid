// CampusGrid — Marketplace Filters & Client Interactivity
document.addEventListener('DOMContentLoaded', () => {
  const filterForm = document.querySelector('#filter-form');
  if (filterForm) {
    const autoInputs = filterForm.querySelectorAll('select, input[type="radio"]');
    // Only auto-submit on desktop to prevent erratic page jumps on mobile
    if (window.innerWidth > 768) {
      autoInputs.forEach(input => {
        input.addEventListener('change', () => filterForm.submit());
      });
    }
  }

  // Mobile Filter Drawer Toggle & Close
  const filterToggleBtn = document.querySelector('#open-filters');
  const filterCloseBtn = document.querySelector('#close-filters');
  const filterSidebar = document.querySelector('.filter-sidebar');
  
  if (filterToggleBtn && filterSidebar) {
    filterToggleBtn.addEventListener('click', () => {
      filterSidebar.classList.add('open-mobile');
    });
  }

  if (filterCloseBtn && filterSidebar) {
    filterCloseBtn.addEventListener('click', () => {
      filterSidebar.classList.remove('open-mobile');
    });
  }

  // Close drawer if clicking outside on mobile
  document.addEventListener('click', (e) => {
    if (filterSidebar && filterSidebar.classList.contains('open-mobile')) {
      if (!filterSidebar.contains(e.target) && filterToggleBtn && !filterToggleBtn.contains(e.target)) {
        filterSidebar.classList.remove('open-mobile');
      }
    }
  });
});

// Product detail gallery image switcher
window.switchGalleryImage = (imageUrl, thumbnailElement) => {
  const mainImg = document.getElementById('gallery-main-img');
  if (mainImg) {
    mainImg.src = imageUrl;
    mainImg.style.display = 'block';
  }
  document.querySelectorAll('.gallery-thumb').forEach(thumb => thumb.classList.remove('active'));
  if (thumbnailElement) {
    thumbnailElement.classList.add('active');
  }
};
