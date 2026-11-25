/* Главная: сколько денег всего, как прошел месяц, куда уходят деньги, последние операции и счета. */
(function () {
  'use strict';
  const { h, icon, fmt, button, card, segmented, amountEl, lineChart, stackBar, meter, catIcon } = UI;

  let range = 30; // дней на графике общего баланса

  UI.register('dashboard', {
    title: 'Главная',
    render(view) {
      const today = DATA.today, y = +today.slice(0, 4), m = +today.slice(5, 7) - 1, dom = +today.slice(8, 10);
      const daysInMonth = +DATA.monthEnd(y, m).slice(8, 10);
      UI.setHeader({ title: 'Главная', crumbs: [{ label: fmt.dayTitle(today) + ', ' + fmt.date(today) }] });

      // ---- всего на счетах ----
      const total = DATA.total();
      const series = DATA.totalSeries(range);
      const change = total - series.values[0];
      const hiddenW = DATA.wallets.filter(w => w.hidden);
      const eyeBtn = button(null, { kind: 'ghost', size: 'sm', icon: UI.privacy ? 'eyeOff' : 'eye', title: UI.privacy ? 'Показать суммы' : 'Скрыть суммы', onClick: () => { UI.setPrivacy(!UI.privacy); UI.refresh(); } });
      const chartHolder = h('div');
      const drawChart = () => chartHolder.replaceChildren(lineChart({
        labels: series.days, height: 190, area: true, ariaLabel: 'Общий баланс за ' + range + ' дней',
        series: [{ name: 'Всего', color: 'var(--accent)', values: series.values }],
        xFormat: d => fmt.dateShort(d), tipTitle: d => fmt.date(d), tipFormat: v => fmt.money(v, DATA.base, { frac: 'never' }),
        yFormat: v => UI.privacy ? '•••' : fmt.short(v),
      }));
      drawChart();
      const hero = card({ class: 'col-8', body: [
        h('div', { class: 'row-between', style: 'align-items:flex-start' },
          h('div', { class: 'stack', style: 'gap:6px' },
            h('div', { class: 'row', style: 'gap:4px' }, h('span', { class: 'eyebrow' }, 'Всего на счетах'), eyeBtn),
            h('div', { class: 'hero-amount' }, amountEl(total, DATA.base, { frac: 'always' })),
            h('div', { class: 'row', style: 'gap:10px' },
              UI.delta(change, (change >= 0 ? '+' : fmt.MINUS) + fmt.money(Math.abs(change), DATA.base, { frac: 'never' }) + ' за ' + (range === 365 ? 'год' : range + ' дней')),
              hiddenW.length ? h('span', { class: 'small muted' }, 'без счета «' + hiddenW.map(w => w.name).join('», «') + '»') : null)),
          segmented({ label: 'Период графика', value: range, options: [{ value: 30, label: '30 дней' }, { value: 90, label: '3 месяца' }, { value: 365, label: 'Год' }], onChange: v => { range = v; UI.refresh(); } })),
        chartHolder,
      ] });

      // ---- этот месяц ----
      const [from, to] = DATA.monthRange(y, m);
      const sum = DATA.summary(from, to);
      const perDay = sum.expense / dom;
      const forecast = perDay * daysInMonth;
      const prev = DATA.summary(DATA.monthStart(m ? y : y - 1, m ? m - 1 : 11), DATA.monthEnd(m ? y : y - 1, m ? m - 1 : 11));
      const spentShare = sum.income ? sum.expense / sum.income : 0;
      const month = card({ class: 'col-side', title: fmt.monthName(m), subtitle: 'Прошло ' + dom + ' из ' + daysInMonth + ' дней', body: [
        h('div', { class: 'stack', style: 'gap:10px' },
          h('div', { class: 'row-between' }, h('span', { class: 'soft' }, 'Доходы'), amountEl(sum.income, DATA.base, { kind: 'income', frac: 'never' })),
          h('div', { class: 'row-between' }, h('span', { class: 'soft' }, 'Расходы'), amountEl(sum.expense, DATA.base, { kind: 'expense', frac: 'never' })),
          h('div', { class: 'row-between', style: 'padding-top:10px;border-top:1px solid var(--line)' }, h('span', { style: 'font-weight:600' }, 'Осталось'), h('span', { class: 'big-amount', style: 'font-size:var(--fs-xl)' }, amountEl(sum.net, DATA.base, { kind: 'net', frac: 'never' })))),
        h('div', { class: 'stack', style: 'gap:6px' },
          meter(sum.expense, sum.income || 1, spentShare > 0.9 ? 'bad' : spentShare > 0.75 ? 'warn' : null),
          h('span', { class: 'small muted' }, 'Потрачено ' + fmt.pct(spentShare) + ' дохода')),
      ], foot: h('div', { class: 'stack', style: 'gap:2px' },
        h('span', { class: 'small' }, 'В среднем ', h('b', { class: 'num' }, fmt.money(perDay, DATA.base, { frac: 'never' })), ' в день'),
        h('span', { class: 'small muted' }, 'К концу месяца ≈ ' + fmt.money(forecast, DATA.base, { frac: 'never' }) + ' расходов · в ' + fmt.monthPrep(m ? m - 1 : 11) + ' ' + fmt.money(prev.expense, DATA.base, { frac: 'never' }))) });

      // ---- куда уходят деньги ----
      const rows = UI.parts.topCats(sum.byCat, 'expense', 6);
      const cats = card({ class: 'col-6', title: 'Расходы в ' + fmt.monthPrep(m), subtitle: rows.length ? fmt.money(sum.expense, DATA.base, { frac: 'never' }) + ' на ' + rows.length + ' ' + fmt.plural(rows.length, 'категорию', 'категории', 'категорий') : null,
        actions: button('Аналитика', { kind: 'ghost', size: 'sm', iconRight: 'chevronRight', href: '#analytics' }),
        body: rows.length ? [stackBar(rows.map(r => ({ label: r.cat.name, value: r.sum, color: r.cat.color }))), UI.parts.shareList(rows, sum.expense)] : UI.empty({ icon: 'cart', title: 'Расходов пока нет', text: 'Добавьте первую операцию кнопкой «Операция»' }) });

      // ---- последние операции ----
      const recent = DATA.opsBetween(DATA.start, today).slice(0, 6);
      const ops = card({ class: 'col-6', title: 'Последние операции', flush: true,
        actions: button('Все', { kind: 'ghost', size: 'sm', iconRight: 'chevronRight', href: '#operations' }),
        body: UI.parts.opList(recent) });

      // ---- счета ----
      const wallets = card({ class: 'col-12', title: 'Счета', subtitle: DATA.wallets.length + ' ' + fmt.plural(DATA.wallets.length, 'счет', 'счета', 'счетов') + ' в ' + new Set(DATA.wallets.map(w => w.currency)).size + ' ' + fmt.plural(new Set(DATA.wallets.map(w => w.currency)).size, 'валюте', 'валютах', 'валютах'),
        actions: [button('Перевод', { size: 'sm', icon: 'transfer', onClick: () => UI.parts.editOp({ type: 'transfer' }) }), button('Все', { kind: 'ghost', size: 'sm', iconRight: 'chevronRight', href: '#wallets' })],
        body: h('div', { class: 'wallet-tiles' }, DATA.wallets.map(UI.parts.walletTile)) });

      view.appendChild(h('div', { class: 'grid' }, hero, month, cats, ops, wallets));
    },
  });
})();
