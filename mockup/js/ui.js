/* UI-кит макета Evercoin: построитель элементов, иконки, деньги и даты, компоненты, графики.
   Устроен так же, как UI-кит макета AI Capper (ai_agent_capper/mockup/js/ui.js). Экраны пользуются только window.UI. */
(function () {
  'use strict';

  // ---------- элементы ----------
  // h('div', {class, style, on:{click}, text, ...атрибуты}, ...дети); дети: строка | число | Node | массив | null
  const SVG_TAGS = new Set(['svg', 'path', 'g', 'line', 'rect', 'circle', 'text', 'title']);
  function h(tag, attrs, ...children) {
    const el = SVG_TAGS.has(tag) ? document.createElementNS('http://www.w3.org/2000/svg', tag) : document.createElement(tag);
    if (attrs) {
      for (const [k, v] of Object.entries(attrs)) {
        if (v == null || v === false) continue;
        if (k === 'class') el.setAttribute('class', Array.isArray(v) ? v.filter(Boolean).join(' ') : v);
        else if (k === 'style') {
          if (typeof v === 'string') el.setAttribute('style', v);
          else for (const [sk, sv] of Object.entries(v)) { if (sv != null) el.style.setProperty(sk.startsWith('--') ? sk : sk.replace(/[A-Z]/g, m => '-' + m.toLowerCase()), sv); }
        }
        else if (k === 'on') for (const [ev, fn] of Object.entries(v)) { if (fn) el.addEventListener(ev, fn); }
        else if (k === 'text') el.textContent = v;
        else el.setAttribute(k, v === true ? '' : v);
      }
    }
    append(el, children);
    return el;
  }
  function append(el, children) {
    if (!Array.isArray(children)) children = [children];
    for (const c of children) {
      if (c == null || c === false || c === true) continue;
      if (Array.isArray(c)) append(el, c);
      else if (c instanceof Node) el.appendChild(c);
      else el.appendChild(document.createTextNode(String(c)));
    }
    return el;
  }
  function clear(el) { while (el.firstChild) el.removeChild(el.firstChild); return el; }
  const isMobile = () => window.matchMedia('(max-width: 960px)').matches;
  const isPhone = () => window.matchMedia('(max-width: 720px)').matches;

  // ---------- иконки (24×24, линия 1.8 — как в AI Capper) ----------
  const ICONS = {
    home: 'M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z',
    list: 'M8 6h13M8 12h13M8 18h13M3.5 6h.01M3.5 12h.01M3.5 18h.01',
    wallet: 'M4 7a2 2 0 0 1 2-2h12v4M4 7v11a2 2 0 0 0 2 2h14V9H6a2 2 0 0 1-2-2zM16 14.5h.01',
    tag: 'M3 12V4a1 1 0 0 1 1-1h8l9 9-9 9zM7.5 7.5h.01',
    chart: 'M4 20V4M4 20h16M8 16l4-5 3 3 5-7',
    bars: 'M5 20V10M12 20V4M19 20v-7',
    user: 'M20 21v-1.5a4.5 4.5 0 0 0-4.5-4.5h-7A4.5 4.5 0 0 0 4 19.5V21M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z',
    plus: 'M12 5v14M5 12h14',
    x: 'M6 6l12 12M18 6 6 18',
    check: 'M5 12.5 10 17 19 7',
    search: 'M11 18a7 7 0 1 0 0-14 7 7 0 0 0 0 14zM20 20l-4-4',
    chevronRight: 'M9 6l6 6-6 6',
    chevronLeft: 'M15 6l-6 6 6 6',
    chevronDown: 'M6 9l6 6 6-6',
    arrowUp: 'M12 19V5M6 11l6-6 6 6',
    arrowDown: 'M12 5v14M6 13l6 6 6-6',
    arrowRight: 'M5 12h14M13 6l6 6-6 6',
    transfer: 'M4 8h15M15 4l4 4-4 4M20 16H5M9 12l-4 4 4 4',
    sun: 'M12 16a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4',
    moon: 'M20 14.5A8.5 8.5 0 0 1 9.5 4 8.5 8.5 0 1 0 20 14.5z',
    logout: 'M15 4h3a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-3M10 17l-5-5 5-5M5 12h11',
    menu: 'M4 7h16M4 12h16M4 17h16',
    eye: 'M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12zM12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z',
    eyeOff: 'M3 3l18 18M10.6 5.1A10 10 0 0 1 12 5c6.5 0 10 7 10 7a17 17 0 0 1-3.2 4.1M6.6 6.6C3.9 8.4 2 12 2 12s3.5 7 10 7c1.7 0 3.2-.5 4.5-1.2M9.9 9.9a3 3 0 0 0 4.2 4.2',
    edit: 'M4 20h4L19 9l-4-4L4 16zM13.5 6.5l4 4',
    trash: 'M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13',
    copy: 'M9 9h10a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H9a1 1 0 0 1-1-1V10a1 1 0 0 1 1-1zM5 15H4a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v1',
    download: 'M12 4v12M7 11l5 5 5-5M4 16v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3',
    lock: 'M6 11h12a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1v-8a1 1 0 0 1 1-1zM8 11V7a4 4 0 0 1 8 0v4',
    info: 'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM12 11v5M12 8h.01',
    alert: 'M12 4 2.5 20h19zM12 10v4M12 17h.01',
    calendar: 'M5 5h14a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1zM4 10h16M8 3v4M16 3v4',
    merge: 'M6 4v4a4 4 0 0 0 4 4h4a4 4 0 0 1 4 4v4M18 4v4a4 4 0 0 1-4 4M6 20v-4',
    more: 'M5 12h.01M12 12h.01M19 12h.01',
    star: 'M12 3.5l2.6 5.3 5.9.9-4.2 4.1 1 5.8-5.3-2.8-5.3 2.8 1-5.8-4.2-4.1 5.9-.9z',
    // счета
    card: 'M3 6a1 1 0 0 1 1-1h16a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1zM3 10h18M7 15h3',
    cash: 'M3 7h18v10H3zM12 14.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zM6.5 10h.01M17.5 14h.01',
    safe: 'M4 4h16a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1zM13 14.5a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM7 9v4M7 19v2M17 19v2',
    currency: 'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM14.8 9.2A3 3 0 0 0 12 7.5c-1.7 0-3 .9-3 2.2 0 3 6 1.6 6 4.6 0 1.3-1.3 2.2-3 2.2a3 3 0 0 1-2.8-1.7M12 6v1.5M12 16.5V18',
    trendUp: 'M3 17l6-6 4 4 8-8M15 7h6v6',
    coins: 'M9 14c3.3 0 6-1.3 6-3s-2.7-3-6-3-6 1.3-6 3 2.7 3 6 3zM3 11v4c0 1.7 2.7 3 6 3s6-1.3 6-3v-4M15 8.5c3.3 0 6-1.3 6-3s-2.7-3-6-3-6 1.3-6 3M21 5.5v4c0 1.4-1.8 2.5-4.3 2.9M21 9.5v4c0 1.4-1.8 2.5-4.3 2.9',
    // категории
    cart: 'M3 4h2l2.4 10.2a1 1 0 0 0 1 .8h8.9a1 1 0 0 0 1-.8L20 8H6.2M10 19.5h.01M17 19.5h.01',
    bus: 'M6 4h12a2 2 0 0 1 2 2v10a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a2 2 0 0 1 2-2zM4 11h16M8 17v2M16 17v2M8 14h.01M16 14h.01',
    heart: 'M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z',
    ticket: 'M4 7a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v2a2 2 0 0 0 0 4v2a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-2a2 2 0 0 0 0-4zM14 5v14',
    shirt: 'M8 4 4 6.5l1.5 4L8 9.5V20h8V9.5l2.5 1 1.5-4L16 4a4 4 0 0 1-8 0z',
    bolt: 'M13 2 4 14h7l-1 8 9-12h-7z',
    repeat: 'M17 3l3 3-3 3M4 12v-2a4 4 0 0 1 4-4h12M7 21l-3-3 3-3M20 12v2a4 4 0 0 1-4 4H4',
    briefcase: 'M4 8h16a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1zM9 8V5.5A1.5 1.5 0 0 1 10.5 4h3A1.5 1.5 0 0 1 15 5.5V8M3 13h18',
    laptop: 'M5 6a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v9H5zM3 18h18',
    gift: 'M4 11h16v9a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1zM3 7h18v4H3zM12 7v14M12 7S10.5 3 8 3a2 2 0 0 0 0 4M12 7s1.5-4 4-4a2 2 0 0 1 0 4',
    book: 'M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2zM4 19a2 2 0 0 1 2-2h13',
    plane: 'M10.5 13.5 3 11l1.5-1.5 8 1L17 6a2 2 0 0 1 3 3l-4.5 4.5 1 8L15 23l-2.5-7.5L9 19v2.5L7.5 23 6 19l-4-1.5L3.5 16H6z',
    coffee: 'M5 9h11v5a5 5 0 0 1-5 5h-1a5 5 0 0 1-5-5zM16 10h1.5a2.5 2.5 0 0 1 0 5H16M8 3v3M11 3v3',
  };
  function icon(name, attrs) {
    const d = ICONS[name] || ICONS.info;
    return h('svg', Object.assign({ viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.8', 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'aria-hidden': 'true' }, attrs || {}), h('path', { d }));
  }

  // ---------- деньги и даты (ru-RU) ----------
  const MINUS = '−', NBSP = ' ';
  const CURRENCIES = {
    RUB: { code: 'RUB', sym: '₽', name: 'Российский рубль', dec: 2 },
    USD: { code: 'USD', sym: '$', name: 'Доллар США', dec: 2 },
    EUR: { code: 'EUR', sym: '€', name: 'Евро', dec: 2 },
    GBP: { code: 'GBP', sym: '£', name: 'Фунт стерлингов', dec: 2 },
    CNY: { code: 'CNY', sym: '¥', name: 'Китайский юань', dec: 2 },
    JPY: { code: 'JPY', sym: 'JP¥', name: 'Японская иена', dec: 0 },
  };
  const nfCache = {};
  const nf = dec => nfCache[dec] || (nfCache[dec] = new Intl.NumberFormat('ru-RU', { minimumFractionDigits: dec, maximumFractionDigits: dec }));
  const MONTHS_GEN = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'];
  const MONTHS_NOM = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];
  const MONTHS_SHORT = ['янв', 'фев', 'мар', 'апр', 'май', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек'];
  const WEEKDAYS = ['воскресенье', 'понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота'];
  const pad = n => String(n).padStart(2, '0');
  const isoDay = d => d.getUTCFullYear() + '-' + pad(d.getUTCMonth() + 1) + '-' + pad(d.getUTCDate());
  const parseDay = s => new Date(s.slice(0, 10) + 'T12:00:00Z');
  function addDays(iso, n) { const d = parseDay(iso); d.setUTCDate(d.getUTCDate() + n); return isoDay(d); }

  // Скрытые суммы: «глаз» на главной и настройка в профиле
  let privacy = false;
  try { privacy = localStorage.getItem('evercoin.privacy') === '1'; } catch (e) { /* хранилище недоступно */ }

  const fmt = {
    MINUS,
    plural: (n, one, few, many) => { const a = Math.abs(n) % 100, b = a % 10; return a > 10 && a < 20 ? many : b > 1 && b < 5 ? few : b === 1 ? one : many; },
    num: (v, dec = 0) => nf(dec).format(v).replace('-', MINUS),
    pct: (v, dec = 0) => nf(dec).format(v * 100) + NBSP + '%',
    sym: code => (CURRENCIES[code] || CURRENCIES.RUB).sym,
    // части суммы: целая часть, копейки (если есть), знак, символ валюты
    parts(v, code = 'RUB', o = {}) {
      const c = CURRENCIES[code] || CURRENCIES.RUB;
      const abs = Math.abs(v);
      const hasFrac = c.dec > 0 && Math.round(abs * 100) % 100 !== 0;
      const showFrac = o.frac === 'always' ? c.dec > 0 : o.frac === 'never' ? false : hasFrac;
      const s = nf(showFrac ? c.dec : 0).format(showFrac ? abs : Math.round(abs));
      const i = s.lastIndexOf(',');
      let sign = '';
      if (o.sign === 'always') sign = v > 0 ? '+' : v < 0 ? MINUS : '';
      else if (v < 0) sign = MINUS;
      return { sign, int: showFrac ? s.slice(0, i) : s, frac: showFrac ? s.slice(i) : '', sym: c.sym };
    },
    money(v, code = 'RUB', o = {}) {
      if (privacy && !o.reveal) return '••••' + NBSP + fmt.sym(code);
      const p = fmt.parts(v, code, o);
      return p.sign + p.int + p.frac + NBSP + p.sym;
    },
    // короткая сумма для осей графиков: 120 тыс, 1,2 млн
    short(v) {
      const a = Math.abs(v), s = v < 0 ? MINUS : '';
      if (a >= 1e6) return s + nf(a >= 1e7 ? 0 : 1).format(a / 1e6).replace(/,0$/, '') + NBSP + 'млн';
      if (a >= 1e3) return s + nf(0).format(Math.round(a / 1e3)) + NBSP + 'тыс';
      return s + nf(0).format(a);
    },
    date(iso, withYear) {
      const d = parseDay(iso);
      const y = d.getUTCFullYear();
      return d.getUTCDate() + NBSP + MONTHS_GEN[d.getUTCMonth()] + (withYear || y !== fmt.todayYear() ? NBSP + y : '');
    },
    dateShort: iso => { const d = parseDay(iso); return d.getUTCDate() + NBSP + MONTHS_SHORT[d.getUTCMonth()]; },
    time: iso => iso.length > 10 ? iso.slice(11, 16) : '',
    weekday: iso => WEEKDAYS[parseDay(iso).getUTCDay()],
    // заголовок дня в списке операций: «Сегодня», «Вчера», «23 ноября, понедельник»
    dayTitle(iso) {
      const t = fmt.today();
      if (iso === t) return 'Сегодня';
      if (iso === addDays(t, -1)) return 'Вчера';
      return fmt.date(iso) + ', ' + fmt.weekday(iso);
    },
    month: (y, m) => MONTHS_NOM[m] + ' ' + y,
    monthName: m => MONTHS_NOM[m],
    monthShort: m => MONTHS_SHORT[m],
    monthGen: m => MONTHS_GEN[m],
    monthPrep: m => ['январе', 'феврале', 'марте', 'апреле', 'мае', 'июне', 'июле', 'августе', 'сентябре', 'октябре', 'ноябре', 'декабре'][m],
    today: () => (window.DATA ? DATA.today : isoDay(new Date())),
    todayYear: () => +fmt.today().slice(0, 4),
  };

  // ---------- компоненты ----------
  function button(label, o = {}) {
    const cls = ['btn', o.kind || 'secondary', o.size, o.block && 'block', !label && 'icon-only', o.class];
    const kids = [o.icon && icon(o.icon), label && h('span', null, label), o.iconRight && icon(o.iconRight)];
    if (o.href) return h('a', Object.assign({ class: cls, href: o.href, title: o.title, 'aria-label': o.ariaLabel || (label ? null : o.title) }, o.attrs || {}), kids);
    return h('button', Object.assign({ class: cls, type: o.type || 'button', title: o.title, disabled: o.disabled, 'aria-label': o.ariaLabel || (label ? null : o.title), on: o.onClick ? { click: o.onClick } : null }, o.attrs || {}), kids);
  }

  // card({eyebrow, title, subtitle, actions, body, foot, flush, class, href})
  function card(o = {}) {
    const head = (o.title || o.actions || o.eyebrow) ? h('div', { class: 'card-head' },
      h('div', { style: 'min-width:0' }, o.eyebrow && h('div', { class: 'eyebrow' }, o.eyebrow), o.title && h('h3', null, o.title), o.subtitle && h('div', { class: 'card-sub' }, o.subtitle)),
      o.actions && h('div', { class: 'row' }, o.actions)) : null;
    return h(o.href ? 'a' : 'section', { class: ['card', o.class], href: o.href, style: o.style },
      head,
      o.body != null && h('div', { class: ['card-body', o.flush && 'flush'] }, o.body),
      o.foot && h('div', { class: 'card-foot' }, o.foot));
  }

  // delta({value, text, good}) — good: true, если рост — это хорошо
  function delta(value, text, goodWhenUp = true) {
    if (!value) return h('span', { class: 'delta flat' }, text);
    const up = value > 0, good = up === goodWhenUp;
    return h('span', { class: ['delta', good ? 'good' : 'bad'] }, icon(up ? 'arrowUp' : 'arrowDown'), text);
  }

  // stat({label, value: node, foot: node, class})
  function stat(o) {
    return h('section', { class: ['card', o.class] }, h('div', { class: 'stat' },
      h('div', { class: 'stat-label' }, o.label),
      h('div', { class: 'stat-value' }, o.value),
      o.foot && h('div', { class: 'stat-foot' }, o.foot)));
  }

  function chip(text, kind, ic) { return h('span', { class: ['chip', kind] }, ic && icon(ic), text); }

  // segmented({label, options:[{value,label}], value, onChange, block})
  function segmented(o) {
    const el = h('div', { class: ['segmented', o.block && 'block'], role: 'group', 'aria-label': o.label });
    let cur = o.value;
    function draw() {
      clear(el);
      o.options.forEach(opt => el.appendChild(h('button', { type: 'button', 'aria-pressed': opt.value === cur ? 'true' : 'false', on: { click: () => { if (opt.value === cur) return; cur = opt.value; draw(); o.onChange && o.onChange(cur); } } }, opt.label)));
    }
    draw();
    return el;
  }

  // field({id, label, hint, type, value, placeholder, suffix, icon, inputmode, textarea, attrs, labelAside})
  function field(o) {
    const common = Object.assign({ id: o.id, name: o.id, placeholder: o.placeholder, autocomplete: o.autocomplete || 'off', inputmode: o.inputmode, required: o.required }, o.attrs || {});
    let control;
    if (o.textarea) control = h('textarea', Object.assign({ class: 'textarea', rows: o.rows || 2 }, common), o.value || '');
    else control = h('input', Object.assign({ class: ['input', o.suffix && 'has-suffix', o.icon && 'has-icon', o.action && 'has-action'], type: o.type || 'text', value: o.value }, common));
    const wrap = (o.suffix || o.icon || o.action) ? h('div', { class: 'input-wrap' }, o.icon && icon(o.icon, { class: 'input-icon' }), control, o.suffix && h('span', { class: 'input-suffix' }, o.suffix), o.action) : control;
    return h('div', { class: ['field', o.class] },
      o.label && h('label', { class: 'field-label', for: o.id }, h('span', null, o.label), o.labelAside),
      wrap,
      o.hint && h('div', { class: 'field-hint' }, o.hint),
      h('div', { class: 'field-error', id: o.id + '-error', hidden: true }));
  }
  function fieldError(id, text) {
    const err = document.getElementById(id + '-error'), input = document.getElementById(id);
    if (err) { err.textContent = text || ''; err.hidden = !text; }
    if (input) { input.classList.toggle('invalid', !!text); if (text) input.setAttribute('aria-invalid', 'true'); else input.removeAttribute('aria-invalid'); }
  }

  // toggle({id, label, hint, checked, disabled, onChange})
  function toggle(o) {
    const input = h('input', { type: 'checkbox', id: o.id, role: 'switch', checked: o.checked, disabled: o.disabled, on: { change: e => o.onChange && o.onChange(e.target.checked) } });
    return h('label', { class: 'toggle', for: o.id },
      h('span', { class: 'toggle-text' }, h('span', { class: 'toggle-label' }, o.label), o.hint && h('span', { class: 'field-hint' }, o.hint)),
      h('span', { class: 'switch' }, input, h('span')));
  }

  function meter(value, max, kind, color) {
    const pct = max > 0 ? Math.max(0, Math.min(100, value / max * 100)) : 0;
    return h('div', { class: ['meter', kind], role: 'meter', 'aria-valuenow': Math.round(pct), 'aria-valuemin': 0, 'aria-valuemax': 100 }, h('i', { style: { width: pct + '%', background: color } }));
  }

  function callout(kind, ic, ...content) { return h('div', { class: ['callout', kind] }, icon(ic || 'info'), h('div', { style: 'min-width:0' }, content)); }

  function empty(o) {
    return h('div', { class: 'empty' },
      h('div', { class: 'empty-icon' }, icon(o.icon || 'list')),
      h('div', { class: 'empty-title' }, o.title),
      o.text && h('p', { class: 'empty-text' }, o.text),
      o.action);
  }

  function kv(pairs) { return h('dl', { class: 'kv' }, pairs.filter(Boolean).map(([k, v]) => [h('dt', null, k), h('dd', null, v)])); }

  // ---------- выпадающий список: один компонент на все приложение, без системного select ----------
  // dropdown({id, label, options:[{value,label,icon,color,hint}], value, onChange, compact, ariaLabel})
  function dropdown(o) {
    let cur = o.value;
    const valueEl = h('span', { class: 'dd-value' });
    const trigger = h('button', { type: 'button', id: o.id, class: ['input', 'dd-trigger', o.compact && 'compact'], 'aria-haspopup': 'listbox', 'aria-expanded': 'false', 'aria-label': o.ariaLabel }, valueEl, h('span', { class: 'dd-chev' }, icon('chevronDown')));
    function optVisual(opt) {
      return [opt.icon && catIcon({ icon: opt.icon, color: opt.color }, 'sm'), !opt.icon && opt.color && h('i', { class: 'dot', style: { background: opt.color } })];
    }
    function drawValue() {
      clear(valueEl);
      const opt = o.options.find(x => x.value === cur);
      if (opt) append(valueEl, [optVisual(opt), h('span', { style: 'overflow:hidden;text-overflow:ellipsis' }, opt.label)]);
      else valueEl.appendChild(h('span', { class: 'muted' }, o.placeholder || 'Выберите'));
    }
    drawValue();
    let pop = null, back = null;
    function close(focus) {
      if (!pop) return;
      pop.remove(); back.remove(); pop = back = null;
      trigger.setAttribute('aria-expanded', 'false');
      document.removeEventListener('keydown', onKey, true);
      if (focus) trigger.focus();
    }
    let active = 0, optEls = [];
    function setActive(i) {
      active = Math.max(0, Math.min(optEls.length - 1, i));
      optEls.forEach((el, j) => el.classList.toggle('is-active', j === active));
      if (optEls[active]) optEls[active].scrollIntoView({ block: 'nearest' });
    }
    function choose(i) {
      const opt = o.options[i];
      if (!opt) return;
      close(true);
      if (opt.value !== cur) { cur = opt.value; drawValue(); o.onChange && o.onChange(cur); }
    }
    function onKey(e) {
      if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); close(true); }
      else if (e.key === 'ArrowDown') { e.preventDefault(); setActive(active + 1); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); setActive(active - 1); }
      else if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); choose(active); }
      else if (e.key === 'Tab') close(false);
    }
    function open() {
      back = h('div', { class: 'dd-back', on: { click: () => close(true) } });
      optEls = o.options.map((opt, i) => h('div', { class: 'dd-opt', role: 'option', 'aria-selected': opt.value === cur ? 'true' : 'false', on: { click: () => choose(i), pointermove: () => setActive(i) } },
        optVisual(opt), h('span', { class: 'dd-opt-label' }, opt.label), opt.hint && h('span', { class: 'dd-opt-hint' }, opt.hint), icon('check', { class: 'check-ic' })));
      pop = h('div', { class: 'dd-pop', role: 'listbox', tabindex: '-1', 'aria-label': o.label || o.ariaLabel }, optEls);
      document.body.appendChild(back); document.body.appendChild(pop);
      if (!isPhone()) {
        const r = trigger.getBoundingClientRect();
        pop.style.minWidth = Math.max(r.width, 200) + 'px';
        const below = window.innerHeight - r.bottom;
        const ph = Math.min(pop.offsetHeight, 360);
        pop.style.left = Math.max(12, Math.min(r.left, window.innerWidth - pop.offsetWidth - 12)) + 'px';
        pop.style.top = (below < ph + 16 && r.top > below ? r.top - ph - 6 : r.bottom + 6) + 'px';
      }
      trigger.setAttribute('aria-expanded', 'true');
      document.addEventListener('keydown', onKey, true);
      setActive(Math.max(0, o.options.findIndex(x => x.value === cur)));
      pop.focus();
    }
    trigger.addEventListener('click', () => (pop ? close(true) : open()));
    const wrap = o.label ? h('div', { class: 'field' }, h('label', { class: 'field-label', for: o.id }, o.label), trigger, o.hint && h('div', { class: 'field-hint' }, o.hint)) : trigger;
    wrap.getValue = () => cur;
    wrap.setValue = v => { cur = v; drawValue(); };
    wrap.setOptions = opts => { o.options = opts; if (!opts.find(x => x.value === cur)) cur = opts[0] && opts[0].value; drawValue(); };
    return wrap;
  }

  // ---------- модальное окно: по центру на компьютере, шторка снизу на телефоне ----------
  // modal({title, body: close => node, foot: close => nodes, onClose})
  function modal(o) {
    const prevFocus = document.activeElement;
    const onKey = e => { if (e.key === 'Escape' && !document.querySelector('.dd-pop')) close(); };
    function close() {
      back.remove(); document.removeEventListener('keydown', onKey);
      if (prevFocus && prevFocus.focus && document.contains(prevFocus)) prevFocus.focus();
      o.onClose && o.onClose();
    }
    const box = h('div', { class: 'modal', tabindex: '-1', role: 'dialog', 'aria-modal': 'true', 'aria-label': o.title },
      h('div', { class: 'modal-head' }, h('h2', { style: 'font-size:var(--fs-lg)' }, o.title), button(null, { kind: 'ghost', icon: 'x', title: 'Закрыть', onClick: close })),
      h('div', { class: 'modal-body' }, o.body(close)),
      o.foot && h('div', { class: 'modal-foot' }, o.foot(close)));
    const back = h('div', { class: 'modal-backdrop', on: { click: e => { if (e.target === back) close(); } } }, box);
    document.body.appendChild(back);
    document.addEventListener('keydown', onKey);
    box.focus();
    return { close, box };
  }

  function toast(msg, ic) {
    const host = document.getElementById('toast-host');
    const t = h('div', { class: 'toast', role: 'status' }, icon(ic || 'check'), h('span', null, msg));
    host.appendChild(t);
    setTimeout(() => t.remove(), 3200);
  }

  // ---------- значки и суммы Evercoin ----------
  function catIcon(c, size) {
    return h('span', { class: ['cat-ic', size, c.square && 'sq'], style: { '--c': c.color || 'var(--fg-3)' }, 'aria-hidden': 'true' }, icon(c.icon || 'tag'));
  }
  // amountEl(v, code, {kind: 'income'|'expense'|'transfer'|'balance', frac, reveal}) — копейки мельче
  function amountEl(v, code, o = {}) {
    const kind = o.kind || 'balance';
    if (privacy && !o.reveal) return h('span', { class: ['amount', o.class] }, '••••' + NBSP + fmt.sym(code));
    const signed = kind === 'expense' ? -Math.abs(v) : kind === 'income' ? Math.abs(v) : v;
    const p = fmt.parts(signed, code, { sign: kind === 'income' || kind === 'net' ? 'always' : null, frac: o.frac });
    const cls = ['amount', kind === 'income' && 'income', kind === 'transfer' && 'transfer', ((kind === 'balance' || kind === 'net') && v < 0) && 'debt', o.class];
    return h('span', { class: cls }, p.sign + p.int, p.frac && h('span', { class: 'frac' }, p.frac), NBSP + p.sym);
  }

  // ---------- графики ----------
  let tipEl = null;
  function showTip(x, y, title, rows) {
    if (!tipEl) { tipEl = h('div', { class: 'chart-tip', role: 'tooltip', hidden: true }); document.body.appendChild(tipEl); }
    clear(tipEl);
    tipEl.appendChild(h('div', { class: 'tip-title' }, title));
    rows.forEach(r => tipEl.appendChild(h('div', { class: 'tip-row' }, h('span', { class: 'tip-key' }, r.color && h('i', { style: { background: r.color } }), r.name), h('b', null, r.value))));
    tipEl.hidden = false;
    const w = tipEl.offsetWidth, hh = tipEl.offsetHeight;
    let left = x + 14, top = y - hh - 10;
    if (left + w > window.innerWidth - 8) left = x - w - 14;
    if (top < 8) top = y + 16;
    tipEl.style.left = Math.max(8, left) + 'px'; tipEl.style.top = top + 'px';
  }
  function hideTip() { if (tipEl) tipEl.hidden = true; }
  window.addEventListener('scroll', hideTip, { passive: true });

  // перерисовка по ширине контейнера
  function responsive(draw, height) {
    const box = h('div', { class: 'chart', style: { height: height + 'px' } });
    let lastW = 0;
    const render = () => { const w = Math.floor(box.clientWidth); if (w > 0 && w !== lastW) { lastW = w; clear(box); draw(box, w, height); } };
    if (typeof ResizeObserver !== 'undefined') new ResizeObserver(render).observe(box);
    const first = n => { if (box.isConnected && box.clientWidth) render(); else if (n < 60) requestAnimationFrame(() => first(n + 1)); };
    requestAnimationFrame(() => first(0));
    return box;
  }
  function niceTicks(min, max, count) {
    const span = max - min || 1;
    const step0 = span / count, mag = Math.pow(10, Math.floor(Math.log10(step0)));
    const norm = step0 / mag, step = (norm >= 5 ? 10 : norm >= 2 ? 5 : norm >= 1 ? 2 : 1) * mag;
    const lo = Math.floor(min / step) * step, hi = Math.ceil(max / step) * step;
    const out = []; for (let v = lo; v <= hi + step / 2; v += step) out.push(+v.toFixed(6));
    return out;
  }
  const textW = s => String(s).length * 6.2;

  // lineChart({labels, series:[{name,color,values}], height, yFormat, xFormat, tipFormat, tipTitle, area, ariaLabel})
  function lineChart(o) {
    const yf = o.yFormat || fmt.short, xf = o.xFormat || (l => l), tf = o.tipFormat || yf;
    return responsive((box, W, H) => {
      const all = o.series.flatMap(s => s.values);
      let lo = Math.min(...all), hi = Math.max(...all);
      const padV = (hi - lo) * 0.12 || Math.abs(hi) * 0.05 || 1;
      lo -= padV; hi += padV * 0.6;
      const ticks = niceTicks(lo, hi, H < 200 ? 3 : 4);
      lo = ticks[0]; hi = ticks[ticks.length - 1];
      const m = { t: 8, r: 8, b: 24, l: Math.max(...ticks.map(t => textW(yf(t)))) + 10 };
      const iw = W - m.l - m.r, ih = H - m.t - m.b, n = o.labels.length;
      const X = i => m.l + (n <= 1 ? iw / 2 : i / (n - 1) * iw);
      const Y = v => m.t + ih - (v - lo) / (hi - lo) * ih;
      const svg = h('svg', { width: W, height: H, viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': o.ariaLabel || o.series.map(s => s.name).join(', ') });
      ticks.forEach(t => { svg.appendChild(h('line', { class: 'grid-line', x1: m.l, x2: W - m.r, y1: Y(t), y2: Y(t) })); svg.appendChild(h('text', { x: m.l - 8, y: Y(t) + 4, 'text-anchor': 'end' }, yf(t))); });
      const lw = Math.max(...o.labels.map((l, i) => textW(xf(l, i)))) + 18;
      const stepL = Math.max(1, Math.ceil(n / Math.max(2, Math.floor(iw / lw))));
      for (let i = 0; i < n; i += stepL) {
        if (n - 1 - i < stepL / 2 && i !== 0) continue; // последняя подпись не налезает на предыдущую
        svg.appendChild(h('text', { x: X(i), y: H - 6, 'text-anchor': i === 0 ? 'start' : 'middle' }, xf(o.labels[i], i)));
      }
      svg.appendChild(h('text', { x: X(n - 1), y: H - 6, 'text-anchor': 'end' }, xf(o.labels[n - 1], n - 1)));
      o.series.forEach((s, si) => {
        const d = s.values.map((v, i) => (i ? 'L' : 'M') + X(i).toFixed(1) + ' ' + Y(v).toFixed(1)).join('');
        if (o.area && si === 0) svg.appendChild(h('path', { d: d + `L${X(n - 1).toFixed(1)} ${m.t + ih}L${X(0).toFixed(1)} ${m.t + ih}Z`, fill: s.color, opacity: '.1', stroke: 'none' }));
        svg.appendChild(h('path', { d, fill: 'none', stroke: s.color, 'stroke-width': s.width || 2, 'stroke-linejoin': 'round', 'stroke-linecap': 'round' }));
        svg.appendChild(h('circle', { cx: X(n - 1), cy: Y(s.values[n - 1]), r: 4, fill: s.color, stroke: 'var(--surface)', 'stroke-width': 2 }));
      });
      const cross = h('line', { class: 'crosshair', y1: m.t, y2: m.t + ih, visibility: 'hidden' });
      const dots = o.series.map(s => h('circle', { r: 4, fill: s.color, stroke: 'var(--surface)', 'stroke-width': 2, visibility: 'hidden' }));
      svg.appendChild(cross); dots.forEach(d => svg.appendChild(d));
      const hit = h('rect', { x: m.l, y: 0, width: iw, height: H, fill: 'transparent', tabindex: '0', style: 'outline:none' });
      let cur = -1;
      const at = (i, cx, cy) => {
        cur = Math.max(0, Math.min(n - 1, i));
        cross.setAttribute('x1', X(cur)); cross.setAttribute('x2', X(cur)); cross.setAttribute('visibility', 'visible');
        o.series.forEach((s, si) => { dots[si].setAttribute('cx', X(cur)); dots[si].setAttribute('cy', Y(s.values[cur])); dots[si].setAttribute('visibility', 'visible'); });
        const r = svg.getBoundingClientRect();
        showTip(cx != null ? cx : r.left + X(cur), cy != null ? cy : r.top + m.t + 20, (o.tipTitle || xf)(o.labels[cur], cur), o.series.map(s => ({ name: s.name, color: s.color, value: tf(s.values[cur]) })));
      };
      const off = () => { cross.setAttribute('visibility', 'hidden'); dots.forEach(d => d.setAttribute('visibility', 'hidden')); hideTip(); };
      hit.addEventListener('pointermove', e => { const r = svg.getBoundingClientRect(); at(Math.round((e.clientX - r.left - m.l) / iw * (n - 1)), e.clientX, e.clientY); });
      hit.addEventListener('pointerleave', off);
      hit.addEventListener('blur', off);
      hit.addEventListener('keydown', e => { if (e.key === 'ArrowRight') { at(cur + 1); e.preventDefault(); } if (e.key === 'ArrowLeft') { at(cur < 0 ? n - 1 : cur - 1); e.preventDefault(); } });
      svg.appendChild(hit);
      box.appendChild(svg);
    }, o.height || 220);
  }

  // barChart({labels, series:[{name,color,values}], height, yFormat, tipFormat, tipTitle, highlight}) — столбцы группами
  function barChart(o) {
    const yf = o.yFormat || fmt.short, tf = o.tipFormat || yf;
    return responsive((box, W, H) => {
      const all = o.series.flatMap(s => s.values);
      const ticks = niceTicks(0, Math.max(1, ...all), 3);
      const hi = ticks[ticks.length - 1];
      const m = { t: 8, r: 4, b: 24, l: Math.max(...ticks.map(t => textW(yf(t)))) + 10 };
      const iw = W - m.l - m.r, ih = H - m.t - m.b, n = o.labels.length, k = o.series.length;
      const band = iw / n, gap = 2;
      const bw = Math.max(3, Math.min(18, (band * 0.72 - gap * (k - 1)) / k));
      const groupW = bw * k + gap * (k - 1);
      const Y = v => m.t + ih - v / hi * ih;
      const svg = h('svg', { width: W, height: H, viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': o.ariaLabel || 'Столбчатая диаграмма' });
      ticks.forEach(t => { svg.appendChild(h('line', { class: t === 0 ? 'axis-line' : 'grid-line', x1: m.l, x2: W - m.r, y1: Y(t), y2: Y(t) })); svg.appendChild(h('text', { x: m.l - 8, y: Y(t) + 4, 'text-anchor': 'end' }, yf(t))); });
      const every = Math.max(1, Math.ceil(n / Math.max(2, Math.floor(iw / 40))));
      o.labels.forEach((lab, i) => {
        const x0 = m.l + band * i + (band - groupW) / 2;
        const g = h('g', { opacity: o.highlight != null && o.highlight !== i ? '.55' : null });
        o.series.forEach((s, si) => {
          const v = s.values[i], y = Y(v), hgt = Math.max(1, m.t + ih - y), x = x0 + si * (bw + gap), r = Math.min(3, hgt, bw / 2);
          g.appendChild(h('path', { d: `M${x} ${m.t + ih}V${y + r}Q${x} ${y} ${x + r} ${y}H${x + bw - r}Q${x + bw} ${y} ${x + bw} ${y + r}V${m.t + ih}Z`, fill: s.color }));
        });
        const hitR = h('rect', { x: m.l + band * i, y: m.t, width: band, height: ih, fill: 'transparent', tabindex: '0', style: 'outline:none' });
        const show = e => { g.setAttribute('opacity', '1'); const rb = svg.getBoundingClientRect(); showTip(e && e.clientX != null ? e.clientX : rb.left + x0, e && e.clientY != null ? e.clientY : rb.top + m.t + 20, (o.tipTitle || (l => l))(lab, i), o.series.map(s => ({ name: s.name, color: s.color, value: tf(s.values[i]) }))); };
        const hide = () => { g.setAttribute('opacity', o.highlight != null && o.highlight !== i ? '.55' : '1'); hideTip(); };
        hitR.addEventListener('pointermove', show); hitR.addEventListener('pointerleave', hide);
        hitR.addEventListener('focus', () => show()); hitR.addEventListener('blur', hide);
        svg.appendChild(g); svg.appendChild(hitR);
        if (i % every === 0) svg.appendChild(h('text', { x: m.l + band * i + band / 2, y: H - 6, 'text-anchor': 'middle' }, lab));
      });
      box.appendChild(svg);
    }, o.height || 220);
  }

  // stackBar([{label, value, color}]) — одна полоса из долей
  function stackBar(items) {
    const total = items.reduce((s, x) => s + x.value, 0) || 1;
    return h('div', { class: 'stackbar', role: 'img', 'aria-label': items.map(x => x.label + ' ' + fmt.pct(x.value / total)).join(', ') },
      items.map(x => h('i', { title: x.label + ': ' + fmt.pct(x.value / total), style: { flex: x.value / total + ' 1 0', background: x.color } })));
  }
  function legend(items) { return h('div', { class: 'chart-legend' }, items.map(it => h('span', null, h('i', { style: { background: it.color } }), it.name))); }

  // ---------- реестр экранов ----------
  const screens = {};
  function register(id, def) { screens[id] = def; }
  function go(id) { if (location.hash.slice(1) === id) window.dispatchEvent(new HashChangeEvent('hashchange')); else location.hash = id; }

  window.UI = {
    h, append, clear, icon, ICONS, fmt, CURRENCIES, isMobile, isPhone, addDays, parseDay, isoDay,
    button, card, delta, stat, chip, segmented, field, fieldError, toggle, meter, callout, empty, kv, dropdown, modal, toast,
    catIcon, amountEl, lineChart, barChart, stackBar, legend, hideTip,
    screens, register, go,
    get privacy() { return privacy; },
    setPrivacy(v) { privacy = !!v; try { localStorage.setItem('evercoin.privacy', v ? '1' : '0'); } catch (e) { /* ок */ } },
  };
})();
