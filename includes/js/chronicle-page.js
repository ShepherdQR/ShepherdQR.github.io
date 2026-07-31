(function () {
    const plane = window.SITE_PLANE || {};
    const corpus = window.HOMEPAGE_DATA || { items: [] };
    const items = Array.isArray(corpus.items) ? corpus.items : [];
    const baseline = plane.control_plane_baseline || {};
    const frontier = baseline.evolution_frontier || {};
    const candidate = frontier.next_stage_candidate || {};
    const projection = window.PROJECTION_TRUTH || { state: 'catalogued', label: 'dated projection' };

    renderControlRecord();
    renderPublicationSpine();

    function renderControlRecord() {
        const host = document.getElementById('control-chronicle-object');
        if (!host) return;
        const article = document.createElement('article');
        article.className = 'chronicle-control-object folio';
        article.dataset.state = projection.state;
        const marker = document.createElement('span');
        marker.className = 'state-marker';
        marker.dataset.state = projection.state;
        marker.textContent = projection.label;
        const heading = document.createElement('h3');
        heading.textContent = candidate.title_zh || candidate.title || 'Next-stage candidate';
        const invariant = document.createElement('blockquote');
        invariant.textContent = candidate.derived_invariant_zh || candidate.derived_invariant || 'Origin is federated; effect is governed.';
        const registry = document.createElement('dl');
        registry.className = 'object-registry';
        [
            ['As known at', baseline.as_of || 'undated'],
            ['Lifecycle', candidate.status || 'catalogued'],
            ['Canonical registry changed', candidate.canonical_stage_registry_changed ? 'yes' : 'no'],
            ['Adoption authorized', candidate.adoption_authorized ? 'yes' : 'no'],
            ['Authority effect', candidate.authority_effect || 'none']
        ].forEach(([key, value]) => registry.appendChild(registerRow(key, value)));
        article.appendChild(marker);
        article.appendChild(heading);
        article.appendChild(invariant);
        article.appendChild(registry);
        host.appendChild(article);
    }

    function renderPublicationSpine() {
        const host = document.getElementById('chronicle-spine');
        if (!host) return;
        const groups = groupByYear(items);
        groups.forEach((group, index) => {
            const li = document.createElement('li');
            li.className = 'chronicle-year';
            li.dataset.state = index === 0 ? 'current' : 'displayed';
            const rail = document.createElement('div');
            rail.className = 'chronicle-year-mark';
            const year = document.createElement('time');
            year.dateTime = `${group.year}-01-01`;
            year.textContent = group.year;
            const count = document.createElement('span');
            count.textContent = `${group.items.length} accessioned`;
            rail.appendChild(year);
            rail.appendChild(count);
            const body = document.createElement('div');
            body.className = 'chronicle-year-body';
            const marker = document.createElement('span');
            marker.className = 'state-marker';
            marker.dataset.state = index === 0 ? 'current' : 'displayed';
            marker.textContent = index === 0 ? 'Current publication year' : 'Displayed history';
            const list = document.createElement('ol');
            group.items.slice(0, 6).forEach(item => list.appendChild(renderObject(item)));
            const more = document.createElement('a');
            more.className = 'chronicle-more';
            more.href = `./archive.html?year=${encodeURIComponent(group.year)}&view=ledger`;
            more.textContent = `读取 ${group.year} 完整登记线 →`;
            body.appendChild(marker);
            body.appendChild(list);
            body.appendChild(more);
            li.appendChild(rail);
            li.appendChild(body);
            host.appendChild(li);
        });
    }

    function renderObject(item) {
        const li = document.createElement('li');
        li.dataset.state = item.supersededBy || item.superseded_by ? 'superseded' : 'displayed';
        const date = document.createElement('time');
        date.dateTime = item.published || '';
        date.textContent = item.published || 'undated';
        const link = document.createElement('a');
        link.href = item.href;
        link.textContent = item.title;
        const meta = document.createElement('span');
        meta.textContent = `${item.type} ${item.id} · ${item.summarySource === 'explicit' ? 'authored summary' : 'derived excerpt'}`;
        li.appendChild(date);
        li.appendChild(link);
        li.appendChild(meta);
        return li;
    }

    function groupByYear(source) {
        const groups = new Map();
        source.forEach(item => {
            const year = String(item.published || '').slice(0, 4) || 'Undated';
            if (!groups.has(year)) groups.set(year, []);
            groups.get(year).push(item);
        });
        return Array.from(groups.entries())
            .sort((a, b) => b[0].localeCompare(a[0]))
            .map(([year, yearItems]) => ({ year, items: yearItems }));
    }

    function registerRow(key, value) {
        const row = document.createElement('div');
        const dt = document.createElement('dt');
        const dd = document.createElement('dd');
        dt.textContent = key;
        dd.textContent = value;
        row.appendChild(dt);
        row.appendChild(dd);
        return row;
    }
})();
