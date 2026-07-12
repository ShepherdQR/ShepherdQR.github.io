(function () {
    const data = window.HOMEPAGE_DATA || { items: [], stats: { byType: {}, years: {} } };
    const plane = window.SITE_PLANE || {};
    const items = Array.isArray(data.items) ? data.items : [];
    const stats = data.stats || {};
    const byType = stats.byType || {};
    const years = stats.years || {};

    renderSummary();
    renderOverview();
    renderMetadata();
    renderGovernance();
    renderTypes();
    renderYears();
    renderBaseline();
    renderRecent();

    function renderSummary() {
        const tagged = items.filter(item => Array.isArray(item.tags) && item.tags.length).length;
        const summary = document.getElementById('archive-summary');
        if (summary) summary.textContent = `${items.length} public objects across ${Object.keys(years).length} years. ${tagged} now carry explicit thematic tags; every count is generated from repository evidence.`;
    }

    function renderOverview() {
        const host = document.getElementById('stats-overview');
        if (!host) return;
        host.appendChild(metric(items.length, 'Public objects'));
        host.appendChild(metric(byType.Thoughts || 0, 'Thought objects'));
        host.appendChild(metric(percent(items.filter(item => Array.isArray(item.tags) && item.tags.length).length, items.length), 'Tagged coverage'));
        host.appendChild(metric(new Set(items.map(item => item.series).filter(Boolean)).size, 'Declared series'));
    }

    function renderMetadata() {
        const rows = [
            ['Summary', items.filter(item => item.summary).length, items.length],
            ['Tags', items.filter(item => Array.isArray(item.tags) && item.tags.length).length, items.length],
            ['Series', items.filter(item => item.series).length, items.length],
            ['Lead image', items.filter(item => item.leadImage).length, items.length],
            ['Math flag', items.filter(item => item.math).length, items.length],
            ['Interactive flag', items.filter(item => item.interactive).length, items.length]
        ];
        renderKeyValues('stats-metadata', rows.map(([label, value, total]) => [label, `${value} · ${percent(value, total)}`]));
    }

    function renderGovernance() {
        const governance = plane.governance || {};
        const site = plane.site || {};
        renderKeyValues('stats-governance', [
            ['Owner', site.owner || 'human'],
            ['Control level', governance.control_level || 'L1'],
            ['Operating mode', governance.operating_mode || 'human_owned_advisory'],
            ['Authority effect', governance.authority_effect || 'none'],
            ['Standing publish', includes(governance.standing_denials, 'publish') ? 'human gate' : 'undeclared'],
            ['Resident runtime', includes(governance.standing_denials, 'resident_agent_runtime') ? 'not authorized' : 'undeclared']
        ]);
    }

    function renderTypes() {
        const rows = ['Books', 'Thoughts', 'Study', 'Videos'].map(type => [type, byType[type] || 0]);
        renderTable('stats-types', ['Collection', 'Objects'], rows);
    }

    function renderYears() {
        const rows = Object.keys(years).sort((a, b) => b.localeCompare(a)).map(year => [year, years[year]]);
        renderTable('stats-years', ['Year', 'Objects'], rows);
    }

    function renderBaseline() {
        const baseline = plane.control_plane_baseline || {};
        const frontier = baseline.evolution_frontier || {};
        const candidate = frontier.next_stage_candidate || {};
        const operational = baseline.operational_frontier || {};
        renderKeyValues('stats-baseline', [
            ['As known at', baseline.as_of || '—'],
            ['Evolution record', `${(frontier.completed_work_packages || []).length} work packages · WP0–WP8`],
            ['Next candidate', candidate.title_zh || candidate.title || '—'],
            ['Candidate state', candidate.status || '—'],
            ['Authority effect', candidate.authority_effect || 'none'],
            ['Broker process', operational.broker_process_started ? 'started' : 'not started']
        ]);
    }

    function renderRecent() {
        const host = document.getElementById('stats-recent');
        if (!host) return;
        items.slice(0, 6).forEach(item => {
            const li = document.createElement('li');
            const link = document.createElement('a');
            link.href = item.href;
            link.textContent = item.title;
            const value = document.createElement('strong');
            value.textContent = item.published;
            li.appendChild(link);
            li.appendChild(value);
            host.appendChild(li);
        });
    }

    function metric(value, label) {
        const item = document.createElement('div');
        item.className = 'stats-metric';
        const valueEl = document.createElement('span');
        valueEl.className = 'stats-metric-value';
        valueEl.textContent = value;
        const labelEl = document.createElement('span');
        labelEl.className = 'stats-metric-label';
        labelEl.textContent = label;
        item.appendChild(valueEl);
        item.appendChild(labelEl);
        return item;
    }

    function renderKeyValues(hostId, rows) {
        const host = document.getElementById(hostId);
        if (!host) return;
        rows.forEach(([label, value]) => {
            const li = document.createElement('li');
            const key = document.createElement('span');
            key.textContent = label;
            const dataValue = document.createElement('strong');
            dataValue.textContent = value;
            li.appendChild(key);
            li.appendChild(dataValue);
            host.appendChild(li);
        });
    }

    function renderTable(hostId, headers, rows) {
        const host = document.getElementById(hostId);
        if (!host) return;
        const table = document.createElement('table');
        table.className = 'stats-table';
        const thead = document.createElement('thead');
        const headRow = document.createElement('tr');
        headers.forEach(header => { const th = document.createElement('th'); th.textContent = header; headRow.appendChild(th); });
        thead.appendChild(headRow);
        const tbody = document.createElement('tbody');
        rows.forEach(row => { const tr = document.createElement('tr'); row.forEach(cell => { const td = document.createElement('td'); td.textContent = cell; tr.appendChild(td); }); tbody.appendChild(tr); });
        table.appendChild(thead); table.appendChild(tbody); host.appendChild(table);
    }

    function percent(value, total) {
        return total ? `${Math.round(value / total * 100)}%` : '0%';
    }

    function includes(values, item) {
        return Array.isArray(values) && values.includes(item);
    }
})();
