// All content and links work without JavaScript.
const yearEl = document.getElementById('year');
if (yearEl) yearEl.textContent = new Date().getFullYear();

// Recompute from all sections, so both upward and downward scrolling are stable.
const links = Array.from(document.querySelectorAll('.nav a[href^="#"]'));
const sections = links
  .map((link) => document.getElementById(link.hash.slice(1)))
  .filter(Boolean);
let scheduled = false;

const updateActiveSection = () => {
  const topbar = document.querySelector('.topbar');
  const offset = (topbar ? topbar.getBoundingClientRect().height : 0) + 40;
  let active = sections[0];
  sections.forEach((section) => {
    if (section.getBoundingClientRect().top <= offset) active = section;
  });
  if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 2) {
    active = sections[sections.length - 1];
  }
  links.forEach((link) => {
    const selected = Boolean(active && link.hash === `#${active.id}`);
    link.classList.toggle('active', selected);
    if (selected) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  });
  scheduled = false;
};

const scheduleUpdate = () => {
  if (!scheduled) {
    scheduled = true;
    window.requestAnimationFrame(updateActiveSection);
  }
};

if (sections.length) {
  window.addEventListener('scroll', scheduleUpdate, { passive: true });
  window.addEventListener('resize', scheduleUpdate);
  window.addEventListener('load', scheduleUpdate);
  updateActiveSection();
}
