// Run with Playwright available on NODE_PATH (no runtime dependency on the public site).
// BASE_URL defaults to the local Python static server. Artifacts are ignored by Git.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const base = process.env.BASE_URL || 'http://127.0.0.1:8000';
const out = path.resolve(__dirname, '../output/playwright/theme-upgrade');
fs.mkdirSync(out, { recursive: true });
const results = [];
const check = (label, value) => { assert(value, label); results.push(label); };
(async () => {
    const browser = await chromium.launch({ channel: 'msedge', headless: true });
    const context = await browser.newContext({ viewport: { width: 1440, height: 1100 } });
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    const requests = [];
    page.on('request', request => requests.push(request.url()));
    const go = async route => { await page.goto(base + route); await page.evaluate(() => window.ZQRTheme.ready); };
    const theme = async id => {
        await page.evaluate(id => window.ZQRTheme.setTheme(id), id);
        check('theme selected: ' + id, await page.getAttribute('html', 'data-theme') === id);
    };
    const screenshot = async name => {
        await page.evaluate(() => { if (document.activeElement instanceof HTMLElement) document.activeElement.blur(); });
        await page.screenshot({ path: path.join(out, name + '.png'), animations: 'disabled' });
    };
    const overflow = async label => check('no horizontal overflow: ' + label,
        await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
    await go('/');
    check('default package is weave', await page.getAttribute('html', 'data-theme') === 'weave');
    await page.waitForSelector('.theme-canvas');
    check('only default package requested at startup', !requests.some(u => /themes\/(twilight|tomography)\//.test(u)));
    const first = await page.getAttribute('#home-spatial', 'data-selected-document');
    await page.getByRole('button', { name: '下一篇精选文章' }).click();
    const second = await page.getAttribute('#home-spatial', 'data-selected-document');
    check('next document changes real selection', first !== second);
    await page.getByRole('button', { name: '上一篇精选文章' }).focus();
    await page.keyboard.press('ArrowLeft');
    check('keyboard selects previous document', await page.getAttribute('#home-spatial', 'data-selected-document') === first);
    for (const id of ['weave', 'twilight', 'tomography']) {
        await theme(id);
        check('theme preserves selected document: ' + id, await page.getAttribute('#home-spatial', 'data-selected-document') === first);
        check('one active stylesheet: ' + id, await page.locator('link[data-theme-package]').count() === 1);
        check('one active scene: ' + id, await page.locator('.theme-canvas').count() === 1);
        await overflow('home-' + id);
        await screenshot('home-' + id + '-desktop');
        await page.setViewportSize({ width: 390, height: 844 });
        await overflow('home-' + id + '-mobile');
        await screenshot('home-' + id + '-mobile');
        await page.setViewportSize({ width: 1440, height: 1100 });
    }
    await page.getByRole('button', { name: '选择视觉主题与阅读偏好' }).click();
    check('theme dialog opens', await page.locator('#theme-dialog').evaluate(d => d.open));
    await page.locator('#reader-size').selectOption('22');
    await page.locator('#reader-motion').selectOption('off');
    await page.keyboard.press('Escape');
    check('escape restores opener focus', await page.locator('[data-theme-toggle]').evaluate(b => document.activeElement === b));
    await go('/books/0147/');
    check('theme survives deep navigation', await page.getAttribute('html', 'data-theme') === 'tomography');
    check('font preference survives navigation', await page.locator('.article-content').evaluate(e => getComputedStyle(e).fontSize) === '22px');
    check('motion preference survives navigation', await page.getAttribute('html', 'data-motion') === 'reduced');
    const articleBefore = await page.locator('#markdown-content').innerHTML();
    const canonical = await page.locator('link[rel=canonical]').getAttribute('href');
    await theme('twilight');
    check('theme keeps complete article HTML', articleBefore === await page.locator('#markdown-content').innerHTML());
    check('theme keeps canonical', canonical === await page.locator('link[rel=canonical]').getAttribute('href'));
    await screenshot('article-twilight-desktop');
    await page.setViewportSize({ width: 390, height: 844 });
    await overflow('article-mobile');
    check('mobile article navigation never stacks individual characters', await page.locator('.article-nav-links > a, .article-nav-links > button').evaluateAll(items => items.every(e => e.getBoundingClientRect().height <= 44)));
    await screenshot('article-twilight-mobile');
    await page.getByRole('button', { name: '专注阅读', exact: true }).click();
    check('focus reading selected', await page.getAttribute('html', 'data-reading') === 'focus');
    check('focus mode keeps article HTML', articleBefore === await page.locator('#markdown-content').innerHTML());
    await screenshot('article-focus-mobile');
    await page.evaluate(() => { window.ZQRTheme.setReading('spatial'); window.ZQRTheme.setFontSize(20); });
    await page.setViewportSize({ width: 1440, height: 1100 });
    await go('/archive.html?q=数学');
    const count = await page.locator('#atlas-result-count').textContent();
    const selected = await page.getAttribute('#atlas-spatial-browser', 'data-selected-document');
    await theme('tomography');
    check('theme keeps archive query', page.url().includes('q='));
    check('theme keeps filtered results', count === await page.locator('#atlas-result-count').textContent());
    check('theme keeps archive selection', selected === await page.getAttribute('#atlas-spatial-browser', 'data-selected-document'));
    await screenshot('atlas-tomography-desktop');
    await page.locator('[data-atlas-mode="ledger"]').click();
    check('ledger remains selectable', await page.locator('#atlas-ledger').isVisible());
    check('spatial view hidden in ledger', await page.locator('#atlas-spatial').isHidden());
    await theme('weave');
    check('theme keeps ledger mode', await page.getAttribute('body', 'data-atlas-mode') === 'ledger');
    await page.setViewportSize({ width: 390, height: 844 });
    await overflow('atlas-mobile');
    await screenshot('atlas-weave-mobile');
    // Representative maintained template families, all using the shared runtime.
    for (const route of ['/books.html', '/thoughts.html', '/study.html', '/videos.html',
        '/stats.html', '/field.html', '/chronicle.html', '/series.html',
        '/series/nobel-literature/', '/series/hanyi-world-academic-classics/', '/series/20th-century-world-poetry/',
        '/thoughts/0003/', '/study/0001/', '/thoughts/0028/']) {
        await go(route);
        await overflow(route);
        check('theme entry exists: ' + route, await page.locator('[data-theme-toggle]').count() === 1);
        check('shared theme layout exists: ' + route, await page.locator('link[href*="themes/shared/layout.css"]').count() === 1);
    }
    // Legacy dynamic reader remains a supported path.
    const md = await page.locator('#article-config').textContent().then(s => JSON.parse(s).md);
    await go('/render.html?md=' + encodeURIComponent(md));
    await page.waitForSelector('#markdown-content h2');
    check('legacy reader loads content', (await page.locator('#markdown-content').innerText()).length > 100);
    // Unknown and retired preferences choose the supported default.
    await page.evaluate(() => localStorage.setItem('zqr-display-v1', JSON.stringify({ theme: 'museum' })));
    await go('/');
    check('retired theme falls back to default', await page.getAttribute('html', 'data-theme') === 'weave');
    // Delayed styles: the most recent choice wins and old resources do not accumulate.
    await page.route('**/themes/twilight/theme.css', async route => {
        await new Promise(resolve => setTimeout(resolve, 250)); await route.continue();
    });
    await page.evaluate(async () => { await Promise.all([window.ZQRTheme.setTheme('twilight'), window.ZQRTheme.setTheme('tomography')]); });
    check('rapid switch last selection wins', await page.getAttribute('html', 'data-theme') === 'tomography');
    check('rapid switch releases old style links', await page.locator('link[data-theme-package]').count() === 1);
    await page.unroute('**/themes/twilight/theme.css');
    // Failed stylesheet must preserve the currently usable theme.
    await page.route('**/themes/twilight/theme.css', route => route.abort());
    const ok = await page.evaluate(() => window.ZQRTheme.setTheme('twilight'));
    check('failed stylesheet returns failure', ok === false);
    check('failed stylesheet retains current package', await page.getAttribute('html', 'data-theme') === 'tomography');
    await page.unroute('**/themes/twilight/theme.css');
    await page.evaluate(() => window.ZQRTheme.setMotion('auto'));
    await page.getByRole('button', { name: '下一篇精选文章' }).click();
    await page.evaluate(() => window.ZQRTheme.setMotion('off'));
    check('motion off cancels document transitions', await page.locator('.selected-document').evaluate(e => e.getAnimations().length === 0));
    // Reduced motion is reflected in the live scene, independently of theme.
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await theme('weave');
    check('system reduced motion respected', await page.getAttribute('html', 'data-motion') === 'reduced');
    await page.evaluate(() => window.ZQRTheme.setReading('focus'));
    check('focus reading disposes scene', await page.locator('.theme-canvas').count() === 0);
    await page.evaluate(() => window.ZQRTheme.setReading('spatial'));
    await page.waitForSelector('.theme-canvas');
    check('return to spatial recreates one scene', await page.locator('.theme-canvas').count() === 1);
    // A late scene import must not announce a theme that has already been replaced.
    const raced = await browser.newContext();
    await raced.route('**/themes/twilight/scene.js', async route => {
        await new Promise(resolve => setTimeout(resolve, 400)); await route.continue();
    });
    const racedPage = await raced.newPage();
    await racedPage.goto(base + '/');
    await racedPage.evaluate(() => window.ZQRTheme.ready);
    const raceResults = await racedPage.evaluate(async () => {
        const a = window.ZQRTheme.setTheme('twilight');
        await new Promise(resolve => setTimeout(resolve, 100));
        const b = window.ZQRTheme.setTheme('tomography');
        return Promise.all([a, b]);
    });
    check('late scene selection reports cancellation', raceResults[0] === false && raceResults[1] === true);
    check('late scene cannot overwrite current announcement', (await racedPage.locator('#theme-status').textContent()).includes('思想层析'));
    check('late scene leaves one canvas', await racedPage.locator('.theme-canvas').count() === 1);
    await raced.close();
    const bootFallback = await browser.newContext();
    await bootFallback.route('**/themes/weave/theme.css', route => route.abort());
    const fallbackPage = await bootFallback.newPage();
    await fallbackPage.goto(base + '/');
    await fallbackPage.evaluate(() => window.ZQRTheme.ready);
    check('startup stylesheet failure uses registered fallback', await fallbackPage.getAttribute('html', 'data-theme') === 'tomography');
    await bootFallback.close();
    await page.setViewportSize({ width: 900, height: 900 });
    await overflow('narrow-desktop');
    await screenshot('home-weave-narrow-desktop');
    // Storage denied is handled, not required for the current-page controls.
    const denied = await browser.newContext();
    await denied.addInitScript(() => {
        Object.defineProperty(Storage.prototype, 'getItem', { value() { throw new Error('denied'); } });
        Object.defineProperty(Storage.prototype, 'setItem', { value() { throw new Error('denied'); } });
    });
    const deniedPage = await denied.newPage();
    await deniedPage.goto(base + '/');
    await deniedPage.evaluate(() => window.ZQRTheme.ready);
    await deniedPage.evaluate(() => window.ZQRTheme.setTheme('tomography'));
    check('storage denied does not disable theme selection', await deniedPage.getAttribute('html', 'data-theme') === 'tomography');
    await denied.close();
    // Scene failure is reported while HTML navigation remains available.
    const degraded = await browser.newContext();
    await degraded.route('**/themes/weave/scene.js', route => route.abort());
    const degradedPage = await degraded.newPage();
    await degradedPage.goto(base + '/');
    await degradedPage.evaluate(() => window.ZQRTheme.ready);
    await degradedPage.waitForFunction(() => document.getElementById('theme-status').textContent.includes('空间效果暂不可用'));
    check('scene failure keeps article link', !!await degradedPage.locator('.document-read').getAttribute('href'));
    await degraded.close();
    // With JS unavailable, the published body and original image references still exist.
    const staticContext = await browser.newContext({ javaScriptEnabled: false });
    const staticPage = await staticContext.newPage();
    await staticPage.goto(base + '/books/0147/');
    check('no-JS article body survives', (await staticPage.locator('#markdown-content').innerText()).length > 1000);
    check('no-JS correct article title', (await staticPage.locator('h1').innerText()).includes('巴比伦'));
    await staticPage.emulateMedia({ media: 'print' });
    check('print keeps readable surface', await staticPage.locator('.article-frame').evaluate(e => getComputedStyle(e).backgroundColor) === 'rgb(255, 255, 255)');
    await staticContext.close();
    check('no uncaught browser errors', errors.length === 0);
    fs.writeFileSync(path.join(out, 'browser-checks.json'), JSON.stringify({ base, checks: results.length, results, errors }, null, 2));
    console.log('Browser checks passed: ' + results.length);
    await browser.close();
})().catch(error => { console.error(error); process.exitCode = 1; process.exit(1); });
