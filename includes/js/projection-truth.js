(function () {
    const plane = window.SITE_PLANE || {};
    const baseline = plane.control_plane_baseline || {};
    const loop = plane.control_loop || {};
    const asOf = baseline.as_of || plane.asOf || '';
    const thresholdDays = Number(loop.freshness_threshold_days || 14);
    const dateParts = /^\d{4}-\d{2}-\d{2}$/.test(asOf)
        ? asOf.split('-').map(Number)
        : null;
    const now = new Date();
    const todayUtc = Date.UTC(now.getFullYear(), now.getMonth(), now.getDate());
    const baselineUtc = dateParts
        ? Date.UTC(dateParts[0], dateParts[1] - 1, dateParts[2])
        : Number.NaN;
    const ageDays = Number.isFinite(baselineUtc)
        ? Math.max(0, Math.floor((todayUtc - baselineUtc) / 86400000))
        : null;
    const stale = ageDays === null ? true : ageDays > thresholdDays;
    const state = stale ? 'stale' : (ageDays === thresholdDays ? 'review-due' : 'current');
    const label = stale ? 'stale · requires re-observation' : (state === 'review-due' ? 'review due' : 'current projection');

    const truth = Object.freeze({
        asOf,
        thresholdDays,
        ageDays,
        stale,
        state,
        label
    });

    window.PROJECTION_TRUTH = truth;
    document.documentElement.dataset.projectionFreshness = state;

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', hydrateProjectionTruth, { once: true });
    } else {
        hydrateProjectionTruth();
    }

    function hydrateProjectionTruth() {
        document.querySelectorAll('[data-projection-label]').forEach(node => {
            node.dataset.state = state;
            node.textContent = label;
        });
        document.querySelectorAll('[data-projection-as-of]').forEach(node => {
            node.textContent = asOf || 'undated';
        });
        document.querySelectorAll('[data-projection-age]').forEach(node => {
            node.textContent = ageDays === null ? 'unknown age' : `${ageDays} days old`;
        });
        document.dispatchEvent(new CustomEvent('zqr:projection-truth', { detail: truth }));
    }
})();
