/**
 * main.js - Public Page JavaScript
 * Handles: live search, sort links, pagination, UI effects
 */

document.addEventListener('DOMContentLoaded', function () {

  // ============================================================
  // LIVE SEARCH (debounced)
  // ============================================================

  const searchInput = document.getElementById('searchInput');
  let searchTimer = null;

  if (searchInput) {
    searchInput.addEventListener('input', function () {
      clearTimeout(searchTimer);
      // Wait 400ms after user stops typing before searching
      searchTimer = setTimeout(() => {
        const url = new URL(window.location.href);
        url.searchParams.set('search', this.value.trim());
        url.searchParams.set('page', 1); // Reset to first page on search
        window.location.href = url.toString();
      }, 400);
    });

    // Handle Enter key
    searchInput.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') {
        clearTimeout(searchTimer);
        const url = new URL(window.location.href);
        url.searchParams.set('search', this.value.trim());
        url.searchParams.set('page', 1);
        window.location.href = url.toString();
      }
    });
  }

  // Clear search button
  const clearSearchBtn = document.getElementById('clearSearch');
  if (clearSearchBtn) {
    clearSearchBtn.addEventListener('click', function () {
      const url = new URL(window.location.href);
      url.searchParams.delete('search');
      url.searchParams.set('page', 1);
      window.location.href = url.toString();
    });
  }

  // ============================================================
  // COLUMN SORT - Update URL when clicking sort headers
  // ============================================================

  const sortableHeaders = document.querySelectorAll('[data-sort]');
  sortableHeaders.forEach(function (th) {
    th.addEventListener('click', function () {
      const column = this.dataset.sort;
      const url = new URL(window.location.href);
      const currentSort = url.searchParams.get('sort');
      const currentOrder = url.searchParams.get('order') || 'desc';

      if (currentSort === column) {
        // Toggle order if same column clicked
        url.searchParams.set('order', currentOrder === 'asc' ? 'desc' : 'asc');
      } else {
        url.searchParams.set('sort', column);
        url.searchParams.set('order', 'asc');
      }
      url.searchParams.set('page', 1);
      window.location.href = url.toString();
    });
  });

  // ============================================================
  // AUTO-DISMISS FLASH MESSAGES after 4 seconds
  // ============================================================

  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-10px)';
      alert.style.transition = 'all 0.4s ease';
      setTimeout(() => alert.remove(), 400);
    }, 4000);
  });

  // ============================================================
  // ANIMATE STATS COUNTER
  // ============================================================

  const counters = document.querySelectorAll('[data-count]');
  counters.forEach(function (el) {
    const target = parseFloat(el.dataset.count);
    const isAmount = el.dataset.type === 'amount';
    let start = 0;
    const duration = 1200;
    const startTime = performance.now();

    function update(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // cubic ease-out
      const value = start + (target - start) * eased;

      if (isAmount) {
        el.textContent = '₹' + value.toLocaleString('en-IN', {
          minimumFractionDigits: 0,
          maximumFractionDigits: 0
        });
      } else {
        el.textContent = Math.floor(value).toLocaleString('en-IN');
      }

      if (progress < 1) requestAnimationFrame(update);
    }

    requestAnimationFrame(update);
  });

});
