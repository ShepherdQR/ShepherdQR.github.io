(function () {
    const content = document.getElementById('markdown-content');
    const titleEl = document.getElementById('currentInnerTitle');
    const metaEl = document.getElementById('currentInnerMeta');
    const typeEl = document.getElementById('currentInnerType');
    const neighborsEl = document.getElementById('article-neighbors');

    if (!content || !titleEl || !metaEl || !typeEl) return;

    const config = readArticleConfig();
    ensureArticleChrome();
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
            const currentItem = renderArticleNeighbors(parsed.meta, mdFile, config);
            renderArticleTaxonomy(currentItem, parsed.meta);
            enhanceArticleContent();
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
        if (!neighborsEl) return null;

        const items = ((window.HOMEPAGE_DATA || {}).items || []);
        const currentItem = findCurrentItem(items, meta, currentPath, config);
        const currentIndex = currentItem ? items.indexOf(currentItem) : -1;

        neighborsEl.innerHTML = '';
        if (currentIndex < 0) {
            neighborsEl.hidden = true;
            return null;
        }
        applyCanonical(currentItem.canonicalHref || currentItem.href);

        const entries = [
            { label: '较新', item: items[currentIndex - 1] },
            { label: '较早', item: items[currentIndex + 1] }
        ].filter(entry => entry.item);

        if (!entries.length) {
            neighborsEl.hidden = true;
            return currentItem;
        }

        neighborsEl.hidden = false;
        entries.forEach(entry => neighborsEl.appendChild(renderNeighbor(entry.label, entry.item)));
        return currentItem;
    }

    function ensureArticleChrome() {
        const frame = document.querySelector('.article-frame');
        if (frame && !frame.parentElement.classList.contains('article-stage')) {
            const stage = document.createElement('div');
            stage.className = 'article-stage';
            frame.parentNode.insertBefore(stage, frame);
            stage.appendChild(frame);
        }

        if (!document.querySelector('.reading-progress')) {
            const progress = document.createElement('div');
            progress.className = 'reading-progress';
            progress.setAttribute('aria-hidden', 'true');
            const bar = document.createElement('div');
            bar.className = 'reading-progress-bar';
            progress.appendChild(bar);
            document.body.appendChild(progress);
            updateReadingProgress();
            window.addEventListener('scroll', updateReadingProgress, { passive: true });
            window.addEventListener('resize', updateReadingProgress, { passive: true });
        }

        document.querySelectorAll('.article-nav-links, .article-footer-links').forEach(nav => {
            if (nav.querySelector('a[href*="field.html"]')) return;
            const link = document.createElement('a');
            link.href = absolutizeSiteHref('field.html');
            link.textContent = 'System';
            nav.appendChild(link);
        });
    }

    function renderArticleTaxonomy(item, meta) {
        const header = document.querySelector('.article-header');
        if (!header) return;
        const old = header.querySelector('.article-header-tags');
        if (old) old.remove();

        const tags = item && Array.isArray(item.tags) ? item.tags : parseInlineList(meta.tags);
        const series = (item && item.series) || meta.series || '';
        const values = [];
        if (series) values.push({ label: series, href: '/archive.html?series=' + encodeURIComponent(series) });
        tags.forEach(tag => values.push({ label: '#' + tag, href: '/archive.html?tag=' + encodeURIComponent(tag) }));
        if (!values.length) return;

        const host = document.createElement('div');
        host.className = 'article-header-tags';
        values.forEach(value => {
            const link = document.createElement('a');
            link.href = value.href;
            link.textContent = value.label;
            host.appendChild(link);
        });
        header.appendChild(host);
    }

    function enhanceArticleContent() {
        const plainText = (content.textContent || '').replace(/\s+/g, ' ').trim();
        if (plainText) {
            const readTime = document.createElement('span');
            readTime.textContent = estimateReadingTime(plainText) + ' min read';
            metaEl.appendChild(readTime);
        }

        const headings = Array.from(content.querySelectorAll('h2, h3'));
        if (!headings.length) return;

        const seen = new Map();
        headings.forEach((heading, index) => {
            const base = slugifyHeading(heading.textContent) || `section-${index + 1}`;
            const count = seen.get(base) || 0;
            seen.set(base, count + 1);
            heading.id = count ? `${base}-${count + 1}` : base;
        });

        const stage = document.querySelector('.article-stage');
        if (!stage) return;
        const old = stage.querySelector('.article-toc');
        if (old) old.remove();

        const toc = document.createElement('aside');
        toc.className = 'article-toc';
        toc.setAttribute('aria-label', '文章目录');
        const title = document.createElement('p');
        title.className = 'article-toc-title';
        title.textContent = 'Object index';
        const list = document.createElement('ol');
        headings.forEach(heading => {
            const li = document.createElement('li');
            const link = document.createElement('a');
            link.href = '#' + encodeURIComponent(heading.id);
            link.textContent = heading.textContent;
            link.className = heading.tagName === 'H3' ? 'toc-level-3' : 'toc-level-2';
            li.appendChild(link);
            list.appendChild(li);
        });
        toc.appendChild(title);
        toc.appendChild(list);
        stage.appendChild(toc);

        if ('IntersectionObserver' in window) {
            const links = new Map(Array.from(toc.querySelectorAll('a')).map(link => [decodeURIComponent(link.hash.slice(1)), link]));
            const observer = new IntersectionObserver(entries => {
                entries.forEach(entry => {
                    if (!entry.isIntersecting) return;
                    links.forEach(link => link.classList.remove('is-current'));
                    const active = links.get(entry.target.id);
                    if (active) active.classList.add('is-current');
                });
            }, { rootMargin: '-18% 0px -70% 0px', threshold: 0 });
            headings.forEach(heading => observer.observe(heading));
        }
    }

    function updateReadingProgress() {
        const bar = document.querySelector('.reading-progress-bar');
        if (!bar) return;
        const max = document.documentElement.scrollHeight - window.innerHeight;
        const ratio = max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0;
        bar.style.width = (ratio * 100).toFixed(2) + '%';
    }

    function estimateReadingTime(text) {
        const latinWords = (text.match(/[A-Za-z0-9]+/g) || []).length;
        const cjkCharacters = (text.match(/[\u3400-\u9fff]/g) || []).length;
        return Math.max(1, Math.ceil(latinWords / 220 + cjkCharacters / 430));
    }

    function parseInlineList(value) {
        if (Array.isArray(value)) return value;
        const source = String(value || '').trim();
        if (!source) return [];
        try {
            const parsed = JSON.parse(source);
            return Array.isArray(parsed) ? parsed.map(String) : [];
        } catch (error) {
            return source.replace(/^\[|\]$/g, '').split(',').map(item => item.trim().replace(/^['"]|['"]$/g, '')).filter(Boolean);
        }
    }

    function slugifyHeading(value) {
        return String(value || '')
            .trim()
            .toLowerCase()
            .replace(/[^a-z0-9\u3400-\u9fff]+/g, '-')
            .replace(/^-+|-+$/g, '')
            .slice(0, 72);
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
