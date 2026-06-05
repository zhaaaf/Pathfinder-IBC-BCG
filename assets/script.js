// =============================================
// PATHFINDER — NAVIGATION & INTERACTIONS
// =============================================

function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => {
    s.classList.remove('active');
    s.style.display = 'none';
    s.style.opacity = '0';
  });
  const target = document.getElementById(id);
  if (!target) return;
  target.style.display = 'block';
  requestAnimationFrame(() => {
    target.style.opacity = '1';
    target.classList.add('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
  localStorage.setItem('pathfinder_screen', id);
}

// Slider realtime calculation
function initSlider() {
  const slider = document.getElementById('hours-slider');
  const display = document.getElementById('hours-display');
  if (!slider) return;
  function update() {
    const h = parseInt(slider.value);
    display.textContent = h + ' jam / hari';
    document.getElementById('fast-days').textContent = Math.ceil(68 / h) + ' hari';
    document.getElementById('mid-days').textContent = Math.ceil(102 / h) + ' hari';
    document.getElementById('full-days').textContent = Math.ceil(156 / h) + ' hari';
    localStorage.setItem('pathfinder_hours', h);
  }
  slider.addEventListener('input', update);
  const saved = localStorage.getItem('pathfinder_hours');
  if (saved) { slider.value = saved; }
  update();
}

// Package selection
function selectPackage(pkg) {
  document.querySelectorAll('.package-card').forEach(c => c.classList.remove('selected'));
  const card = document.getElementById('pkg-' + pkg);
  if (card) card.classList.add('selected');
  localStorage.setItem('pathfinder_package', pkg);
}

// Profession selection
function selectProfession(prof) {
  document.querySelectorAll('.profession-card').forEach(c => c.classList.remove('selected'));
  const card = document.getElementById('prof-' + prof);
  if (card) card.classList.add('selected');
  localStorage.setItem('pathfinder_profession', prof);
}

// Add custom profession chip
function addProfession() {
  const input = document.getElementById('custom-prof-input');
  if (!input || !input.value.trim()) return;
  const val = input.value.trim();
  const container = document.getElementById('custom-prof-chips');
  const chip = document.createElement('span');
  chip.className = 'chip chip-blue';
  chip.style.margin = '4px';
  chip.innerHTML = val + ' <span onclick="this.parentElement.remove()" style="cursor:pointer;margin-left:4px;font-weight:700;">×</span>';
  container.appendChild(chip);
  input.value = '';
}

// AI scanning animation
function runAIScanning() {
  const btn = document.getElementById('analyze-btn');
  if (btn) {
    btn.disabled = true;
    btn.textContent = 'Menganalisis...';
  }
  let dots = 0;
  const scanBar = document.getElementById('scan-progress');
  if (scanBar) {
    scanBar.style.width = '0%';
    const interval = setInterval(() => {
      dots += 2;
      if (scanBar) scanBar.style.width = Math.min(dots, 98) + '%';
      if (dots >= 98) {
        clearInterval(interval);
        setTimeout(() => showScreen('screen-3'), 400);
      }
    }, 30);
  } else {
    setTimeout(() => showScreen('screen-3'), 800);
  }
}

// Initialization is called directly from app.py after DOM is ready
