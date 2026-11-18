/* TIFT Admin — sidebar yig'ish, sirg'aluvchi indikator, skeleton va kichik yaxshilanishlar.
   Django admin / Jazzmin funksiyalariga aralashmaydi: faqat qo'shimcha xatti-harakat. */
(function () {
    'use strict';
    var DESKTOP = window.matchMedia('(min-width: 992px)');
    var REDUCE = window.matchMedia('(prefers-reduced-motion: reduce)');
    var body = document.body;

    function setCookie(name, value) {
        document.cookie = name + '=' + value + ';path=/;max-age=31536000;SameSite=Lax';
    }
    function store(key, val) { try { if (val === undefined) return localStorage.getItem(key); localStorage.setItem(key, val); } catch (e) { return null; } }

    /* ── 1. Sidebar: kompyuterda mini/keng (holat saqlanadi), mobilda drawer ── */
    function applyCollapsed(collapsed) {
        body.classList.toggle('tift-collapsed', collapsed);
        setCookie('tift_sidebar', collapsed ? 'mini' : 'full');
        store('tift_sidebar', collapsed ? 'mini' : 'full');
        var t = document.querySelector('#jazzy-navbar [data-lte-toggle="sidebar"]');
        if (t) t.setAttribute('aria-expanded', String(!collapsed));
        window.setTimeout(placeIndicator, 260);
    }
    // Eski Jazzmin cookie'si sidebar'ni butunlay yashirib qo'ymasin
    if (DESKTOP.matches && body.classList.contains('sidebar-collapse')) {
        body.classList.remove('sidebar-collapse');
        setCookie('jazzy_menu', 'open');
    }
    if (store('tift_sidebar') === 'mini' && !body.classList.contains('tift-collapsed')) body.classList.add('tift-collapsed');

    var toggle = document.querySelector('#jazzy-navbar [data-lte-toggle="sidebar"]');
    if (toggle) {
        toggle.setAttribute('aria-label', 'Menyu');
        toggle.setAttribute('aria-controls', 'jazzy-sidebar');
        toggle.setAttribute('aria-expanded', String(!body.classList.contains('tift-collapsed')));
        // Kompyuterda AdminLTE'ning "butunlay yashirish" xatti-harakati o'rniga mini-sidebar
        window.addEventListener('click', function (e) {
            if (!DESKTOP.matches) return;               // mobil: AdminLTE drawer o'zi ishlaydi
            var t = e.target.closest && e.target.closest('#jazzy-navbar [data-lte-toggle="sidebar"]');
            if (!t) return;
            e.preventDefault();
            e.stopImmediatePropagation();
            applyCollapsed(!body.classList.contains('tift-collapsed'));
        }, true);
    }

    /* ── 2. Sirg'aluvchi faol menyu indikatori ── */
    var nav = document.querySelector('#jazzy-sidebar nav');
    var list = nav && nav.querySelector('ul');
    var indicator = null;
    function activeLink() { return list && list.querySelector('.custom-admin-nav-item.active'); }
    function placeIndicator(link, instant) {
        if (!indicator) return;
        link = link || activeLink();
        if (!link) { indicator.classList.remove('is-ready'); return; }
        var y = link.offsetTop, h = link.offsetHeight;
        if (instant) indicator.style.transition = 'none';
        indicator.style.transform = 'translateY(' + y + 'px)';
        indicator.style.height = h + 'px';
        indicator.classList.add('is-ready');
        if (instant) { indicator.offsetHeight; indicator.style.transition = ''; }
        store('tift_indicator_y', String(y));
    }
    if (list) {
        indicator = document.createElement('li');
        indicator.className = 'tift-indicator';
        indicator.setAttribute('aria-hidden', 'true');
        list.insertBefore(indicator, list.firstChild);
        nav.classList.add('has-indicator');
        list.querySelectorAll('.custom-admin-nav-item').forEach(function (a) {
            var label = (a.querySelector('span') || a).textContent.trim();
            a.setAttribute('data-label', label);
            if (a.classList.contains('active')) a.setAttribute('aria-current', 'page');
            a.addEventListener('mouseenter', function () {
                var r = a.getBoundingClientRect();
                a.style.setProperty('--tip-y', (r.top + r.height / 2) + 'px');
            });
            a.addEventListener('click', function (e) {
                if (e.metaKey || e.ctrlKey || e.shiftKey || a.target === '_blank') return;
                // bosilgan menyuga indikator darhol siljiydi (keyingi sahifa shu joydan davom etadi)
                list.querySelectorAll('.custom-admin-nav-item.active').forEach(function (x) { x.classList.remove('active'); });
                a.classList.add('active');
                placeIndicator(a);
            });
        });
        // Oldingi sahifadagi joydan yangi faol menyuga silliq o'tish
        var prev = parseFloat(store('tift_indicator_y'));
        var current = activeLink();
        if (!isNaN(prev) && current && !REDUCE.matches) {
            indicator.style.transition = 'none';
            indicator.style.transform = 'translateY(' + prev + 'px)';
            indicator.style.height = current.offsetHeight + 'px';
            indicator.classList.add('is-ready');
            indicator.offsetHeight;
            indicator.style.transition = '';
            requestAnimationFrame(function () { placeIndicator(current); });
        } else {
            placeIndicator(current, true);
        }
        window.addEventListener('resize', function () { placeIndicator(null, true); }, { passive: true });
    }

    /* ── 3. Skeleton: sahifa sekin ochilsa kontent joyida ko'rsatiladi ── */
    var main = document.querySelector('.app-main');
    if (main && !main.querySelector('.tift-skeleton')) {
        var sk = document.createElement('div');
        sk.className = 'tift-skeleton';
        sk.setAttribute('aria-hidden', 'true');
        sk.innerHTML = '<div class="sk sk-title"></div><div class="sk sk-bar"></div>' + new Array(7).join('<div class="sk sk-row"></div>');
        main.appendChild(sk);
    }
    var skTimer = null;
    function startLoading() {
        clearTimeout(skTimer);
        skTimer = setTimeout(function () { body.classList.add('tift-loading'); main && main.setAttribute('aria-busy', 'true'); }, 180);
    }
    function stopLoading() { clearTimeout(skTimer); body.classList.remove('tift-loading'); main && main.removeAttribute('aria-busy'); }
    document.addEventListener('click', function (e) {
        if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
        var a = e.target.closest && e.target.closest('a[href]');
        if (!a || a.target === '_blank' || a.hasAttribute('download')) return;
        var href = a.getAttribute('href');
        if (!href || href.charAt(0) === '#' || href.indexOf('javascript:') === 0) return;
        var url = new URL(a.href, location.href);
        if (url.origin !== location.origin || url.pathname.indexOf('/admin/') !== 0) return;
        if (a.closest('.related-widget-wrapper, .modal, [data-bs-toggle], .dropdown-menu .dropdown-toggle')) return;
        if (url.pathname === location.pathname && url.search === location.search) return;
        startLoading();
    });
    window.addEventListener('pageshow', stopLoading);   // orqaga/oldinga (bfcache) qaytilganda
    window.addEventListener('pagehide', function () { clearTimeout(skTimer); });

    /* ── 4. Kontentga o'tish havolasi (accessibility) ── */
    if (main && !document.querySelector('.tift-skip')) {
        if (!main.id) main.id = 'tift-main';
        main.setAttribute('tabindex', '-1');
        var skip = document.createElement('a');
        skip.className = 'tift-skip';
        skip.href = '#' + main.id;
        skip.textContent = 'Kontentga o‘tish';
        body.insertBefore(skip, body.firstChild);
    }
})();
