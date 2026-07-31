(function () {
    const data = window.HOMEPAGE_DATA || { items: [], stats: { byType: {}, years: {} } };
    const plane = window.SITE_PLANE || {};
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
    const constellationEl = document.getElementById('atlas-constellation');
    const ledgerEl = document.getElementById('atlas-ledger');
    const pathHost = document.getElementById('atlas-paths');
    const modeButtons = Array.from(document.querySelectorAll('[data-atlas-mode]'));
    const params = new URLSearchParams(window.location.search);

    const state = {
        query: params.get('q') || '',
        type: collection || params.get('type') || '',
        year: params.get('year') || '',
        series: params.get('series') || '',
        tag: params.get('tag') || '',
        mode: constellationEl ? (params.get('view') === 'ledger' ? 'ledger' : 'constellation') : 'ledger'
    };

    populateControls();
    renderPaths();
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
        modeButtons.forEach(button => button.addEventListener('click', () => updateMode(button.dataset.atlasMode)));
    }

    function update(key, value) {
        state[key] = String(value || '').trim();
        writeQuery();
        render();
    }

    function updateMode(mode) {
        if (mode !== 'constellation' && mode !== 'ledger') return;
        state.mode = mode;
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
        renderConstellation(filtered);
        renderList(filtered);
        renderMode();
        if (resultCount) resultCount.textContent = `${filtered.length} / ${allItems.filter(item => !collection || item.type === collection).length} OBJECTS`;
    }

    function renderMode() {
        document.body.dataset.atlasMode = state.mode;
        modeButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.atlasMode === state.mode)));
        if (constellationEl) constellationEl.hidden = state.mode !== 'constellation';
        if (ledgerEl) ledgerEl.hidden = state.mode !== 'ledger';
    }

    function renderPaths() {
        if (!pathHost) return;
        const lines = narrativeLines().slice().sort((a, b) => Number(b.weight_hint_percent || 0) - Number(a.weight_hint_percent || 0)).slice(0, 3);
        pathHost.innerHTML = '';
        lines.forEach((line, index) => {
            const li = document.createElement('li');
            li.className = 'path-entry';
            const link = document.createElement('a');
            link.href = line.href || './archive.html';
            const marker = document.createElement('span');
            marker.className = 'path-index';
            marker.textContent = String(index + 1).padStart(2, '0');
            const copy = document.createElement('span');
            const title = document.createElement('strong');
            title.textContent = line.title_zh || line.title || line.title_en || line.id;
            const question = document.createElement('small');
            question.textContent = line.core_question_zh || line.question || line.title_en || '';
            copy.appendChild(title);
            copy.appendChild(question);
            link.appendChild(marker);
            link.appendChild(copy);
            li.appendChild(link);
            pathHost.appendChild(li);
        });
    }

    function renderConstellation(filtered) {
        if (!constellationEl) return;
        constellationEl.innerHTML = '';
        const hub = document.createElement('div');
        hub.className = 'constellation-hub';
        hub.setAttribute('role', 'note');
        const hubLabel = document.createElement('span');
        hubLabel.textContent = 'PUBLIC KNOWLEDGE FIELD';
        const hubCount = document.createElement('strong');
        hubCount.textContent = String(filtered.length);
        const hubUnit = document.createElement('small');
        hubUnit.textContent = 'related objects';
        hub.appendChild(hubLabel);
        hub.appendChild(hubCount);
        hub.appendChild(hubUnit);
        constellationEl.appendChild(hub);
        const assigned = new Set();
        narrativeLines().forEach((line, index) => {
            const fieldId = line.id || line.title_zh || line.title;
            const related = filtered.filter(item => fieldIds(item).includes(fieldId));
            related.forEach(item => assigned.add(itemKey(item)));
            if (!related.length) return;
            constellationEl.appendChild(renderFieldCluster(line, related, index));
        });
        const unmapped = filtered.filter(item => !assigned.has(itemKey(item)));
        if (unmapped.length) {
            constellationEl.appendChild(renderFieldCluster({ title_zh: '尚未映射', title_en: 'Catalogued / unmapped', id: 'unmapped' }, unmapped, 5));
        }
    }

    function renderFieldCluster(line, related, index) {
        const cluster = document.createElement('article');
        cluster.className = 'constellation-cluster atlas-node';
        cluster.dataset.state = line.id === 'unmapped' ? 'catalogued' : (index === 0 ? 'current' : 'displayed');
        const positions = [
            [2, 1, 4], [8, 2, 4], [5, 4, 4], [9, 6, 4], [1, 7, 4], [5, 9, 4]
        ];
        const [column, row, span] = positions[index % positions.length];
        cluster.style.setProperty('--atlas-column', column);
        cluster.style.setProperty('--atlas-row', row);
        cluster.style.setProperty('--atlas-span', span);
        const heading = document.createElement('header');
        const marker = document.createElement('span');
        marker.className = 'state-marker';
        marker.dataset.state = cluster.dataset.state;
        marker.textContent = line.id === 'unmapped' ? 'Catalogued' : (index === 0 ? 'Current path' : 'Displayed path');
        const title = document.createElement('h2');
        title.textContent = line.title_zh || line.title || line.title_en || line.id;
        const count = document.createElement('strong');
        count.textContent = `${related.length} objects`;
        heading.appendChild(marker);
        heading.appendChild(title);
        heading.appendChild(count);
        const list = document.createElement('ol');
        related.slice(0, 5).forEach(item => {
            const li = document.createElement('li');
            const link = document.createElement('a');
            link.href = item.href;
            link.textContent = item.title;
            const meta = document.createElement('span');
            meta.textContent = `${item.type} ${item.id} · ${item.published || 'undated'}`;
            li.appendChild(link);
            li.appendChild(meta);
            list.appendChild(li);
        });
        cluster.appendChild(heading);
        cluster.appendChild(list);
        return cluster;
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
        li.dataset.state = item.supersededBy || item.superseded_by ? 'superseded' : 'displayed';

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
        const marker = document.createElement('span');
        marker.className = 'state-marker';
        marker.dataset.state = li.dataset.state;
        marker.textContent = li.dataset.state === 'superseded' ? 'Superseded' : 'Displayed';
        const summarySource = document.createElement('span');
        summarySource.className = 'summary-source';
        summarySource.textContent = item.summarySource === 'explicit' ? 'authored summary' : 'derived excerpt';
        kind.appendChild(marker);
        kind.appendChild(accession);
        kind.appendChild(summarySource);

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
        if (constellationEl && state.mode === 'ledger') next.set('view', 'ledger');
        const suffix = next.toString();
        window.history.replaceState(null, '', window.location.pathname + (suffix ? '?' + suffix : '') + window.location.hash);
    }

    function unique(values) {
        return Array.from(new Set(values));
    }

    function localeCompare(a, b) {
        return String(a).localeCompare(String(b), 'zh-CN');
    }

    function narrativeLines() {
        if (Array.isArray(plane.narrativeLines)) return plane.narrativeLines;
        return (((plane.narrative_lines || {}).items) || []);
    }

    function fieldIds(item) {
        if (Array.isArray(item.fieldIds)) return item.fieldIds;
        if (Array.isArray(item.field_ids)) return item.field_ids;
        return [];
    }

    function itemKey(item) {
        return `${item.type}:${item.id}`;
    }
})();
