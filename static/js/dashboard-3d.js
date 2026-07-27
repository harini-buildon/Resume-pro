/**
 * static/js/dashboard-3d.js
 * Dashboard visual animation script (score count-up and progress bars).
 */
document.addEventListener('DOMContentLoaded', () => {

  /* ── Stat counter animation ── */
  document.querySelectorAll('.stat-value-sm').forEach(el => {
    const target = parseInt(el.textContent, 10);
    if (isNaN(target) || target === 0) return;
    let start = 0;
    const step = Math.ceil(target / 20);
    const timer = setInterval(() => {
      start = Math.min(start + step, target);
      el.textContent = start;
      if (start >= target) clearInterval(timer);
    }, 40);
  });

  /* ── Animate ATS score count-up ── */
  const scoreEl = document.getElementById('ats-score-number');
  if (scoreEl) {
    const final = parseInt(scoreEl.textContent, 10);
    let cur = 0;
    const stepScore = Math.ceil(final / 40);
    const t = setInterval(() => {
      cur = Math.min(cur + stepScore, final);
      scoreEl.textContent = cur;
      if (cur >= final) clearInterval(t);
    }, 25);
  }

  /* ── Progress bars animate on scroll ── */
  const bars = document.querySelectorAll('.breakdown-progress .progress-bar');
  if ('IntersectionObserver' in window && bars.length > 0) {
    const obs = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const bar = entry.target;
          const w = bar.style.width;
          bar.style.width = '0%';
          requestAnimationFrame(() => { bar.style.width = w; });
          obs.unobserve(bar);
        }
      });
    }, { threshold: 0.2 });
    bars.forEach(b => obs.observe(b));
  }

});
