(function () {
    const storageKey = 'zqr-visual-system';
    const fieldTheme = 'field';
    const museumTheme = 'museum';
    const root = document.documentElement;

    let active = readPreference();
    applyTheme(active, false);

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', bindControls, { once: true });
    } else {
        bindControls();
    }

    function readPreference() {
        try {
            const stored = window.localStorage.getItem(storageKey);
            if (stored === fieldTheme || stored === museumTheme) return stored;
        } catch (error) {
            // Local storage may be unavailable in a hardened browser.
        }
        return fieldTheme;
    }

    function bindControls() {
        let controls = Array.from(document.querySelectorAll('[data-theme-toggle]'));
        if (!controls.length) {
            const nav = document.querySelector('.primary-nav, .archive-nav, .series-nav, .article-nav-links');
            if (nav) {
                const button = document.createElement('button');
                button.type = 'button';
                button.className = 'theme-toggle';
                button.setAttribute('data-theme-toggle', '');
                button.innerHTML = '<span class="theme-toggle-orbit" aria-hidden="true"></span><span data-theme-label></span>';
                nav.appendChild(button);
                controls = [button];
            }
        }

        controls.forEach(control => {
            if (!control.querySelector('[data-theme-label]')) {
                control.innerHTML = '<span class="theme-toggle-orbit" aria-hidden="true"></span><span data-theme-label></span>';
            }
            control.addEventListener('click', toggleTheme);
        });
        updateControls();
    }

    function toggleTheme() {
        active = active === museumTheme ? fieldTheme : museumTheme;
        applyTheme(active, true);
        try {
            window.localStorage.setItem(storageKey, active);
        } catch (error) {
            // The switch still works for the current page without persistence.
        }
    }

    function applyTheme(theme, announce) {
        root.dataset.theme = theme;
        root.style.colorScheme = theme === museumTheme ? 'dark' : 'light';
        if (document.body && announce) {
            document.body.classList.add('theme-changing');
            window.setTimeout(() => document.body.classList.remove('theme-changing'), 260);
        }
        updateControls();
    }

    function updateControls() {
        if (!document.querySelectorAll) return;
        const isMuseum = active === museumTheme;
        document.querySelectorAll('[data-theme-toggle]').forEach(control => {
            const label = control.querySelector('[data-theme-label]');
            if (label) label.textContent = isMuseum ? 'Field' : 'Museum';
            control.setAttribute('aria-pressed', String(isMuseum));
            control.setAttribute('aria-label', isMuseum ? '切换到学术约束场风格' : '切换到深层博物馆风格');
            control.title = isMuseum ? 'Field · 学术约束场' : 'Museum · 深层博物馆';
        });
    }
})();
