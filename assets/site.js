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
  // Quote forms submit to the same-origin PHP endpoint used on cPanel.
  document.querySelectorAll('[data-quote-form]').forEach((form) => {
    const submit = form.querySelector('button[type="submit"]');
    const status = form.querySelector('.form-status');
    if (!submit || !status) return;

    let pending = false;
    let submissionId = '';
    const showStatus = (message, state) => {
      status.textContent = message;
      status.className = `form-status form-status--${state}`;
      status.hidden = false;
    };

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (pending || !form.reportValidity()) return;

      if (!submissionId) {
        submissionId = crypto.randomUUID?.()
          || `${Date.now()}-${Math.random().toString(36).slice(2)}-${Math.random().toString(36).slice(2)}`;
      }
      const formData = new FormData(form);
      formData.set('submission_id', submissionId);
      pending = true;
      submit.disabled = true;
      form.setAttribute('aria-busy', 'true');
      showStatus('Sending your request…', 'pending');

      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 15000);
      try {
        const response = await fetch(form.action, {
          method: 'POST',
          body: formData,
          headers: { Accept: 'application/json' },
          credentials: 'same-origin',
          signal: controller.signal,
        });
        const result = await response.json().catch(() => ({}));
        if (!response.ok) {
          const responseError = new Error(result.message || 'The request could not be sent.');
          responseError.isResponseError = true;
          throw responseError;
        }
        showStatus(result.message || 'Thank you. Your request was sent to Space Up Construction.', 'success');
        form.reset();
        submissionId = '';
      } catch (error) {
        const message = error.name === 'AbortError'
          ? 'The request took too long. Please try again or call (508) 474-9407.'
          : (error.isResponseError ? error.message : 'We could not send your request. Please try again or call (508) 474-9407.');
        showStatus(message, 'error');
      } finally {
        clearTimeout(timeout);
        pending = false;
        submit.disabled = false;
        form.removeAttribute('aria-busy');
      }
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
