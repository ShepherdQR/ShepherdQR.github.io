(function () {
    const content = document.getElementById('markdown-content');
    const titleEl = document.getElementById('currentInnerTitle');
    const metaEl = document.getElementById('currentInnerMeta');
    const typeEl = document.getElementById('currentInnerType');
    const neighborsEl = document.getElementById('article-neighbors');

    if (!content || !titleEl || !metaEl || !typeEl) return;

    const config = readArticleConfig();
    let mdFile = config.md;

    if (!mdFile) {
        renderError('缺少参数：?md=/qrthoughts/.../[Type][0001][Title].md');
        return;
    }

    mdFile = ensureMarkdownExtension(normalizeRootPath(mdFile));
    applyCanonical(config.canonical);

    if (window.marked && typeof window.marked.setOptions === 'function') {
        window.marked.setOptions({ gfm: true, breaks: true });
    }

    content.innerHTML = '<p class="article-loading">Loading...</p>';

    fetch(encodeFetchPath(mdFile))
        .then(res => {
            if (!res.ok) throw new Error('文件不存在：' + mdFile);
            return res.text();
        })
        .then(mdText => {
            const parsed = parseMarkdownDocument(mdText);
            const titleMatch = parsed.body.match(/^#\s+(.*)/m);
            const title = parsed.meta.title || (titleMatch ? titleMatch[1].trim() : 'Untitled');
            const firstHeading = titleMatch ? titleMatch[1].trim() : '';
            const contentMd = firstHeading === title ? parsed.body.replace(/^\s*#\s+.*\n?/, '') : parsed.body;

            document.title = title;
            titleEl.textContent = title;
            typeEl.textContent = [parsed.meta.type, parsed.meta.id].filter(Boolean).join(' · ');
            metaEl.textContent = formatArticleMeta(parsed.meta);
            content.innerHTML = renderMarkdown(contentMd);

            activateEmbeddedScripts(content);
            renderArticleNeighbors(parsed.meta, mdFile, config);
            if (config.math) scheduleMathJax();
        })
        .catch(err => {
            renderError('加载失败：' + err.message);
            console.error(err);
        });

    function readArticleConfig() {
        const params = new URLSearchParams(window.location.search);
        const queryMd = params.get('md');
        const embedded = readEmbeddedConfig();

        return {
            md: queryMd || embedded.md || '',
            canonical: embedded.canonical || embedded.canonicalHref || '',
            math: typeof embedded.math === 'boolean'
                ? embedded.math
                : Boolean(document.getElementById('MathJax-script')),
            interactive: typeof embedded.interactive === 'boolean'
                ? embedded.interactive
                : Boolean(document.querySelector('script[src*="/d3.js"]'))
        };
    }

    function readEmbeddedConfig() {
        const configEl = document.getElementById('article-config');
        if (!configEl) return {};

        try {
            return JSON.parse(configEl.textContent || '{}') || {};
        } catch (e) {
            console.warn('Invalid article config:', e);
            return {};
        }
    }

    function applyCanonical(canonical) {
        if (!canonical) return;

        const href = absolutizeSiteHref(canonical);
        let link = document.querySelector('link[rel="canonical"]');
        if (!link) {
            link = document.createElement('link');
            link.rel = 'canonical';
            document.head.appendChild(link);
        }
        link.href = new URL(href, window.location.origin).href;
    }

    function renderError(message) {
        titleEl.textContent = 'Page unavailable';
        metaEl.textContent = '';
        typeEl.textContent = '';
        content.innerHTML = '<p class="article-error">' + escapeHtml(message) + '</p>';
        if (neighborsEl) {
            neighborsEl.innerHTML = '';
            neighborsEl.hidden = true;
        }
    }

    function parseMarkdownDocument(rawText) {
        const meta = {};
        let body = rawText.replace(/^\uFEFF/, '');
        body = stripLeadingHtmlComments(body);
        const frontMatterMatch = body.match(/^---\s*\n([\s\S]*?)\n---\s*\n?/);

        if (frontMatterMatch) {
            frontMatterMatch[1].split(/\r?\n/).forEach(line => {
                if (/^\s/.test(line)) return;
                const field = line.match(/^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$/);
                if (!field) return;
                let value = field[2].trim();
                if (value.startsWith('"') && value.endsWith('"')) {
                    value = value.slice(1, -1).replace(/\\"/g, '"').replace(/\\\\/g, '\\');
                }
                meta[field[1]] = value;
            });
            body = body.slice(frontMatterMatch[0].length);
        }

        body = stripLeadingHtmlComments(body);
        return { meta, body };
    }

    function stripLeadingHtmlComments(source) {
        return source.replace(/^(?:<!--[\s\S]*?-->\s*)+/, '');
    }

    function formatArticleMeta(meta) {
        const parts = [];
        if (meta.created_date) parts.push('创建 ' + meta.created_date);
        if (meta.published && meta.published !== meta.created_date) parts.push('发布 ' + meta.published);
        if (meta.updated_date) parts.push('更新 ' + meta.updated_date);
        return parts.join(' · ');
    }

    function renderMarkdown(source) {
        if (!window.marked || typeof window.marked.parse !== 'function') {
            return '<pre>' + escapeHtml(source) + '</pre>';
        }
        return window.marked.parse(source);
    }

    function renderArticleNeighbors(meta, currentPath, config) {
        if (!neighborsEl) return;

        const items = ((window.HOMEPAGE_DATA || {}).items || []);
        const currentItem = findCurrentItem(items, meta, currentPath, config);
        const currentIndex = currentItem ? items.indexOf(currentItem) : -1;

        neighborsEl.innerHTML = '';
        if (currentIndex < 0) {
            neighborsEl.hidden = true;
            return;
        }
        applyCanonical(currentItem.canonicalHref || currentItem.href);

        const entries = [
            { label: '较新', item: items[currentIndex - 1] },
            { label: '较早', item: items[currentIndex + 1] }
        ].filter(entry => entry.item);

        if (!entries.length) {
            neighborsEl.hidden = true;
            return;
        }

        neighborsEl.hidden = false;
        entries.forEach(entry => neighborsEl.appendChild(renderNeighbor(entry.label, entry.item)));
    }

    function renderNeighbor(label, item) {
        const link = document.createElement('a');
        link.className = 'article-neighbor';
        link.href = hrefFromItem(item);

        const labelEl = document.createElement('span');
        labelEl.className = 'article-neighbor-label';
        labelEl.textContent = label;

        const title = document.createElement('span');
        title.className = 'article-neighbor-title';
        title.textContent = item.title;

        const date = document.createElement('time');
        date.className = 'article-neighbor-date';
        date.dateTime = item.published || '';
        date.textContent = [item.published, item.type, item.updatedDate ? '更新 ' + item.updatedDate : ''].filter(Boolean).join(' · ');

        link.appendChild(labelEl);
        link.appendChild(title);
        link.appendChild(date);
        return link;
    }

    function findCurrentItem(items, meta, currentPath, config) {
        const direct = items.find(item => item.type === meta.type && item.id === meta.id);
        if (direct) return direct;

        const normalizedCurrent = normalizeMdPath(currentPath);
        const normalizedCanonical = normalizeHrefPath(config.canonical);
        return items.find(item => {
            if (normalizeMdPath(pathFromItem(item)) === normalizedCurrent) return true;
            return normalizedCanonical && itemHrefCandidates(item).some(href => normalizeHrefPath(href) === normalizedCanonical);
        });
    }

    function pathFromItem(item) {
        if (item.sourcePath) return item.sourcePath;

        const hrefs = itemHrefCandidates(item);
        for (const href of hrefs) {
            const md = mdFromHref(href);
            if (md) return md;
        }
        return hrefs[0] || '';
    }

    function hrefFromItem(item) {
        const href = item.canonicalHref || item.href || item.legacyHref || '';
        return absolutizeSiteHref(href);
    }

    function itemHrefCandidates(item) {
        return [item.sourcePath, item.canonicalHref, item.href, item.legacyHref].filter(Boolean);
    }

    function mdFromHref(href) {
        try {
            const url = new URL(href, window.location.origin + '/');
            return url.searchParams.get('md') || '';
        } catch (e) {
            const match = String(href || '').match(/[?&]md=([^&]+)/);
            return match ? match[1] : '';
        }
    }

    function normalizeMdPath(value) {
        let path = decodeURIComponent(value || '').replace(/\\/g, '/');
        const md = mdFromHref(path);
        if (md) path = md;
        path = path.split('#')[0].split('?')[0];
        path = normalizeRootPath(path);
        return ensureMarkdownExtension(path);
    }

    function normalizeHrefPath(value) {
        if (!value) return '';
        try {
            return new URL(absolutizeSiteHref(value), window.location.origin).pathname.replace(/\/index\.html$/i, '/');
        } catch (e) {
            return normalizeRootPath(value).replace(/\/index\.html$/i, '/');
        }
    }

    function normalizeRootPath(value) {
        let path = String(value || '').trim().replace(/\\/g, '/');
        if (!path) return '';
        if (/^[a-z][a-z0-9+.-]*:/i.test(path) || path.startsWith('//')) return path;
        if (path.startsWith('./')) path = path.slice(2);
        if (path.startsWith('../')) {
            return new URL(path, window.location.href).pathname;
        }
        return path.startsWith('/') ? path : '/' + path;
    }

    function ensureMarkdownExtension(path) {
        if (!path || /^[a-z][a-z0-9+.-]*:/i.test(path)) return path;
        return /\.(md|html)$/i.test(path) ? path : path + '.md';
    }

    function absolutizeSiteHref(href) {
        if (!href) return '';
        if (/^[a-z][a-z0-9+.-]*:/i.test(href) || href.startsWith('//') || href.startsWith('#')) return href;
        if (href.startsWith('/')) return href;
        if (href.startsWith('./')) return '/' + href.slice(2);
        if (href.startsWith('../')) return new URL(href, window.location.href).pathname;
        return '/' + href;
    }

    function activateEmbeddedScripts(container) {
        container.querySelectorAll('script').forEach(oldScript => {
            const script = document.createElement('script');
            Array.from(oldScript.attributes).forEach(attr => script.setAttribute(attr.name, attr.value));
            script.textContent = oldScript.textContent;
            oldScript.replaceWith(script);
        });
    }

    function scheduleMathJax() {
        const maxWait = 5000;
        const interval = 100;
        const startTime = Date.now();

        function tryTypeset() {
            if (window.MathJax && window.MathJax.startup) {
                window.MathJax.startup.promise
                    .then(function () {
                        if (typeof window.MathJax.typesetPromise === 'function') {
                            return window.MathJax.typesetPromise();
                        }
                        if (typeof window.MathJax.typeset === 'function') {
                            window.MathJax.typeset();
                        }
                    })
                    .catch(function (e) {
                        console.warn('MathJax typeset failed:', e);
                    });
            } else if (Date.now() - startTime < maxWait) {
                setTimeout(tryTypeset, interval);
            }
        }

        tryTypeset();
    }

    function encodeFetchPath(path) {
        if (/^[a-z][a-z0-9+.-]*:/i.test(path) || path.startsWith('//')) return path;
        return path
            .split('/')
            .map(function (segment, index) {
                if (!segment && index === 0) return '';
                return encodeURIComponent(segment);
            })
            .join('/');
    }

    function escapeHtml(value) {
        return String(value).replace(/[&<>"']/g, ch => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        })[ch]);
    }
})();
