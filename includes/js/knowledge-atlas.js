/* Progressive enhancement: the generated HTML remains the failure/no-JS path. */
(() => {
    'use strict';
    const data = window.KNOWLEDGE_ATLAS;
    const host = document.getElementById('knowledge-interactive');
    if (!host || !data || !Array.isArray(data.domains) || !data.items) return;
    const directory = document.querySelector('#knowledge-static .knowledge-directory');
    if (!directory) return;
    const view = document.getElementById('knowledge-view');
    const breadcrumbs = document.getElementById('knowledge-breadcrumbs');
    const input = document.getElementById('knowledge-search');
    const form = document.getElementById('knowledge-search-form');
    const status = document.getElementById('knowledge-status');
    const nodes = new Map();
    const families = new Map(data.families.map(f => [f.id, f]));
    const types = { all: '全部', Books: '书籍', Thoughts: '思考', Study: '学习', Videos: '影像' };
    const origins = { human: '人类', ai: 'AI', collaborative: '人机协作' };
    const evidence = { conjecture: '猜想', argument: '论证', 'formal-proof': '形式证明', empirical: '实证', contested: '存在争议', superseded: '已被修订' };
    function register(node, index, parent = null, family = node.family) {
        nodes.set(node.id, { ...node, number:String(index + 1).padStart(2,'0'), parent, family });
        (node.children || []).forEach((child, i) => register(child, i, node.id, family));
    }
    data.domains.forEach((d, i) => register(d, i));
    const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    let state = { node: '', query: '', type: 'all', limit: 18 };
    let renderedSearch;
    let invalidLink = false;
    const resolve = id => data.redirects?.[id] || id;
    function readURL() {
        const p = new URLSearchParams(location.search);
        const requested = resolve(p.get('branch') || p.get('domain') || '');
        invalidLink = Boolean(requested && !nodes.has(requested) && requested !== 'unassigned');
        state = { node: invalidLink ? '' : requested, query: (p.get('q') || '').trim().slice(0, 120),
            type: Object.hasOwn(types, p.get('kind')) ? p.get('kind') : 'all', limit: 18 };
    }
    function url(next) {
        const s = { ...state, ...next };
        const u = new URL(location.href);
        ['domain','branch','q','kind'].forEach(k => u.searchParams.delete(k));
        if (s.node) {
            u.searchParams.set('domain', s.node.split('.')[0]);
            if (s.node.includes('.')) u.searchParams.set('branch', s.node);
        }
        if (s.query) u.searchParams.set('q', s.query);
        if (s.type !== 'all') u.searchParams.set('kind', s.type);
        u.hash = 'knowledge-map';
        return u.pathname + u.search + u.hash;
    }
    const link = (id, title, extra = '') => `<a href="${esc(url({node:id,query:'',type:'all'}))}" data-knowledge-node="${esc(id)}" ${extra}>${esc(title)}</a>`;
    // Enhance the printed index in place so both reading modes use the same groups and counts.
    directory.querySelectorAll('[data-knowledge-node]').forEach(anchor => {
        anchor.href = url({node:anchor.dataset.knowledgeNode, query:'', type:'all'});
    });
    function navigate(next, replace = false, focus = true) {
        state = { ...state, ...next, limit: 18 }; invalidLink = false;
        try { history[replace ? 'replaceState' : 'pushState']({}, '', url(state)); } catch (_) { /* Sandboxed previews may deny history. */ }
        render();
        if (focus) {
            const title = view.querySelector('[data-knowledge-focus]');
            title?.focus({ preventScroll: true });
            document.getElementById('knowledge-map').scrollIntoView({ block:'start', behavior:'instant' });
        }
    }
    function tile(node) {
        const count = node.itemKeys.length;
        const title = node.parent ? nodes.get(node.parent).title : families.get(node.family).title;
        return `<a class="knowledge-tile${count ? ' has-notes' : ''}" data-family="${esc(node.family)}" href="${esc(url({node:node.id,query:'',type:'all'}))}" data-knowledge-node="${esc(node.id)}" aria-label="${esc(node.title)}，${count} 篇笔记">
            <div class="knowledge-tile-top"><span>${node.number} <span class="knowledge-family">/ ${esc(title)}</span></span><span class="knowledge-tile-arrow" aria-hidden="true">↗</span></div>
            <h3>${esc(node.title)}</h3>${node.en ? `<span class="knowledge-tile-en" lang="en">${esc(node.en)}</span>` : ''}
            <span class="knowledge-tile-bottom">${count ? count + ' 篇笔记' : '尚无公开笔记'}</span></a>`;
    }
    function note(key) {
        const item = data.items[key];
        const summary = item.summary && item.summary !== item.title ? `<p>${esc(item.summary)}</p>` : '';
        const declared = [origins[item.origin], evidence[item.evidence]].filter(Boolean);
        return `<article class="knowledge-note"><div class="knowledge-note-meta"><span>${esc(types[item.type] || item.type)}</span><time datetime="${esc(item.published)}">${esc(item.published)}</time></div>
            <h4><a href="${esc(item.canonicalHref)}">${esc(item.title)}</a></h4>${summary}
            <div class="knowledge-note-topics">${item.nodes.slice(0, 3).map(id => link(id, nodes.get(id).title)).join('')}</div>
            ${declared.length ? `<p class="knowledge-scope-note">作者标注：${esc(declared.join(' · '))}</p>` : ''}</article>`;
    }
    function notes(keys, heading) {
        const selected = keys.filter(key => state.type === 'all' || data.items[key].type === state.type);
        const controls = Object.entries(types).map(([type, title]) => `<button type="button" data-knowledge-type="${type}" aria-pressed="${type === state.type}">${title}</button>`).join('');
        return `<div class="knowledge-content-header"><h3>${esc(heading)} <small>· ${selected.length}</small></h3><div class="knowledge-type-filters" aria-label="内容类型">${controls}</div></div>
            ${selected.length ? `<div class="knowledge-notes">${selected.slice(0,state.limit).map(note).join('')}</div>${selected.length > state.limit ? `<button class="knowledge-more" type="button" data-knowledge-more>继续展开 · 还有 ${selected.length-state.limit} 篇</button>` : ''}` : `<div class="knowledge-empty"><h3>${keys.length ? '这个类型下，暂时没有笔记。' : state.query ? '暂未找到相应记录。' : '这里，等待第一篇笔记。'}</h3><p>${state.query ? '试试较短的关键词，或回到全图搜索。' : '领域与分支已经有了位置。未来的阅读、问题与发现，会逐渐在这里留下痕迹。'}</p></div>`}`;
    }
    function render() {
        renderedSearch = location.search;
        const node = nodes.get(state.node);
        const domain = node ? nodes.get(node.id.split('.')[0]) : null;
        const q = state.query.toLocaleLowerCase();
        input.value = state.query;
        input.placeholder = node ? `在${node.title}中搜索` : '搜索领域、书籍与思考';
        input.setAttribute('aria-label', input.placeholder);
        const isDirectory = !node && state.node !== 'unassigned' && !q;
        const crumbs = [isDirectory ? '<span aria-current="page">全部领域</span>' : link('', '全部领域')];
        if (node) {
            const path = []; let cursor = node;
            while (cursor) { path.unshift(cursor); cursor = nodes.get(cursor.parent); }
            path.forEach((n, i) => crumbs.push(i === path.length-1 ? `<span aria-current="page">${esc(n.title)}</span>` : link(n.id,n.title)));
        }
        if (state.node === 'unassigned') crumbs.push('<span aria-current="page">待归档笔记</span>');
        breadcrumbs.innerHTML = crumbs.join('<span class="knowledge-separator" aria-hidden="true">/</span>') + (!state.node ? `<span class="knowledge-root-meta">${data.counts.domains} 个领域 · ${data.counts.branches} 个分支 · ${data.counts.articles} 篇公开笔记</span>` : '');
        let markup = invalidLink ? '<p class="knowledge-scope-note">这个领域链接暂未找到，已回到全图。原有笔记仍可在文库中检索。</p>' : '';
        let keys = state.node === 'unassigned' ? data.unassigned : node ? node.itemKeys : Object.keys(data.items);
        keys = [...keys].sort((a,b) => (data.items[b].published || '').localeCompare(data.items[a].published || '') || b.localeCompare(a));
        if (q) {
            const matches = [...nodes.values()].filter(n => (!node || n.id === node.id || n.id.startsWith(node.id + '.')) && `${n.title} ${n.en || ''} ${(n.aliases || []).join(' ')} ${n.id}`.toLocaleLowerCase().includes(q));
            keys = keys.filter(k => `${data.items[k].title} ${data.items[k].summary || ''}`.toLocaleLowerCase().includes(q));
            markup += `<h2 class="knowledge-search-heading" data-knowledge-focus tabindex="-1">“${esc(state.query)}”的相关记录</h2>`;
            if (matches.length) markup += `<div class="knowledge-grid knowledge-subgrid">${matches.map(tile).join('')}</div>`;
            markup += notes(keys, '书籍与思考');
        } else if (isDirectory) {
            markup += '<h2 class="visually-hidden" data-knowledge-focus tabindex="-1">全部知识领域</h2>';
            if (data.unassigned.length) markup += `<p class="knowledge-scope-note">${link('unassigned', `${data.unassigned.length} 篇待归档笔记`)}</p>`;
        } else {
            const title = node?.title || '待归档笔记';
            markup += `<div class="knowledge-domain-intro"><div><p class="eyebrow">${esc(domain?.en || 'TO BE CLASSIFIED')}</p><h2 data-knowledge-focus tabindex="-1">${esc(title)}</h2><p>${esc(domain?.description || '新笔记先保留在这里，等待明确的主题归属。')}</p></div>${domain ? `<p class="knowledge-domain-question">${esc(domain.question)}</p>` : ''}</div>`;
            if (node?.children?.length) markup += `<div class="knowledge-grid knowledge-subgrid">${node.children.map(c => tile(nodes.get(c.id))).join('')}</div>`;
            markup += notes(keys, '在这里，读过与想过');
            if (domain) markup += `<nav class="knowledge-neighbours" aria-label="相邻领域"><span>沿着联系继续</span>${domain.related.map(id => link(id, nodes.get(id).title + ' ↗')).join('')}</nav>`;
            markup += '<p class="knowledge-scope-note">主题关联依据公开标题、摘要与必要正文整理；未声明的内容来源与验证状态保持未标注。</p>';
        }
        view.innerHTML = markup;
        if (isDirectory) view.appendChild(directory);
        host.dataset.knowledgeNode = state.node;
        const visibleCount = keys.filter(k => state.type === 'all' || data.items[k].type === state.type).length;
        status.textContent = q ? `找到 ${visibleCount} 篇相关笔记` : `${node?.title || '全部领域'}，${visibleCount} 篇公开笔记`;
    }
    host.addEventListener('click', event => {
        const target = event.target.closest('a[data-knowledge-node], button[data-knowledge-type], button[data-knowledge-more]');
        if (!target || !host.contains(target) || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button > 0) return;
        if (target.hasAttribute('data-knowledge-node')) {
            event.preventDefault(); navigate({ node:target.dataset.knowledgeNode, query:'', type:'all' });
        } else if (target.hasAttribute('data-knowledge-type')) {
            const type = target.dataset.knowledgeType;
            navigate({ type }, true, false);
            host.querySelector(`[data-knowledge-type="${type}"]`)?.focus({preventScroll:true});
        } else {
            const previous = state.limit; state.limit += 18; render();
            view.querySelectorAll('.knowledge-note h4 a')[previous]?.focus({preventScroll:true});
        }
    });
    form.addEventListener('submit', event => { event.preventDefault(); navigate({query:input.value.trim().slice(0,120)}, false, false); });
    input.addEventListener('input', () => { if (!input.value && state.query) navigate({query:''}, true, false); });
    window.addEventListener('popstate', () => {
        if (location.search === renderedSearch) return;
        readURL(); render();
    });
    readURL(); render();
    document.getElementById('knowledge-static').hidden = true;
    host.hidden = false; form.hidden = false;
    const sources = document.getElementById('knowledge-sources');
    sources.innerHTML = data.coverage.map(s => `<div class="knowledge-source"><a href="${esc(s.url)}" rel="noopener">${esc(s.title)} ↗</a><span>${s.count} / ${s.count} 个入口已对照</span><small>${esc(s.version)}</small></div>`).join('') + '<p><a href="./data/knowledge-crosswalk.json">逐项对应关系</a> · <a href="./data/knowledge-standards.json">来源与范围清单</a></p>';
    const frontiers = document.getElementById('knowledge-frontiers');
    frontiers.innerHTML = data.frontiers.map(f => `<a href="${esc(url({node:f.nodes[0],query:'',type:'all'}))}">${esc(f.title)} <span aria-hidden="true">↗</span></a>`).join('');
})();
