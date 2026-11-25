/* Общие части экранов Evercoin: строка операции, список по дням, доли категорий, плитка счета
   и окна: операция, ввод операции и перевода, счет, категория, объединение категорий. */
(function () {
  'use strict';
  const { h, icon, fmt, button, catIcon, amountEl, dropdown, field, fieldError, segmented, toggle, modal, toast, kv, callout, chip } = UI;
  const refresh = () => UI.refresh && UI.refresh();

  // ---------- операции ----------
  function opVisual(op) {
    if (op.type === 'transfer') return { icon: 'transfer', color: 'var(--fg-3)' };
    const c = DATA.category(op.category);
    return c ? { icon: c.icon, color: c.color } : { icon: 'tag', color: 'var(--fg-3)' };
  }
  function opSub(op, o) {
    const w = DATA.wallet(op.wallet), to = op.toWallet && DATA.wallet(op.toWallet);
    if (op.type === 'transfer') return (w ? w.name : 'Счет удален') + ' → ' + (to ? to.name : 'Счет удален');
    const c = DATA.category(op.category);
    return [c ? c.name : 'Без категории', o && o.hideWallet ? null : w && w.name].filter(Boolean).join(' · ');
  }
  // сумма операции: в списке счета перевод — минус или плюс по направлению
  function opAmount(op, walletId) {
    const w = DATA.wallet(op.wallet);
    const cur = w ? w.currency : 'RUB';
    if (op.type === 'transfer') {
      if (walletId === op.toWallet) return amountEl(op.toAmount, DATA.wallet(op.toWallet).currency, { kind: 'income' });
      if (walletId === op.wallet) return amountEl(op.amount, cur, { kind: 'expense' });
      return amountEl(op.amount, cur, { kind: 'transfer' });
    }
    return amountEl(op.amount, cur, { kind: op.type });
  }
  function opRow(op, o = {}) {
    const w = DATA.wallet(op.wallet);
    const foreign = w && w.currency !== DATA.base && op.type !== 'transfer';
    return h('button', { class: 'op-row', type: 'button', on: { click: () => openOp(op) } },
      catIcon(opVisual(op)),
      h('span', { class: 'op-main' }, h('span', { class: 'op-title' }, op.title), h('span', { class: 'op-sub' }, opSub(op, o))),
      h('span', { class: 'op-side' }, opAmount(op, o.walletId),
        h('span', { class: 'op-sub' }, foreign ? '≈ ' + fmt.money(DATA.opBase(op), DATA.base) : (o.showDate ? fmt.dateShort(op.date) : fmt.time(op.date)))));
  }
  // список с заголовками дней; у дня справа — сколько потрачено (или получено, если трат не было)
  function opList(ops, o = {}) {
    const box = h('div', { class: 'op-list' });
    let day = null, group = null;
    ops.forEach(op => {
      const d = op.date.slice(0, 10);
      if (o.flat) { box.appendChild(opRow(op, Object.assign({ showDate: true }, o))); return; }
      if (d !== day) {
        day = d;
        const dayOps = ops.filter(x => x.date.slice(0, 10) === d && x.type !== 'transfer' && (!o.walletId || x.wallet === o.walletId));
        const spent = dayOps.filter(x => x.type === 'expense').reduce((s, x) => s + DATA.opBase(x), 0);
        const got = dayOps.filter(x => x.type === 'income').reduce((s, x) => s + DATA.opBase(x), 0);
        box.appendChild(h('div', { class: 'day-head' }, h('span', null, h('b', null, fmt.dayTitle(d))),
          spent ? amountEl(spent, DATA.base, { kind: 'expense' }) : got ? amountEl(got, DATA.base, { kind: 'income' }) : null));
        group = h('div', { class: 'op-list' });
        box.appendChild(group);
      }
      group.appendChild(opRow(op, o));
    });
    return box;
  }

  function openOp(op) {
    const w = DATA.wallet(op.wallet), to = op.toWallet && DATA.wallet(op.toWallet), c = DATA.category(op.category);
    const cur = w ? w.currency : 'RUB';
    let foot = null;
    const m = modal({
      title: op.type === 'transfer' ? 'Перевод' : op.type === 'income' ? 'Доход' : 'Расход',
      body: () => h('div', { class: 'stack', style: 'gap:16px' },
        h('div', { class: 'row', style: 'gap:14px;flex-wrap:nowrap' }, catIcon(opVisual(op), 'lg'),
          h('div', { class: 'op-main' }, h('div', { class: 'op-title', style: 'font-size:var(--fs-lg)' }, op.title),
            h('div', { class: 'big-amount' }, op.type === 'transfer' ? amountEl(op.amount, cur, { kind: 'transfer', frac: 'always' }) : amountEl(op.amount, cur, { kind: op.type, frac: 'always' })))),
        kv([
          op.type === 'transfer' ? ['Откуда', w ? w.name : '—'] : ['Счет', w ? w.name : '—'],
          op.type === 'transfer' ? ['Куда', to ? to.name : '—'] : ['Категория', c ? c.name : 'Без категории'],
          op.type === 'transfer' && to && to.currency !== cur ? ['Зачислено', fmt.money(op.toAmount, to.currency)] : null,
          cur !== DATA.base && op.type !== 'transfer' ? ['В основной валюте', '≈ ' + fmt.money(DATA.opBase(op), DATA.base)] : null,
          ['Дата', fmt.date(op.date.slice(0, 10), true) + ', ' + fmt.time(op.date)],
          op.comment ? ['Комментарий', op.comment] : null,
        ])),
      foot: close => (foot = h('div', { class: 'row', style: 'width:100%;justify-content:flex-end' }, normalFoot(close))),
    });
    function normalFoot(close) {
      return [
        button('Удалить', { kind: 'ghost', icon: 'trash', class: 'spacer', onClick: () => { foot.replaceChildren(...confirmFoot(close)); } }),
        button('Повторить', { icon: 'copy', onClick: () => { close(); editOp({ op, mode: 'copy' }); } }),
        button('Изменить', { kind: 'primary', icon: 'edit', onClick: () => { close(); editOp({ op, mode: 'edit' }); } }),
      ];
    }
    function confirmFoot(close) {
      return [
        h('p', { class: 'small soft', style: 'flex:1 1 100%' }, 'Удалить операцию? Остаток счета «' + (w ? w.name : '') + '» изменится на ' + fmt.money(op.amount, cur) + '.'),
        button('Отмена', { onClick: () => { foot.replaceChildren(...normalFoot(close)); } }),
        button('Удалить', { kind: 'danger', icon: 'trash', onClick: () => { DATA.removeOp(op.id); close(); toast('Операция удалена', 'trash'); refresh(); } }),
      ];
    }
    return m;
  }

  const parseAmount = s => { const v = parseFloat(String(s).replace(/[\s ]/g, '').replace(',', '.')); return isFinite(v) ? Math.round(v * 100) / 100 : NaN; };
  const amountText = v => (v ? String(v).replace('.', ',') : '');
  function nowTime() { const d = new Date(); return String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0'); }
  const walletOptions = (exclude) => DATA.wallets.filter(w => w.id !== exclude).map(w => ({ value: w.id, label: w.name, icon: w.icon, color: w.color, hint: fmt.money(DATA.balance(w.id), w.currency) }));

  // Ввод операции: расход, доход или перевод. editOp({op, mode: 'new'|'edit'|'copy', type, wallet})
  function editOp(o = {}) {
    const src = o.op;
    const mode = o.mode || 'new';
    const st = {
      type: src ? src.type : o.type || 'expense',
      wallet: src ? src.wallet : o.wallet || DATA.defaultWallet().id,
      toWallet: src && src.toWallet ? src.toWallet : null,
      category: src ? src.category : null,
    };
    if (!st.toWallet) { const other = DATA.wallets.find(w => w.id !== st.wallet && w.currency === DATA.wallet(st.wallet).currency) || DATA.wallets.find(w => w.id !== st.wallet); st.toWallet = other && other.id; }
    const date0 = src && mode === 'edit' ? src.date.slice(0, 10) : DATA.today;
    let body;
    const amountField = field({ id: 'op-amount', label: 'Сумма', inputmode: 'decimal', placeholder: '0', value: src ? amountText(src.amount) : '', suffix: fmt.sym(DATA.wallet(st.wallet).currency), class: 'amount-field' });
    const amountInput = () => document.getElementById('op-amount');
    const toAmountField = field({ id: 'op-to-amount', label: 'Зачислено', inputmode: 'decimal', value: src && src.toAmount && src.type === 'transfer' ? amountText(src.toAmount) : '', suffix: '¤' });
    const titleField = field({ id: 'op-title', label: 'Название', placeholder: 'Например, продукты на неделю', value: src ? src.title : '' });
    const dateField = field({ id: 'op-date', label: 'Дата', type: 'date', value: date0, attrs: { max: DATA.today } });
    const commentField = field({ id: 'op-comment', label: 'Комментарий', textarea: true, value: src ? src.comment : '', placeholder: 'Необязательно' });
    const catBox = h('div', { class: 'field' });
    const walletBox = h('div');
    const rateNote = h('div', { class: 'field-hint' });

    function setSuffix() { const s = amountField.querySelector('.input-suffix'); if (s) s.textContent = fmt.sym(DATA.wallet(st.wallet).currency); }
    function syncToAmount() {
      const from = DATA.wallet(st.wallet), to = DATA.wallet(st.toWallet);
      const cross = st.type === 'transfer' && to && from.currency !== to.currency;
      toAmountField.hidden = !cross;
      if (!cross) return;
      toAmountField.querySelector('.input-suffix').textContent = fmt.sym(to.currency);
      const v = parseAmount(amountInput().value);
      const toInput = document.getElementById('op-to-amount');
      if (isFinite(v) && !toInput.dataset.touched) toInput.value = amountText(Math.round(v * DATA.rates[from.currency] / DATA.rates[to.currency] * 100) / 100);
      rateNote.textContent = 'По курсу 1 ' + fmt.sym(to.currency === 'RUB' ? from.currency : to.currency) + ' = ' + fmt.num(to.currency === 'RUB' ? DATA.rates[from.currency] : DATA.rates[to.currency], 2) + ' ₽ — исправьте, если банк дал другой курс';
    }
    function drawCats() {
      catBox.replaceChildren();
      if (st.type === 'transfer') { catBox.hidden = true; return; }
      catBox.hidden = false;
      const list = DATA.cats(st.type);
      if (!list.some(c => c.id === st.category)) st.category = null;
      catBox.append(h('span', { class: 'field-label', id: 'op-cat-label' }, 'Категория'),
        h('div', { class: 'cat-pick', role: 'group', 'aria-labelledby': 'op-cat-label' }, list.map(c => h('button', { type: 'button', 'aria-pressed': st.category === c.id ? 'true' : 'false', on: { click: () => { st.category = c.id; drawCats(); } } }, catIcon(c), c.name))),
        h('div', { class: 'field-error', id: 'op-cat-error', hidden: true }, 'Выберите категорию'));
    }
    function drawWallets() {
      walletBox.replaceChildren();
      if (st.type === 'transfer') {
        walletBox.append(h('div', { class: 'form-grid' },
          dropdown({ id: 'op-from', label: 'Откуда', options: walletOptions(), value: st.wallet, onChange: v => { st.wallet = v; if (st.toWallet === v) st.toWallet = DATA.wallets.find(w => w.id !== v).id; setSuffix(); drawWallets(); syncToAmount(); } }),
          dropdown({ id: 'op-to', label: 'Куда', options: walletOptions(st.wallet), value: st.toWallet, onChange: v => { st.toWallet = v; delete document.getElementById('op-to-amount').dataset.touched; syncToAmount(); } })));
      } else {
        walletBox.append(dropdown({ id: 'op-wallet', label: 'Счет', options: walletOptions(), value: st.wallet, onChange: v => { st.wallet = v; setSuffix(); } }));
      }
    }
    function save(close) {
      const amount = parseAmount(amountInput().value);
      let ok = true;
      if (!(amount > 0)) { fieldError('op-amount', 'Введите сумму больше нуля'); ok = false; } else fieldError('op-amount', '');
      if (st.type !== 'transfer' && !st.category) { document.getElementById('op-cat-error').hidden = false; ok = false; }
      const from = DATA.wallet(st.wallet), to = DATA.wallet(st.toWallet);
      let toAmount = amount;
      if (st.type === 'transfer' && from.currency !== to.currency) {
        toAmount = parseAmount(document.getElementById('op-to-amount').value);
        if (!(toAmount > 0)) { fieldError('op-to-amount', 'Сколько пришло на счет «' + to.name + '»'); ok = false; } else fieldError('op-to-amount', '');
      }
      if (!ok) return;
      const date = document.getElementById('op-date').value || DATA.today;
      const c = DATA.category(st.category);
      const title = document.getElementById('op-title').value.trim() || (st.type === 'transfer' ? 'Перевод на «' + to.name + '»' : c.name);
      const rec = {
        type: st.type, title, amount, wallet: st.wallet, comment: document.getElementById('op-comment').value.trim(),
        category: st.type === 'transfer' ? null : st.category, toWallet: st.type === 'transfer' ? st.toWallet : null, toAmount: st.type === 'transfer' ? toAmount : null,
        date: date + 'T' + (mode === 'edit' && src.date.slice(0, 10) === date ? src.date.slice(11, 16) : date === DATA.today ? nowTime() : '12:00'),
      };
      if (mode === 'edit') { DATA.updateOp(src.id, rec); toast('Изменения сохранены'); }
      else { DATA.addOp(rec); toast(st.type === 'transfer' ? 'Перевод сохранен' : 'Операция сохранена'); }
      close(); refresh();
    }
    modal({
      title: mode === 'edit' ? 'Изменить операцию' : mode === 'copy' ? 'Повторить операцию' : 'Новая операция',
      body: () => (body = h('div', { class: 'stack', style: 'gap:16px' },
        mode === 'edit' && src.type === 'transfer' ? null : segmented({ label: 'Тип операции', block: true, value: st.type, options: [{ value: 'expense', label: 'Расход' }, { value: 'income', label: 'Доход' }, { value: 'transfer', label: 'Перевод' }], onChange: v => { st.type = v; drawCats(); drawWallets(); syncToAmount(); } }),
        amountField, h('div', { class: 'stack', style: 'gap:6px' }, toAmountField, rateNote), catBox, walletBox,
        h('div', { class: 'form-grid' }, titleField, dateField), commentField)),
      foot: close => [button('Отмена', { onClick: close }), button(mode === 'edit' ? 'Сохранить' : 'Добавить', { kind: 'primary', icon: 'check', onClick: () => save(close) })],
    });
    drawCats(); drawWallets(); syncToAmount();
    amountInput().addEventListener('input', () => { fieldError('op-amount', ''); syncToAmount(); });
    document.getElementById('op-to-amount').addEventListener('input', e => { e.target.dataset.touched = '1'; });
    body.closest('.modal').addEventListener('keydown', e => { if (e.key === 'Enter' && e.target.tagName === 'INPUT' && e.target.type !== 'date') { e.preventDefault(); body.closest('.modal').querySelector('.modal-foot .btn.primary').click(); } });
    if (!UI.isPhone()) amountInput().focus();
  }

  // ---------- доли категорий ----------
  // shareList([{cat, sum, count}], total, {onClick, note}) — строки с полосой доли
  function shareList(rows, totalSum, o = {}) {
    return h('div', { class: 'list' }, rows.map(r => {
      const c = r.cat;
      const inner = [catIcon(c, 'sm'),
        h('span', { class: 'share-name' }, h('span', null, c.name), UI.meter(r.sum, totalSum, null, c.color)),
        h('span', { class: 'share-side' }, amountEl(r.sum, DATA.base, { kind: 'balance', frac: 'never' }), h('small', null, fmt.pct(totalSum ? r.sum / totalSum : 0) + (r.count ? ' · ' + r.count + ' ' + fmt.plural(r.count, 'операция', 'операции', 'операций') : '')))];
      return o.onClick && c.id ? h('button', { class: 'share-row', type: 'button', on: { click: () => o.onClick(c) } }, inner) : h('div', { class: 'share-row' }, inner);
    }));
  }
  // топ категорий периода + «Остальное»
  function topCats(byCat, type, limit) {
    const rows = Object.entries(byCat).map(([id, v]) => ({ cat: DATA.category(id), sum: v.sum, count: v.count }))
      .filter(r => r.cat && r.cat.type === type).sort((a, b) => b.sum - a.sum);
    if (!limit || rows.length <= limit) return rows;
    const rest = rows.slice(limit - 1);
    return rows.slice(0, limit - 1).concat([{ cat: { name: 'Остальное', icon: 'more', color: 'var(--fg-3)' }, sum: rest.reduce((s, r) => s + r.sum, 0), count: rest.reduce((s, r) => s + r.count, 0) }]);
  }

  function walletTile(w) {
    const b = DATA.balance(w.id);
    return h('a', { class: ['wallet-tile', w.hidden && 'is-hidden'], href: '#wallet-' + w.id, title: w.hidden ? 'Не входит в общий баланс' : null },
      catIcon(w, 'sq'),
      h('span', { class: 'op-main' }, h('span', { class: 'op-sub' }, w.name), amountEl(b, w.currency, { frac: 'never' })),
      w.hidden ? icon('eyeOff', { width: 16, height: 16, style: 'color:var(--fg-3);flex:none' }) : null);
  }

  // ---------- выбор цвета и значка ----------
  function swatches(id, value, onPick) {
    const el = h('div', { class: 'swatches', role: 'group', 'aria-labelledby': id });
    const draw = v => { el.replaceChildren(...DATA.COLORS.map(c => h('button', { type: 'button', title: c.label, 'aria-label': c.label, 'aria-pressed': c.value === v ? 'true' : 'false', on: { click: () => { draw(c.value); onPick(c.value); } } }, h('i', { style: { background: c.value } })))); };
    draw(value);
    return el;
  }
  function iconGrid(id, list, value, onPick) {
    const el = h('div', { class: 'icon-grid', role: 'group', 'aria-labelledby': id });
    const draw = v => { el.replaceChildren(...list.map(n => h('button', { type: 'button', 'aria-label': n, 'aria-pressed': n === v ? 'true' : 'false', on: { click: () => { draw(n); onPick(n); } } }, icon(n)))); };
    draw(value);
    return el;
  }

  // ---------- счет ----------
  function editWallet(w) {
    const isNew = !w;
    const st = w ? { icon: w.icon, color: w.color, currency: w.currency, isDefault: w.isDefault, hidden: w.hidden } : { icon: 'card', color: 'var(--s1)', currency: DATA.base, isDefault: false, hidden: false };
    const preview = h('span');
    const drawPreview = () => preview.replaceChildren(catIcon({ icon: st.icon, color: st.color }, 'lg'));
    drawPreview();
    modal({
      title: isNew ? 'Новый счет' : 'Счет «' + w.name + '»',
      body: () => h('div', { class: 'stack', style: 'gap:16px' },
        h('div', { class: 'row', style: 'gap:14px;flex-wrap:nowrap;align-items:flex-end' }, preview, field({ id: 'w-name', label: 'Название', value: w ? w.name : '', placeholder: 'Например, карта для покупок', class: 'grow' })),
        h('div', { class: 'form-grid' },
          isNew ? dropdown({ id: 'w-cur', label: 'Валюта', value: st.currency, options: Object.values(UI.CURRENCIES).map(c => ({ value: c.code, label: c.name, hint: c.sym })), onChange: v => { st.currency = v; document.querySelector('#w-initial ~ .input-suffix').textContent = fmt.sym(v); } })
            : field({ id: 'w-cur-ro', label: 'Валюта', value: UI.CURRENCIES[w.currency].name, attrs: { disabled: true }, hint: 'После первой операции валюту не меняем' }),
          isNew ? field({ id: 'w-initial', label: 'Остаток сейчас', inputmode: 'decimal', placeholder: '0', suffix: fmt.sym(st.currency) })
            : field({ id: 'w-bal-ro', label: 'Остаток', value: fmt.money(DATA.balance(w.id), w.currency), attrs: { disabled: true }, hint: 'Меняется операциями' })),
        h('div', { class: 'field' }, h('span', { class: 'field-label', id: 'w-icon-label' }, 'Значок'), iconGrid('w-icon-label', DATA.WALLET_ICONS, st.icon, v => { st.icon = v; drawPreview(); })),
        h('div', { class: 'field' }, h('span', { class: 'field-label', id: 'w-color-label' }, 'Цвет'), swatches('w-color-label', st.color, v => { st.color = v; drawPreview(); })),
        h('div', { class: 'stack', style: 'gap:4px' },
          toggle({ id: 'w-default', label: 'Основной счет', hint: 'Подставляется в новые операции', checked: st.isDefault, disabled: !isNew && w.isDefault, onChange: v => { st.isDefault = v; } }),
          toggle({ id: 'w-total', label: 'Учитывать в общем балансе', hint: 'Выключите для вкладов и брокерских счетов', checked: !st.hidden, onChange: v => { st.hidden = !v; } }))),
      foot: close => [button('Отмена', { onClick: close }), button(isNew ? 'Создать счет' : 'Сохранить', { kind: 'primary', icon: 'check', onClick: () => {
        const name = document.getElementById('w-name').value.trim();
        if (!name) { fieldError('w-name', 'Назовите счет'); return; }
        if (isNew) {
          const initial = parseAmount(document.getElementById('w-initial').value) || 0;
          const nw = DATA.addWallet({ name, currency: st.currency, icon: st.icon, color: st.color, hidden: st.hidden, isDefault: false, note: '', initial });
          if (st.isDefault) DATA.updateWallet(nw.id, { isDefault: true });
          close(); toast('Счет «' + name + '» создан'); UI.go('wallet-' + nw.id);
        } else {
          DATA.updateWallet(w.id, { name, icon: st.icon, color: st.color, hidden: st.hidden, isDefault: st.isDefault || w.isDefault });
          close(); toast('Счет сохранен'); refresh();
        }
      } })],
    });
  }

  // ---------- категория ----------
  function editCategory(c, type) {
    const isNew = !c;
    const st = c ? { type: c.type, icon: c.icon, color: c.color, active: c.active } : { type: type || 'expense', icon: 'star', color: 'var(--s1)', active: true };
    const preview = h('span');
    const drawPreview = () => preview.replaceChildren(catIcon({ icon: st.icon, color: st.color }, 'lg'));
    drawPreview();
    const n = c ? DATA.catOpsCount(c.id) : 0;
    modal({
      title: isNew ? 'Новая категория' : 'Категория «' + c.name + '»',
      body: () => h('div', { class: 'stack', style: 'gap:16px' },
        isNew ? segmented({ label: 'Тип категории', block: true, value: st.type, options: [{ value: 'expense', label: 'Расходы' }, { value: 'income', label: 'Доходы' }], onChange: v => { st.type = v; } }) : null,
        h('div', { class: 'row', style: 'gap:14px;flex-wrap:nowrap;align-items:flex-end' }, preview, field({ id: 'c-name', label: 'Название', value: c ? c.name : '', placeholder: 'Например, кафе' })),
        h('div', { class: 'field' }, h('span', { class: 'field-label', id: 'c-icon-label' }, 'Значок'), iconGrid('c-icon-label', DATA.CATEGORY_ICONS, st.icon, v => { st.icon = v; drawPreview(); })),
        h('div', { class: 'field' }, h('span', { class: 'field-label', id: 'c-color-label' }, 'Цвет'), swatches('c-color-label', st.color, v => { st.color = v; drawPreview(); })),
        toggle({ id: 'c-active', label: 'Показывать при вводе операций', hint: 'Отключенная категория остается в истории и отчетах', checked: st.active, onChange: v => { st.active = v; } }),
        c && n ? h('p', { class: 'small muted' }, n + ' ' + fmt.plural(n, 'операция', 'операции', 'операций') + ' в этой категории. Удалить ее нельзя — можно объединить с другой.') : null),
      foot: close => [
        c && n ? button('Объединить', { icon: 'merge', class: 'spacer', onClick: () => { close(); mergeCategory(c); } }) : null,
        button('Отмена', { onClick: close }),
        button(isNew ? 'Создать' : 'Сохранить', { kind: 'primary', icon: 'check', onClick: () => {
          const name = document.getElementById('c-name').value.trim();
          if (!name) { fieldError('c-name', 'Назовите категорию'); return; }
          if (isNew) DATA.addCategory({ name, type: st.type, icon: st.icon, color: st.color, active: st.active, isDefault: false });
          else DATA.updateCategory(c.id, { name, icon: st.icon, color: st.color, active: st.active });
          close(); toast(isNew ? 'Категория «' + name + '» создана' : 'Категория сохранена'); refresh();
        } })],
    });
  }
  function mergeCategory(c) {
    const others = DATA.cats(c.type).filter(x => x.id !== c.id);
    let target = others[0] && others[0].id;
    const n = DATA.catOpsCount(c.id);
    modal({
      title: 'Объединить категории',
      body: () => h('div', { class: 'stack', style: 'gap:14px' },
        h('p', null, 'Перенесем ' + n + ' ' + fmt.plural(n, 'операцию', 'операции', 'операций') + ' из «' + c.name + '» в выбранную категорию. Категория «' + c.name + '» исчезнет, операции и суммы останутся.'),
        dropdown({ id: 'merge-to', label: 'Куда перенести', value: target, options: others.map(x => ({ value: x.id, label: x.name, icon: x.icon, color: x.color })), onChange: v => { target = v; } })),
      foot: close => [button('Отмена', { onClick: close }), button('Объединить', { kind: 'primary', icon: 'merge', onClick: () => {
        const to = DATA.category(target);
        const moved = DATA.mergeCategory(c.id, target);
        close(); toast('Перенесли ' + moved + ' ' + fmt.plural(moved, 'операцию', 'операции', 'операций') + ' в «' + to.name + '»', 'merge'); refresh();
      } })],
    });
  }

  UI.parts = { opRow, opList, openOp, editOp, shareList, topCats, walletTile, editWallet, editCategory, mergeCategory, parseAmount };
})();
