/**
 * stt.js — Shared Speech-to-Text Utility for RapidAID / RapidAID
 * Supports: en-IN (English India) and hi-IN (Hindi India)
 * Uses: Web Speech API (webkitSpeechRecognition / SpeechRecognition)
 * Usage: Call STT.init() on page load, then STT.toggle(micBtn, targetId, lang)
 */

const STT = (() => {
  let recognition = null;
  let activeMic = null;
  let isListening = false;

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  function isSupported() {
    return !!SpeechRecognition;
  }

  function getLang(btn) {
    // Find the nearest language toggle sibling
    const wrap = btn.closest('.mic-wrap') || btn.parentElement;
    const toggle = wrap ? wrap.querySelector('.lang-toggle') : null;
    if (!toggle) return 'en-IN';
    return toggle.dataset.lang === 'hi' ? 'hi-IN' : 'en-IN';
  }

  function setMicListening(btn, listening) {
    btn.classList.toggle('mic-listening', listening);
    btn.title = listening ? 'Tap to stop' : 'Tap to speak';
    isListening = listening;
    activeMic = listening ? btn : null;
  }

  function stop() {
    if (recognition) { try { recognition.stop(); } catch(e){} }
    if (activeMic) setMicListening(activeMic, false);
    isListening = false;
    activeMic = null;
  }

  function toggle(btn, targetId) {
    if (!isSupported()) {
      showUnsupportedMsg();
      return;
    }

    // If already listening on some mic, always stop first
    if (isListening) {
      stop();
      if (activeMic === btn || !btn) return;
    }

    const target = document.getElementById(targetId);
    if (!target) return;

    const lang = getLang(btn);
    recognition = new SpeechRecognition();
    recognition.lang = lang;
    recognition.continuous = true;
    recognition.interimResults = true;

    let baseText = target.value || '';
    let interimSpan = '';

    recognition.onstart = () => setMicListening(btn, true);

    recognition.onresult = (e) => {
      let interim = '';
      let final = '';
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const t = e.results[i][0].transcript;
        if (e.results[i].isFinal) final += t + ' ';
        else interim += t;
      }
      if (final) baseText += final;
      target.value = baseText + interim;
      // Auto-resize textareas
      if (target.tagName === 'TEXTAREA') {
        target.style.height = 'auto';
        target.style.height = target.scrollHeight + 'px';
      }
      target.dispatchEvent(new Event('input'));
    };

    recognition.onerror = (e) => {
      console.warn('STT error:', e.error);
      stop();
    };

    recognition.onend = () => {
      if (isListening) {
        // Auto-restart for continuous listening
        try { recognition.start(); } catch(e) { stop(); }
      }
    };

    try { recognition.start(); } catch(e) { stop(); }
  }

  function toggleLang(btn) {
    const isHi = btn.dataset.lang !== 'hi';
    btn.dataset.lang = isHi ? 'hi' : 'en';
    btn.textContent = isHi ? 'हि' : 'En';
    btn.title = isHi ? 'हिंदी चुना है — Hindi selected' : 'English selected';
    // Stop any active recognition so language change takes effect on next start
    if (isListening) stop();
  }

  function showUnsupportedMsg() {
    const existing = document.getElementById('stt-unsupported');
    if (existing) return;
    const msg = document.createElement('div');
    msg.id = 'stt-unsupported';
    msg.style.cssText = 'position:fixed;bottom:20px;left:50%;transform:translateX(-50%);z-index:9999;background:#1e3a5f;color:#fff;padding:12px 22px;border-radius:12px;font-size:13px;font-weight:600;box-shadow:0 8px 24px rgba(0,0,0,.3);';
    msg.textContent = '🎤 Speech recognition requires Chrome or Edge browser.';
    document.body.appendChild(msg);
    setTimeout(() => msg.remove(), 4000);
  }

  return { toggle, toggleLang, stop, isSupported };
})();

/**
 * Helper: render a mic button + language toggle pair
 * Usage: insertMicButton(inputId, containerSelector)
 * OR: call STT.toggle(btn, 'inputId') directly from HTML onclick
 */
function renderMicBtn(targetId, color = '#2563eb') {
  return `
    <div class="mic-wrap" role="group" aria-label="Voice input controls">
      <button type="button" class="lang-toggle" data-lang="en"
        onclick="STT.toggleLang(this)" title="English selected">En</button>
      <button type="button" class="mic-btn" id="mic-${targetId}"
        onclick="STT.toggle(this,'${targetId}')" title="Tap to speak">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
          <rect x="9" y="2" width="6" height="13" rx="3"/>
          <path d="M5 10a7 7 0 0014 0"/>
          <line x1="12" y1="19" x2="12" y2="23"/>
          <line x1="8" y1="23" x2="16" y2="23"/>
        </svg>
      </button>
    </div>`;
}

/* ── Global STT styles (injected once) ── */
(function injectSTTStyles() {
  if (document.getElementById('stt-styles')) return;
  const s = document.createElement('style');
  s.id = 'stt-styles';
  s.textContent = `
    .input-mic-wrap { position: relative; }
    .input-mic-wrap input,
    .input-mic-wrap textarea { padding-right: 90px !important; }

    .mic-wrap {
      position: absolute; right: 8px; top: 50%; transform: translateY(-50%);
      display: flex; align-items: center; gap: 4px; z-index: 5;
    }
    .input-mic-wrap textarea ~ .mic-wrap,
    .mic-wrap.top { top: 12px; transform: none; }

    .lang-toggle {
      height: 26px; padding: 0 8px;
      background: #e0e7ff; border: 1.5px solid #a5b4fc;
      border-radius: 6px; font-size: 11px; font-weight: 700;
      color: #4338ca; cursor: pointer; transition: all .2s;
      white-space: nowrap;
    }
    .lang-toggle:hover { background: #c7d2fe; }
    .lang-toggle[data-lang="hi"] { background: #fef3c7; border-color: #fcd34d; color: #92400e; }

    .mic-btn {
      width: 32px; height: 32px; border-radius: 50%;
      background: #eff6ff; border: 1.5px solid #bfdbfe;
      display: flex; align-items: center; justify-content: center;
      cursor: pointer; transition: all .2s; color: #2563eb;
      flex-shrink: 0;
    }
    .mic-btn svg { width: 15px; height: 15px; }
    .mic-btn:hover { background: #dbeafe; border-color: #2563eb; }
    .mic-btn.mic-listening {
      background: #fee2e2; border-color: #ef4444; color: #ef4444;
      animation: mic-pulse 1s ease-in-out infinite;
    }
    @keyframes mic-pulse {
      0%, 100% { box-shadow: 0 0 0 0 rgba(239,68,68,0.4); transform: scale(1); }
      50%       { box-shadow: 0 0 0 8px rgba(239,68,68,0); transform: scale(1.08); }
    }

    /* Dark-theme overrides (used in doctor-dashboard modals) */
    .dark-mic .lang-toggle { background: rgba(255,255,255,0.12); border-color: rgba(255,255,255,0.2); color: #e2e8f0; }
    .dark-mic .mic-btn { background: rgba(255,255,255,0.08); border-color: rgba(255,255,255,0.15); color: #93c5fd; }
    .dark-mic .mic-btn:hover { background: rgba(255,255,255,0.15); }
  `;
  document.head.appendChild(s);
})();

