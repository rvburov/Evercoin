/* Аналитика: показатели периода со сравнением, доходы и расходы по месяцам, структура расходов, крупные траты. */
(function () {
  'use strict';
  const { h, fmt, button, card, segmented, amountEl, stat, delta, barChart, stackBar, legend, toast } = UI;

  let period = 'month';

  function ym(y, m) { while (m < 0) { m += 12; y--; } return [y, m]; }
  // период и такой же по длине предыдущий: месяц — с 1-го по сегодня, квартал — 3 месяца, год — 12
  function ranges() {
    const t = DATA.today, y = +t.slice(0, 4), m = +t.slice(5, 7) - 1, dom = +t.slice(8, 10);
    const len = period === 'month' ? 1 : period === 'quarter' ? 3 : 12;
    const [sy, sm] = ym(y, m - len + 1), [py, pm] = ym(y, m - 2 * len + 1), [ey, em] = ym(y, m - len);
    const prevEnd = DATA.monthStart(ey, em).slice(0, 8) + String(Math.min(dom, +DATA.monthEnd(ey, em).slice(8, 10))).padStart(2, '0');
    const from = DATA.monthStart(sy, sm), prevFrom = DATA.monthStart(py, pm);
    const label = period === 'month' ? fmt.month(y, m) : fmt.monthShort(sm) + (sy !== y ? ' ' + sy : '') + ' – ' + fmt.monthShort(m) + ' ' + y;
    return { from, to: t, prevFrom, prevTo: prevEnd, hasPrev: prevFrom >= DATA.start, label, days: Math.round((UI.parseDay(t) - UI.parseDay(from)) / 864e5) + 1, prevName: period === 'month' ? 'к ' + fmt.monthShort(em) + ' (те же дни)' : 'к прошлому периоду' };
  }
  const pctChange = (a, b) => (b ? (a - b) / b : 0);

  UI.register('analytics', {
    title: 'Аналитика',
    render(view) {
      UI.setHeader({ title: 'Аналитика', actions: button('Выгрузить CSV', { icon: 'download', class: 'hide-mobile', onClick: () => toast('В приложении здесь скачается CSV с операциями периода', 'download') }) });
      const r = ranges();
      const cur = DATA.summary(r.from, r.to), prev = r.hasPrev ? DATA.summary(r.prevFrom, r.prevTo) : null;
      const rate = cur.income ? cur.net / cur.income : 0, prevRate = prev && prev.income ? prev.net / prev.income : 0;
      const perDay = cur.expense / r.days;

      view.appendChild(h('div', { class: 'toolbar' },
        segmented({ label: 'Период', value: period, options: [{ value: 'month', label: 'Месяц' }, { value: 'quarter', label: '3 месяца' }, { value: 'year', label: 'Год' }], onChange: v => { period = v; UI.refresh(); } }),
        h('span', { class: 'small muted' }, r.label + ' · ' + r.days + ' ' + fmt.plural(r.days, 'день', 'дня', 'дней'))));

      const d = (v, goodUp) => prev ? delta(v, (v > 0 ? '+' : v < 0 ? fmt.MINUS : '') + fmt.pct(Math.abs(v)) + ' ' + r.prevName, goodUp) : h('span', { class: 'stat-hint' }, 'сравнить не с чем');
      view.appendChild(h('div', { class: 'grid' },
        stat({ class: 'col-3 half-mobile', label: 'Доходы', value: amountEl(cur.income, DATA.base, { kind: 'income', frac: 'never' }), foot: d(prev ? pctChange(cur.income, prev.income) : 0, true) }),
        stat({ class: 'col-3 half-mobile', label: 'Расходы', value: amountEl(cur.expense, DATA.base, { frac: 'never' }), foot: d(prev ? pctChange(cur.expense, prev.expense) : 0, false) }),
        stat({ class: 'col-3 half-mobile', label: 'Отложено', value: amountEl(cur.net, DATA.base, { kind: 'net', frac: 'never' }), foot: h('span', { class: 'stat-hint' }, fmt.pct(rate) + ' дохода' + (prev ? ' · было ' + fmt.pct(prevRate) : '')) }),
        stat({ class: 'col-3 half-mobile', label: 'Расход в день', value: amountEl(perDay, DATA.base, { frac: 'never' }), foot: h('span', { class: 'stat-hint' }, 'в среднем за ' + r.days + ' ' + fmt.plural(r.days, 'день', 'дня', 'дней')) })));

      // ---- 12 месяцев ----
      const months = [];
      const ty = +DATA.today.slice(0, 4), tm = +DATA.today.slice(5, 7) - 1;
      for (let i = 11; i >= 0; i--) { const [y, m] = ym(ty, tm - i); const [f, t] = DATA.monthRange(y, m); months.push({ y, m, s: DATA.summary(f, t) }); }
      const bars = card({ class: 'col-8', title: 'Доходы и расходы по месяцам', subtitle: 'Последние 12 месяцев, ' + fmt.monthName(tm).toLowerCase() + ' — по сегодняшний день',
        body: [legend([{ name: 'Доходы', color: 'var(--accent)' }, { name: 'Расходы', color: 'var(--s2)' }]),
          barChart({ labels: months.map(x => fmt.monthShort(x.m)), height: 230, highlight: 11, ariaLabel: 'Доходы и расходы по месяцам',
            series: [{ name: 'Доходы', color: 'var(--accent)', values: months.map(x => x.s.income) }, { name: 'Расходы', color: 'var(--s2)', values: months.map(x => x.s.expense) }],
            tipTitle: (l, i) => fmt.month(months[i].y, months[i].m), tipFormat: v => fmt.money(v, DATA.base, { frac: 'never' }), yFormat: v => UI.privacy ? '•••' : fmt.short(v) })] });
      const best = months.slice(0, 11).filter(x => x.s.income).sort((a, b) => b.s.net / b.s.income - a.s.net / a.s.income)[0];
      const avgExp = months.slice(0, 11).reduce((s, x) => s + x.s.expense, 0) / 11;
      const insights = card({ class: 'col-side', title: 'Коротко', body: h('div', { class: 'stack', style: 'gap:14px' },
        h('div', null, h('div', { class: 'small soft' }, 'Средние расходы в месяц'), h('div', { class: 'big-amount', style: 'font-size:var(--fs-xl)' }, amountEl(avgExp, DATA.base, { frac: 'never' })), h('div', { class: 'xsmall muted' }, 'за 11 полных месяцев')),
        best ? h('div', null, h('div', { class: 'small soft' }, 'Лучший месяц по накоплениям'), h('div', { class: 'big-amount', style: 'font-size:var(--fs-xl)' }, fmt.month(best.y, best.m)), h('div', { class: 'xsmall muted' }, 'отложено ' + fmt.pct(best.s.net / best.s.income) + ' дохода')) : null,
        h('div', null, h('div', { class: 'small soft' }, 'Всего на счетах'), h('div', { class: 'big-amount', style: 'font-size:var(--fs-xl)' }, amountEl(DATA.total(), DATA.base, { frac: 'never' })), h('div', { class: 'xsmall muted' }, 'без счетов вне общего баланса'))) });

      // ---- структура и крупные траты ----
      const rows = UI.parts.topCats(cur.byCat, 'expense', 0);
      const structure = card({ class: 'col-7', title: 'Структура расходов', subtitle: r.label, body: rows.length ? [stackBar(rows.map(x => ({ label: x.cat.name, value: x.sum, color: x.cat.color }))), UI.parts.shareList(rows, cur.expense)] : UI.empty({ icon: 'chart', title: 'Расходов нет', text: 'За этот период нет расходов.' }) });
      const big = DATA.opsBetween(r.from, r.to, op => op.type === 'expense').sort((a, b) => DATA.opBase(b) - DATA.opBase(a)).slice(0, 6);
      const topOps = card({ class: 'col-5', title: 'Крупные расходы', subtitle: r.label, flush: true, body: UI.parts.opList(big, { flat: true }) });

      view.appendChild(h('div', { class: 'grid' }, bars, insights, structure, topOps));
    },
  });
})();
