/**
 * Categories Tree - panel for the InvenTree React UI (Parts page / part category pages).
 *
 * Shows the part category tree as text and offers CSV / XLSX / TXT downloads.
 * Rendered with plain DOM (legacy two-argument entry point), so no build step
 * is required. Talks to /plugin/category_exporter/tree/ and .../export/<format>/.
 */

const STRINGS = {
  en: {
    title: 'Categories Tree',
    loading: 'Loading…',
    empty: 'No categories.',
    loadFailed: 'Could not load the tree',
    refresh: 'Refresh',
    copy: 'Copy',
    copied: 'Copied',
    download: 'Download:',
    scope: 'Scope',
    scopeAll: 'All categories',
    scopeSub: 'This category and its subcategories',
    csv: 'CSV',
    xlsx: 'XLSX',
    tree: 'TXT',
    columns: 'CSV / XLSX: ID, name, path, level, description, parent, default location, parent default location, default keywords, parts, subcategories, structural, starred, icon.',
  },
  pl: {
    title: 'Drzewo kategorii',
    loading: 'Wczytywanie…',
    empty: 'Brak kategorii.',
    loadFailed: 'Nie udało się wczytać drzewa',
    refresh: 'Odśwież',
    copy: 'Kopiuj',
    copied: 'Skopiowano',
    download: 'Pobierz:',
    scope: 'Zakres',
    scopeAll: 'Wszystkie kategorie',
    scopeSub: 'Ta kategoria i jej podkategorie',
    csv: 'CSV',
    xlsx: 'XLSX',
    tree: 'TXT',
    columns: 'CSV / XLSX: ID, nazwa, ścieżka, poziom, opis, nadrzędna, domyślna lokalizacja, domyślna lokalizacja nadrzędnej, domyślne słowa kluczowe, części, podkategorie, strukturalna, oznaczona gwiazdką, ikona.',
  },
};

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (key === 'style') Object.assign(node.style, value);
    else if (key.startsWith('on')) node.addEventListener(key.slice(2), value);
    else if (value !== undefined && value !== null && value !== false) node.setAttribute(key, value);
  }
  for (const child of children.flat()) {
    if (child === null || child === undefined) continue;
    node.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return node;
}

function linkButton(label, color) {
  return el(
    'a',
    {
      style: {
        display: 'inline-block',
        padding: '6px 14px',
        borderRadius: 'var(--mantine-radius-sm, 4px)',
        border: `1px solid var(--mantine-color-${color}-filled, #228be6)`,
        background: `var(--mantine-color-${color}-filled, #228be6)`,
        color: 'var(--mantine-color-white, #fff)',
        fontSize: '14px',
        fontWeight: 600,
        textDecoration: 'none',
        fontFamily: 'inherit',
      },
    },
    label
  );
}

function smallButton(label, onClick) {
  return el(
    'button',
    {
      type: 'button',
      onclick: onClick,
      style: {
        padding: '4px 10px',
        borderRadius: 'var(--mantine-radius-sm, 4px)',
        border: '1px solid var(--mantine-color-default-border, #ced4da)',
        background: 'transparent',
        color: 'inherit',
        fontSize: '13px',
        cursor: 'pointer',
        fontFamily: 'inherit',
      },
    },
    label
  );
}

export function renderPanel(target, data) {
  const ctx = data?.context || {};
  const base = (ctx.base_url || '/plugin/category_exporter/').replace(/\/?$/, '/');
  const lang = String(data?.locale || navigator.language || 'en').toLowerCase().startsWith('pl') ? 'pl' : 'en';
  const t = STRINGS[lang];
  const categoryId = ctx.category_id ?? null;

  let scope = categoryId !== null ? 'sub' : 'all';

  const formats = [
    ['csv', t.csv, 'blue'],
    ['xlsx', t.xlsx, 'green'],
    ['tree', t.tree, 'grape'],
  ];

  const links = formats.map(([fmt, label, color]) => {
    const link = linkButton(label, color);
    link.dataset.fmt = fmt;
    return link;
  });

  const query = () => (scope === 'sub' && categoryId !== null ? `?category=${encodeURIComponent(categoryId)}` : '');

  const treeBox = el('pre', {
    style: {
      margin: 0,
      padding: '12px',
      maxHeight: '70vh',
      overflow: 'auto',
      borderRadius: 'var(--mantine-radius-sm, 4px)',
      border: '1px solid var(--mantine-color-default-border, #dee2e6)',
      background: 'var(--mantine-color-default-hover, rgba(0,0,0,0.03))',
      fontFamily: 'var(--mantine-font-family-monospace, ui-monospace, monospace)',
      fontSize: '13px',
      lineHeight: 1.45,
      whiteSpace: 'pre',
    },
  });

  let treeText = '';
  let requestNo = 0;

  async function loadTree() {
    const current = ++requestNo;
    treeBox.textContent = t.loading;

    try {
      const response = await fetch(`${base}tree/${query()}`, { credentials: 'same-origin' });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const text = await response.text();
      if (current !== requestNo) return; // a newer request was started
      treeText = text;
      treeBox.textContent = text || t.empty;
    } catch (err) {
      if (current !== requestNo) return;
      treeText = '';
      treeBox.textContent = `${t.loadFailed}: ${err.message}`;
    }
  }

  const copyButton = smallButton(t.copy, async () => {
    if (!treeText) return;
    try {
      await navigator.clipboard.writeText(treeText);
      copyButton.textContent = t.copied;
      setTimeout(() => (copyButton.textContent = t.copy), 1500);
    } catch {
      // Clipboard API unavailable (e.g. plain http): select the text instead
      const range = document.createRange();
      range.selectNodeContents(treeBox);
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
    }
  });

  function updateLinks() {
    for (const link of links) {
      link.href = `${base}export/${link.dataset.fmt}/${query()}`;
    }
  }

  let scopeRow = null;

  if (categoryId !== null) {
    const option = (value, label) =>
      el(
        'label',
        { style: { display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' } },
        el('input', {
          type: 'radio',
          name: `category-exporter-scope-${categoryId}`,
          value,
          checked: scope === value ? 'checked' : null,
          onchange: () => {
            scope = value;
            updateLinks();
            loadTree();
          },
        }),
        label
      );

    scopeRow = el(
      'div',
      { style: { display: 'flex', gap: '16px', flexWrap: 'wrap', alignItems: 'center', fontSize: '14px' } },
      el('strong', {}, `${t.scope}:`),
      option('sub', t.scopeSub),
      option('all', t.scopeAll)
    );
  }

  updateLinks();

  target.replaceChildren(
    el(
      'div',
      { style: { display: 'flex', flexDirection: 'column', gap: '12px' } },
      el(
        'div',
        { style: { display: 'flex', alignItems: 'center', gap: '12px' } },
        el('span', { style: { fontSize: '18px', fontWeight: 700 } }, t.title),
        el('span', { style: { marginLeft: 'auto', fontSize: '12px', opacity: 0.6 } }, `v${ctx.version || ''}`)
      ),
      scopeRow,
      el(
        'div',
        { style: { display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' } },
        el('span', { style: { fontSize: '14px', fontWeight: 600 } }, t.download),
        links,
        el(
          'span',
          { style: { marginLeft: 'auto', display: 'flex', gap: '8px' } },
          copyButton,
          smallButton(t.refresh, loadTree)
        )
      ),
      treeBox,
      el('div', { style: { fontSize: '12px', opacity: 0.6 } }, t.columns)
    )
  );

  loadTree();
}
