(function () {
    const dataUrl = './data/series-books.json';
    const summaryEl = document.getElementById('series-summary');
    const listEl = document.getElementById('series-list');

    loadSeriesData()
        .then(render)
        .catch(error => {
            summaryEl.textContent = 'Series data could not be loaded.';
            listEl.appendChild(message('series-error', error.message));
        });

    async function loadSeriesData() {
        const response = await fetch(dataUrl);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status} loading ${dataUrl}`);
        }
        return response.json();
    }

    function render(data) {
        const series = Array.isArray(data.series) ? data.series : [];
        summaryEl.textContent = `${series.length} series, grouped by reading progress and public note links.`;
        listEl.innerHTML = '';

        if (!series.length) {
            listEl.appendChild(message('series-empty', 'No series have been registered yet.'));
            return;
        }

        series.forEach(item => listEl.appendChild(renderSeriesCard(item)));
    }

    function renderSeriesCard(series) {
        const counts = countItems(series.items || []);
        const link = document.createElement('a');
        link.className = 'series-card';
        link.href = series.href || `./series/${series.slug}/`;

        const title = document.createElement('h2');
        title.textContent = series.displayTitle || series.title || series.slug;

        const description = document.createElement('p');
        description.textContent = series.description || '';

        const meta = document.createElement('div');
        meta.className = 'series-card-meta';
        meta.appendChild(pill('metric-pill', `${counts.total} works`));
        meta.appendChild(pill('metric-pill', `${counts.done} done`));
        meta.appendChild(pill('metric-pill', `${counts.todo} todo`));
        if (counts.candidate) {
            meta.appendChild(pill('metric-pill', `${counts.candidate} candidate`));
        }

        const tags = document.createElement('div');
        tags.className = 'tag-list';
        (series.tags || []).forEach(tag => tags.appendChild(pill('tag-pill', tag)));
        if (series.lastUpdated) {
            tags.appendChild(pill('tag-pill', `updated ${series.lastUpdated}`));
        }

        link.appendChild(title);
        link.appendChild(description);
        link.appendChild(meta);
        link.appendChild(tags);
        return link;
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

    function pill(className, text) {
        const span = document.createElement('span');
        span.className = className;
        span.textContent = text;
        return span;
    }

    function message(className, text) {
        const node = document.createElement('p');
        node.className = className;
        node.textContent = text;
        return node;
    }
})();
