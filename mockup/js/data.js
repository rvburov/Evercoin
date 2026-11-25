/* Демо-данные макета Evercoin. Все цифры вымышлены.
   Модель — как в старом backend Evercoin: счета (валюта, «основной», «не в общем балансе»), категории расходов и доходов,
   операции (расход, доход, перевод между счетами). Балансы не хранятся отдельно: они считаются из начальных остатков
   и операций, поэтому числа на всех экранах сходятся и меняются вместе с добавленной в макете операцией. */
(function () {
  'use strict';
  const { isoDay, parseDay, addDays } = UI;

  const TODAY = '2026-11-25';
  const START = '2025-12-01';

  // Курсы к рублю (демо): основная валюта пересчитывается через них
  const RATES = { RUB: 1, USD: 92.4, EUR: 100.6, GBP: 117.8, CNY: 12.75, JPY: 0.61 };

  // Палитра выбора цвета — серии графиков AI Capper (--s1…--s8) и два спокойных цвета
  const COLORS = [
    { value: 'var(--s1)', label: 'Синий' }, { value: 'var(--s2)', label: 'Оранжевый' },
    { value: 'var(--s3)', label: 'Бирюзовый' }, { value: 'var(--s4)', label: 'Янтарный' },
    { value: 'var(--s5)', label: 'Розовый' }, { value: 'var(--s6)', label: 'Зеленый' },
    { value: 'var(--s7)', label: 'Фиолетовый' }, { value: 'var(--s8)', label: 'Красный' },
    { value: 'var(--accent)', label: 'Изумрудный' }, { value: 'var(--fg-3)', label: 'Серый' },
  ];
  const WALLET_ICONS = ['card', 'cash', 'safe', 'wallet', 'currency', 'trendUp', 'coins', 'briefcase'];
  const CATEGORY_ICONS = ['cart', 'bus', 'home', 'heart', 'ticket', 'shirt', 'bolt', 'repeat', 'coffee', 'plane', 'book', 'gift', 'briefcase', 'laptop', 'trendUp', 'star'];

  const wallets = [
    { id: 'card', name: 'Основная карта', currency: 'RUB', icon: 'card', color: 'var(--s1)', isDefault: true, hidden: false, note: 'Зарплатная, •• 4821', initial: 61200 },
    { id: 'cash', name: 'Наличные', currency: 'RUB', icon: 'cash', color: 'var(--s3)', isDefault: false, hidden: false, note: '', initial: 9400 },
    { id: 'savings', name: 'Накопительный счет', currency: 'RUB', icon: 'safe', color: 'var(--s6)', isDefault: false, hidden: false, note: '13% годовых, проценты 24-го числа', initial: 214000 },
    { id: 'credit', name: 'Кредитная карта', currency: 'RUB', icon: 'card', color: 'var(--s2)', isDefault: false, hidden: false, note: 'Льготный период 55 дней', initial: 0 },
    { id: 'usd', name: 'Доллары', currency: 'USD', icon: 'currency', color: 'var(--s4)', isDefault: false, hidden: false, note: 'Наличные на поездки', initial: 1450 },
    { id: 'broker', name: 'Брокерский счет', currency: 'RUB', icon: 'trendUp', color: 'var(--s7)', isDefault: false, hidden: true, note: 'Не входит в общий баланс: стоимость бумаг меняется', initial: 236000 },
  ];

  const categories = [
    { id: 'food', name: 'Продукты', type: 'expense', icon: 'cart', color: 'var(--s3)', active: true, isDefault: true },
    { id: 'home', name: 'Жилье', type: 'expense', icon: 'home', color: 'var(--s1)', active: true, isDefault: true },
    { id: 'transport', name: 'Транспорт', type: 'expense', icon: 'bus', color: 'var(--s4)', active: true, isDefault: true },
    { id: 'fun', name: 'Развлечения', type: 'expense', icon: 'ticket', color: 'var(--s7)', active: true, isDefault: true },
    { id: 'health', name: 'Здоровье', type: 'expense', icon: 'heart', color: 'var(--s8)', active: true, isDefault: true },
    { id: 'clothes', name: 'Одежда', type: 'expense', icon: 'shirt', color: 'var(--s5)', active: true, isDefault: true },
    { id: 'utilities', name: 'Коммунальные услуги', type: 'expense', icon: 'bolt', color: 'var(--s2)', active: true, isDefault: true },
    { id: 'subs', name: 'Подписки', type: 'expense', icon: 'repeat', color: 'var(--s6)', active: true, isDefault: true },
    { id: 'edu', name: 'Образование', type: 'expense', icon: 'book', color: 'var(--fg-3)', active: false, isDefault: false },
    { id: 'salary', name: 'Зарплата', type: 'income', icon: 'briefcase', color: 'var(--s6)', active: true, isDefault: true },
    { id: 'freelance', name: 'Фриланс', type: 'income', icon: 'laptop', color: 'var(--s1)', active: true, isDefault: true },
    { id: 'invest', name: 'Инвестиции', type: 'income', icon: 'trendUp', color: 'var(--s7)', active: true, isDefault: true },
    { id: 'gifts', name: 'Подарки', type: 'income', icon: 'gift', color: 'var(--s5)', active: true, isDefault: true },
  ];

  // ---------- генерация операций за год: случайность с постоянным зерном, у всех одинаковые цифры ----------
  let seed = 20261125;
  function rnd() { seed = (seed + 0x6D2B79F5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }
  const pick = arr => arr[Math.floor(rnd() * arr.length)];
  const between = (a, b, step) => Math.round((a + rnd() * (b - a)) / (step || 1)) * (step || 1);
  const kop = (a, b) => Math.round((a + rnd() * (b - a)) * 100) / 100; // сумма с копейками
  const time = (h1, h2) => String(between(h1, h2)).padStart(2, '0') + ':' + String(between(0, 59)).padStart(2, '0');

  const ops = [];
  let nextId = 1;
  const bal = {};
  wallets.forEach(w => { bal[w.id] = w.initial; });
  function apply(op) {
    if (op.type === 'expense') bal[op.wallet] -= op.amount;
    else if (op.type === 'income') bal[op.wallet] += op.amount;
    else { bal[op.wallet] -= op.amount; bal[op.toWallet] += op.toAmount; }
  }
  function add(day, t, type, title, amount, wallet, extra) {
    const op = Object.assign({ id: 'o' + nextId++, type, title, amount: Math.round(amount * 100) / 100, wallet, date: day + 'T' + t, comment: '' }, extra || {});
    if (type === 'transfer' && op.toAmount == null) op.toAmount = op.amount;
    ops.push(op);
    return op;
  }
  const FREELANCE = { '2025-12': 'Проект: лендинг кофейни', '2026-02': 'Проект: интернет-магазин', '2026-03': 'Консультация по сайту', '2026-05': 'Проект: личный кабинет', '2026-07': 'Доработка сайта', '2026-08': 'Проект: сайт клиники', '2026-10': 'Проект: мобильная версия', '2026-11': 'Аудит интерфейса' };

  for (let day = START; day <= TODAY; day = addDays(day, 1)) {
    const d = parseDay(day), dom = d.getUTCDate(), dow = d.getUTCDay(), mon = d.getUTCMonth(), ym = day.slice(0, 7);
    const isToday = day === TODAY;
    const dayOps = [];
    const push = (...a) => dayOps.push(a);
    // регулярные
    if (dom === 1) push('08:12', 'expense', 'Проездной на месяц', 2900, 'card', { category: 'transport' });
    if (dom === 2) push('10:05', 'expense', 'Аренда квартиры', 45000, 'card', { category: 'home' });
    if (dom === 3) push('19:40', 'expense', 'Спортзал', 3500, 'card', { category: 'health' });
    if (dom === 5) push('11:00', 'income', 'Зарплата', 98000, 'card', { category: 'salary' });
    if (dom === 7) push('09:00', 'expense', 'Музыка', 299, 'card', { category: 'subs' });
    if (dom === 10) push('20:15', 'expense', 'Коммунальные платежи', kop([10, 11, 0, 1, 2].includes(mon) ? 6200 : 4700, [10, 11, 0, 1, 2].includes(mon) ? 7600 : 5600), 'card', { category: 'utilities' });
    if (dom === 12) push('21:30', 'expense', 'Онлайн-кинотеатр', 399, 'card', { category: 'subs' });
    if (dom === 15) push('09:30', 'expense', 'Интернет и связь', 1150, 'card', { category: 'utilities' });
    if (dom === 16 && FREELANCE[ym]) push('15:20', 'income', FREELANCE[ym], between(18000, 42000, 500), 'card', { category: 'freelance' });
    if (dom === 20) { push('11:00', 'income', 'Зарплата · аванс', 64000, 'card', { category: 'salary' }); push('09:10', 'expense', 'Облачное хранилище', 149, 'card', { category: 'subs' }); }
    // разовые
    if (day === '2025-12-28') push('13:00', 'income', 'Подарок от родителей', 15000, 'cash', { category: 'gifts' });
    if (day === '2026-03-14') push('18:00', 'income', 'День рождения', 12000, 'card', { category: 'gifts' });
    if (day === '2026-07-17') push('10:00', 'income', 'Дивиденды', 8400, 'broker', { category: 'invest' });
    if (day === '2026-10-20') push('10:00', 'income', 'Дивиденды', 6150, 'broker', { category: 'invest' });
    if (day === '2026-07-11') push('16:20', 'expense', 'Отель на неделю', 420, 'usd', { category: 'fun', comment: 'Отпуск' });
    if (day === '2026-07-13') push('12:40', 'expense', 'Экскурсия', 65, 'usd', { category: 'fun', comment: 'Отпуск' });
    if (day === '2026-07-15') push('20:10', 'expense', 'Ужин у моря', 48, 'usd', { category: 'fun', comment: 'Отпуск' });
    if (day === '2026-04-18') push('12:00', 'expense', 'Стоматолог', 9800, 'card', { category: 'health' });
    if (day === '2026-09-05') push('15:00', 'expense', 'Курс английского', 14500, 'card', { category: 'edu' });
    // каждый день — по вероятности (сегодня — свои операции ниже)
    if (!isToday) {
      if (dow === 6) push(time(10, 13), 'expense', 'Продукты на неделю', kop(3400, 6900), 'card', { category: 'food' });
      else if (rnd() < 0.3) {
        const amount = kop(450, 2600);
        push(time(9, 21), 'expense', pick(['Продукты', 'Супермаркет', 'Овощи и фрукты', 'Пекарня', 'Рынок']), amount, rnd() < 0.3 && bal.cash > amount + 500 ? 'cash' : 'card', { category: 'food' });
      }
      if (dow >= 1 && dow <= 5 && rnd() < 0.28) push(time(8, 10), 'expense', 'Кофе с собой', between(190, 420, 10), rnd() < 0.25 && bal.cash > 500 ? 'cash' : 'card', { category: 'fun' });
      if (rnd() < 0.11) push(time(18, 23), 'expense', 'Такси', between(290, 1180, 10), 'card', { category: 'transport' });
      if ((dow === 5 || dow === 6) && rnd() < 0.33) push(time(19, 21), 'expense', pick(['Ресторан', 'Ужин с друзьями', 'Бар']), between(1800, 6200, 50), rnd() < 0.5 ? 'credit' : 'card', { category: 'fun' });
      if (rnd() < 0.045) push(time(18, 21), 'expense', 'Кино', between(700, 1600, 50), 'card', { category: 'fun' });
      if (rnd() < 0.055) push(time(10, 20), 'expense', 'Аптека', kop(380, 2300), rnd() < 0.3 && bal.cash > 2500 ? 'cash' : 'card', { category: 'health' });
      if (rnd() < 0.04) push(time(12, 19), 'expense', pick(['Одежда', 'Обувь', 'Куртка', 'Джинсы']), between(2400, 11000, 100), 'credit', { category: 'clothes' });
    }
    // сегодня: несколько операций до текущего времени
    if (isToday) {
      push('08:41', 'expense', 'Кофе с собой', 340, 'card', { category: 'fun' });
      push('13:18', 'expense', 'Продукты', 2186.4, 'card', { category: 'food' });
      push('17:55', 'expense', 'Такси', 640, 'card', { category: 'transport' });
    }
    dayOps.sort((a, b) => a[0].localeCompare(b[0]));
    dayOps.forEach(a => { const op = add(day, ...a); apply(op); });
    // переводы по правилам — после операций дня, по сложившемуся остатку
    const tr = (t, title, amount, from, to, extra) => { if (amount > 0) apply(add(day, t, 'transfer', title, amount, from, Object.assign({ toWallet: to }, extra || {}))); };
    // крупное — сразу после зарплаты, остальное сверх 85 000 ₽ уходит на накопительный: карта не уходит в минус перед арендой
    if (day === '2026-09-06') tr('11:30', 'Покупка долларов', 46200, 'card', 'usd', { toAmount: 500 });
    if (dom === 6) tr('12:00', 'На накопительный', Math.floor((bal.card - 85000) / 5000) * 5000, 'card', 'savings');
    if (dom === 8) tr('10:15', 'Погашение кредитной карты', Math.round(-bal.credit * 100) / 100, 'card', 'credit');
    if ((dom === 14 || dom === 28) && bal.cash < 6000) tr('18:30', 'Снял наличные', 10000, 'card', 'cash');
    if (dom === 9 && [11, 2, 5, 8].includes(mon)) tr('11:00', 'Пополнение брокерского счета', 20000, 'savings', 'broker');
    if (dom === 24) apply(add(day, '06:00', 'income', 'Проценты по накопительному', Math.round(bal.savings * 0.0108 * 100) / 100, 'savings', { category: 'invest' }));
  }

  // ---------- состояние и расчеты ----------
  let base = 'RUB';
  try { const b = localStorage.getItem('evercoin.base'); if (RATES[b]) base = b; } catch (e) { /* ок */ }
  let version = 1, cache = null;

  const wallet = id => wallets.find(w => w.id === id);
  const category = id => categories.find(c => c.id === id);
  // сумма в основной валюте
  const toBase = (amount, cur) => amount * RATES[cur] / RATES[base];
  const opBase = op => toBase(op.amount, wallet(op.wallet).currency);

  // Проигрываем операции от начальных остатков: остатки на конец каждого дня
  function ledger() {
    if (cache && cache.version === version) return cache;
    const b = {}; wallets.forEach(w => { b[w.id] = w.initial; });
    const sorted = ops.slice().sort((x, y) => x.date.localeCompare(y.date));
    const days = [], snaps = [];
    let i = 0;
    for (let day = START; day <= TODAY; day = addDays(day, 1)) {
      while (i < sorted.length && sorted[i].date.slice(0, 10) <= day) {
        const op = sorted[i++];
        if (!b.hasOwnProperty(op.wallet)) continue;
        if (op.type === 'expense') b[op.wallet] -= op.amount;
        else if (op.type === 'income') b[op.wallet] += op.amount;
        else { b[op.wallet] -= op.amount; if (b.hasOwnProperty(op.toWallet)) b[op.toWallet] += op.toAmount; }
      }
      days.push(day); snaps.push(Object.assign({}, b));
    }
    cache = { version, days, snaps, final: snaps[snaps.length - 1] };
    return cache;
  }
  const balance = id => ledger().final[id] || 0;
  // общий баланс в основной валюте: без счетов «не в общем балансе»
  function totalOf(snap) { return wallets.filter(w => !w.hidden).reduce((s, w) => s + toBase(snap[w.id] || 0, w.currency), 0); }
  const total = () => totalOf(ledger().final);
  // ряд общего баланса за последние n дней
  function totalSeries(n) {
    const L = ledger(), from = Math.max(0, L.days.length - n);
    return { days: L.days.slice(from), values: L.snaps.slice(from).map(totalOf) };
  }
  function walletSeries(id, n) {
    const L = ledger(), from = Math.max(0, L.days.length - n);
    return { days: L.days.slice(from), values: L.snaps.slice(from).map(s => s[id] || 0) };
  }

  // операции в периоде [from, to] (даты включительно), новые сверху
  function opsBetween(from, to, filter) {
    return ops.filter(op => { const d = op.date.slice(0, 10); return d >= from && d <= to && (!filter || filter(op)); })
      .sort((x, y) => y.date.localeCompare(x.date));
  }
  // итоги периода в основной валюте: доходы, расходы, по категориям
  function summary(from, to, walletId) {
    const out = { income: 0, expense: 0, net: 0, count: 0, byCat: {} };
    opsBetween(from, to, op => !walletId || op.wallet === walletId || op.toWallet === walletId).forEach(op => {
      if (op.type === 'transfer') return;
      if (walletId && op.wallet !== walletId) return;
      const v = opBase(op);
      out[op.type] += v; out.count++;
      const c = out.byCat[op.category] || (out.byCat[op.category] = { sum: 0, count: 0 });
      c.sum += v; c.count++;
    });
    out.net = out.income - out.expense;
    return out;
  }
  const monthStart = (y, m) => y + '-' + String(m + 1).padStart(2, '0') + '-01';
  function monthEnd(y, m) { const d = new Date(Date.UTC(y, m + 1, 0, 12)); return isoDay(d); }
  function monthRange(y, m) { const end = monthEnd(y, m); return [monthStart(y, m), end < TODAY ? end : TODAY]; }

  function bump() { version++; }

  window.DATA = {
    today: TODAY, start: START, rates: RATES, COLORS, WALLET_ICONS, CATEGORY_ICONS,
    user: { name: 'Мария Котова', email: 'maria@example.com', initials: 'МК', since: '2025-12-01' },
    wallets, categories, ops,
    get base() { return base; },
    setBase(code) { if (!RATES[code]) return; base = code; bump(); try { localStorage.setItem('evercoin.base', code); } catch (e) { /* ок */ } },
    wallet, category, toBase, opBase, balance, total, totalSeries, walletSeries, opsBetween, summary, monthStart, monthEnd, monthRange, ledger,
    activeWallets: () => wallets,
    cats: (type, all) => categories.filter(c => c.type === type && (all || c.active)),
    defaultWallet: () => wallets.find(w => w.isDefault) || wallets[0],
    walletOpsCount: id => ops.filter(op => op.wallet === id || op.toWallet === id).length,
    catOpsCount: id => ops.filter(op => op.category === id).length,
    addOp(op) { op.id = 'o' + nextId++; if (op.type === 'transfer' && op.toAmount == null) op.toAmount = op.amount; ops.push(op); bump(); return op; },
    updateOp(id, patch) { const op = ops.find(x => x.id === id); if (op) { Object.assign(op, patch); bump(); } return op; },
    removeOp(id) { const i = ops.findIndex(x => x.id === id); if (i >= 0) { ops.splice(i, 1); bump(); } },
    addWallet(w) { w.id = 'w' + nextId++; wallets.push(w); bump(); return w; },
    updateWallet(id, patch) { const w = wallet(id); if (patch.isDefault) wallets.forEach(x => { x.isDefault = false; }); Object.assign(w, patch); bump(); return w; },
    removeWallet(id) { const i = wallets.findIndex(w => w.id === id); if (i < 0) return; const wasDefault = wallets[i].isDefault; wallets.splice(i, 1); if (wasDefault && wallets[0]) wallets[0].isDefault = true; bump(); },
    addCategory(c) { c.id = 'c' + nextId++; categories.push(c); bump(); return c; },
    updateCategory(id, patch) { Object.assign(category(id), patch); bump(); },
    // объединение: операции переходят в целевую категорию, исходная удаляется
    mergeCategory(fromId, toId) { let n = 0; ops.forEach(op => { if (op.category === fromId) { op.category = toId; n++; } }); const i = categories.findIndex(c => c.id === fromId); if (i >= 0) categories.splice(i, 1); bump(); return n; },
  };
})();
