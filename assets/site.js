(() => {
 const filter = document.querySelector('[data-filter]');
 if (!filter) return;
 const normalize = text => text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
 filter.addEventListener('input', () => {
  const query = normalize(filter.value.trim()); let visible = 0;
  document.querySelectorAll('.guide-group').forEach(group => {
   let found = 0;
   group.querySelectorAll('.guide-grid a').forEach(card => {card.hidden = !normalize(card.textContent).includes(query); if (!card.hidden) found++;});
   group.hidden = !found; visible += found;
  });
  document.querySelector('.empty-results').hidden = visible > 0;
 });
})();
