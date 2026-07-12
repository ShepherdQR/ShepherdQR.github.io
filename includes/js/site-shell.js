(function () {
    const path = window.location.pathname.replace(/\/index\.html$/i, '/');
    const section = document.body ? document.body.dataset.section || '' : '';
    document.querySelectorAll('[data-route]').forEach(link => {
        const route = link.getAttribute('data-route');
        if (!route) return;
        const isHome = route === 'home' && (path === '/' || /\/index\.html$/i.test(window.location.pathname));
        const isMatch = route !== 'home' && (path.includes(route) || section === route);
        if (isHome || isMatch) {
            link.setAttribute('aria-current', 'page');
            link.classList.add('is-active');
        }
    });

    document.querySelectorAll('[data-current-year]').forEach(node => {
        node.textContent = String(new Date().getFullYear());
    });
})();
