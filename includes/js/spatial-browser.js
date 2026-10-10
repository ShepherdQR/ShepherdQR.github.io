(function () {
    'use strict';
    const typeLabels = { Books: '阅读札记', Thoughts: '思想与研究', Study: '学习与实验', Videos: '影像记录' };
    const key = item => item.type + ':' + item.id;
    function create(host, initialItems, label) {
        let items = [], index = 0;
        host.classList.add('spatial-browser');
        host.innerHTML = '<p class="deck-label"></p><div class="document-stage"><div class="document-echo" style="--layer:3" aria-hidden="true"></div><div class="document-echo" style="--layer:2" aria-hidden="true"></div><div class="document-echo" style="--layer:1" aria-hidden="true"></div><article class="selected-document"><div class="document-meta"><span class="document-code"></span><time></time></div><div class="document-body"><div class="document-copy"><span class="document-type"></span><h2><a class="document-title"></a></h2><p class="document-summary"></p></div><img class="document-image" alt="" hidden decoding="async"></div><a class="document-read">继续阅读 <span aria-hidden="true">↗</span></a><div class="document-bottom"><span class="document-series"></span><span>ZQR.WORLD / COLLECTION</span></div></article></div><div class="document-controls"><span class="document-counter" role="status" aria-live="polite"></span><div class="document-actions"><button type="button" class="focus-switch" data-reading-toggle>专注阅读</button><button type="button" class="document-prev" aria-label="上一篇精选文章">←</button><button type="button" class="document-next" aria-label="下一篇精选文章">→</button></div></div>';
        const $ = selector => host.querySelector(selector);
        $('.deck-label').textContent = label || 'SELECTED DOCUMENT / 精选阅读';
        const previous = $('.document-prev'), next = $('.document-next');
        previous.addEventListener('click', () => select(index - 1));
        next.addEventListener('click', () => select(index + 1));
        host.addEventListener('keydown', event => {
            if (event.target.matches('input,select,textarea')) return;
            if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
                event.preventDefault();
                select(index + (event.key === 'ArrowRight' ? 1 : -1));
            }
        });
        function select(value) {
            if (!items.length) return;
            const hadSelection = !!host.dataset.selectedDocument;
            index = (value + items.length) % items.length;
            const item = items[index];
            $('.selected-document').hidden = false;
            $('.document-code').textContent = item.type.toUpperCase() + ' / ' + item.id;
            $('.document-type').textContent = typeLabels[item.type] || item.type;
            $('.document-title').textContent = item.title;
            $('.document-title').href = item.href;
            $('.document-read').href = item.href;
            const date = $('time'); date.dateTime = item.published || ''; date.textContent = item.published || '';
            let summary = item.annotation || item.summary || '';
            if (!summary || /^(?:【END】|\[END\]|\/\/)/.test(summary.trim())) summary = '打开这篇笔记，继续阅读与思考。';
            $('.document-summary').textContent = summary;
            $('.document-series').textContent = item.series || (Array.isArray(item.tags) ? item.tags.slice(0, 2).join(' · ') : '');
            const image = $('.document-image');
            image.hidden = !item.leadImage;
            $('.document-body').classList.toggle('has-image', !!item.leadImage);
            if (item.leadImage) {
                const source = (window.ZQR_IMAGE_SOURCES || {})[item.leadImage] || item.leadImage;
                image.src = source; image.alt = item.title + ' · 文章配图';
            } else { image.removeAttribute('src'); image.alt = ''; }
            $('.document-counter').textContent = String(index + 1).padStart(2, '0') + ' / ' + String(items.length).padStart(2, '0');
            host.querySelectorAll('.document-echo').forEach((echo, layer) => {
                let title = echo.querySelector('span');
                if (!title) { title = document.createElement('span'); echo.appendChild(title); }
                title.textContent = items[(index + layer + 1) % items.length].title;
            });
            host.dataset.selectedDocument = key(item);
            document.dispatchEvent(new CustomEvent('zqr:documentchange', {
                detail: { host, item: { ...item }, index, count: items.length }
            }));
            const documentElement = $('.selected-document');
            if (hadSelection && document.documentElement.dataset.motion !== 'reduced' && documentElement.animate) {
                documentElement.getAnimations().forEach(animation => animation.cancel());
                documentElement.animate([{ opacity: .7, transform: 'translateY(5px)' }, { opacity: 1, transform: 'none' }],
                    { duration: 260, easing: 'cubic-bezier(.2,.7,.2,1)' });
            }
            previous.disabled = next.disabled = items.length < 2;
        }
        function update(nextItems) {
            const selected = items[index] && key(items[index]);
            items = (nextItems || []).filter(item => item && item.href);
            index = Math.max(0, items.findIndex(item => key(item) === selected));
            if (!items.length) {
                $('.selected-document').hidden = true;
                $('.document-counter').textContent = '没有符合筛选条件的文章';
                previous.disabled = next.disabled = true;
                delete host.dataset.selectedDocument;
            } else select(index);
        }
        update(initialItems);
        return { update, select, selected: () => items[index] };
    }
    window.ZQRSpatial = { create };
})();
