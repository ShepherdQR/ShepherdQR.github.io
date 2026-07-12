(function () {
    const plane = window.SITE_PLANE || {};
    const site = plane.site || {};
    const governance = plane.governance || {};
    const baseline = plane.control_plane_baseline || {};
    const frontier = baseline.evolution_frontier || {};
    const candidate = frontier.next_stage_candidate || {};
    const operational = baseline.operational_frontier || {};

    setText('boundary-statement', site.boundary_statement_zh || '本站由人类拥有；公开投影不创造权威。');
    renderBoundary();
    renderLoop();
    renderChronicle();
    renderGates();
    renderSources();

    function renderBoundary() {
        const rows = [
            ['Evidence state', 'derived / dated'],
            ['Lifecycle', candidate.status || 'candidate_not_adopted'],
            ['Authority effect', governance.authority_effect || 'none'],
            ['Owner', site.owner || 'human']
        ];
        const host = document.getElementById('boundary-grid');
        rows.forEach(([label, value]) => { const cell = document.createElement('div'); cell.className = 'boundary-cell'; const key = document.createElement('span'); key.textContent = label; const data = document.createElement('strong'); data.textContent = value; cell.appendChild(key); cell.appendChild(data); host.appendChild(cell); });
    }

    function renderLoop() {
        const labels = {
            human_intent: ['人的意图', '目标、价值与边界首先由人给出。'],
            capture_and_authoring: ['捕获与写作', 'Markdown 保存对象及其语境。'],
            source_and_evidence_binding: ['来源绑定', '声明指向来源、例证与不确定性。'],
            local_build_and_validation: ['本地构建验证', '生成物、链接与元数据接受检查。'],
            human_release_decision: ['人类释放决定', '写入与发布在此处获得一次性授权。'],
            public_projection: ['公共投影', '静态站点呈现获准对象。'],
            dated_observation: ['带日期观察', '状态以 as-known-at 证据记录。'],
            revise_retire_or_continue: ['修订、退役或继续', '保留回滚、否决与下一步。']
        };
        const host = document.getElementById('control-loop');
        (((plane.control_loop || {}).steps) || []).forEach(step => { const li = document.createElement('li'); const title = document.createElement('strong'); const detail = document.createElement('span'); const copy = labels[step] || [step, '']; title.textContent = copy[0]; detail.textContent = copy[1]; li.appendChild(title); li.appendChild(detail); host.appendChild(li); });
    }

    function renderChronicle() {
        const rail = document.getElementById('wp-rail');
        (frontier.completed_work_packages || []).forEach(wp => { const node = document.createElement('div'); node.className = 'wp-node'; const name = document.createElement('strong'); name.textContent = wp; const state = document.createElement('span'); state.textContent = 'evidence completed'; node.appendChild(name); node.appendChild(state); rail.appendChild(node); });
        setText('candidate-state', candidate.status || 'candidate_not_adopted');
        setText('candidate-title', candidate.title_zh || candidate.title || 'T12 candidate');
        setText('candidate-invariant', candidate.derived_invariant_zh || candidate.derived_invariant || '');
        renderKeyValues('candidate-meta', [
            ['As known at', baseline.as_of || '—'],
            ['Canonical registry changed', yesNo(candidate.canonical_stage_registry_changed)],
            ['Adoption authorized', yesNo(candidate.adoption_authorized)],
            ['Authority effect', candidate.authority_effect || 'none']
        ]);
    }

    function renderGates() {
        renderKeyValues('human-gates', (plane.human_gates || []).map(gate => [humanize(gate), 'human release']));
        renderKeyValues('operational-denials', [
            ['Live watcher', started(operational.live_watcher_started)],
            ['Broker process', started(operational.broker_process_started)],
            ['Guarded broker', operational.guarded_broker_authorized ? 'authorized' : 'not authorized'],
            ['Resident runtime', started(operational.resident_agent_runtime_started)],
            ['Target adapter', operational.target_local_adapter_released ? 'released' : 'not released'],
            ['Autonomous publish', ((plane.control_loop || {}).automation || {}).autonomous_content_promotion_enabled ? 'enabled' : 'disabled']
        ]);
    }

    function renderSources() {
        const host = document.getElementById('source-list');
        const sources = [
            ...(((plane.provenance || {}).site_source_refs) || []),
            ...(baseline.source_refs || [])
        ];
        Array.from(new Set(sources)).forEach(source => { const li = document.createElement('li'); li.textContent = source; host.appendChild(li); });
    }

    function renderKeyValues(id, rows) {
        const host = document.getElementById(id);
        if (!host) return;
        rows.forEach(([label, value]) => { const li = document.createElement('li'); const key = document.createElement('span'); key.textContent = label; const data = document.createElement('strong'); data.textContent = value; li.appendChild(key); li.appendChild(data); host.appendChild(li); });
    }

    function setText(id, value) { const node = document.getElementById(id); if (node) node.textContent = value; }
    function yesNo(value) { return value ? 'yes' : 'no'; }
    function started(value) { return value ? 'started' : 'not started'; }
    function humanize(value) { return String(value).replace(/_/g, ' '); }
})();
