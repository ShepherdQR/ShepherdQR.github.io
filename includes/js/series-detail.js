(function () {
    const partOrder = ['第一辑', '第二辑', '第三辑', '第四辑', '第五辑'];
    const slug = document.body.dataset.seriesSlug;
    const state = parseInitialState();

    const titleEl = document.getElementById('series-title');
    const descriptionEl = document.getElementById('series-description');
    const statusControls = document.getElementById('status-controls');
    const partControls = document.getElementById('part-controls');
    const sortControls = document.getElementById('sort-controls');
    const listEl = document.getElementById('work-list');
    const listTitleEl = document.getElementById('work-list-title');
    const listCountEl = document.getElementById('work-list-count');

    let currentSeries = null;

    loadSeriesData()
        .then(data => {
            currentSeries = (data.series || []).find(item => item.slug === slug);
            if (!currentSeries) {
                throw new Error(`Series not found: ${slug}`);
            }
            renderPage();
        })
        .catch(error => {
            descriptionEl.textContent = 'Series data could not be loaded.';
            listEl.appendChild(message('series-error', error.message));
        });

    async function loadSeriesData() {
        const response = await fetch('../../data/series-books.json');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status} loading series data`);
        }
        return response.json();
    }

    function parseInitialState() {
        const params = new URLSearchParams(window.location.search);
        const hash = decodeURIComponent(window.location.hash.replace(/^#/, ''));
        const statusFromHash = hash === 'done' || hash === 'todo' ? hash : '';
        return {
            status: params.get('status') || statusFromHash || 'all',
            part: params.get('part') || 'all',
            sort: params.get('sort') || 'series'
        };
    }

    function renderPage() {
        titleEl.textContent = currentSeries.displayTitle || currentSeries.title;
        descriptionEl.textContent = currentSeries.description || '';
        renderMetrics();
        renderControls();
        renderWorks();
        scrollToHashTarget();
    }

    function renderMetrics() {
        const counts = countItems(currentSeries.items || []);
        document.getElementById('metric-total').textContent = counts.total;
        document.getElementById('metric-done').textContent = counts.done;
        document.getElementById('metric-todo').textContent = counts.todo;
        document.getElementById('metric-candidate').textContent = counts.candidate;
    }

    function renderControls() {
        renderSegmented(statusControls, [
            ['all', 'All'],
            ['done', 'Done'],
            ['todo', 'Todo']
        ], state.status, value => {
            state.status = value;
            updateUrl();
            renderControls();
            renderWorks();
        });

        const parts = ['all'].concat(uniqueParts(currentSeries.items || []));
        renderSegmented(partControls, parts.map(part => [part, part === 'all' ? 'All' : part]), state.part, value => {
            state.part = value;
            updateUrl();
            renderControls();
            renderWorks();
        });

        renderSegmented(sortControls, [
            ['series', '按辑'],
            ['person', '按人/对象'],
            ['note', '按阅读页']
        ], state.sort, value => {
            state.sort = value;
            updateUrl();
            renderControls();
            renderWorks();
        });
    }

    function renderSegmented(host, options, active, onChange) {
        host.innerHTML = '';
        options.forEach(([value, label]) => {
            const button = document.createElement('button');
            button.type = 'button';
            button.textContent = label;
            button.setAttribute('aria-pressed', String(value === active));
            button.addEventListener('click', () => onChange(value));
            host.appendChild(button);
        });
    }

    function renderWorks() {
        const items = sortedItems(filteredItems(currentSeries.items || []));
        listEl.innerHTML = '';
        listTitleEl.textContent = state.status === 'all' ? 'Works' : state.status === 'done' ? 'Done' : 'Todo';
        listCountEl.textContent = `${items.length} shown`;

        if (!items.length) {
            listEl.appendChild(message('series-empty', 'No works match the current filters.'));
            return;
        }

        items.forEach(item => listEl.appendChild(renderWorkCard(item)));
    }

    function filteredItems(items) {
        return items.filter(item => {
            if (state.status !== 'all' && item.status !== state.status) return false;
            if (state.part !== 'all' && item.seriesPart !== state.part) return false;
            return true;
        });
    }

    function sortedItems(items) {
        const copy = items.slice();
        if (state.sort === 'person') {
            return copy.sort((a, b) =>
                (a.personOrScope || a.displayTitle).localeCompare(b.personOrScope || b.displayTitle, 'zh-CN')
                || compareBySeries(a, b)
            );
        }
        if (state.sort === 'note') {
            return copy.sort((a, b) =>
                noteSortValue(a).localeCompare(noteSortValue(b))
                || compareBySeries(a, b)
            );
        }
        return copy.sort(compareBySeries);
    }

    function compareBySeries(a, b) {
        const partA = partOrder.indexOf(a.seriesPart);
        const partB = partOrder.indexOf(b.seriesPart);
        if (partA !== partB) return partA - partB;
        return (a.displayTitle || '').localeCompare(b.displayTitle || '', 'zh-CN');
    }

    function noteSortValue(item) {
        if (item.noteId) return `0-${item.noteId}`;
        return `1-${item.displayTitle || item.workId}`;
    }

    function renderWorkCard(item) {
        const card = document.createElement('article');
        card.className = 'work-card';
        card.id = anchorId(item);

        const main = document.createElement('div');
        main.className = 'work-main';

        const title = document.createElement('a');
        title.className = 'work-title';
        title.href = item.href || `#${anchorId(item)}`;
        title.textContent = item.displayTitle || item.workId;
        main.appendChild(title);

        const meta = document.createElement('div');
        meta.className = 'work-meta';
        meta.appendChild(statusPill(item));
        meta.appendChild(textPill(item.seriesPart));
        if (item.volumes && item.volumes.length) {
            meta.appendChild(textPill(item.volumes.join(' + ')));
        }
        meta.appendChild(textPill(item.personOrScope || item.kind || 'work'));
        main.appendChild(meta);

        const source = document.createElement('div');
        source.className = 'work-source';
        (item.sourceLabels || []).forEach(label => source.appendChild(textPill(label, 'source-pill')));
        if (item.kind === 'anthology') {
            source.appendChild(textPill('anthology', 'source-pill'));
        }
        main.appendChild(source);

        const actions = document.createElement('div');
        actions.className = 'work-actions';
        const action = document.createElement('a');
        action.className = 'work-action-link';
        action.href = item.href || `#${anchorId(item)}`;
        action.textContent = item.href ? '阅读页' : '待写阅读页';
        actions.appendChild(action);

        card.appendChild(main);
        card.appendChild(actions);
        return card;
    }

    function statusPill(item) {
        const span = textPill(item.matchStatus === 'candidate' ? 'Candidate match' : item.status, 'status-pill');
        span.dataset.status = item.status;
        span.dataset.match = item.matchStatus || '';
        return span;
    }

    function textPill(text, className) {
        const span = document.createElement('span');
        span.className = className || 'metric-pill';
        span.textContent = text;
        return span;
    }

    function countItems(items) {
        return items.reduce(
            (acc, item) => {
                acc.total += 1;
                if (item.status === 'done') acc.done += 1;
                if (item.status === 'todo') acc.todo += 1;
                if (item.matchStatus === 'candidate') acc.candidate += 1;
                return acc;
            },
            { total: 0, done: 0, todo: 0, candidate: 0 }
        );
    }

    function uniqueParts(items) {
        const seen = new Set(items.map(item => item.seriesPart).filter(Boolean));
        return partOrder.filter(part => seen.has(part));
    }

    function updateUrl() {
        const params = new URLSearchParams();
        if (state.status !== 'all') params.set('status', state.status);
        if (state.part !== 'all') params.set('part', state.part);
        if (state.sort !== 'series') params.set('sort', state.sort);
        const query = params.toString();
        const hash = state.status === 'done' || state.status === 'todo' ? `#${state.status}` : '';
        const next = `${window.location.pathname}${query ? `?${query}` : ''}${hash}`;
        window.history.replaceState(null, '', next);
    }

    function anchorId(item) {
        return `book-${item.workId}`;
    }

    function scrollToHashTarget() {
        window.requestAnimationFrame(() => {
            const hash = decodeURIComponent(window.location.hash.replace(/^#/, ''));
            if (!hash || hash === 'done' || hash === 'todo') return;
            const target = document.getElementById(hash);
            if (target) target.scrollIntoView();
        });
    }

    function message(className, text) {
        const node = document.createElement('p');
        node.className = className;
        node.textContent = text;
        return node;
    }
})();
