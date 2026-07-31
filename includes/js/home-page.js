(function () {
    const corpus = window.HOMEPAGE_DATA || { items: [], stats: { byType: {}, years: {} } };
    const plane = window.SITE_PLANE || {};
    const items = Array.isArray(corpus.items) ? corpus.items : [];
    const stats = corpus.stats || {};
    const projection = window.PROJECTION_TRUTH || { state: 'catalogued', label: 'dated projection', stale: false };

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
        setText('pulse-observation', projection.label);
        const marker = document.getElementById('pulse-freshness');
        if (marker) {
            marker.dataset.state = projection.state;
            marker.textContent = projection.label;
        }
        const pulse = document.querySelector('.control-pulse');
        if (pulse) pulse.dataset.projectionState = projection.state;
    }

    function renderFields() {
        const host = document.getElementById('field-grid');
        if (!host) return;
        const lines = Array.isArray(plane.narrativeLines)
            ? plane.narrativeLines
            : (((plane.narrative_lines || {}).items) || []);
        host.innerHTML = '';
        const coverage = narrativeCoverage();
        setText('field-coverage', `${coverage.mapped} / ${coverage.total} mapped`);
        const newestFieldId = items.length ? itemFieldIds(items[0])[0] : '';
        const currentFieldId = newestFieldId || (lines[0] && (lines[0].id || lines[0].title_zh || lines[0].title));
        const orderedLines = lines.slice().sort((left, right) => {
            const leftId = left.id || left.title_zh || left.title;
            const rightId = right.id || right.title_zh || right.title;
            return Number(rightId === currentFieldId) - Number(leftId === currentFieldId);
        });
        orderedLines.forEach(line => {
            const entry = document.createElement('li');
            entry.className = 'field-register-entry';
            const card = document.createElement('a');
            card.className = 'field-card';
            const fieldTitle = line.title || line.title_zh || 'Untitled field';
            card.href = line.href || `./archive.html?series=${encodeURIComponent(fieldTitle)}`;
            const fieldId = line.id || fieldTitle;
            const declaredIndex = lines.indexOf(line);
            const mappedCount = countFieldItems(line);
            const isCurrent = fieldId === currentFieldId;
            entry.dataset.state = isCurrent ? 'current' : 'catalogued';
            card.dataset.state = entry.dataset.state;

            const fieldIndex = document.createElement('span');
            fieldIndex.className = 'field-index';
            fieldIndex.textContent = String(declaredIndex + 1).padStart(2, '0') + ' / FIELD';

            const title = document.createElement('h3');
            title.textContent = fieldTitle;

            const question = document.createElement('p');
            question.textContent = line.question || line.core_question_zh || line.summary || '';

            const meta = document.createElement('span');
            meta.className = 'field-card-meta';
            const state = document.createElement('span');
            state.className = 'state-marker';
            state.dataset.state = isCurrent ? 'current' : 'catalogued';
            state.textContent = isCurrent ? 'Current line' : (line.evidenceState || line.status || 'Catalogued');
            const count = document.createElement('span');
            count.textContent = `${mappedCount} mapped / ${items.length} corpus`;
            meta.appendChild(state);
            meta.appendChild(count);

            card.appendChild(fieldIndex);
            card.appendChild(title);
            card.appendChild(question);
            card.appendChild(meta);
            entry.appendChild(card);
            host.appendChild(entry);
        });
    }

    function renderEvidence() {
        const host = document.getElementById('latest-evidence');
        if (!host) return;
        host.innerHTML = '';
        items.slice(0, 7).forEach((item, index) => {
            const li = document.createElement('li');
            li.className = 'evidence-item';
            li.dataset.state = index === 0 ? 'current' : 'displayed';

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
            const state = document.createElement('span');
            state.className = 'state-marker';
            state.dataset.state = index === 0 ? 'current' : 'displayed';
            state.textContent = index === 0 ? 'Current' : 'Displayed';
            const source = document.createElement('span');
            source.className = 'summary-source';
            source.textContent = item.summarySource === 'explicit' ? 'authored summary' : 'derived excerpt';
            kind.appendChild(state);
            kind.appendChild(document.createTextNode(item.type));
            kind.appendChild(source);

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
        const coverage = narrativeCoverage();
        setText('metric-total', stats.total || items.length);
        setText('metric-years', years.length);
        setText('metric-tagged', tagged);
        setText('metric-series', series);
        setText('metric-mapped', `${coverage.mapped}/${coverage.total}`);
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

            const article = document.createElement('li');
            article.className = 'selected-card';
            article.dataset.state = 'displayed';
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
            const marker = document.createElement('span');
            marker.className = 'state-marker';
            marker.dataset.state = 'displayed';
            marker.textContent = 'Displayed';
            meta.appendChild(marker);
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
        const fieldId = line.id || line.title || line.title_zh;
        const explicit = items.filter(item => itemFieldIds(item).includes(fieldId));
        if (explicit.length) return explicit.length;
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

    function itemFieldIds(item) {
        if (Array.isArray(item.fieldIds)) return item.fieldIds;
        if (Array.isArray(item.field_ids)) return item.field_ids;
        return [];
    }

    function narrativeCoverage() {
        const generated = stats.narrativeCoverage || {};
        if (Number.isFinite(generated.mapped) && Number.isFinite(generated.total)) return generated;
        return {
            mapped: items.filter(item => itemFieldIds(item).length).length,
            total: items.length
        };
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
