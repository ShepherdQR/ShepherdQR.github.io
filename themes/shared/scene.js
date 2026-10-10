// Ambient geometry only. Article text, images and controls remain semantic HTML.
export function createScene({ reducedMotion, signal }, kind) {
    const hosts = [...document.querySelectorAll('[data-theme-scene]')];
    let stopped = false, frame = 0, phase = 0, previousTime = 0;
    const scenes = hosts.map(host => {
        const canvas = document.createElement('canvas');
        canvas.className = 'theme-canvas';
        canvas.setAttribute('aria-hidden', 'true');
        host.prepend(canvas);
        return { host, canvas, ctx: canvas.getContext('2d'), width: 0, height: 0, visible: true };
    });
    function resize() {
        scenes.forEach(s => {
            const rect = s.host.getBoundingClientRect();
            const ratio = Math.min(window.devicePixelRatio || 1, 1.5);
            s.width = rect.width; s.height = rect.height;
            s.canvas.width = Math.round(s.width * ratio);
            s.canvas.height = Math.round(s.height * ratio);
            if (s.ctx) s.ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
        });
        draw();
    }
    function draw() {
        const style = getComputedStyle(document.documentElement);
        const ink = style.getPropertyValue('--scene-line').trim() || '190,210,222';
        const light = style.getPropertyValue('--scene-light').trim() || '230,190,145';
        scenes.forEach(s => {
            if (!s.ctx || !s.width || !s.visible) return;
            const { ctx: c, width: w, height: h } = s;
            c.clearRect(0, 0, w, h);
            if (kind === 'weave') {
                for (let i = 0; i < 170; i++) {
                    const t = i / 169, drift = Math.sin(phase + t * 4) * h * .012;
                    c.beginPath();
                    c.moveTo(-w * .08, h * (.02 + t * 1.15));
                    c.bezierCurveTo(w * .4, h * (t * .21 - .06) + drift,
                        w * .35, h * (1.31 - t * .72) - drift, w * 1.04, h * (.03 + t * .95));
                    c.lineWidth = i % 15 === 0 ? 1.3 : .65;
                    c.strokeStyle = 'rgba(' + (i % 15 === 0 ? light : ink) + ',' + (i % 15 === 0 ? .53 : .19) + ')';
                    c.stroke();
                }
            } else if (kind === 'twilight') {
                for (let i = 0; i < 18; i++) {
                    const x = w * (.02 + i * .053) + Math.sin(phase + i) * w * .001;
                    c.beginPath();
                    c.moveTo(x - w * .09, h * 1.02);
                    c.bezierCurveTo(x - w * .2, h * .4, x + w * .05, -h * .16, x + w * .32, -h * .06);
                    c.bezierCurveTo(x + w * .16, h * .26, x - w * .08, h * .68, x - w * .09, h * 1.02);
                    const g = c.createLinearGradient(x - 50, 0, x + 180, h);
                    g.addColorStop(0, 'rgba(' + ink + ',.02)');
                    g.addColorStop(.65, 'rgba(' + ink + ',.06)');
                    g.addColorStop(1, 'rgba(' + ink + ',.01)');
                    c.fillStyle = g; c.fill();
                    c.strokeStyle = 'rgba(' + (i === 7 ? light : ink) + ',' + (i === 7 ? .5 : .16) + ')';
                    c.lineWidth = i === 7 ? 1.6 : .7; c.stroke();
                }
            } else {
                for (let i = 0; i < 24; i++) {
                    const t = i / 23;
                    c.beginPath();
                    c.moveTo(w * (-.3 + t * .043), h * -.15);
                    c.bezierCurveTo(w * (.18 + t * .025), h * .65,
                        w * (.05 + t * .04), h * .89, w * (1.1 + t * .1), h * 1.05);
                    c.lineWidth = i === 15 ? 1.3 : .65;
                    c.strokeStyle = 'rgba(' + (i === 15 ? light : ink) + ',' + (i === 15 ? .38 : .1) + ')';
                    c.stroke();
                }
            }
        });
    }
    function canAnimate() {
        return kind !== 'tomography' && !stopped && !reducedMotion && !document.hidden && scenes.some(s => s.visible);
    }
    function tick(time) {
        frame = 0;
        if (!canAnimate()) return;
        if (time - previousTime > 65) { phase += .006; draw(); previousTime = time; }
        frame = requestAnimationFrame(tick);
    }
    function schedule() {
        cancelAnimationFrame(frame); frame = 0;
        if (canAnimate()) frame = requestAnimationFrame(tick);
        else draw();
    }
    const resizer = new ResizeObserver(resize);
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => { const s = scenes.find(s => s.host === entry.target); if (s) s.visible = entry.isIntersecting; });
        schedule();
    });
    scenes.forEach(s => { resizer.observe(s.host); observer.observe(s.host); });
    document.addEventListener('visibilitychange', schedule);
    resize(); schedule();
    function dispose() {
        if (stopped) return;
        stopped = true; cancelAnimationFrame(frame);
        resizer.disconnect(); observer.disconnect();
        document.removeEventListener('visibilitychange', schedule);
        scenes.forEach(s => s.canvas.remove());
    }
    if (signal) signal.addEventListener('abort', dispose, { once: true });
    return { dispose, pause() { reducedMotion = true; schedule(); }, resume() { reducedMotion = false; schedule(); } };
}
