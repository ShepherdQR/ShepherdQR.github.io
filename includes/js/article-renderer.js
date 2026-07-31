(function () {
    const content = document.getElementById('markdown-content');
    const titleEl = document.getElementById('currentInnerTitle');
    const metaEl = document.getElementById('currentInnerMeta');
    const typeEl = document.getElementById('currentInnerType');
    const neighborsEl = document.getElementById('article-neighbors');

    if (!content || !titleEl || !metaEl || !typeEl) return;

    const config = readArticleConfig();
    ensureArticleChrome();
    applyCanonical(config.canonical);
    applyArticleForm(config.articleForm);

    if (config.staticRendered && content.dataset.buildRendered === 'true' && content.children.length) {
        initializeStaticArticle();
        return;
    }

    initializeLegacyArticle();

    function initializeStaticArticle() {
        const meta = config.meta || {};
        const title = meta.title || titleEl.textContent.trim() || 'Untitled';
        document.title = title;
        if (!titleEl.textContent.trim()) titleEl.textContent = title;
        if (!typeEl.textContent.trim()) {
            typeEl.textContent = [meta.type, meta.id, config.articleForm].filter(Boolean).join(' · ');
        }
        if (!metaEl.textContent.trim()) metaEl.textContent = formatArticleMeta(meta);

        const currentItem = renderArticleNeighbors(meta, config.md, config);
        if (!document.querySelector('.article-header-tags')) renderArticleTaxonomy(currentItem, meta);
        enhanceArticleContent();
        initializeThemeAwareMedia();
        if (config.math) scheduleMathJax();
    }

    function initializeLegacyArticle() {
        let mdFile = config.md;
        if (!mdFile) {
            renderError('缺少 Markdown 路径参数。');
            return;
        }
        mdFile = ensureMarkdownExtension(normalizeRootPath(mdFile));

        if (window.marked && typeof window.marked.setOptions === 'function') {
            window.marked.setOptions({ gfm: true, breaks: true });
        }

        content.innerHTML = '<p class="article-loading">Loading…</p>';
        fetch(encodeFetchPath(mdFile))
            .then(response => {
                if (!response.ok) throw new Error('文件不存在：' + mdFile);
                return response.text();
            })
            .then(markdown => {
                const parsed = parseMarkdownDocument(markdown);
                const titleMatch = parsed.body.match(/^#\s+(.*)/m);
                const title = parsed.meta.title || (titleMatch ? titleMatch[1].trim() : 'Untitled');
                document.title = title;
                titleEl.textContent = title;
                typeEl.textContent = [parsed.meta.type, parsed.meta.id].filter(Boolean).join(' · ');
                metaEl.textContent = formatArticleMeta(parsed.meta);
                content.innerHTML = renderMarkdown(parsed.body);
                normalizeDynamicHeadings(title);
                activateEmbeddedScripts(content);
                const currentItem = renderArticleNeighbors(parsed.meta, mdFile, config);
                renderArticleTaxonomy(currentItem, parsed.meta);
                enhanceArticleContent();
                initializeThemeAwareMedia();
                if (config.math) scheduleMathJax();
            })
            .catch(error => {
                renderError('加载失败：' + error.message);
                console.error(error);
            });
    }

    function readArticleConfig() {
        const params = new URLSearchParams(window.location.search);
        const embedded = readEmbeddedConfig();
        return {
            md: params.get('md') || embedded.md || '',
            canonical: embedded.canonical || embedded.canonicalHref || '',
            math: typeof embedded.math === 'boolean'
                ? embedded.math
                : Boolean(document.getElementById('MathJax-script')),
            interactive: typeof embedded.interactive === 'boolean'
                ? embedded.interactive
                : Boolean(document.querySelector('script[src*="/d3.js"]')),
            staticRendered: embedded.staticRendered === true,
            articleForm: embedded.articleForm || (embedded.meta && embedded.meta.article_form) || '',
            meta: embedded.meta || {},
            governance: embedded.governance || {},
            themeAssets: embedded.themeAssets || {}
        };
    }

    function readEmbeddedConfig() {
        const configEl = document.getElementById('article-config');
        if (!configEl) return {};
        try {
            return JSON.parse(configEl.textContent || '{}') || {};
        } catch (error) {
            console.warn('Invalid article config:', error);
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

    function applyArticleForm(form) {
        if (!form) return;
        document.body.dataset.articleForm = form;
        const frame = document.querySelector('.article-frame');
        if (frame) frame.classList.add('article-form-' + form);
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
        return { meta, body: stripLeadingHtmlComments(body) };
    }

    function stripLeadingHtmlComments(source) {
        return source.replace(/^(?:<!--[\s\S]*?-->\s*)+/, '');
    }

    function formatArticleMeta(meta) {
        const parts = [];
        if (meta.created_date) parts.push('Created ' + meta.created_date);
        if (meta.published) parts.push('Published ' + meta.published);
        if (meta.updated_date) parts.push('Updated ' + meta.updated_date);
        return parts.join(' · ');
    }

    function renderMarkdown(source) {
        if (!window.marked || typeof window.marked.parse !== 'function') {
            return '<pre>' + escapeHtml(source) + '</pre>';
        }
        return window.marked.parse(source);
    }

    function normalizeDynamicHeadings(pageTitle) {
        const headings = Array.from(content.querySelectorAll('h1, h2, h3, h4, h5, h6'));
        const comparableTitle = normalizeText(pageTitle);
        headings.forEach(heading => {
            if (heading.tagName === 'H1' && normalizeText(heading.textContent) === comparableTitle) {
                heading.remove();
                return;
            }
            if (heading.tagName === 'H1') replaceHeading(heading, 2);
        });
    }

    function replaceHeading(heading, level) {
        const replacement = document.createElement('h' + level);
        Array.from(heading.attributes).forEach(attribute => replacement.setAttribute(attribute.name, attribute.value));
        while (heading.firstChild) replacement.appendChild(heading.firstChild);
        heading.replaceWith(replacement);
    }

    function normalizeText(value) {
        return String(value || '').replace(/\s+/g, ' ').trim().toLocaleLowerCase();
    }

    function renderArticleNeighbors(meta, currentPath, articleConfig) {
        if (!neighborsEl) return null;
        const items = ((window.HOMEPAGE_DATA || {}).items || []);
        const currentItem = findCurrentItem(items, meta, currentPath, articleConfig);
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
        if (frame && (!frame.parentElement || !frame.parentElement.classList.contains('article-stage'))) {
            const stage = document.createElement('div');
            stage.className = 'article-stage';
            frame.parentNode.insertBefore(stage, frame);
            stage.appendChild(frame);
        }
        if (!document.querySelector('.reading-progress')) {
            const progress = document.createElement('div');
            progress.className = 'reading-progress';
            progress.setAttribute('aria-hidden', 'true');
            progress.innerHTML = '<div class="reading-progress-bar"></div>';
            document.body.appendChild(progress);
            updateReadingProgress();
            window.addEventListener('scroll', updateReadingProgress, { passive: true });
            window.addEventListener('resize', updateReadingProgress, { passive: true });
        }
        document.querySelectorAll('.article-nav-links, .article-footer-links').forEach(navigation => {
            if (navigation.querySelector('a[href*="chronicle.html"]')) return;
            const link = document.createElement('a');
            link.href = absolutizeSiteHref('chronicle.html');
            link.textContent = 'Chronicle';
            const series = navigation.querySelector('a[href*="series.html"]');
            if (series) navigation.insertBefore(link, series);
            else navigation.appendChild(link);
        });
    }

    function renderArticleTaxonomy(item, meta) {
        const header = document.querySelector('.article-header');
        if (!header || header.querySelector('.article-header-tags')) return;
        const tags = item && Array.isArray(item.tags) ? item.tags : parseInlineList(meta.tags);
        const series = (item && item.series) || meta.series || '';
        const values = [];
        if (series) values.push({ label: series, href: '/archive.html?series=' + encodeURIComponent(series) });
        tags.forEach(tag => values.push({ label: '#' + tag, href: '/archive.html?tag=' + encodeURIComponent(tag) }));
        if (!values.length) return;
        const host = document.createElement('div');
        host.className = 'article-header-tags';
        host.setAttribute('aria-label', 'Taxonomy');
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
        if (plainText && !metaEl.querySelector('[data-reading-time]')) {
            const readTime = document.createElement('span');
            readTime.dataset.readingTime = '';
            readTime.textContent = estimateReadingTime(plainText) + ' min read';
            metaEl.appendChild(readTime);
        }

        const headings = Array.from(content.querySelectorAll('h2, h3'));
        if (!headings.length) return;
        const seen = new Map();
        headings.forEach((heading, index) => {
            if (heading.id) {
                seen.set(heading.id, (seen.get(heading.id) || 0) + 1);
                return;
            }
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
        toc.innerHTML = '<p class="article-toc-title">Object index</p>';
        const list = document.createElement('ol');
        headings.forEach(heading => {
            const item = document.createElement('li');
            const link = document.createElement('a');
            link.href = '#' + encodeURIComponent(heading.id);
            link.textContent = heading.textContent;
            link.className = heading.tagName === 'H3' ? 'toc-level-3' : 'toc-level-2';
            item.appendChild(link);
            list.appendChild(item);
        });
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

    function initializeThemeAwareMedia() {
        const root = document.documentElement;
        const sync = function () {
            const theme = root.dataset.theme || 'field';
            document.querySelectorAll('[data-theme-affinity]').forEach(media => {
                const active = media.dataset.themeAffinity === theme;
                media.dataset.themeState = active ? 'active' : 'dormant';
                const image = media.querySelector('img');
                if (image) image.setAttribute('fetchpriority', active ? 'high' : 'low');
            });
        };
        sync();
        const observer = new MutationObserver(sync);
        observer.observe(root, { attributes: true, attributeFilter: ['data-theme'] });
        document.addEventListener('zqr:museum-material-ready', sync);
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
        link.innerHTML = '<span class="article-neighbor-label"></span><span class="article-neighbor-title"></span><time class="article-neighbor-date"></time>';
        link.querySelector('.article-neighbor-label').textContent = label;
        link.querySelector('.article-neighbor-title').textContent = item.title;
        const date = link.querySelector('.article-neighbor-date');
        date.dateTime = item.published || '';
        date.textContent = [item.published, item.type, item.updatedDate ? 'Updated ' + item.updatedDate : ''].filter(Boolean).join(' · ');
        return link;
    }

    function findCurrentItem(items, meta, currentPath, articleConfig) {
        const direct = items.find(item => item.type === meta.type && item.id === meta.id);
        if (direct) return direct;
        const normalizedCurrent = normalizeMdPath(currentPath);
        const normalizedCanonical = normalizeHrefPath(articleConfig.canonical);
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
        return absolutizeSiteHref(item.canonicalHref || item.href || item.legacyHref || '');
    }

    function itemHrefCandidates(item) {
        return [item.sourcePath, item.canonicalHref, item.href, item.legacyHref].filter(Boolean);
    }

    function mdFromHref(href) {
        try {
            return new URL(href, window.location.origin + '/').searchParams.get('md') || '';
        } catch (error) {
            const match = String(href || '').match(/[?&]md=([^&]+)/);
            return match ? match[1] : '';
        }
    }

    function normalizeMdPath(value) {
        let path = decodeURIComponent(value || '').replace(/\\/g, '/');
        const md = mdFromHref(path);
        if (md) path = md;
        path = path.split('#')[0].split('?')[0];
        return ensureMarkdownExtension(normalizeRootPath(path));
    }

    function normalizeHrefPath(value) {
        if (!value) return '';
        try {
            return new URL(absolutizeSiteHref(value), window.location.origin).pathname.replace(/\/index\.html$/i, '/');
        } catch (error) {
            return normalizeRootPath(value).replace(/\/index\.html$/i, '/');
        }
    }

    function normalizeRootPath(value) {
        let path = String(value || '').trim().replace(/\\/g, '/');
        if (!path) return '';
        if (/^[a-z][a-z0-9+.-]*:/i.test(path) || path.startsWith('//')) return path;
        if (path.startsWith('./')) path = path.slice(2);
        if (path.startsWith('../')) return new URL(path, window.location.href).pathname;
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
            Array.from(oldScript.attributes).forEach(attribute => script.setAttribute(attribute.name, attribute.value));
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
                        if (typeof window.MathJax.typesetPromise === 'function') return window.MathJax.typesetPromise();
                        if (typeof window.MathJax.typeset === 'function') window.MathJax.typeset();
                    })
                    .catch(function (error) { console.warn('MathJax typeset failed:', error); });
            } else if (Date.now() - startTime < maxWait) {
                setTimeout(tryTypeset, interval);
            }
        }
        tryTypeset();
    }

    function encodeFetchPath(path) {
        if (/^[a-z][a-z0-9+.-]*:/i.test(path) || path.startsWith('//')) return path;
        return path.split('/').map(function (segment, index) {
            if (!segment && index === 0) return '';
            return encodeURIComponent(segment);
        }).join('/');
    }

    function escapeHtml(value) {
        return String(value).replace(/[&<>"']/g, character => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        })[character]);
    }
})();
