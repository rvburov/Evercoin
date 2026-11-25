/* Счета: все счета с остатками и карточка счета (#wallet-<id>) с графиком, итогами месяца, операциями и настройками. */
(function () {
  'use strict';
  const { h, icon, fmt, button, card, chip, amountEl, catIcon, lineChart, toggle, empty, toast } = UI;

  function monthFlow(w) {
    const y = +DATA.today.slice(0, 4), m = +DATA.today.slice(5, 7) - 1;
    const [from, to] = DATA.monthRange(y, m);
    let inc = 0, exp = 0;
    DATA.opsBetween(from, to, op => op.wallet === w.id || op.toWallet === w.id).forEach(op => {
      if (op.type === 'income') inc += op.amount;
      else if (op.type === 'expense') exp += op.amount;
      else if (op.toWallet === w.id) inc += op.toAmount;
      else exp += op.amount;
    });
    return { inc, exp };
  }

  function walletCard(w) {
    const b = DATA.balance(w.id), f = monthFlow(w);
    return card({ class: ['col-4', 'wallet-card', w.hidden && 'is-hidden'].filter(Boolean).join(' '), href: '#wallet-' + w.id, body: [
      h('div', { class: 'wallet-head' }, catIcon(w, 'sq'),
        h('span', { class: 'op-main' }, h('span', { class: 'op-title' }, w.name), h('span', { class: 'op-sub' }, w.note || UI.CURRENCIES[w.currency].name)),
        icon('chevronRight', { width: 18, height: 18, style: 'color:var(--fg-3);flex:none' })),
      h('div', null,
        h('div', { class: 'big-amount' }, amountEl(b, w.currency, { frac: 'always' })),
        w.currency !== DATA.base ? h('div', { class: 'small muted' }, '≈ ' + fmt.money(DATA.toBase(b, w.currency), DATA.base, { frac: 'never' }) + ' по курсу ' + fmt.num(DATA.rates[w.currency] / DATA.rates[DATA.base], 2)) : null),
      h('div', { class: 'row-between' },
        h('span', { class: 'small muted' }, 'В ' + fmt.monthPrep(+DATA.today.slice(5, 7) - 1) + ': ', amountEl(f.inc, w.currency, { kind: 'income', frac: 'never', class: 'small' }), ' / ', amountEl(f.exp, w.currency, { kind: 'expense', frac: 'never', class: 'small' })),
        h('span', { class: 'row', style: 'gap:6px' }, w.isDefault ? chip('Основной', 'accent', 'star') : null, w.hidden ? chip('Не в общем балансе', 'outline', 'eyeOff') : null)),
    ] });
  }

  UI.register('wallets', {
    title: 'Счета',
    render(view) {
      UI.setHeader({ title: 'Счета', actions: [button('Перевод', { icon: 'transfer', class: 'hide-mobile', onClick: () => UI.parts.editOp({ type: 'transfer' }) }), button('Новый счет', { icon: 'plus', class: 'hide-mobile', onClick: () => UI.parts.editWallet() })] });
      const visible = DATA.wallets.filter(w => !w.hidden), hidden = DATA.wallets.filter(w => w.hidden);
      const debt = DATA.wallets.filter(w => !w.hidden && DATA.balance(w.id) < 0).reduce((s, w) => s + DATA.toBase(DATA.balance(w.id), w.currency), 0);
      view.appendChild(h('section', { class: 'card' }, h('div', { class: 'sum-strip' },
        h('div', null, h('span', { class: 'small soft' }, 'Всего на счетах'), amountEl(DATA.total(), DATA.base, { frac: 'never' })),
        h('div', null, h('span', { class: 'small soft' }, 'Долг по картам'), amountEl(debt, DATA.base, { frac: 'never' })),
        h('div', null, h('span', { class: 'small soft' }, 'Вне общего баланса'), amountEl(hidden.reduce((s, w) => s + DATA.toBase(DATA.balance(w.id), w.currency), 0), DATA.base, { frac: 'never', kind: 'transfer' })))));
      view.appendChild(h('div', { class: 'row', style: 'gap:8px' },
        button('Перевод', { icon: 'transfer', class: 'grow', attrs: { style: 'flex:1' }, onClick: () => UI.parts.editOp({ type: 'transfer' }) }),
        button('Новый счет', { icon: 'plus', attrs: { style: 'flex:1' }, onClick: () => UI.parts.editWallet() })))
        .classList.add('mobile-only-row');
      view.appendChild(h('div', { class: 'grid' }, visible.concat(hidden).map(walletCard)));
    },
  });

  UI.register('wallet', {
    title: 'Счет',
    nav: 'wallets',
    render(view, id) {
      const w = DATA.wallet(id);
      if (!w) {
        UI.setHeader({ title: 'Счет не найден', crumbs: [{ label: 'Счета', href: '#wallets' }] });
        view.appendChild(card({ body: empty({ icon: 'wallet', title: 'Такого счета нет', text: 'Возможно, его удалили.', action: button('Ко всем счетам', { kind: 'primary', href: '#wallets' }) }) }));
        return;
      }
      view.dataset.title = w.name;
      UI.setHeader({ title: w.name, crumbs: [{ label: 'Счета', href: '#wallets' }], actions: button('Изменить', { icon: 'edit', class: 'hide-mobile', onClick: () => UI.parts.editWallet(w) }) });
      const b = DATA.balance(w.id), s = DATA.walletSeries(w.id, 30), f = monthFlow(w);
      const ops = DATA.opsBetween(DATA.start, DATA.today, op => op.wallet === w.id || op.toWallet === w.id);
      const hero = card({ class: 'col-8', body: [
        h('div', { class: 'row-between', style: 'align-items:flex-start' },
          h('div', { class: 'row', style: 'gap:14px;flex-wrap:nowrap' }, catIcon(w, 'lg'),
            h('div', { class: 'stack', style: 'gap:2px' },
              h('span', { class: 'eyebrow' }, 'Остаток · ' + UI.CURRENCIES[w.currency].name),
              h('div', { class: 'hero-amount' }, amountEl(b, w.currency, { frac: 'always' })),
              w.currency !== DATA.base ? h('span', { class: 'small muted' }, '≈ ' + fmt.money(DATA.toBase(b, w.currency), DATA.base, { frac: 'never' })) : null)),
          h('div', { class: 'row' }, button('Операция', { kind: 'primary', icon: 'plus', onClick: () => UI.parts.editOp({ wallet: w.id }) }), button('Перевод', { icon: 'transfer', onClick: () => UI.parts.editOp({ type: 'transfer', wallet: w.id }) }))),
        lineChart({ labels: s.days, height: 170, area: true, ariaLabel: 'Остаток за 30 дней', series: [{ name: 'Остаток', color: w.color, values: s.values }], xFormat: d => fmt.dateShort(d), tipTitle: d => fmt.date(d), tipFormat: v => fmt.money(v, w.currency), yFormat: v => UI.privacy ? '•••' : fmt.short(v) }),
      ] });
      const n = DATA.walletOpsCount(w.id);
      const settings = card({ class: 'col-side', title: 'Настройки счета', body: [
        UI.kv([['Доходы в ' + fmt.monthPrep(+DATA.today.slice(5, 7) - 1), amountEl(f.inc, w.currency, { kind: 'income', frac: 'never' })], ['Расходы', amountEl(f.exp, w.currency, { kind: 'expense', frac: 'never' })], ['Начальный остаток', amountEl(w.initial, w.currency, { frac: 'never' })], ['Операций всего', String(n)]]),
        h('div', { class: 'stack', style: 'gap:4px;padding-top:6px;border-top:1px solid var(--line)' },
          toggle({ id: 'ws-default', label: 'Основной счет', hint: w.isDefault ? 'Подставляется в новые операции' : 'Сейчас основной — «' + DATA.defaultWallet().name + '»', checked: w.isDefault, disabled: w.isDefault, onChange: () => { DATA.updateWallet(w.id, { isDefault: true }); toast('«' + w.name + '» — основной счет', 'star'); UI.refresh(); } }),
          toggle({ id: 'ws-total', label: 'Учитывать в общем балансе', checked: !w.hidden, onChange: v => { DATA.updateWallet(w.id, { hidden: !v }); toast(v ? 'Счет учитывается в общем балансе' : 'Счет больше не входит в общий баланс', v ? 'eye' : 'eyeOff'); UI.refresh(); } })),
        w.note ? h('p', { class: 'small muted' }, w.note) : null,
      ], foot: [
        button('Изменить', { icon: 'edit', size: 'sm', onClick: () => UI.parts.editWallet(w) }),
        button('Удалить', { kind: 'ghost', icon: 'trash', size: 'sm', disabled: n > 0, title: n > 0 ? 'Нельзя удалить счет с операциями: сначала удалите или перенесите их' : null, onClick: () => { DATA.removeWallet(w.id); toast('Счет удален', 'trash'); UI.go('wallets'); } }),
        n > 0 ? h('span', { class: 'xsmall muted', style: 'flex-basis:100%' }, 'Счет с операциями удалить нельзя — сначала удалите или перенесите их.') : null,
      ] });
      const list = card({ class: 'col-12', title: 'Операции по счету', subtitle: n + ' ' + fmt.plural(n, 'операция', 'операции', 'операций') + ' с ' + fmt.date(DATA.start), flush: true,
        actions: button('Все операции', { kind: 'ghost', size: 'sm', iconRight: 'chevronRight', href: '#operations' }),
        body: ops.length ? UI.parts.opList(ops.slice(0, 30), { walletId: w.id, hideWallet: true }) : empty({ icon: 'list', title: 'Операций пока нет', text: 'Добавьте первую — остаток посчитается сам.' }),
        foot: ops.length > 30 ? h('span', { class: 'small muted' }, 'Показаны последние 30 операций') : null });
      view.appendChild(h('div', { class: 'grid' }, hero, settings, list));
    },
  });
})();
