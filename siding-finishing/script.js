// Prototype only: validate the form locally without sending or storing data.
const quoteForm = document.querySelector('.quote-form');
quoteForm.querySelector('button[type="submit"]').disabled = false;
quoteForm.addEventListener('submit', (event) => {
  event.preventDefault();
  if (!quoteForm.reportValidity()) return;
  const status = quoteForm.querySelector('.form-status');
  status.textContent = 'This is a preview. Your request has not been sent.';
  status.hidden = false;
});
