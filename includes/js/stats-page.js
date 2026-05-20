(function () {
    const data = window.HOMEPAGE_DATA || { items: [], stats: { byType: {}, years: {} } };
    const items = data.items || [];
    const stats = data.stats || {};
    const byType = stats.byType || {};
    const years = stats.years || {};

    setActiveNav('Stats');
    renderSummary();
    renderOverview();
    renderTypes();
    renderYears();

    function renderSummary() {
        const summaryEl = document.getElementById('archive-summary');
        const yearCount = Object.keys(years).length;
        summaryEl.textContent = `${items.length} published notes across ${yearCount} years. Counts are generated from Markdown front matter.`;
    }

    function renderOverview() {
        const host = document.getElementById('stats-overview');
        host.appendChild(renderMetric(items.length, 'Published notes'));
        host.appendChild(renderMetric(byType.Books || 0, 'Books'));
        host.appendChild(renderMetric(byType.Thoughts || 0, 'Thoughts'));
    }

    function renderTypes() {
        const rows = ['Books', 'Thoughts', 'Study', 'Videos']
            .map(type => [type, byType[type] || 0]);
        renderTable('stats-types', ['Collection', 'Notes'], rows);
    }

    function renderYears() {
        const rows = Object.keys(years)
            .sort((a, b) => b.localeCompare(a))
            .map(year => [year, years[year]]);
        renderTable('stats-years', ['Year', 'Notes'], rows);
    }

    function renderMetric(value, label) {
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

    function renderTable(hostId, headers, rows) {
        const host = document.getElementById(hostId);
        const table = document.createElement('table');
        table.className = 'stats-table';

        const thead = document.createElement('thead');
        const headRow = document.createElement('tr');
        headers.forEach(header => {
            const th = document.createElement('th');
            th.textContent = header;
            headRow.appendChild(th);
        });
        thead.appendChild(headRow);

        const tbody = document.createElement('tbody');
        rows.forEach(row => {
            const tr = document.createElement('tr');
            row.forEach(cell => {
                const td = document.createElement('td');
                td.textContent = cell;
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });

        table.appendChild(thead);
        table.appendChild(tbody);
        host.appendChild(table);
    }

    function setActiveNav(name) {
        document.querySelectorAll('[data-nav]').forEach(link => {
            if (link.dataset.nav === name) link.classList.add('is-active');
        });
    }
})();
