/* Step guide: the step in the middle of the screen becomes active; its screenshot glides in on the sticky stage. */
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
document.querySelectorAll('[data-steps]').forEach((root) => {
  const steps = [...root.querySelectorAll('[data-step]')];
  const imgs = [...root.querySelectorAll('[data-step-img]')];
  const btns = [...root.querySelectorAll('[data-step-go]')];
  const bar = root.querySelector('.steps__bar b');
  let cur = 0;
  const set = (i) => {
    if (i === cur) return;
    const dir = i > cur ? 1 : -1;
    const from = imgs.find((im) => +im.dataset.stepImg === cur);
    const to = imgs.find((im) => +im.dataset.stepImg === i);
    cur = i;
    steps.forEach((s, k) => s.classList.toggle('is-active', k === i));
    btns.forEach((b, k) => b.setAttribute('aria-current', String(k === i)));
    if (bar) bar.style.width = `${((i + 1) / steps.length) * 100}%`;
    imgs.forEach((im) => im.classList.toggle('is-active', im === to));
    if (reduce || !to) return;
    from?.animate([{ opacity: 1, transform: 'none' }, { opacity: 0, transform: `translateY(${-dir * 24}px) scale(0.97)` }], { duration: 380, easing: 'cubic-bezier(0.65, 0, 0.35, 1)' });
    to.animate([{ opacity: 0, transform: `translateY(${dir * 32}px) scale(0.97)` }, { opacity: 1, transform: 'none' }], { duration: 560, easing: 'cubic-bezier(0.22, 1, 0.36, 1)', delay: 60, fill: 'backwards' });
  };
  const io = new IntersectionObserver((entries) => entries.forEach((e) => { if (e.isIntersecting) set(+e.target.dataset.step); }), { rootMargin: '-45% 0px -50% 0px' });
  steps.forEach((s) => io.observe(s));
  btns.forEach((b) => b.addEventListener('click', () => steps[+b.dataset.stepGo].scrollIntoView({ block: 'center', behavior: reduce ? 'auto' : 'smooth' })));
  if (bar) bar.style.width = `${100 / steps.length}%`;
});
