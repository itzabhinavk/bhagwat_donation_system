/**
 * admin.js - Admin Panel JavaScript
 * Handles: modals, edit forms, delete confirmation, loading states
 */

document.addEventListener('DOMContentLoaded', function () {

  // ============================================================
  // MODAL UTILITY FUNCTIONS
  // ============================================================

  function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('active');
      document.body.style.overflow = 'hidden';
      // Focus first input
      const firstInput = modal.querySelector('input, select, textarea');
      if (firstInput) setTimeout(() => firstInput.focus(), 100);
    }
  }

  function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('active');
      document.body.style.overflow = '';
    }
  }

  // Close modal on overlay click
  document.querySelectorAll('.modal-overlay').forEach(function (overlay) {
    overlay.addEventListener('click', function (e) {
      if (e.target === this) {
        closeModal(this.id);
      }
    });
  });

  // Close modal buttons
  document.querySelectorAll('[data-close-modal]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const modalId = this.dataset.closeModal;
      closeModal(modalId);
    });
  });

  // Close on Escape key
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      document.querySelectorAll('.modal-overlay.active').forEach(function (m) {
        m.classList.remove('active');
        document.body.style.overflow = '';
      });
    }
  });

  // Expose openModal globally for inline use
  window.openModal = openModal;
  window.closeModal = closeModal;

  // ============================================================
  // ADD DONATION MODAL
  // ============================================================

  const addDonationBtn = document.getElementById('addDonationBtn');
  if (addDonationBtn) {
    addDonationBtn.addEventListener('click', function () {
      openModal('addDonationModal');
    });
  }

  // ============================================================
  // EDIT DONATION - Fetch data and populate modal
  // ============================================================

  document.querySelectorAll('[data-edit-donation]').forEach(function (btn) {
    btn.addEventListener('click', async function () {
      const donationId = this.dataset.editDonation;
      const tableKey = this.dataset.tableKey;
      const form = document.getElementById('editDonationForm');

      // Show loading state
      form.innerHTML = '<div class="text-center" style="padding: 40px; color: var(--text-muted);">Loading...</div>';
      openModal('editDonationModal');

      try {
        const response = await fetch(`/admin/get-donation/${tableKey}/${donationId}`);
        const data = await response.json();

        if (data.error) {
          throw new Error(data.error);
        }

        // Set form action to correct URL
        document.getElementById('editDonationModalForm').action = `/admin/edit-donation/${tableKey}/${donationId}`;

        // Populate form
        form.innerHTML = `
          <div class="form-grid">
            <div class="form-group">
              <label>Donor Name *</label>
              <input type="text" name="donor_name" value="${escHtml(data.donor_name)}" required>
            </div>
            <div class="form-group">
              <label>Village *</label>
              <input type="text" name="village" value="${escHtml(data.village)}" required>
            </div>
            <div class="form-group">
              <label>Contact Info</label>
              <input type="text" name="donor_contact" value="${escHtml(data.donor_contact || '')}">
            </div>
            <div class="form-group">
              <label>Amount (₹) *</label>
              <input type="number" name="amount" value="${data.amount}" step="0.01" min="1" required>
            </div>
            <div class="form-group">
              <label>Payment Method</label>
              <select name="payment_method">
                ${['Cash', 'Online', 'Cheque', 'Other'].map(m =>
                  `<option value="${m}" ${data.payment_method === m ? 'selected' : ''}>${m}</option>`
                ).join('')}
              </select>
            </div>
            <div class="form-group">
              <label>Payment Status</label>
              <select name="payment_status">
                ${['Received', 'Pending', 'Cancelled'].map(m =>
                  `<option value="${m}" ${data.payment_status === m ? 'selected' : ''}>${m}</option>`
                ).join('')}
              </select>
            </div>
            <div class="form-group">
              <label>Date *</label>
              <input type="date" name="donated_at" value="${data.donated_at}" required>
            </div>
            <div class="form-group full-width">
              <label>Remark</label>
              <textarea name="remark" rows="3">${escHtml(data.remark || '')}</textarea>
            </div>
          </div>
        `;

      } catch (err) {
        form.innerHTML = `<div class="alert alert-error">Error loading donation: ${err.message}</div>`;
      }
    });
  });

  // ============================================================
  // DELETE DONATION - Confirmation dialog
  // ============================================================

  document.querySelectorAll('[data-delete-donation]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const donationId = this.dataset.deleteDonation;
      const tableKey = this.dataset.tableKey;
      const donorName = this.dataset.donorName || 'this donation';

      if (confirm(`⚠️ Delete donation from "${donorName}"?\n\nThis action cannot be undone.`)) {
        // Submit delete form
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/admin/delete-donation/${tableKey}/${donationId}`;
        document.body.appendChild(form);
        form.submit();
      }
    });
  });

  // ============================================================
  // ADD NOTICE MODAL
  // ============================================================

  const addNoticeBtn = document.getElementById('addNoticeBtn');
  if (addNoticeBtn) {
    addNoticeBtn.addEventListener('click', function () {
      openModal('addNoticeModal');
    });
  }

  // ============================================================
  // EDIT NOTICE - Fetch and populate modal
  // ============================================================

  document.querySelectorAll('[data-edit-notice]').forEach(function (btn) {
    btn.addEventListener('click', async function () {
      const noticeId = this.dataset.editNotice;
      const form = document.getElementById('editNoticeForm');

      form.innerHTML = '<div class="text-center" style="padding: 30px; color: var(--text-muted);">Loading...</div>';
      openModal('editNoticeModal');

      try {
        const response = await fetch(`/admin/get-notice/${noticeId}`);
        const data = await response.json();

        if (data.error) throw new Error(data.error);

        document.getElementById('editNoticeModalForm').action = `/admin/edit-notice/${noticeId}`;

        form.innerHTML = `
          <div class="form-group mb-2">
            <label>Notice Title *</label>
            <input type="text" name="title" value="${escHtml(data.title)}" required>
          </div>
          <div class="form-group">
            <label>Message *</label>
            <textarea name="message" rows="5" required>${escHtml(data.message)}</textarea>
          </div>
        `;

      } catch (err) {
        form.innerHTML = `<div class="alert alert-error">Error: ${err.message}</div>`;
      }
    });
  });

  // ============================================================
  // DELETE NOTICE - Confirmation
  // ============================================================

  document.querySelectorAll('[data-delete-notice]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const noticeId = this.dataset.deleteNotice;

      if (confirm('Delete this notice? This cannot be undone.')) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/admin/delete-notice/${noticeId}`;
        document.body.appendChild(form);
        form.submit();
      }
    });
  });

  // ============================================================
  // AUTO-DISMISS FLASH MESSAGES
  // ============================================================

  document.querySelectorAll('.alert').forEach(function (alert) {
    setTimeout(function () {
      alert.style.transition = 'all 0.4s ease';
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-10px)';
      setTimeout(() => alert.remove(), 400);
    }, 5000);
  });

  // ============================================================
  // FORM VALIDATION - Add basic validation feedback
  // ============================================================

  document.querySelectorAll('form').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Processing...';
        // Re-enable after 5s in case of error
        setTimeout(() => {
          submitBtn.disabled = false;
          submitBtn.textContent = submitBtn.dataset.originalText || 'Submit';
        }, 5000);
      }
    });
  });

  // ============================================================
  // UTILITY: HTML escape to prevent XSS
  // ============================================================

  function escHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // ============================================================
  // ANIMATE STATS COUNTER
  // ============================================================

  document.querySelectorAll('[data-count]').forEach(function (el) {
    const target = parseFloat(el.dataset.count);
    const isAmount = el.dataset.type === 'amount';
    const duration = 1000;
    const startTime = performance.now();

    function update(currentTime) {
      const progress = Math.min((currentTime - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const value = target * eased;

      if (isAmount) {
        el.textContent = '₹' + value.toLocaleString('en-IN', { maximumFractionDigits: 0 });
      } else {
        el.textContent = Math.floor(value);
      }

      if (progress < 1) requestAnimationFrame(update);
    }

    requestAnimationFrame(update);
  });

  // ============================================================
  // SMOOTH SCROLL TO SECTIONS (for anchor links)
  // ============================================================

  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

});
