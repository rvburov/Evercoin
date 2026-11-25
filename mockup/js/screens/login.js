/* Вход, регистрация и сброс пароля. В макете подойдет любой пароль, кроме wrong. */
(function () {
  'use strict';
  const { h, icon, button, card, field, fieldError, callout } = UI;

  function passwordField(id, label, labelAside) {
    let shown = false;
    const toggleBtn = h('button', { class: 'input-action', type: 'button', 'aria-label': 'Показать пароль', on: { click: () => {
      shown = !shown;
      const input = document.getElementById(id);
      input.type = shown ? 'text' : 'password';
      toggleBtn.setAttribute('aria-label', shown ? 'Скрыть пароль' : 'Показать пароль');
      toggleBtn.replaceChildren(icon(shown ? 'eyeOff' : 'eye'));
    } } }, icon('eye'));
    return field({ id, label, type: 'password', autocomplete: id === 'l-pass' ? 'current-password' : 'new-password', action: toggleBtn, labelAside });
  }

  UI.register('login', {
    title: 'Вход',
    render(app) {
      let mode = 'login';
      const box = h('div', { class: 'auth-box' });
      const form = h('form', { novalidate: true, on: { submit: e => { e.preventDefault(); submit(); } } });

      function draw() {
        form.replaceChildren();
        if (mode === 'login') {
          form.append(card({ body: [
            h('h1', { style: 'font-size:var(--fs-xl)' }, 'Вход'),
            field({ id: 'l-email', label: 'Почта', type: 'email', autocomplete: 'email', value: DATA.user.email, inputmode: 'email' }),
            passwordField('l-pass', 'Пароль', h('button', { class: 'link-btn', type: 'button', style: 'font-weight:500', on: { click: () => { mode = 'reset'; draw(); } } }, 'Забыли пароль?')),
            button('Войти', { kind: 'primary', type: 'submit', block: true, size: 'lg' }),
            h('p', { class: 'xsmall muted', style: 'text-align:center' }, 'Макет: подойдет любой пароль, кроме «wrong»'),
          ] }));
          box.lastChild.replaceChildren(h('span', null, 'Нет аккаунта? '), h('button', { class: 'link-btn', type: 'button', on: { click: () => { mode = 'register'; draw(); } } }, 'Зарегистрироваться'));
        } else if (mode === 'register') {
          form.append(card({ body: [
            h('h1', { style: 'font-size:var(--fs-xl)' }, 'Регистрация'),
            field({ id: 'r-name', label: 'Как к вам обращаться', autocomplete: 'name', placeholder: 'Имя' }),
            field({ id: 'r-email', label: 'Почта', type: 'email', autocomplete: 'email', inputmode: 'email' }),
            passwordField('r-pass', 'Пароль'),
            h('p', { class: 'field-hint', style: 'margin-top:-6px' }, 'Не короче 8 символов. Основная валюта — рубли, поменять можно в профиле.'),
            button('Создать аккаунт', { kind: 'primary', type: 'submit', block: true, size: 'lg' }),
          ] }));
          box.lastChild.replaceChildren(h('span', null, 'Уже есть аккаунт? '), h('button', { class: 'link-btn', type: 'button', on: { click: () => { mode = 'login'; draw(); } } }, 'Войти'));
        } else {
          form.append(card({ body: [
            h('h1', { style: 'font-size:var(--fs-xl)' }, 'Сброс пароля'),
            h('p', { class: 'soft' }, 'Пришлем на почту ссылку для нового пароля. Ссылка действует 24 часа.'),
            field({ id: 's-email', label: 'Почта', type: 'email', autocomplete: 'email', value: DATA.user.email, inputmode: 'email' }),
            h('div', { id: 's-done', hidden: true }, callout('good', 'check', 'Письмо отправлено. Проверьте почту и папку «Спам».')),
            button('Отправить ссылку', { kind: 'primary', type: 'submit', block: true, size: 'lg' }),
          ] }));
          box.lastChild.replaceChildren(h('button', { class: 'link-btn', type: 'button', on: { click: () => { mode = 'login'; draw(); } } }, 'Вернуться ко входу'));
        }
      }
      function submit() {
        if (mode === 'reset') { document.getElementById('s-done').hidden = false; return; }
        const pre = mode === 'login' ? 'l' : 'r';
        const email = document.getElementById(pre + '-email').value.trim();
        const pass = document.getElementById(pre + '-pass').value;
        let ok = true;
        if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { fieldError(pre + '-email', 'Проверьте адрес почты'); ok = false; } else fieldError(pre + '-email', '');
        if (mode === 'register' && pass.length < 8) { fieldError('r-pass', 'Пароль короче 8 символов'); ok = false; }
        else if (mode === 'login' && (!pass || pass === 'wrong')) { fieldError('l-pass', pass ? 'Неверная почта или пароль' : 'Введите пароль'); ok = false; }
        else fieldError(pre + '-pass', '');
        if (ok) UI.auth.login();
      }
      box.append(h('div', { class: 'auth-brand' }, UI.brandMark(), h('div', null, h('div', { class: 'brand-name' }, 'Evercoin'), h('div', { class: 'brand-sub' }, 'личные финансы'))), form, h('div', { class: 'auth-foot' }));
      draw();
      app.appendChild(h('div', { class: 'auth' }, box));
    },
  });
})();
