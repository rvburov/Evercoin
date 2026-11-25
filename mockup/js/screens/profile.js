/* Профиль и настройки: основная валюта, тема, скрытие сумм, безопасность, выгрузка и удаление данных.
   Адрес — #profile: адрес #settings в артефактах занят. */
(function () {
  'use strict';
  const { h, fmt, button, card, segmented, dropdown, toggle, modal, toast, field, fieldError, callout } = UI;

  function changePassword() {
    modal({
      title: 'Смена пароля',
      body: () => h('div', { class: 'stack', style: 'gap:14px' },
        field({ id: 'p-old', label: 'Текущий пароль', type: 'password', autocomplete: 'current-password' }),
        field({ id: 'p-new', label: 'Новый пароль', type: 'password', autocomplete: 'new-password', hint: 'Не короче 8 символов' })),
      foot: close => [button('Отмена', { onClick: close }), button('Сменить пароль', { kind: 'primary', onClick: () => {
        if (!document.getElementById('p-old').value) { fieldError('p-old', 'Введите текущий пароль'); return; }
        if (document.getElementById('p-new').value.length < 8) { fieldError('p-new', 'Пароль короче 8 символов'); return; }
        close(); toast('Пароль изменен. Другие устройства вышли из аккаунта', 'lock');
      } })],
    });
  }
  function deleteAccount() {
    modal({
      title: 'Удалить аккаунт',
      body: () => h('div', { class: 'stack', style: 'gap:14px' },
        callout('bad', 'alert', 'Удалим ' + DATA.wallets.length + ' ' + fmt.plural(DATA.wallets.length, 'счет', 'счета', 'счетов') + ', ' + DATA.ops.length + ' ' + fmt.plural(DATA.ops.length, 'операцию', 'операции', 'операций') + ' и все категории. Вернуть их будет нельзя.'),
        h('p', { class: 'small soft' }, 'Сначала можно выгрузить операции в CSV.'),
        field({ id: 'del-confirm', label: 'Чтобы подтвердить, введите «удалить»' })),
      foot: close => [button('Отмена', { onClick: close }), button('Удалить навсегда', { kind: 'danger', icon: 'trash', onClick: () => {
        if (document.getElementById('del-confirm').value.trim().toLowerCase() !== 'удалить') { fieldError('del-confirm', 'Введите слово «удалить»'); return; }
        close(); toast('В макете аккаунт не удаляется', 'info');
      } })],
    });
  }

  UI.register('profile', {
    title: 'Профиль',
    render(view) {
      UI.setHeader({ title: 'Профиль и настройки' });
      const u = DATA.user;
      const profile = card({ class: 'col-6', body: [
        h('div', { class: 'row', style: 'gap:16px;flex-wrap:nowrap' }, h('span', { class: 'avatar lg' }, u.initials),
          h('div', { class: 'op-main' }, h('h2', { style: 'font-size:var(--fs-xl)' }, u.name), h('span', { class: 'soft' }, u.email), h('span', { class: 'small muted' }, 'В Evercoin с ' + fmt.date(u.since, true)))),
        h('div', { class: 'row' }, button('Изменить имя и почту', { size: 'sm', icon: 'edit', onClick: () => toast('В макете профиль не меняется', 'info') })),
      ] });

      const settings = card({ class: 'col-6', title: 'Настройки', body: [
        h('div', { class: 'set-row' }, h('div', null, h('div', { class: 'toggle-label' }, 'Основная валюта'), h('div', { class: 'field-hint' }, 'В ней считаем общий баланс и аналитику. Суммы счетов остаются в их валютах.')),
          dropdown({ id: 'base-cur', compact: true, ariaLabel: 'Основная валюта', value: DATA.base, options: Object.values(UI.CURRENCIES).map(c => ({ value: c.code, label: c.name, hint: c.sym })), onChange: v => { DATA.setBase(v); toast('Основная валюта: ' + UI.CURRENCIES[v].name.toLowerCase()); UI.refresh(); } })),
        h('div', { class: 'set-row' }, h('div', null, h('div', { class: 'toggle-label' }, 'Тема'), h('div', { class: 'field-hint' }, 'Как в системе, светлая или темная')),
          segmented({ label: 'Тема', value: UI.theme.get(), options: [{ value: 'system', label: 'Как в системе' }, { value: 'light', label: 'Светлая' }, { value: 'dark', label: 'Темная' }], onChange: v => UI.theme.set(v) })),
        h('div', { class: 'set-row' }, toggle({ id: 'privacy', label: 'Скрывать суммы', hint: 'Например, в метро: вместо сумм — точки. На главной то же делает кнопка с глазом.', checked: UI.privacy, onChange: v => { UI.setPrivacy(v); UI.refresh(); } })),
      ] });

      const security = card({ class: 'col-6', title: 'Безопасность', body: [
        h('div', { class: 'set-row' }, h('div', null, h('div', { class: 'toggle-label' }, 'Пароль'), h('div', { class: 'field-hint' }, 'Меняли 2 месяца назад')), button('Сменить', { size: 'sm', icon: 'lock', onClick: changePassword })),
        h('div', { class: 'set-row' }, h('div', null, h('div', { class: 'toggle-label' }, 'Другие устройства'), h('div', { class: 'field-hint' }, 'Телефон · вход вчера в 21:14')), button('Выйти на них', { size: 'sm', onClick: () => toast('Другие устройства вышли из аккаунта', 'logout') })),
      ] });

      const data = card({ class: 'col-6', title: 'Данные', body: [
        h('div', { class: 'set-row' }, h('div', null, h('div', { class: 'toggle-label' }, 'Выгрузка операций'), h('div', { class: 'field-hint' }, 'CSV со всеми операциями: дата, сумма, валюта, счет, категория')), button('Выгрузить', { size: 'sm', icon: 'download', onClick: () => toast('В приложении здесь скачается CSV', 'download') })),
        h('div', { class: 'set-row' }, h('div', null, h('div', { class: 'toggle-label' }, 'Удаление аккаунта'), h('div', { class: 'field-hint' }, 'Удалит все счета, операции и категории')), button('Удалить', { size: 'sm', kind: 'danger', onClick: deleteAccount })),
      ] });

      view.appendChild(h('div', { class: 'grid' }, profile, settings, security, data));
      view.appendChild(h('div', null, button('Выйти из аккаунта', { kind: 'ghost', icon: 'logout', onClick: () => UI.auth.logout() })));
    },
  });
})();
