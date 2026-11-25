/* Категории: расходы и доходы за текущий месяц, правка цвета и значка, объединение, отключенные категории. */
(function () {
  'use strict';
  const { h, fmt, button, card, segmented, amountEl, catIcon, empty, toast } = UI;

  let type = 'expense';

  UI.register('categories', {
    title: 'Категории',
    render(view) {
      UI.setHeader({ title: 'Категории', actions: button('Новая категория', { icon: 'plus', class: 'hide-mobile', onClick: () => UI.parts.editCategory(null, type) }) });
      const y = +DATA.today.slice(0, 4), m = +DATA.today.slice(5, 7) - 1;
      const [from, to] = DATA.monthRange(y, m);
      const sum = DATA.summary(from, to);
      const active = DATA.cats(type);
      const totalSum = type === 'expense' ? sum.expense : sum.income;
      const rows = active.map(c => ({ cat: c, sum: (sum.byCat[c.id] || {}).sum || 0, count: (sum.byCat[c.id] || {}).count || 0 })).sort((a, b) => b.sum - a.sum);

      view.appendChild(h('div', { class: 'toolbar' },
        segmented({ label: 'Тип категорий', value: type, options: [{ value: 'expense', label: 'Расходы' }, { value: 'income', label: 'Доходы' }], onChange: v => { type = v; UI.refresh(); } }),
        h('span', { class: 'small muted' }, 'Суммы за ' + fmt.month(y, m).toLowerCase() + ' · нажмите на категорию, чтобы изменить ее'),
        h('span', { class: 'grow' }),
        button('Новая категория', { icon: 'plus', class: 'mobile-only', onClick: () => UI.parts.editCategory(null, type) })));

      const main = card({ class: 'col-8', title: type === 'expense' ? 'Категории расходов' : 'Категории доходов',
        subtitle: active.length + ' ' + fmt.plural(active.length, 'категория', 'категории', 'категорий') + ' · ' + fmt.money(totalSum, DATA.base, { frac: 'never' }) + ' в ' + fmt.monthPrep(m),
        body: rows.length ? UI.parts.shareList(rows, totalSum, { onClick: c => UI.parts.editCategory(c) }) : empty({ icon: 'tag', title: 'Категорий нет', text: 'Создайте первую категорию.' }) });

      const off = DATA.categories.filter(c => c.type === type && !c.active);
      const side = h('div', { class: 'col-side stack', style: 'gap:16px' },
        card({ title: 'Отключенные', subtitle: off.length ? 'Не предлагаются при вводе, но остаются в истории и отчетах' : 'Все категории включены', body: off.length ? h('div', { class: 'list' }, off.map(c => {
          const n = DATA.catOpsCount(c.id);
          return h('div', { class: 'share-row' }, catIcon(c, 'sm'),
            h('span', { class: 'op-main' }, h('span', { class: 'op-title' }, c.name), h('span', { class: 'op-sub' }, n ? n + ' ' + fmt.plural(n, 'операция', 'операции', 'операций') : 'Без операций')),
            button('Включить', { size: 'sm', onClick: () => { DATA.updateCategory(c.id, { active: true }); toast('Категория «' + c.name + '» включена'); UI.refresh(); } }));
        })) : null }),
        card({ title: 'Как устроены категории', body: h('ul', { class: 'small soft', style: 'margin:0;padding-left:18px;display:flex;flex-direction:column;gap:6px' },
          h('li', null, 'Цвет категории — только метка: в списке операций и на графиках.'),
          h('li', null, 'Категорию с операциями не удаляем — объединяем с другой, операции переходят в нее.'),
          h('li', null, 'Стандартные категории можно отключить: история не теряется.')) }));

      view.appendChild(h('div', { class: 'grid' }, main, side));
    },
  });
})();
