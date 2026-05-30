// Slug availability check
const slugInput = document.getElementById('slugInput');
const slugStatus = document.getElementById('slugStatus');
let slugTimer = null;

if (slugInput) {
  slugInput.addEventListener('input', () => {
    const val = slugInput.value.trim().toLowerCase();
    slugInput.value = val.replace(/[^a-z0-9-]/g, '');
    clearTimeout(slugTimer);
    if (!val || val.length < 3) {
      slugStatus.textContent = '';
      return;
    }
    slugStatus.textContent = 'جاري التحقق...';
    slugStatus.className = 'slug-status slug-check';
    slugTimer = setTimeout(async () => {
      try {
        const res = await fetch(`/api/check-slug?slug=${encodeURIComponent(val)}`);
        const data = await res.json();
        if (data.available) {
          slugStatus.textContent = '✓ متاح';
          slugStatus.className = 'slug-status slug-ok';
        } else {
          slugStatus.textContent = '✗ مستخدم بالفعل';
          slugStatus.className = 'slug-status slug-taken';
        }
      } catch {
        slugStatus.textContent = '';
      }
    }, 500);
  });

  // Auto-suggest slug from English name
  const nameEnInput = document.getElementById('nameEnInput');
  if (nameEnInput) {
    nameEnInput.addEventListener('input', () => {
      if (slugInput.dataset.edited) return;
      const suggested = nameEnInput.value.trim().toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-+|-+$/g, '')
        .slice(0, 50);
      if (suggested.length >= 3) slugInput.value = suggested;
    });
    slugInput.addEventListener('input', () => { slugInput.dataset.edited = '1'; });
  }
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});
