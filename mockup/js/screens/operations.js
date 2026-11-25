/* Операции: месяц, тип, поиск и счет; итоги периода и список по дням. */
(function () {
  'use strict';
  const { h, fmt, button, card, segmented, dropdown, field, amountEl, empty } = UI;

  const st = { y: null, m: null, type: 'all', q: '', wallet: 'all' };

  UI.register('operations', {
    title: 'Операции',
    render(view) {
      const ty = +DATA.today.slice(0, 4), tm = +DATA.today.slice(5, 7) - 1;
      if (st.y == null) { st.y = ty; st.m = tm; }
      const isCurrent = st.y === ty && st.m === tm;
      const firstY = +DATA.start.slice(0, 4), firstM = +DATA.start.slice(5, 7) - 1;
      const isFirst = st.y === firstY && st.m === firstM;
      const shift = d => { let m = st.m + d, y = st.y; if (m < 0) { m = 11; y--; } if (m > 11) { m = 0; y++; } st.y = y; st.m = m; UI.refresh(); };

      UI.setHeader({ title: 'Операции', actions: button('Перевод', { icon: 'transfer', class: 'hide-mobile', onClick: () => UI.parts.editOp({ type: 'transfer' }) }) });

      const search = field({ id: 'ops-q', icon: 'search', type: 'search', placeholder: 'Поиск по названию и комментарию', value: st.q, attrs: { 'aria-label': 'Поиск операций' }, class: 'grow' });
      const toolbar = h('div', { class: 'toolbar' },
        h('div', { class: 'month-nav' },
          button(null, { kind: 'ghost', icon: 'chevronLeft', title: 'Предыдущий месяц', disabled: isFirst, onClick: () => shift(-1) }),
          h('span', { class: 'label', 'aria-live': 'polite' }, fmt.month(st.y, st.m)),
          button(null, { kind: 'ghost', icon: 'chevronRight', title: 'Следующий месяц', disabled: isCurrent, onClick: () => shift(1) })),
        segmented({ label: 'Тип операций', value: st.type, options: [{ value: 'all', label: 'Все' }, { value: 'expense', label: 'Расходы' }, { value: 'income', label: 'Доходы' }, { value: 'transfer', label: 'Переводы' }], onChange: v => { st.type = v; drawList(); } }),
        search,
        dropdown({ id: 'ops-wallet', compact: true, ariaLabel: 'Счет', value: st.wallet, options: [{ value: 'all', label: 'Все счета', icon: 'wallet', color: 'var(--fg-3)' }].concat(DATA.wallets.map(w => ({ value: w.id, label: w.name, icon: w.icon, color: w.color }))), onChange: v => { st.wallet = v; drawList(); } }));

      const results = h('div', { class: 'stack', style: 'gap:16px' });
      function drawList() {
        const [from, to] = DATA.monthRange(st.y, st.m);
        const q = st.q.trim().toLowerCase();
        const list = DATA.opsBetween(from, to, op =>
          (st.type === 'all' || op.type === st.type) &&
          (st.wallet === 'all' || op.wallet === st.wallet || op.toWallet === st.wallet) &&
          (!q || (op.title + ' ' + (op.comment || '') + ' ' + ((DATA.category(op.category) || {}).name || '')).toLowerCase().includes(q)));
        let inc = 0, exp = 0;
        list.forEach(op => { if (op.type === 'income') inc += DATA.opBase(op); if (op.type === 'expense') exp += DATA.opBase(op); });
        const strip = h('section', { class: 'card' }, h('div', { class: 'sum-strip' },
          h('div', null, h('span', { class: 'small soft' }, 'Доходы'), amountEl(inc, DATA.base, { kind: 'income', frac: 'never' })),
          h('div', null, h('span', { class: 'small soft' }, 'Расходы'), amountEl(exp, DATA.base, { kind: 'expense', frac: 'never' })),
          h('div', null, h('span', { class: 'small soft' }, 'Итог'), amountEl(inc - exp, DATA.base, { kind: 'net', frac: 'never' }))));
        const body = list.length
          ? card({ flush: true, body: UI.parts.opList(list, { walletId: st.wallet === 'all' ? null : st.wallet }), foot: h('span', { class: 'small muted' }, list.length + ' ' + fmt.plural(list.length, 'операция', 'операции', 'операций') + ' за ' + fmt.month(st.y, st.m).toLowerCase()) })
          : card({ body: empty({ icon: q ? 'search' : 'list', title: q ? 'Ничего не нашли' : 'Операций нет', text: q ? 'Попробуйте другое слово или уберите фильтры.' : 'За ' + fmt.month(st.y, st.m).toLowerCase() + ' нет операций с такими фильтрами.', action: button('Добавить операцию', { kind: 'primary', icon: 'plus', onClick: () => UI.parts.editOp() }) }) });
        results.replaceChildren(strip, body);
      }
      drawList();
      view.append(toolbar, results);
      document.getElementById('ops-q').addEventListener('input', e => { st.q = e.target.value; drawList(); });
    },
  });
})();
