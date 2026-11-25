/* Оболочка макета Evercoin: навигация (боковая на компьютере, нижние вкладки на телефоне), роутер по #адресу, вход, тема.
   Устроена как оболочка макета AI Capper (ai_agent_capper/mockup/js/app.js). */
(function () {
  'use strict';
  const { h, icon, clear, fmt, button, modal, toast } = UI;

  const NAV = [
    { id: 'dashboard', label: 'Главная', icon: 'home' },
    { id: 'operations', label: 'Операции', icon: 'list' },
    { id: 'wallets', label: 'Счета', icon: 'wallet' },
    { id: 'categories', label: 'Категории', icon: 'tag' },
    { id: 'analytics', label: 'Аналитика', icon: 'chart' },
  ];
  const TABS = [
    { id: 'dashboard', label: 'Главная', icon: 'home' },
    { id: 'operations', label: 'Операции', icon: 'list' },
    { id: 'add', label: 'Добавить', icon: 'plus', primary: true },
    { id: 'analytics', label: 'Аналитика', icon: 'chart' },
    { id: 'more', label: 'Еще', icon: 'menu' },
  ];
  const MORE_IDS = ['wallets', 'categories', 'profile'];

  // ---- вход: прямая ссылка на экран открывает его без входа — так удобнее согласовывать макет ----
  const store = {
    get(k) { try { return sessionStorage.getItem('evercoin.' + k); } catch (e) { return null; } },
    set(k, v) { try { if (v == null) sessionStorage.removeItem('evercoin.' + k); else sessionStorage.setItem('evercoin.' + k, v); } catch (e) { /* работаем в памяти */ } },
  };
  const state = { authed: store.get('authed') === '1' };
  if (location.hash.slice(1) && location.hash.slice(1) !== 'login') state.authed = true;
  UI.auth = {
    login() { state.authed = true; store.set('authed', '1'); UI.go('dashboard'); },
    logout() { state.authed = false; store.set('authed', null); UI.go('login'); toast('Вы вышли из аккаунта', 'logout'); },
  };

  // ---- тема: как в системе, светлая или темная ----
  function systemDark() { return window.matchMedia('(prefers-color-scheme: dark)').matches; }
  UI.theme = {
    get() { return document.documentElement.dataset.theme || 'system'; },
    isDark() { const t = UI.theme.get(); return t === 'dark' || (t === 'system' && systemDark()); },
    set(v) {
      if (v === 'system') delete document.documentElement.dataset.theme; else document.documentElement.dataset.theme = v;
      try { localStorage.setItem('evercoin.theme', v); } catch (e) { /* ок */ }
      UI.refresh();
    },
    toggle() { UI.theme.set(UI.theme.isDark() ? 'light' : 'dark'); },
  };
  try { const t = localStorage.getItem('evercoin.theme'); if (t === 'light' || t === 'dark') document.documentElement.dataset.theme = t; } catch (e) { /* ок */ }

  // ---- знак: монета с буквой E и бликом (блик — цвет мяча из знака AI Capper) ----
  function brandMark() {
    return h('svg', { class: 'brand-mark', viewBox: '0 0 36 36', 'aria-hidden': 'true' },
      h('rect', { x: 1, y: 1, width: 34, height: 34, rx: 9, fill: 'var(--accent)' }),
      h('circle', { cx: 16.5, cy: 19, r: 8.5, fill: 'none', stroke: 'var(--accent-fg)', 'stroke-width': 1.7 }),
      h('path', { d: 'M19.5 15H14v8h5.5M14 19h4.5', fill: 'none', stroke: 'var(--accent-fg)', 'stroke-width': 1.7, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }),
      h('circle', { cx: 25.5, cy: 10.5, r: 3.2, fill: 'var(--brand-spark)', stroke: 'var(--accent)', 'stroke-width': 1.2 }));
  }
  UI.brandMark = brandMark;

  // ---- шапка экрана: экран задает заголовок, путь и свои кнопки ----
  let headerSlot = null;
  UI.setHeader = function (o) {
    if (!headerSlot) return;
    const t = headerSlot.querySelector('.topbar-title');
    clear(t);
    if (o.crumbs) t.appendChild(h('div', { class: 'crumbs' }, o.crumbs.map((c, i) => [i ? ' / ' : null, c.href ? h('a', { href: c.href }, c.label) : c.label])));
    t.appendChild(h('h1', null, o.title));
    const extra = headerSlot.querySelector('.topbar-extra');
    clear(extra);
    if (o.actions) UI.append(extra, [o.actions]);
  };

  function themeLabel() { return UI.theme.isDark() ? 'Светлая тема' : 'Темная тема'; }
  function moreSheet(navId) {
    modal({
      title: 'Еще',
      body: close => h('nav', { class: 'list', 'aria-label': 'Другие разделы' },
        [{ id: 'wallets', label: 'Счета', icon: 'wallet' }, { id: 'categories', label: 'Категории', icon: 'tag' }, { id: 'profile', label: 'Профиль и настройки', icon: 'user' }]
          .map(it => h('a', { class: 'nav-link', href: '#' + it.id, 'aria-current': navId === it.id ? 'page' : null, on: { click: close } }, icon(it.icon), it.label)),
        h('button', { class: 'nav-link', type: 'button', on: { click: () => { close(); UI.theme.toggle(); } } }, icon(UI.theme.isDark() ? 'sun' : 'moon'), themeLabel()),
        h('button', { class: 'nav-link danger', type: 'button', on: { click: () => { close(); UI.auth.logout(); } } }, icon('logout'), 'Выйти')),
    });
  }

  function shell(navId) {
    const sidebar = h('aside', { class: 'sidebar', 'aria-label': 'Основная навигация' },
      h('a', { class: 'brand', href: '#dashboard' }, brandMark(), h('div', null, h('div', { class: 'brand-name' }, 'Evercoin'), h('div', { class: 'brand-sub' }, 'личные финансы'))),
      NAV.map(it => h('a', { class: 'nav-link', href: '#' + it.id, 'aria-current': navId === it.id ? 'page' : null }, icon(it.icon), it.label)),
      h('div', { class: 'sidebar-foot' },
        h('a', { class: 'nav-link', href: '#profile', 'aria-current': navId === 'profile' ? 'page' : null }, icon('user'), 'Профиль'),
        h('button', { class: 'nav-link', type: 'button', on: { click: () => UI.theme.toggle() } }, icon(UI.theme.isDark() ? 'sun' : 'moon'), themeLabel()),
        h('button', { class: 'nav-link', type: 'button', on: { click: () => UI.auth.logout() } }, icon('logout'), 'Выйти')));

    const total = DATA.total();
    const topbar = h('header', { class: 'topbar' },
      h('a', { class: 'topbar-home', href: '#dashboard', 'aria-label': 'На главную' }, brandMark()),
      h('div', { class: 'topbar-title' }),
      h('div', { class: 'topbar-actions' },
        h('span', { class: 'demo-pill hide-mobile', title: 'Это макет: все цифры вымышлены' }, 'Макет · данные вымышлены'),
        h('div', { class: 'topbar-extra row' }),
        h('a', { class: 'total-pill hide-mobile', href: '#wallets', title: 'Всего на счетах, без счетов вне общего баланса' }, h('span', { class: 'muted' }, 'Всего'), h('b', null, fmt.money(total, DATA.base, { frac: 'never' }))),
        button('Операция', { kind: 'primary', icon: 'plus', class: 'hide-mobile', onClick: () => UI.parts.editOp() }),
        h('a', { class: 'avatar', href: '#profile', title: 'Профиль · ' + DATA.user.name, 'aria-label': 'Профиль' }, DATA.user.initials)));
    headerSlot = topbar;

    const tabbar = h('nav', { class: 'tabbar', 'aria-label': 'Нижняя навигация' }, TABS.map(t => {
      if (t.primary) return h('button', { class: 'tab tab-primary', type: 'button', on: { click: () => UI.parts.editOp() } }, h('span', { class: 'tab-plus' }, icon(t.icon)), t.label);
      if (t.id === 'more') return h('button', { class: 'tab', type: 'button', 'aria-current': MORE_IDS.includes(navId) ? 'page' : null, on: { click: () => moreSheet(navId) } }, icon(t.icon), t.label);
      return h('a', { class: 'tab', href: '#' + t.id, 'aria-current': navId === t.id ? 'page' : null }, icon(t.icon), t.label);
    }));

    const view = h('main', { class: 'view', id: 'view', tabindex: '-1' });
    const root = h('div', { class: 'shell' }, h('div', { class: 'sidebar-col' }, sidebar), h('div', { class: 'main' }, topbar, view), tabbar);
    return { root, view };
  }

  // ---- роутер: #dashboard, #operations, #wallets, #wallet-<id>, #categories, #analytics, #profile, #login, #new ----
  function parse() {
    const raw = location.hash.slice(1);
    if (!raw) return { id: state.authed ? 'dashboard' : 'login', param: null };
    const i = raw.indexOf('-');
    const id = i > 0 ? raw.slice(0, i) : raw, param = i > 0 ? raw.slice(i + 1) : null;
    return { id, param };
  }
  let lastKey = '';
  function render(keepScroll) {
    UI.hideTip();
    document.querySelectorAll('.dd-pop, .dd-back').forEach(el => el.remove());
    let { id, param } = parse();
    const app = document.getElementById('app');
    if (!state.authed && id !== 'login') id = 'login';
    const openNew = id === 'new';
    if (openNew) id = 'dashboard';
    const def = UI.screens[id] || UI.screens.dashboard;
    const y = window.scrollY;
    clear(app);
    if (id === 'login') { def.render(app, param); document.title = 'Вход · Evercoin'; return; }
    const { root, view } = shell(def.nav || id);
    app.appendChild(root);
    UI.setHeader({ title: def.title });
    view.appendChild(h('span', { class: 'demo-pill mobile-note' }, 'Макет · данные вымышлены'));
    def.render(view, param);
    document.title = (view.dataset.title || def.title) + ' · Evercoin';
    const key = id + ':' + param;
    if (keepScroll && key === lastKey) window.scrollTo(0, y); else window.scrollTo(0, 0);
    lastKey = key;
    if (openNew) UI.parts.editOp();
  }
  // перерисовать текущий экран после изменения данных (новая операция, смена валюты, темы)
  UI.refresh = () => render(true);
  window.addEventListener('hashchange', () => render(false));
  let wasMobile = UI.isMobile();
  window.addEventListener('resize', () => { const m = UI.isMobile(); if (m !== wasMobile) { wasMobile = m; render(true); } });
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => { if (UI.theme.get() === 'system') render(true); });
  render(false);
})();
