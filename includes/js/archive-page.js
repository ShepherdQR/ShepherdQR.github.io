(function () {
    const data = window.HOMEPAGE_DATA || { items: [], stats: { byType: {}, years: {} } };
    const allItems = Array.isArray(data.items) ? data.items : [];
    const collection = document.body.dataset.collection || '';
    const summaryEl = document.getElementById('archive-summary');
    const listEl = document.getElementById('archive-list');
    const resultCount = document.getElementById('atlas-result-count');
    const activeFilters = document.getElementById('active-filters');
    const searchInput = document.getElementById('archive-search');
    const typeSelect = document.getElementById('filter-type');
    const yearSelect = document.getElementById('filter-year');
    const seriesSelect = document.getElementById('filter-series');
    const tagSelect = document.getElementById('filter-tag');
    const clearButton = document.getElementById('clear-filters');
    const params = new URLSearchParams(window.location.search);

    const state = {
        query: params.get('q') || '',
        type: collection || params.get('type') || '',
        year: params.get('year') || '',
        series: params.get('series') || '',
        tag: params.get('tag') || ''
    };

    populateControls();
    bindControls();
    render();

    function populateControls() {
        populateSelect(typeSelect, unique(allItems.map(item => item.type)), '全部类型');
        populateSelect(yearSelect, unique(allItems.map(item => String(item.published || '').slice(0, 4))).sort().reverse(), '全部年份');
        populateSelect(seriesSelect, unique(allItems.map(item => item.series).filter(Boolean)).sort(localeCompare), '全部系列');
        populateSelect(tagSelect, unique(allItems.flatMap(item => Array.isArray(item.tags) ? item.tags : [])).sort(localeCompare), '全部标签');

        if (searchInput) searchInput.value = state.query;
        if (typeSelect) {
            typeSelect.value = state.type;
            if (collection) typeSelect.disabled = true;
        }
        if (yearSelect) yearSelect.value = state.year;
        if (seriesSelect) seriesSelect.value = state.series;
        if (tagSelect) tagSelect.value = state.tag;
    }

    function bindControls() {
        if (searchInput) searchInput.addEventListener('input', () => update('query', searchInput.value));
        if (typeSelect) typeSelect.addEventListener('change', () => update('type', typeSelect.value));
        if (yearSelect) yearSelect.addEventListener('change', () => update('year', yearSelect.value));
        if (seriesSelect) seriesSelect.addEventListener('change', () => update('series', seriesSelect.value));
        if (tagSelect) tagSelect.addEventListener('change', () => update('tag', tagSelect.value));
        if (clearButton) clearButton.addEventListener('click', clearFilters);
    }

    function update(key, value) {
        state[key] = String(value || '').trim();
        writeQuery();
        render();
    }

    function clearFilters() {
        state.query = '';
        state.type = collection || '';
        state.year = '';
        state.series = '';
        state.tag = '';
        populateControls();
        writeQuery();
        render();
        if (searchInput) searchInput.focus();
    }

    function render() {
        const filtered = allItems.filter(matchesState);
        renderSummary(filtered);
        renderActiveFilters();
        renderList(filtered);
        if (resultCount) resultCount.textContent = `${filtered.length} / ${allItems.filter(item => !collection || item.type === collection).length} OBJECTS`;
    }

    function matchesState(item) {
        if (collection && item.type !== collection) return false;
        if (state.type && item.type !== state.type) return false;
        if (state.year && String(item.published || '').slice(0, 4) !== state.year) return false;
        if (state.series && item.series !== state.series) return false;
        if (state.tag && !(Array.isArray(item.tags) && item.tags.includes(state.tag))) return false;
        if (!state.query) return true;
        const haystack = [
            item.type,
            item.id,
            item.title,
            item.summary,
            item.series,
            ...(Array.isArray(item.tags) ? item.tags : [])
        ].filter(Boolean).join(' ').toLocaleLowerCase('zh-CN');
        return haystack.includes(state.query.toLocaleLowerCase('zh-CN'));
    }

    function renderSummary(filtered) {
        if (!summaryEl) return;
        const baseItems = allItems.filter(item => !collection || item.type === collection);
        const yearCount = new Set(baseItems.map(item => String(item.published || '').slice(0, 4))).size;
        const label = collection || 'published knowledge';
        summaryEl.textContent = `${baseItems.length} ${label} objects across ${yearCount} years. ${filtered.length === baseItems.length ? 'Browse by provenance, series and time.' : `${filtered.length} objects match the current field.`}`;
    }

    function renderActiveFilters() {
        if (!activeFilters) return;
        activeFilters.innerHTML = '';
        const values = [
            ['query', state.query && `“${state.query}”`],
            ['type', !collection && state.type],
            ['year', state.year],
            ['series', state.series],
            ['tag', state.tag && `#${state.tag}`]
        ].filter(([, value]) => value);
        values.forEach(([key, value]) => {
            const chip = document.createElement('span');
            chip.className = 'active-filter';
            chip.textContent = `${key} · ${value}`;
            activeFilters.appendChild(chip);
        });
    }

    function renderList(items) {
        if (!listEl) return;
        listEl.innerHTML = '';
        if (!items.length) {
            const empty = document.createElement('p');
            empty.className = 'archive-empty';
            empty.textContent = '没有对象满足当前约束。调整筛选器，或回到完整知识星图。';
            listEl.appendChild(empty);
            return;
        }
        groupByYear(items).forEach(group => listEl.appendChild(renderYear(group.year, group.items)));
    }

    function renderYear(year, yearItems) {
        const section = document.createElement('section');
        section.className = 'archive-year';
        section.id = `year-${year}`;

        const heading = document.createElement('h2');
        heading.className = 'archive-year-heading';
        heading.textContent = year;
        const count = document.createElement('span');
        count.className = 'archive-year-count';
        count.textContent = `${yearItems.length} accessioned`;
        heading.appendChild(count);

        const list = document.createElement('ol');
        list.className = 'archive-note-list';
        yearItems.forEach(item => list.appendChild(renderNote(item)));
        section.appendChild(heading);
        section.appendChild(list);
        return section;
    }

    function renderNote(item) {
        const li = document.createElement('li');
        li.className = 'archive-note';

        const date = document.createElement('time');
        date.dateTime = item.published || '';
        date.textContent = item.published || '—';

        const main = document.createElement('div');
        main.className = 'archive-note-main';
        const link = document.createElement('a');
        link.className = 'archive-note-title';
        link.href = item.href;
        link.textContent = item.title;
        const summary = document.createElement('p');
        summary.className = 'archive-note-summary';
        summary.textContent = item.summary || '';
        const meta = document.createElement('div');
        meta.className = 'archive-note-meta';
        if (item.series) meta.appendChild(renderMeta(item.series, `?series=${encodeURIComponent(item.series)}`));
        (Array.isArray(item.tags) ? item.tags.slice(0, 4) : []).forEach(tag => meta.appendChild(renderMeta('#' + tag, `?tag=${encodeURIComponent(tag)}`)));
        main.appendChild(link);
        if (summary.textContent) main.appendChild(summary);
        main.appendChild(meta);

        const kind = document.createElement('div');
        kind.className = 'archive-note-kind';
        const accession = document.createElement('span');
        accession.className = 'archive-note-accession';
        accession.textContent = `${item.type} · ${item.id}`;
        kind.appendChild(accession);

        li.appendChild(date);
        li.appendChild(main);
        li.appendChild(kind);
        return li;
    }

    function renderMeta(label, query) {
        const link = document.createElement('a');
        link.className = 'meta-chip';
        link.href = './archive.html' + query;
        link.textContent = label;
        return link;
    }

    function groupByYear(source) {
        const map = new Map();
        source.forEach(item => {
            const year = String(item.published || '').slice(0, 4) || 'Undated';
            if (!map.has(year)) map.set(year, []);
            map.get(year).push(item);
        });
        return Array.from(map.entries())
            .sort((a, b) => b[0].localeCompare(a[0]))
            .map(([year, yearItems]) => ({ year, items: yearItems }));
    }

    function populateSelect(select, values, firstLabel) {
        if (!select) return;
        select.innerHTML = '';
        const first = document.createElement('option');
        first.value = '';
        first.textContent = firstLabel;
        select.appendChild(first);
        values.filter(Boolean).forEach(value => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = value;
            select.appendChild(option);
        });
    }

    function writeQuery() {
        const next = new URLSearchParams();
        if (state.query) next.set('q', state.query);
        if (!collection && state.type) next.set('type', state.type);
        if (state.year) next.set('year', state.year);
        if (state.series) next.set('series', state.series);
        if (state.tag) next.set('tag', state.tag);
        const suffix = next.toString();
        window.history.replaceState(null, '', window.location.pathname + (suffix ? '?' + suffix : '') + window.location.hash);
    }

    function unique(values) {
        return Array.from(new Set(values));
    }

    function localeCompare(a, b) {
        return String(a).localeCompare(String(b), 'zh-CN');
    }
})();
