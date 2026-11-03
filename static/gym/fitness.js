'use strict';
const menu = document.querySelector('.fitness-menu');
const links = document.getElementById('site-links');
function setMenu(open) {
  links?.classList.toggle('open', open);
  menu?.setAttribute('aria-expanded', String(open));
}
menu?.addEventListener('click', () => setMenu(!links.classList.contains('open')));
links?.querySelectorAll('a').forEach(link => link.addEventListener('click', () => setMenu(false)));
document.addEventListener('keydown', e => { if (e.key === 'Escape') setMenu(false); });
document.addEventListener('click', e => {
  if (links?.classList.contains('open') && !links.contains(e.target) && !menu.contains(e.target)) setMenu(false);
});

/* Active section in the nav. */
const navLinks = [...(links?.querySelectorAll('a[href^="#"]') || [])];
const sections = navLinks.map(a => document.querySelector(a.getAttribute('href'))).filter(Boolean);
if ('IntersectionObserver' in window && sections.length) {
  const spy = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      navLinks.forEach(a => a.classList.toggle('active', a.getAttribute('href') === `#${entry.target.id}`));
    });
  }, {rootMargin: '-45% 0px -50% 0px'});
  sections.forEach(section => spy.observe(section));
}

/* Gentle reveal on first view. Content stays visible without JS or with reduced motion. */
const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const revealables = document.querySelectorAll('.reveal');
if (!reduce && 'IntersectionObserver' in window) {
  document.documentElement.classList.add('can-reveal');
  const reveal = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-visible');
      reveal.unobserve(entry.target);
    });
  }, {rootMargin: '0px 0px -8% 0px', threshold: 0.08});
  revealables.forEach(el => reveal.observe(el));
}
