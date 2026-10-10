(function () {
    'use strict';
    const root = document.documentElement;
    const base = new URL('../../', document.currentScript.src);
    const registry = window.ZQR_THEMES || { contractVersion: 1, default: 'weave', themes: [] };
    const packages = registry.themes || [];
    const find = id => packages.find(theme => theme.id === id);
    const defaultId = find(registry.default) ? registry.default : 'weave';
    const storageKey = 'zqr-display-v1';
    const media = window.matchMedia('(prefers-reduced-motion: reduce)');
    let stored = {};
    try { stored = JSON.parse(localStorage.getItem(storageKey) || '{}') || {}; } catch (_) {}
    const preferences = {
        theme: find(stored.theme) ? stored.theme : defaultId,
        reading: stored.reading === 'focus' ? 'focus' : 'spatial',
        fontSize: [18, 20, 22].includes(stored.fontSize) ? stored.fontSize : 20,
        motion: stored.motion === 'off' ? 'off' : 'auto'
    };
    let current = defaultId;
    let generation = 0;
    let sceneGeneration = 0;
    let activeLink = null;
    let scene = null;
    let sceneAbort = null;
    let dialog = null;
    let opener = null;
    let lastMessage = '';
    let domReady = false;
    root.dataset.theme = preferences.theme;
    applyPreferences();
    function save() {
        try { localStorage.setItem(storageKey, JSON.stringify(preferences)); } catch (_) {}
    }
    function reduced() { return preferences.motion === 'off' || media.matches || preferences.reading === 'focus'; }
    function applyPreferences() {
        root.dataset.reading = preferences.reading;
        root.dataset.motion = reduced() ? 'reduced' : 'auto';
        root.style.setProperty('--reader-font-size', preferences.fontSize + 'px');
        if (reduced()) document.querySelectorAll('.selected-document').forEach(element => {
            if (element.getAnimations) element.getAnimations().forEach(animation => animation.cancel());
        });
    }
    function announce(message) {
        lastMessage = message;
        const host = document.getElementById('theme-status');
        if (host) host.textContent = message;
    }
    function emit() {
        document.dispatchEvent(new CustomEvent('zqr:themechange', { detail: { theme: current, preferences: { ...preferences } } }));
    }
    function loadStyle(theme) {
        return new Promise((resolve, reject) => {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = new URL(theme.stylesheet, base).href;
            link.dataset.themePackage = theme.id;
            const timer = setTimeout(() => { link.remove(); reject(new Error('主题样式加载超时')); }, 8000);
            link.onload = () => { clearTimeout(timer); resolve(link); };
            link.onerror = () => { clearTimeout(timer); link.remove(); reject(new Error('主题样式无法加载')); };
            document.head.appendChild(link);
        });
    }
    async function mountScene() {
        const ticket = ++sceneGeneration;
        if (sceneAbort) sceneAbort.abort();
        if (scene) scene.dispose();
        scene = null;
        sceneAbort = new AbortController();
        const controller = sceneAbort;
        const theme = find(current);
        if (!domReady || !theme || !theme.scene || preferences.reading === 'focus' ||
            !document.querySelector('[data-theme-scene]')) return true;
        try {
            const module = await import(new URL(theme.scene, base).href);
            if (ticket !== sceneGeneration || controller.signal.aborted) return false;
            scene = module.mount({ reducedMotion: reduced(), signal: controller.signal,
                hosts: [...document.querySelectorAll('[data-theme-scene]')],
                getDocuments: () => ((window.HOMEPAGE_DATA || {}).items || []).map(item => ({ ...item })) });
            return true;
        } catch (_) {
            if (ticket === sceneGeneration) announce('空间效果暂不可用，文章与阅读功能仍可使用。');
            return false;
        }
    }
    async function setTheme(id, persist = true, allowFallback = true) {
        const theme = find(id) || find(defaultId);
        if (!theme) return false;
        const ticket = ++generation;
        let link;
        try { link = await loadStyle(theme); }
        catch (_) {
            if (ticket !== generation) return false;
            if (!activeLink && allowFallback && theme.fallbackTheme && theme.fallbackTheme !== theme.id) {
                return setTheme(theme.fallbackTheme, persist, false);
            }
            root.dataset.theme = current;
            preferences.theme = current;
            updateControls();
            announce('新主题未能加载，已保留当前外观。');
            return false;
        }
        if (ticket !== generation) { link.remove(); return false; }
        const previousLink = activeLink;
        activeLink = link;
        current = theme.id;
        preferences.theme = current;
        root.dataset.theme = current;
        root.style.colorScheme = theme.colorScheme;
        if (previousLink) previousLink.remove();
        if (persist) save();
        applyPreferences();
        updateControls();
        const sceneReady = await mountScene();
        if (ticket !== generation) return false;
        emit();
        if (sceneReady) announce('已切换到' + theme.label);
        return true;
    }
    function setReading(value) {
        preferences.reading = value === 'focus' ? 'focus' : 'spatial';
        applyPreferences(); save(); updateControls(); mountScene(); emit();
    }
    function setFontSize(size) {
        if (![18, 20, 22].includes(Number(size))) return;
        preferences.fontSize = Number(size);
        applyPreferences(); save(); updateControls(); emit();
    }
    function setMotion(value) {
        preferences.motion = value === 'off' ? 'off' : 'auto';
        applyPreferences(); save(); updateControls(); mountScene(); emit();
    }
    function openDialog(event) {
        if (!dialog) return;
        opener = event && event.currentTarget;
        if (!dialog.open) dialog.showModal();
    }
    function updateControls() {
        const theme = find(current);
        document.querySelectorAll('[data-theme-toggle]').forEach(button => {
            button.textContent = '外观 · ' + (theme ? theme.label : '相位织场');
            button.setAttribute('aria-label', '选择视觉主题与阅读偏好');
            button.setAttribute('aria-haspopup', 'dialog');
        });
        document.querySelectorAll('[data-theme-choice]').forEach(button => {
            button.setAttribute('aria-pressed', String(button.dataset.themeChoice === current));
        });
        document.querySelectorAll('[data-reading-toggle]').forEach(button => {
            button.textContent = preferences.reading === 'focus' ? '空间浏览' : '专注阅读';
            button.setAttribute('aria-pressed', String(preferences.reading === 'focus'));
        });
        const font = document.getElementById('reader-size');
        const motion = document.getElementById('reader-motion');
        if (font) font.value = String(preferences.fontSize);
        if (motion) motion.value = preferences.motion;
    }
    function bindControls() {
        domReady = true;
        let controls = [...document.querySelectorAll('[data-theme-toggle]')];
        if (!controls.length) {
            const nav = document.querySelector('.primary-nav, .archive-nav, .series-nav, .article-nav-links');
            if (nav) {
                const button = document.createElement('button');
                button.type = 'button'; button.className = 'theme-toggle'; button.dataset.themeToggle = '';
                nav.appendChild(button); controls = [button];
            }
        }
        if (document.body.dataset.articleForm) {
            const nav = document.querySelector('.article-nav-links');
            if (nav) { const button = document.createElement('button'); button.type = 'button'; button.className = 'theme-toggle'; button.dataset.readingToggle = ''; nav.appendChild(button); }
        }
        dialog = document.createElement('dialog');
        dialog.className = 'theme-dialog';
        dialog.id = 'theme-dialog';
        dialog.setAttribute('aria-labelledby', 'theme-dialog-title');
        dialog.innerHTML = '<div class="theme-dialog-head"><div><p class="eyebrow">YOUR WAY OF SEEING</p><h2 id="theme-dialog-title">选择一种观看方式。</h2></div><button class="theme-close" type="button" aria-label="关闭外观设置">×</button></div><p class="theme-intro">同一份思想，不同的光与空间。</p><div class="theme-options"></div><div class="reading-preferences"><label>正文字号<select id="reader-size"><option value="18">18 · 紧凑</option><option value="20">20 · 标准</option><option value="22">22 · 舒展</option></select></label><label>动态效果<select id="reader-motion"><option value="auto">跟随系统</option><option value="off">关闭动态</option></select></label><button type="button" data-reading-toggle>专注阅读</button></div><p id="theme-status" class="theme-status" role="status" aria-live="polite"></p>';
        const options = dialog.querySelector('.theme-options');
        packages.forEach(theme => {
            const button = document.createElement('button');
            button.type = 'button'; button.className = 'theme-option'; button.dataset.themeChoice = theme.id;
            const preview = document.createElement('span');
            preview.className = 'theme-preview preview-' + theme.id; preview.setAttribute('aria-hidden', 'true');
            for (let i = 0; i < 5; i++) { const line = document.createElement('i'); line.style.setProperty('--i', i); preview.appendChild(line); }
            const title = document.createElement('strong'); title.textContent = theme.label;
            const description = document.createElement('small'); description.textContent = theme.description;
            button.append(preview, title, description);
            button.addEventListener('click', () => setTheme(theme.id));
            options.appendChild(button);
        });
        document.body.appendChild(dialog);
        controls.forEach(button => button.addEventListener('click', openDialog));
        dialog.querySelector('.theme-close').addEventListener('click', () => dialog.close());
        dialog.addEventListener('click', event => {
            if (event.target !== dialog) return;
            const r = dialog.getBoundingClientRect();
            if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close();
        });
        dialog.addEventListener('close', () => { if (opener) opener.focus({ preventScroll: true }); });
        document.getElementById('reader-size').addEventListener('change', e => setFontSize(e.target.value));
        document.getElementById('reader-motion').addEventListener('change', e => setMotion(e.target.value));
        document.querySelectorAll('[data-reading-toggle]').forEach(button => button.addEventListener('click',
            () => setReading(preferences.reading === 'focus' ? 'spatial' : 'focus')));
        updateControls(); announce(lastMessage); mountScene();
    }
    media.addEventListener('change', () => { applyPreferences(); mountScene(); });
    document.addEventListener('zqr:scene-hosts-changed', mountScene);
    window.addEventListener('pagehide', () => { if (sceneAbort) sceneAbort.abort(); if (scene) scene.dispose(); });
    window.addEventListener('pageshow', event => { if (event.persisted) mountScene(); });
    window.ZQRTheme = { setTheme, setReading, setFontSize, setMotion,
        getTheme: () => current, getPreferences: () => ({ ...preferences }), registry };
    window.ZQRTheme.ready = setTheme(preferences.theme, false);
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', bindControls, { once: true });
    else bindControls();
})();
