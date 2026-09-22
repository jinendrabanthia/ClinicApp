"""
inject_enhancements.py — Inject CSS + JS enhancements into all HTML pages.
Run once. Safe to re-run (idempotent with marker comment).
"""
import glob, re

HTML_FILES = glob.glob(r"c:\jb\clinic app\frontend\static\*.html")

# ── CSS link to inject (just before </head>) ─────────────────────────────────
CSS_INJECT = """  <!-- TriageAID Enhancements CSS -->
  <link rel="stylesheet" href="/enhance.css" />
"""

# ── Scroll progress + Intersection Observer + credit footer JS ─────────────
JS_INJECT = """<!-- TriageAID Enhancement Scripts -->
<div id="scrollProgress"></div>
<script>
(function(){
  /* Scroll progress bar */
  var prog = document.getElementById('scrollProgress');
  if(prog){
    window.addEventListener('scroll', function(){
      var h = document.documentElement;
      var pct = (h.scrollTop / (h.scrollHeight - h.clientHeight)) * 100;
      prog.style.width = Math.min(100, pct) + '%';
    }, {passive:true});
  }

  /* Intersection Observer — reveal on scroll */
  var io = new IntersectionObserver(function(entries){
    entries.forEach(function(e){
      if(e.isIntersecting){
        e.target.classList.add('visible');
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

  /* Mark elements for reveal */
  var selectors = [
    '.step-card', '.level-item', '.feature-item', '.ai-card',
    '.trust-item', '.stat-box', '.photo-band-content',
    '.instruments-content', 'section h2', '.section-title',
    '.result-card', '.info-card', '.row-card', '.patient-row'
  ];
  selectors.forEach(function(sel){
    document.querySelectorAll(sel).forEach(function(el, i){
      if(!el.classList.contains('reveal') && !el.classList.contains('reveal-left')){
        el.classList.add('reveal');
        el.classList.add('delay-' + ((i % 6) + 1));
        io.observe(el);
      }
    });
  });

  /* Animate number counting for stat boxes */
  function animateCount(el, target, duration){
    var start = 0;
    var step = target / (duration / 16);
    function tick(){
      start += step;
      if(start >= target){ el.textContent = target; return; }
      el.textContent = Math.round(start);
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }
  var countIO = new IntersectionObserver(function(entries){
    entries.forEach(function(e){
      if(e.isIntersecting){
        var num = e.target.querySelector('.stat-num');
        if(num){
          var val = parseInt(num.textContent);
          if(!isNaN(val) && val > 0){ animateCount(num, val, 800); }
        }
        countIO.unobserve(e.target);
      }
    });
  }, {threshold: 0.5});
  document.querySelectorAll('.stat-box').forEach(function(b){ countIO.observe(b); });

  /* Add ripple on primary buttons */
  document.querySelectorAll('.btn-nav-solid, .cta-patient, .btn-white').forEach(function(btn){
    btn.classList.add('ripple-btn');
    btn.addEventListener('click', function(e){
      var r = document.createElement('span');
      r.style.cssText = 'position:absolute;border-radius:50%;background:rgba(255,255,255,0.4);transform:scale(0);animation:ripple-anim 0.5s linear;pointer-events:none;';
      var bRect = btn.getBoundingClientRect();
      var size = Math.max(bRect.width, bRect.height);
      r.style.width = r.style.height = size + 'px';
      r.style.left = (e.clientX - bRect.left - size/2) + 'px';
      r.style.top  = (e.clientY - bRect.top  - size/2) + 'px';
      btn.appendChild(r);
      setTimeout(function(){ r.remove(); }, 500);
    });
  });

  /* Wobble logo on click */
  document.querySelectorAll('.logo-mark, .logo-icon').forEach(function(el){
    el.addEventListener('click', function(){
      el.style.animation = 'none';
      setTimeout(function(){ el.style.animation = 'wobble 0.6s ease'; }, 10);
    });
  });

  /* Particle trail on hero CTA hover */
  document.querySelectorAll('.cta-patient').forEach(function(btn){
    btn.addEventListener('mousemove', function(e){
      if(Math.random() > 0.7){
        var p = document.createElement('span');
        p.style.cssText = [
          'position:fixed',
          'pointer-events:none',
          'border-radius:50%',
          'background:rgba(99,102,241,0.5)',
          'width:6px', 'height:6px',
          'left:' + e.clientX + 'px',
          'top:' + e.clientY + 'px',
          'animation:trailFade 0.6s ease-out forwards',
          'z-index:9999'
        ].join(';');
        document.body.appendChild(p);
        setTimeout(function(){ p.remove(); }, 600);
      }
    });
  });
})();
</script>
<style>
@keyframes ripple-anim {
  to { transform: scale(4); opacity: 0; }
}
@keyframes trailFade {
  0%   { opacity: 0.8; transform: scale(1); }
  100% { opacity: 0;   transform: scale(2.5) translateY(-12px); }
}
</style>
"""

# ── Credits footer HTML ──────────────────────────────────────────────────────
CREDITS_HTML = """
<div class="credits-footer">
  made by <strong>JINENDRA BANTHIA</strong> &nbsp;·&nbsp;
  <a href="tel:9124483008">📞 9124483008</a> &nbsp;·&nbsp;
  <a href="mailto:jinendra.banthia.iter@gmail.com">✉️ jinendra.banthia.iter@gmail.com</a>
</div>
"""

MARKER = "<!-- TriageAID Enhancements CSS -->"

processed = 0
skipped = 0

for path in HTML_FILES:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    if MARKER in content:
        print(f"SKIP (already enhanced): {path}")
        skipped += 1
        continue

    # 1. Inject CSS before </head>
    content = content.replace('</head>', CSS_INJECT + '</head>', 1)

    # 2. Inject scroll progress + JS right after <body>
    content = re.sub(r'(<body[^>]*>)', r'\1\n' + JS_INJECT, content, count=1)

    # 3. Inject credits footer before </body>
    content = content.replace('</body>', CREDITS_HTML + '\n</body>', 1)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"ENHANCED: {path}")
    processed += 1

print(f"\nDone! {processed} enhanced, {skipped} skipped.")
