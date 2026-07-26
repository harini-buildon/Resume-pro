/**
 * static/js/dashboard-3d.js
 * Interactive 3-D mouse-tilt effect for dashboard cards.
 */
document.addEventListener('DOMContentLoaded', () => {

  /* ── Mouse-tracking 3-D card tilt ── */
  const TILT_MAX = 10; // degrees

  document.querySelectorAll('.glass-card').forEach(card => {
    card.addEventListener('mousemove', e => {
      const rect = card.getBoundingClientRect();
      const cx   = rect.left + rect.width  / 2;
      const cy   = rect.top  + rect.height / 2;
      const dx   = (e.clientX - cx) / (rect.width  / 2);
      const dy   = (e.clientY - cy) / (rect.height / 2);
      const rx   =  dy * TILT_MAX;   // rotateX (vertical mouse)
      const ry   = -dx * TILT_MAX;   // rotateY (horizontal mouse)
      card.style.transform = `perspective(800px) rotateX(${rx}deg) rotateY(${ry}deg) translateY(-6px) scale(1.02)`;
      card.style.boxShadow = `${ry * 2}px ${-rx * 2}px 40px rgba(30,58,138,.22)`;
    });

    card.addEventListener('mouseleave', () => {
      card.style.transform = '';
      card.style.boxShadow = '';
    });
  });

  /* ── Floating counter animation ── */
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

  /* ── Animate ATS number count-up ── */
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
  if ('IntersectionObserver' in window) {
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
