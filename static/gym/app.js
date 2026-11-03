'use strict';
/* Mobile drawer: scrim, Escape, close button, focus return. */
const toggle = document.querySelector('.menu-toggle');
const sidebar = document.querySelector('.sidebar');
const scrim = document.querySelector('.sidebar-scrim');
const closeButton = document.querySelector('.sidebar-close');
const mobileQuery = window.matchMedia('(max-width: 720px)');

function setDrawer(open, {returnFocus = true} = {}) {
  if (!sidebar || !toggle) return;
  sidebar.classList.toggle('open', open);
  document.body.classList.toggle('drawer-open', open);
  toggle.setAttribute('aria-expanded', String(open));
  if (scrim) scrim.hidden = !open;
  if (open) {
    sidebar.querySelector('nav a[aria-current]')?.focus({preventScroll: true});
  } else if (returnFocus && sidebar.contains(document.activeElement)) {
    toggle.focus({preventScroll: true});
  }
}
toggle?.addEventListener('click', () => setDrawer(!sidebar.classList.contains('open')));
closeButton?.addEventListener('click', () => setDrawer(false));
scrim?.addEventListener('click', () => setDrawer(false));
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && sidebar?.classList.contains('open')) setDrawer(false);
});
mobileQuery.addEventListener?.('change', e => { if (!e.matches) setDrawer(false, {returnFocus: false}); });

/* Messages fade out on their own after a while, except errors. */
document.querySelectorAll('.message:not(.error)').forEach(message => {
  setTimeout(() => message.classList.add('is-leaving'), 6000);
  message.addEventListener('transitionend', () => { if (message.classList.contains('is-leaving')) message.remove(); });
});

document.querySelector('[data-print]')?.addEventListener('click', () => window.print());

/* Live member lookup on the attendance page. */
const search = document.getElementById('member-search');
const results = document.getElementById('lookup-results');
let timer, controller;
function lookupNote(text) {
  const p = document.createElement('p'); p.className = 'lookup-note'; p.textContent = text; results.replaceChildren(p);
}
search?.addEventListener('input', () => {
  clearTimeout(timer); controller?.abort(); results.replaceChildren();
  const q = search.value.trim();
  if (q.length < 2) return;
  results.setAttribute('aria-busy', 'true');
  timer = setTimeout(async () => {
    controller = new AbortController();
    try {
      const response = await fetch(`${search.dataset.lookupUrl}?q=${encodeURIComponent(q)}`, {signal: controller.signal, headers: {'Accept': 'application/json'}});
      if (!response.ok || !response.headers.get('content-type')?.includes('application/json')) throw new Error('unavailable');
      const data = await response.json();
      if (search.value.trim() !== q) return;
      results.replaceChildren();
      if (!data.results.length) lookupNote('No se encontraron socios con ese nombre o código.');
      data.results.forEach(member => {
        const button = document.createElement('button'); button.type = 'button';
        const code = document.createElement('span'); code.className = 'lookup-code'; code.textContent = member.code;
        const name = document.createElement('span'); name.textContent = member.name;
        button.append(code, name);
        if (!member.active) { const tag = document.createElement('span'); tag.className = 'badge muted'; tag.textContent = 'Inactivo'; button.append(tag); }
        button.addEventListener('click', () => {
          const field = document.getElementById('id_code');
          field.value = member.code; field.focus(); results.replaceChildren(); search.value = '';
        });
        results.append(button);
      });
    } catch (error) {
      if (error.name !== 'AbortError') lookupNote('No se pudo buscar. Verifica tu sesión o escribe el código directamente.');
    } finally {
      results.removeAttribute('aria-busy');
    }
  }, 220);
});
