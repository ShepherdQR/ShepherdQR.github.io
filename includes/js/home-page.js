(function () {
    const corpus = window.HOMEPAGE_DATA || { items: [], stats: { byType: {}, years: {} } };
    const plane = window.SITE_PLANE || {};
    const items = Array.isArray(corpus.items) ? corpus.items : [];
    const stats = corpus.stats || {};

    renderPulse();
    renderFields();
    renderEvidence();
    renderCorpus();
    renderSelected();
    renderPrinciples();

    function renderPulse() {
        const control = plane.control || {};
        const governance = plane.governance || {};
        const baseline = plane.control_plane_baseline || {};
        const site = plane.site || {};
        const level = control.level || governance.control_level || 'L1';
        setText('pulse-status', control.label || `${level} advisory`);
        setText('pulse-summary', control.publicStatement || site.boundary_statement_zh || 'Human-owned, evidence-gated public knowledge interface.');
        setText('pulse-level', level);
        setText('pulse-owner', control.owner || site.owner || 'human');
        setText('pulse-authority', formatAuthority(control.authorityEffects ?? governance.authority_effect));
        setText('pulse-as-of', control.asOf || baseline.as_of || plane.asOf || corpus.generatedAt || '—');
    }

    function renderFields() {
        const host = document.getElementById('field-grid');
        if (!host) return;
        const lines = Array.isArray(plane.narrativeLines)
            ? plane.narrativeLines
            : (((plane.narrative_lines || {}).items) || []);
        host.innerHTML = '';
        lines.forEach((line, index) => {
            const card = document.createElement('a');
            card.className = 'field-card';
            const fieldTitle = line.title || line.title_zh || 'Untitled field';
            card.href = line.href || `./archive.html?series=${encodeURIComponent(fieldTitle)}`;

            const fieldIndex = document.createElement('span');
            fieldIndex.className = 'field-index';
            fieldIndex.textContent = String(index + 1).padStart(2, '0') + ' / FIELD';

            const title = document.createElement('h3');
            title.textContent = fieldTitle;

            const question = document.createElement('p');
            question.textContent = line.question || line.core_question_zh || line.summary || '';

            const meta = document.createElement('span');
            meta.className = 'field-card-meta';
            const state = document.createElement('span');
            state.textContent = line.evidenceState || line.status || 'declared';
            const count = document.createElement('span');
            count.textContent = countFieldItems(line) + ' objects';
            meta.appendChild(state);
            meta.appendChild(count);

            card.appendChild(fieldIndex);
            card.appendChild(title);
            card.appendChild(question);
            card.appendChild(meta);
            host.appendChild(card);
        });
    }

    function renderEvidence() {
        const host = document.getElementById('latest-evidence');
        if (!host) return;
        host.innerHTML = '';
        items.slice(0, 7).forEach(item => {
            const li = document.createElement('li');
            li.className = 'evidence-item';

            const date = document.createElement('time');
            date.className = 'evidence-date';
            date.dateTime = item.published || '';
            date.textContent = item.published || '—';

            const main = document.createElement('div');
            main.className = 'evidence-main';
            const link = document.createElement('a');
            link.className = 'evidence-title';
            link.href = item.href;
            link.textContent = item.title;
            const summary = document.createElement('p');
            summary.className = 'evidence-summary';
            summary.textContent = item.summary || `${item.type} ${item.id}`;
            main.appendChild(link);
            main.appendChild(summary);

            const kind = document.createElement('span');
            kind.className = 'evidence-kind';
            kind.textContent = item.type;

            li.appendChild(date);
            li.appendChild(main);
            li.appendChild(kind);
            host.appendChild(li);
        });
    }

    function renderCorpus() {
        const years = Object.keys(stats.years || {});
        const tagged = items.filter(item => Array.isArray(item.tags) && item.tags.length).length;
        const series = new Set(items.map(item => item.series).filter(Boolean)).size;
        setText('metric-total', stats.total || items.length);
        setText('metric-years', years.length);
        setText('metric-tagged', tagged);
        setText('metric-series', series);
    }

    function renderSelected() {
        const host = document.getElementById('selected-grid');
        if (!host) return;
        const selections = Array.isArray(plane.selected)
            ? plane.selected
            : (((plane.selected_entries || {}).items) || []);
        host.innerHTML = '';
        selections.forEach((selection, index) => {
            const item = items.find(candidate => candidate.type === selection.type && candidate.id === selection.id);
            if (!item) return;

            const article = document.createElement('article');
            article.className = 'selected-card';
            const accession = document.createElement('p');
            accession.className = 'accession';
            accession.textContent = `ENTRY ${String(index + 1).padStart(2, '0')} · ${item.type} ${item.id}`;
            const title = document.createElement('h3');
            const link = document.createElement('a');
            link.href = item.href;
            link.textContent = item.title;
            title.appendChild(link);
            const annotation = document.createElement('p');
            annotation.textContent = selection.annotation || item.summary || '';
            const meta = document.createElement('div');
            meta.className = 'selected-meta';
            [selection.field, item.series, item.published].filter(Boolean).forEach(value => {
                const chip = document.createElement('span');
                chip.className = 'meta-chip';
                chip.textContent = value;
                meta.appendChild(chip);
            });

            article.appendChild(accession);
            article.appendChild(title);
            article.appendChild(annotation);
            article.appendChild(meta);
            host.appendChild(article);
        });
    }

    function renderPrinciples() {
        const host = document.getElementById('about-principles');
        if (!host) return;
        const principles = Array.isArray(plane.principles)
            ? plane.principles
            : (Array.isArray(plane.public_principles) ? plane.public_principles : []);
        host.innerHTML = '';
        principles.slice(0, 4).forEach(principle => {
            const item = document.createElement('div');
            item.className = 'about-principle';
            const title = document.createElement('strong');
            title.textContent = principle.title || principle;
            const detail = document.createElement('span');
            detail.textContent = principle.detail || '';
            item.appendChild(title);
            item.appendChild(detail);
            host.appendChild(item);
        });
    }

    function countFieldItems(line) {
        const fallbackSeries = line.title || line.title_zh;
        const seriesNames = Array.isArray(line.series_filters)
            ? line.series_filters
            : (Array.isArray(line.series) ? line.series : [line.series || fallbackSeries].filter(Boolean));
        const tags = Array.isArray(line.tags) ? line.tags : [];
        return items.filter(item => {
            if (item.series && seriesNames.includes(item.series)) return true;
            return Array.isArray(item.tags) && item.tags.some(tag => tags.includes(tag));
        }).length;
    }

    function formatAuthority(value) {
        if (value === 0 || value === '0') return 'none';
        return value === undefined || value === null ? 'none' : String(value);
    }

    function setText(id, value) {
        const node = document.getElementById(id);
        if (node) node.textContent = String(value);
    }
})();
