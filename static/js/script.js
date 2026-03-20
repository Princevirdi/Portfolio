const root = document.documentElement;
const toggle = document.querySelector('.theme-toggle');

const applyTheme = (theme) => {
  root.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
};

const saved = localStorage.getItem('theme');
if (saved === 'light' || saved === 'dark') {
  applyTheme(saved);
}

toggle?.addEventListener('click', () => {
  const next = root.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
  applyTheme(next);
});

