// Auto-hide flash messages
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.flash').forEach(f => {
    setTimeout(() => {
      f.style.transition = 'opacity 0.5s';
      f.style.opacity = '0';
      setTimeout(() => f.remove(), 500);
    }, 4000);
  });

  // auto-init semua tabel dengan data-search
  document.querySelectorAll('table[data-search]').forEach(table => {
    initTable(table.id, parseInt(table.dataset.pagesize) || 20);
  });
});

// ── INIT TABLE (search + sort + pagination) ───────────
function initTable(tableId, pageSize) {
  const table   = document.getElementById(tableId);
  const wrap    = document.getElementById(tableId + '-pagination');
  const counter = document.getElementById(tableId + '-count');
  const input   = document.getElementById('search-' + tableId);
  if (!table) return;

  let currentPage = 1;

  // mark all rows as visible initially
  getAllRows().forEach(r => r.dataset.hidden = 'false');

  // ── SEARCH ──
  if (input) {
    input.addEventListener('input', function () {
      const kw = this.value.toLowerCase().trim();
      getAllRows().forEach(row => {
        const match = kw === '' || row.textContent.toLowerCase().includes(kw);
        row.dataset.hidden = match ? 'false' : 'true';
      });
      currentPage = 1;
      render();
    });
  }

  // ── SORT ──
  table.querySelectorAll('thead th').forEach((th, idx) => {
    th.style.cursor      = 'pointer';
    th.style.userSelect  = 'none';
    th.title             = 'Klik untuk mengurutkan';
    let asc              = true;

    th.addEventListener('click', () => {
      const tbody = table.querySelector('tbody');
      const rows  = Array.from(tbody.querySelectorAll('tr'));

      rows.sort((a, b) => {
        const aT = a.cells[idx]?.textContent.trim() || '';
        const bT = b.cells[idx]?.textContent.trim() || '';
        const aN = parseFloat(aT.replace(/[^0-9.-]/g, ''));
        const bN = parseFloat(bT.replace(/[^0-9.-]/g, ''));
        if (!isNaN(aN) && !isNaN(bN)) return asc ? aN - bN : bN - aN;
        return asc ? aT.localeCompare(bT) : bT.localeCompare(aT);
      });

      rows.forEach(r => tbody.appendChild(r));
      asc = !asc;

      table.querySelectorAll('thead th').forEach(t => {
        t.textContent = t.textContent.replace(' ↑','').replace(' ↓','');
      });
      th.textContent += asc ? ' ↓' : ' ↑';
      currentPage = 1;
      render();
    });
  });

  // ── HELPERS ──
  function getAllRows() {
    return Array.from(table.querySelectorAll('tbody tr'));
  }

  function getSearchRows() {
    return getAllRows().filter(r => r.dataset.hidden !== 'true');
  }

  // ── RENDER ──
  function render() {
    const rows  = getSearchRows();
    const total = rows.length;
    const pages = Math.ceil(total / pageSize) || 1;
    currentPage = Math.min(currentPage, pages);

    // hide all dulu
    getAllRows().forEach(r => { r.style.display = 'none'; });

    // tampilkan baris di halaman ini
    const start = (currentPage - 1) * pageSize;
    const end   = start + pageSize;
    rows.forEach((r, i) => {
      if (i >= start && i < end) r.style.display = '';
    });

    // update counter
    if (counter) counter.textContent = total + ' baris';

    // render pagination
    if (!wrap) return;
    wrap.innerHTML = '';
    if (pages <= 1) return;

    const info = document.createElement('span');
    info.style.cssText = 'font-size:13px;color:var(--muted);align-self:center;';
    info.textContent   = `Halaman ${currentPage} dari ${pages}  (${total} baris)`;
    wrap.appendChild(info);

    const btnWrap = document.createElement('div');
    btnWrap.style.cssText = 'display:flex;gap:6px;flex-wrap:wrap;';

    const prev = makeBtn('← Prev', currentPage <= 1, false);
    prev.onclick = () => { if (currentPage > 1) { currentPage--; render(); } };
    btnWrap.appendChild(prev);

    for (let p = 1; p <= pages; p++) {
      const far = Math.abs(p - currentPage) > 2;
      const edge = p === 1 || p === pages;
      if (pages > 7 && far && !edge) {
        if (p === 2 || p === pages - 1) {
          const dot = document.createElement('span');
          dot.textContent = '...';
          dot.style.cssText = 'padding:6px 2px;color:var(--muted);font-size:13px;align-self:center;';
          btnWrap.appendChild(dot);
        }
        continue;
      }
      const btn = makeBtn(p, false, p === currentPage);
      btn.onclick = (pg => () => { currentPage = pg; render(); })(p);
      btnWrap.appendChild(btn);
    }

    const next = makeBtn('Next →', currentPage >= pages, false);
    next.onclick = () => { if (currentPage < pages) { currentPage++; render(); } };
    btnWrap.appendChild(next);

    wrap.appendChild(btnWrap);
  }

  function makeBtn(label, disabled, active) {
    const btn = document.createElement('button');
    btn.textContent = label;
    btn.disabled    = disabled;
    btn.style.cssText = `
      padding:6px 12px;border-radius:6px;font-size:13px;
      cursor:${disabled ? 'not-allowed' : 'pointer'};
      font-family:inherit;transition:all .15s;
      background:${active ? 'var(--red)' : 'var(--bg3)'};
      color:${active ? '#fff' : disabled ? '#444' : 'var(--muted)'};
      border:1px solid ${active ? 'var(--red)' : 'var(--border)'};
    `;
    if (!disabled && !active) {
      btn.onmouseover = () => { btn.style.color = 'var(--text)'; };
      btn.onmouseout  = () => { btn.style.color = 'var(--muted)'; };
    }
    return btn;
  }

  render();
}