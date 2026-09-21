/* Progressive enhancement: content stays readable without JavaScript. */
(() => {
  // Native grouping plus a fallback for browsers without details[name] support.
  document.querySelectorAll('.faq-list details').forEach((detail) => {
    detail.addEventListener('toggle', () => {
      if (!detail.open) return;
      detail.closest('.faq-list').querySelectorAll('details[open]').forEach((other) => {
        if (other !== detail) other.open = false;
      });
    });
  });
  // Preview forms validate in the browser without sending or storing data.
  document.querySelectorAll('[data-preview-form]').forEach((form) => {
    const submit = form.querySelector('button[type="submit"]');
    const status = form.querySelector('.form-status');
    if (!submit || !status) return;
    submit.disabled = false;
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      if (!form.reportValidity()) return;
      status.textContent = 'This is a preview. Your request has not been sent.';
      status.hidden = false;
    });
  });
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  if (motion.matches || !('IntersectionObserver' in window)) return;
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(({ isIntersecting, target }) => {
      if (!isIntersecting) return;
      target.classList.add('is-visible');
      observer.unobserve(target);
    });
  }, { rootMargin: '0px 0px -24px 0px', threshold: 0.05 });
  const elements = document.querySelectorAll('main > .section > .container, main > .cta-panel > .container');
  elements.forEach((element) => {
    // Do not animate anything already visible, especially above-the-fold content.
    if (element.getBoundingClientRect().top < innerHeight) return;
    element.classList.add('reveal-ready');
    observer.observe(element);
  });
  const revealHash = () => {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
    const target = document.getElementById(id);
    target?.closest('.reveal-ready')?.classList.add('is-visible');
    target?.querySelector('.reveal-ready')?.classList.add('is-visible');
  };
  addEventListener('hashchange', revealHash);
  revealHash();
  motion.addEventListener?.('change', ({ matches }) => {
    if (!matches) return;
    observer.disconnect();
    elements.forEach((element) => element.classList.add('is-visible'));
  });
})();
