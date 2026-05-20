(function () {
    const data = window.HOMEPAGE_DATA || { items: [], stats: { byType: {}, years: {} } };
    const allItems = data.items || [];
    const collection = document.body.dataset.collection || '';
    const items = collection ? allItems.filter(item => item.type === collection) : allItems;
    const summaryEl = document.getElementById('archive-summary');
    const listEl = document.getElementById('archive-list');

    setActiveNav(collection || 'Archive');
    renderSummary();
    renderList();

    if (window.location.hash) {
        window.requestAnimationFrame(() => {
            const target = document.getElementById(decodeURIComponent(window.location.hash.slice(1)));
            if (target) target.scrollIntoView();
        });
    }

    function renderSummary() {
        const yearCount = new Set(items.map(item => item.published.slice(0, 4))).size;
        if (!collection) {
            summaryEl.textContent = `${items.length} notes across ${yearCount} years, ordered by publication date.`;
            return;
        }

        summaryEl.textContent = `${items.length} ${collection} notes, with created and updated dates preserved for each entry.`;
    }

    function renderList() {
        listEl.innerHTML = '';
        if (!items.length) {
            const empty = document.createElement('p');
            empty.className = 'archive-empty';
            empty.textContent = 'No published notes yet.';
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
        count.textContent = `${yearItems.length} notes`;
        heading.appendChild(count);

        const list = document.createElement('ul');
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
        date.dateTime = item.published;
        date.textContent = item.published;

        const main = document.createElement('div');
        main.className = 'archive-note-main';

        const link = document.createElement('a');
        link.className = 'archive-note-title';
        link.href = item.href;
        link.textContent = item.title;

        const meta = document.createElement('div');
        meta.className = 'archive-note-meta';
        meta.textContent = `${item.type} · 创建 ${item.createdDate} · 更新 ${item.updatedDate}`;

        main.appendChild(link);
        main.appendChild(meta);
        li.appendChild(date);
        li.appendChild(main);
        return li;
    }

    function groupByYear(source) {
        const map = new Map();
        source.forEach(item => {
            const year = item.published.slice(0, 4);
            if (!map.has(year)) map.set(year, []);
            map.get(year).push(item);
        });

        return Array.from(map.entries())
            .sort((a, b) => b[0].localeCompare(a[0]))
            .map(([year, yearItems]) => ({ year, items: yearItems }));
    }

    function setActiveNav(name) {
        document.querySelectorAll('[data-nav]').forEach(link => {
            if (link.dataset.nav === name) link.classList.add('is-active');
        });
    }
})();
