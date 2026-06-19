/* ─── GOD'S HOUSE OF REST — shared interactions ─── */
(function () {
  'use strict';

  /* ── 1 · Scroll progress bar ── */
  if (!document.getElementById('scrollProgressBar')) {
    var bar = document.createElement('div');
    bar.className = 'scroll-progress';
    bar.id = 'scrollProgressBar';
    bar.setAttribute('aria-hidden', 'true');
    (document.body || document.documentElement).appendChild(bar);

    var onScroll = function () {
      var h = document.documentElement;
      var scrolled = window.pageYOffset || h.scrollTop || document.body.scrollTop || 0;
      var max = h.scrollHeight - h.clientHeight;
      var p = max > 0 ? scrolled / max : 0;
      bar.style.width = (Math.max(0, Math.min(1, p)) * 100).toFixed(2) + '%';
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
    onScroll();
  }

  /* ── 2 · Magnetic buttons (primary CTAs gently follow the cursor) ── */
  var isTouch = window.matchMedia('(hover:none) and (pointer:coarse)').matches;
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!isTouch && !reduced) {
    document.querySelectorAll('.btn-primary, .nav-cta').forEach(function (b) {
      if (b.dataset.magnetic) return;
      b.dataset.magnetic = '1';
      b.addEventListener('mousemove', function (e) {
        var r = b.getBoundingClientRect();
        var mx = e.clientX - (r.left + r.width / 2);
        var my = e.clientY - (r.top + r.height / 2);
        b.style.transform = 'translate(' + (mx * 0.25).toFixed(1) + 'px,' + (my * 0.3 - 2).toFixed(1) + 'px)';
      });
      b.addEventListener('mouseleave', function () { b.style.transform = ''; });
    });
  }

  /* ── 3 · Hero photo parallax (homepage split hero) ── */
  if (!isTouch && !reduced) {
    var slides = document.querySelector('.hero-media .hero-slides');
    if (slides) {
      slides.style.willChange = 'transform';
      slides.style.transform = 'scale(1.06)';
      window.addEventListener('mousemove', function (e) {
        var dx = (e.clientX - window.innerWidth / 2) / (window.innerWidth / 2);
        var dy = (e.clientY - window.innerHeight / 2) / (window.innerHeight / 2);
        slides.style.transform = 'scale(1.06) translate(' + (dx * -10).toFixed(1) + 'px,' + (dy * -8).toFixed(1) + 'px)';
      }, { passive: true });
    }
  }

  /* ── 4 · Card 3D tilt on hover ── */
  if (!isTouch && !reduced) {
    var TILT = '.inner-card, .blog-card, .ministry-card, .sermon-card, .event-card, .news-card, .value-card, .team-card, .recurring-card';
    document.querySelectorAll(TILT).forEach(function (card) {
      if (card.dataset.tilt) return;
      card.dataset.tilt = '1';
      card.addEventListener('mousemove', function (e) {
        var r = card.getBoundingClientRect();
        var px = (e.clientX - r.left) / r.width - 0.5;
        var py = (e.clientY - r.top) / r.height - 0.5;
        card.style.transform = 'perspective(820px) rotateX(' + (py * -6).toFixed(2) + 'deg) rotateY(' + (px * 6).toFixed(2) + 'deg) translateY(-6px)';
      });
      card.addEventListener('mouseleave', function () { card.style.transform = ''; });
    });
  }

  /* ── 5 · Title gradient sheen on scroll-in ── */
  if (!reduced && 'IntersectionObserver' in window) {
    var sheenObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var el = en.target;
        sheenObs.unobserve(el);
        el.classList.add('sheen');
        el.addEventListener('animationend', function () { el.classList.remove('sheen'); }, { once: true });
      });
    }, { threshold: 0.6 });
    document.querySelectorAll('.section-title, .page-hero h1').forEach(function (t) { sheenObs.observe(t); });
  }

  /* ── 6 · Gold sparkle burst on form submit ── */
  function fireConfetti(x, y) {
    var c = document.createElement('canvas');
    c.style.cssText = 'position:fixed;inset:0;width:100%;height:100%;pointer-events:none;z-index:9999';
    c.width = window.innerWidth; c.height = window.innerHeight;
    document.body.appendChild(c);
    var ctx = c.getContext('2d');
    var colors = ['#C8860A', '#D4A843', '#FFE08A', '#F5F0E8'];
    var parts = [];
    for (var i = 0; i < 80; i++) {
      var a = Math.random() * Math.PI * 2, sp = 4 + Math.random() * 8;
      parts.push({ x: x, y: y, vx: Math.cos(a) * sp, vy: Math.sin(a) * sp - 5, size: 3 + Math.random() * 4, col: colors[i % colors.length], rot: Math.random() * 6.28, vr: (Math.random() - 0.5) * 0.35 });
    }
    var start = null, dur = 1400;
    function frame(t) {
      if (!start) start = t;
      var el = t - start, life = 1 - el / dur;
      ctx.clearRect(0, 0, c.width, c.height);
      parts.forEach(function (p) {
        p.vy += 0.2; p.x += p.vx; p.y += p.vy; p.rot += p.vr;
        ctx.save(); ctx.globalAlpha = Math.max(0, life); ctx.translate(p.x, p.y); ctx.rotate(p.rot);
        ctx.fillStyle = p.col; ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 1.6); ctx.restore();
      });
      if (el < dur) requestAnimationFrame(frame); else c.remove();
    }
    requestAnimationFrame(frame);
  }
  if (!reduced) {
    document.addEventListener('submit', function (e) {
      var r = e.submitter ? e.submitter.getBoundingClientRect() : null;
      fireConfetti(r ? r.left + r.width / 2 : window.innerWidth / 2, r ? r.top : window.innerHeight / 2);
    });
  }
})();
