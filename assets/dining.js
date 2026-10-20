(() => {
  const cards = [...document.querySelectorAll('.restaurant')];
  const query = document.getElementById('q');
  const place = document.getElementById('place-filter');
  if (!query || !place) return;
  const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  let selected = '';
  const update = () => {
    const words = normalize(query.value).trim().split(/\s+/).filter(Boolean);
    let visible = 0;
    cards.forEach(card => {
      const matches = words.every(word => card.dataset.search.includes(word)) &&
        (!place.value || card.dataset.neighborhood === place.value) &&
        (!selected || card.dataset.categories.split(' ').includes(selected));
      card.hidden = !matches;
      visible += Number(matches);
    });
    document.getElementById('count').textContent = `${visible} de ${cards.length} fichas visibles`;
    document.getElementById('empty').hidden = visible > 0;
  };
  query.addEventListener('input', update);
  place.addEventListener('change', update);
  document.querySelectorAll('#filters button').forEach(button => {
    button.addEventListener('click', () => {
      selected = button.dataset.filter;
      document.querySelectorAll('#filters button').forEach(other => {
        const active = other === button;
        other.classList.toggle('is-active', active);
        other.setAttribute('aria-pressed', String(active));
      });
      update();
    });
  });
  const track = document.getElementById('gastronomia-carousel');
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.querySelector('[data-carousel-prev]')?.addEventListener('click', () => track.scrollBy({left: -track.clientWidth * .8, behavior: reduced ? 'instant' : 'smooth'}));
  document.querySelector('[data-carousel-next]')?.addEventListener('click', () => track.scrollBy({left: track.clientWidth * .8, behavior: reduced ? 'instant' : 'smooth'}));
})();
