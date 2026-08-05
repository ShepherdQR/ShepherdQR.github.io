(function () {
    const legacyPartOrder = ['第一辑', '第二辑', '第三辑', '第四辑', '第五辑'];
    const slug = document.body.dataset.seriesSlug;
    const state = parseInitialState();

    const titleEl = document.getElementById('series-title');
    const descriptionEl = document.getElementById('series-description');
    const scopeNoteEl = document.getElementById('series-scope-note');
    const readingListEl = document.getElementById('series-reading-list');
    const statusControls = document.getElementById('status-controls');
    const partControls = document.getElementById('part-controls');
    const sortControls = document.getElementById('sort-controls');
    const viewControls = document.getElementById('view-controls');
    const searchInput = document.getElementById('series-search');
    const groupControlTitle = document.getElementById('group-control-title');
    const listEl = document.getElementById('work-list');
    const listTitleEl = document.getElementById('work-list-title');
    const listCountEl = document.getElementById('work-list-count');
    const loadMoreButton = document.getElementById('series-load-more');

    let currentSeries = null;
    let visibleLimit = Number.POSITIVE_INFINITY;

    loadSeriesData()
        .then(data => {
            currentSeries = (data.series || []).find(item => item.slug === slug);
            if (!currentSeries) {
                throw new Error(`Series not found: ${slug}`);
            }
            if (!state.sort) state.sort = currentSeries.defaultSort || 'series';
            if (!['catalog', 'cards'].includes(state.view)) {
                state.view = currentSeries.defaultView || 'cards';
            }
            visibleLimit = pageSize();
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
            sort: params.get('sort') || '',
            view: params.get('view') || '',
            query: params.get('q') || ''
        };
    }

    function renderPage() {
        titleEl.textContent = currentSeries.displayTitle || currentSeries.title;
        descriptionEl.textContent = currentSeries.description || '';
        document.title = `${currentSeries.displayTitle || currentSeries.title} - Pursuing Immortality`;
        renderScopeLinks();
        renderMetrics();
        renderControls();
        renderWorks();
        scrollToHashTarget();
    }

    function renderScopeLinks() {
        if (scopeNoteEl) {
            scopeNoteEl.textContent = currentSeries.scopeNote || '';
            scopeNoteEl.hidden = !currentSeries.scopeNote;
        }
        if (readingListEl) {
            if (currentSeries.readingListHref) {
                readingListEl.href = currentSeries.readingListHref;
                readingListEl.textContent = currentSeries.readingListLabel || 'Reading list MD';
                readingListEl.hidden = false;
            } else {
                readingListEl.hidden = true;
            }
        }
    }

    function renderMetrics() {
        const counts = countItems(currentSeries.items || []);
        document.getElementById('metric-total').textContent = counts.total;
        document.getElementById('metric-done').textContent = counts.done;
        document.getElementById('metric-todo').textContent = counts.todo;
        document.getElementById('metric-candidate').textContent = counts.candidate;
        const unit = currentSeries.unitLabel || 'works';
        const unitLabel = document.getElementById('metric-total-label');
        if (unitLabel) unitLabel.textContent = unit;
    }

    function renderControls() {
        renderSegmented(statusControls, [
            ['all', 'All'],
            ['done', 'Done'],
            ['todo', 'Todo']
        ], state.status, value => {
            state.status = value;
            resetVisibleLimit();
            updateUrl();
            renderControls();
            renderWorks();
        });

        if (groupControlTitle) {
            groupControlTitle.textContent = currentSeries.groupLabel || 'Series Part';
        }
        const parts = ['all'].concat(uniqueParts(currentSeries.items || []));
        renderSegmented(partControls, parts.map(part => [part, part === 'all' ? 'All' : part]), state.part, value => {
            state.part = value;
            resetVisibleLimit();
            updateUrl();
            renderControls();
            renderWorks();
        });

        const labels = currentSeries.sortLabels || {};
        renderSegmented(sortControls, [
            ['series', labels.series || '按系列顺序'],
            ['person', labels.person || '按人 / 作者'],
            ['note', labels.note || '按阅读页']
        ], state.sort, value => {
            state.sort = value;
            resetVisibleLimit();
            updateUrl();
            renderControls();
            renderWorks();
        });

        if (viewControls) {
            renderSegmented(viewControls, [
                ['catalog', '精简目录'],
                ['cards', '详情卡片']
            ], state.view, value => {
                state.view = value;
                resetVisibleLimit();
                updateUrl();
                renderControls();
                renderWorks();
            });
        }

        if (searchInput) {
            searchInput.value = state.query;
            if (!searchInput.dataset.bound) {
                searchInput.addEventListener('input', event => {
                    state.query = event.target.value.trim();
                    resetVisibleLimit();
                    updateUrl();
                    renderWorks();
                });
                searchInput.dataset.bound = 'true';
            }
        }

        if (loadMoreButton && !loadMoreButton.dataset.bound) {
            loadMoreButton.addEventListener('click', () => {
                visibleLimit += pageSize();
                renderWorks();
            });
            loadMoreButton.dataset.bound = 'true';
        }
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
        const matchedItems = sortedItems(filteredItems(currentSeries.items || []));
        const catalogMode = state.view === 'catalog';
        const renderedItems = catalogMode ? matchedItems : matchedItems.slice(0, visibleLimit);
        listEl.innerHTML = '';
        listEl.classList.toggle('work-list--catalog', catalogMode);
        listTitleEl.textContent = catalogMode
            ? (state.status === 'all' ? '完整目录' : state.status === 'done' ? '已读目录' : '未读目录')
            : (state.status === 'all' ? 'Works' : state.status === 'done' ? 'Done' : 'Todo');

        if (catalogMode) {
            const isComplete = state.status === 'all' && state.part === 'all' && !state.query;
            listCountEl.textContent = `${isComplete ? '完整列出' : '筛选后'} ${matchedItems.length} 项`;
        } else {
            listCountEl.textContent = matchedItems.length === renderedItems.length
                ? `${matchedItems.length} shown`
                : `${renderedItems.length} of ${matchedItems.length} shown`;
        }

        if (!matchedItems.length) {
            listEl.appendChild(message('series-empty', 'No works match the current filters.'));
        } else if (catalogMode) {
            renderCompactCatalog(renderedItems);
        } else {
            renderedItems.forEach(item => listEl.appendChild(renderWorkCard(item)));
        }

        if (loadMoreButton) {
            loadMoreButton.hidden = catalogMode || renderedItems.length >= matchedItems.length;
            loadMoreButton.textContent = `Load ${Math.min(pageSize(), matchedItems.length - renderedItems.length)} more`;
        }
    }

    function renderCompactCatalog(items) {
        const shouldGroup = state.sort === 'series' && state.part === 'all';
        if (!shouldGroup) {
            listEl.appendChild(compactCatalogList(items));
            return;
        }

        uniqueParts(items).forEach(part => {
            const groupItems = items.filter(item => item.seriesPart === part);
            if (!groupItems.length) return;

            const section = document.createElement('section');
            section.className = 'compact-catalog-group';

            const heading = document.createElement('h3');
            heading.className = 'catalog-group-header';
            heading.textContent = part;
            const group = (currentSeries.groups || []).find(candidate => candidate.label === part);
            if (group && group.color) heading.dataset.color = group.color;

            const count = document.createElement('span');
            count.textContent = `${groupItems.length} 项`;
            heading.appendChild(count);

            section.appendChild(heading);
            section.appendChild(compactCatalogList(groupItems));
            listEl.appendChild(section);
        });
    }

    function compactCatalogList(items) {
        const list = document.createElement('ol');
        list.className = 'compact-catalog-list';
        items.forEach(item => list.appendChild(compactCatalogItem(item)));
        return list;
    }

    function compactCatalogItem(item) {
        const row = document.createElement('li');
        row.className = 'compact-catalog-item';
        row.dataset.status = item.status;
        row.dataset.match = item.matchStatus || '';
        row.id = anchorId(item);

        const code = document.createElement('span');
        code.className = 'catalog-code';
        code.textContent = item.catalogCode || item.awardYear || String(item.sequence || '');

        const title = document.createElement(item.href ? 'a' : 'span');
        title.className = 'catalog-title';
        if (item.href) title.href = item.href;
        title.textContent = item.displayTitle || item.workId;
        if (item.annotation) title.title = item.annotation;

        const person = document.createElement('span');
        person.className = 'catalog-person';
        person.textContent = item.personOrScope || item.kind || '';

        const status = document.createElement('span');
        status.className = 'catalog-status';
        status.textContent = item.matchStatus === 'candidate'
            ? '候选'
            : item.status === 'done' ? '已读' : '未读';

        row.appendChild(code);
        row.appendChild(title);
        row.appendChild(person);
        row.appendChild(status);
        return row;
    }

    function filteredItems(items) {
        const query = normalizeSearch(state.query);
        return items.filter(item => {
            if (state.status !== 'all' && item.status !== state.status) return false;
            if (state.part !== 'all' && item.seriesPart !== state.part) return false;
            if (!query) return true;
            return normalizeSearch([
                item.displayTitle,
                item.personOrScope,
                item.seriesPart,
                item.catalogCode,
                item.awardYear,
                ...(item.sourceNames || [])
            ].filter(Boolean).join(' ')).includes(query);
        });
    }

    function normalizeSearch(value) {
        return String(value || '').normalize('NFKC').toLocaleLowerCase('zh-CN').replace(/\s+/g, '');
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
        if (Number.isFinite(a.sequence) && Number.isFinite(b.sequence) && a.sequence !== b.sequence) {
            return a.sequence - b.sequence;
        }
        const order = configuredGroupOrder();
        const partA = groupIndex(order, a.seriesPart);
        const partB = groupIndex(order, b.seriesPart);
        if (partA !== partB) return partA - partB;
        if (Number.isFinite(a.catalogIndex) && Number.isFinite(b.catalogIndex) && a.catalogIndex !== b.catalogIndex) {
            return a.catalogIndex - b.catalogIndex;
        }
        return (a.displayTitle || '').localeCompare(b.displayTitle || '', 'zh-CN');
    }

    function groupIndex(order, value) {
        const index = order.indexOf(value);
        return index === -1 ? order.length : index;
    }

    function noteSortValue(item) {
        if (item.noteId) return `0-${item.noteId}`;
        return `1-${String(item.sequence || '')}-${item.displayTitle || item.workId}`;
    }

    function renderWorkCard(item) {
        const card = document.createElement('article');
        card.className = 'work-card';
        card.id = anchorId(item);

        const main = document.createElement('div');
        main.className = 'work-main';

        const title = document.createElement(item.href ? 'a' : 'h3');
        title.className = 'work-title';
        if (item.href) title.href = item.href;
        title.textContent = item.displayTitle || item.workId;
        main.appendChild(title);

        const meta = document.createElement('div');
        meta.className = 'work-meta';
        meta.appendChild(statusPill(item));
        meta.appendChild(groupPill(item));
        if (item.catalogCode) meta.appendChild(textPill(item.catalogCode));
        if (item.awardYear) meta.appendChild(textPill(item.awardYear));
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

        if (item.annotation) {
            const annotation = document.createElement('p');
            annotation.className = 'work-annotation';
            annotation.textContent = item.annotation;
            main.appendChild(annotation);
        }

        const actions = document.createElement('div');
        actions.className = 'work-actions';
        if (item.href) {
            actions.appendChild(actionLink(item.href, '阅读页'));
        } else {
            const pending = document.createElement('span');
            pending.className = 'work-pending';
            pending.textContent = '待写阅读页';
            actions.appendChild(pending);
        }
        if (item.sourceUrl) {
            actions.appendChild(actionLink(item.sourceUrl, '来源 ↗', true));
        }

        card.appendChild(main);
        card.appendChild(actions);
        return card;
    }

    function actionLink(href, text, external) {
        const action = document.createElement('a');
        action.className = 'work-action-link';
        action.href = href;
        action.textContent = text;
        if (external) {
            action.target = '_blank';
            action.rel = 'noreferrer';
        }
        return action;
    }

    function statusPill(item) {
        const span = textPill(item.matchStatus === 'candidate' ? 'Candidate match' : item.status, 'status-pill');
        span.dataset.status = item.status;
        span.dataset.match = item.matchStatus || '';
        return span;
    }

    function groupPill(item) {
        const span = textPill(item.seriesPart, 'metric-pill series-group-pill');
        if (item.groupColor) span.dataset.color = item.groupColor;
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

    function configuredGroupOrder() {
        const configured = Array.isArray(currentSeries.groupOrder) ? currentSeries.groupOrder : [];
        return configured.length ? configured : legacyPartOrder;
    }

    function uniqueParts(items) {
        const seen = new Set(items.map(item => item.seriesPart).filter(Boolean));
        const ordered = configuredGroupOrder().filter(part => seen.has(part));
        const remainder = Array.from(seen).filter(part => !ordered.includes(part));
        return ordered.concat(remainder);
    }

    function pageSize() {
        const configured = Number(currentSeries && currentSeries.pageSize);
        return Number.isFinite(configured) && configured > 0 ? configured : Number.POSITIVE_INFINITY;
    }

    function resetVisibleLimit() {
        visibleLimit = pageSize();
    }

    function updateUrl() {
        const params = new URLSearchParams();
        if (state.status !== 'all') params.set('status', state.status);
        if (state.part !== 'all') params.set('part', state.part);
        if (state.sort !== (currentSeries.defaultSort || 'series')) params.set('sort', state.sort);
        if (state.view !== (currentSeries.defaultView || 'cards')) params.set('view', state.view);
        if (state.query) params.set('q', state.query);
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
