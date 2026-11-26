import { useEffect, useRef, useState } from "react";
import { Check, X } from "lucide-react";
import { iconChoices, iconMap, type FinanceItem } from "./data";
import "./item-editor.css";

const preferredIcons = [
  "plane",
  "at",
  "bandage",
  "bank",
  "presentation",
  "cocktail",
  "spray",
  "beer",
  "bike",
  "money",
  "book",
  "notebook",
  "chart",
  "camera",
  "car",
  "card",
  "work",
  "wallet",
  "building",
  "coffee",
  "game",
  "calculator",
  "scale",
  "dice",
  "monitor",
  "drama",
  "dumbbell",
  "cafe",
  "radio",
  "film",
  "flower",
  "food",
];
const orderedIcons = [
  ...preferredIcons.filter((key) => iconMap[key]),
  ...iconChoices.filter((key) => !preferredIcons.includes(key)),
];

interface ItemEditorProps {
  item: FinanceItem;
  balance: number;
  onSave: (item: FinanceItem, desiredBalance?: number) => void;
  onDelete: () => void;
  onCancel: () => void;
}

function parseAmount(value: string, allowNegative: boolean): number | null {
  const normalized = value.trim().replace(/\s/g, "").replace(",", ".");
  if (!normalized) return 0;
  const pattern = allowNegative ? /^-?\d+(\.\d{1,2})?$/ : /^\d+(\.\d{1,2})?$/;
  if (!pattern.test(normalized)) return null;
  const amount = Math.round(Number(normalized) * 100);
  return Number.isSafeInteger(amount) && Math.abs(amount) <= 99999999999
    ? amount
    : null;
}

export default function ItemEditor({
  item,
  balance,
  onSave,
  onDelete,
  onCancel,
}: ItemEditorProps) {
  const [name, setName] = useState(item.name);
  const [icon, setIcon] = useState(item.icon);
  const [amount, setAmount] = useState(
    ((item.kind === "account" ? balance : item.budget) / 100).toString(),
  );
  const [included, setIncluded] = useState(item.included);
  const [goal, setGoal] = useState(item.goal);
  const [iconPicker, setIconPicker] = useState(false);
  const [iconPage, setIconPage] = useState(0);
  const [currencyOpen, setCurrencyOpen] = useState(false);
  const [error, setError] = useState("");
  const swipeStart = useRef(0);
  const selectedIcon = iconMap[icon] || iconMap.money;
  const SelectedIcon = selectedIcon;
  const pageCount = Math.ceil(orderedIcons.length / 32);
  const pageIcons = orderedIcons.slice(iconPage * 32, (iconPage + 1) * 32);
  const isAccount = item.kind === "account";
  const isIncome = item.kind === "income";
  const heading = isAccount
    ? "Измените параметры счета"
    : isIncome
      ? "Откуда вы получаете деньги?"
      : "На что вы тратите деньги?";

  useEffect(() => {
    function handleKey(event: KeyboardEvent) {
      if (event.key !== "Escape") return;
      if (iconPicker) setIconPicker(false);
      else if (currencyOpen) setCurrencyOpen(false);
      else onCancel();
    }
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [iconPicker, currencyOpen, onCancel]);

  function save(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!name.trim()) {
      setError("Введите название");
      return;
    }
    const parsedAmount = parseAmount(amount, isAccount);
    if (parsedAmount === null) {
      setError(
        isAccount
          ? "Введите корректный баланс с точностью до копеек"
          : "Введите сумму от 0 до 999 999 999,99 ₽",
      );
      return;
    }
    onSave(
      {
        ...item,
        name: name.trim(),
        icon,
        included,
        goal,
        budget: isAccount ? item.budget : parsedAmount,
      },
      isAccount ? parsedAmount : undefined,
    );
  }

  return (
    <div className={`item-editor kind-${item.kind}`}>
      <form className="item-editor-form" onSubmit={save} noValidate>
        <header className="editor-toolbar">
          <button
            type="button"
            className="editor-control"
            aria-label="Отменить редактирование"
            onClick={onCancel}
          >
            <X />
          </button>
          <button
            type="submit"
            className="editor-control"
            aria-label="Сохранить изменения"
          >
            <Check />
          </button>
        </header>
        <section className="editor-intro">
          <h1>{heading}</h1>
          <button
            type="button"
            className="editor-icon"
            aria-label="Выбрать иконку"
            onClick={() => setIconPicker(true)}
          >
            {icon ? <SelectedIcon strokeWidth={1.1} /> : <span>Иконка</span>}
          </button>
        </section>
        {!isAccount && !isIncome && (
          <div
            className="editor-tabs"
            role="tablist"
            aria-label="Тип категории"
          >
            <button
              type="button"
              role="tab"
              aria-selected={!goal}
              className={!goal ? "selected" : ""}
              onClick={() => setGoal(false)}
            >
              Категория расхода
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={goal}
              className={goal ? "selected" : ""}
              onClick={() => setGoal(true)}
            >
              Цель
            </button>
          </div>
        )}
        <div className="editor-fields">
          <label className="editor-line editor-name-line">
            <span className="editor-visually-hidden">Название</span>
            <input
              aria-label="Название"
              value={name}
              maxLength={60}
              placeholder="Введите название"
              autoComplete="off"
              onChange={(event) => {
                setName(event.target.value);
                setError("");
              }}
            />
            {!isAccount && (
              <button
                type="button"
                className="editor-currency"
                aria-label="Выбрать валюту"
                onClick={() => setCurrencyOpen(true)}
              >
                ₽
              </button>
            )}
          </label>
          <label className="editor-line editor-amount-line">
            <span className="editor-visually-hidden">
              {isAccount
                ? "Баланс счета"
                : goal
                  ? "Сумма цели"
                  : "Планируемая сумма"}
            </span>
            <input
              aria-label={
                isAccount
                  ? "Баланс счета"
                  : goal
                    ? "Сумма цели"
                    : "Планируемая сумма"
              }
              inputMode={isAccount ? "text" : "decimal"}
              value={amount === "0" && !isAccount ? "" : amount}
              placeholder={
                isAccount
                  ? "Баланс"
                  : goal
                    ? "Планирую накопить"
                    : isIncome
                      ? "Планирую получать"
                      : "Планирую тратить"
              }
              onChange={(event) => {
                setAmount(event.target.value);
                setError("");
              }}
            />
            {!isAccount && (
              <span className="editor-period">
                {goal ? "всего" : "в месяц"}
              </span>
            )}
          </label>
          {isAccount && (
            <button
              type="button"
              className="editor-line editor-include"
              role="switch"
              aria-checked={included}
              onClick={() => setIncluded(!included)}
            >
              <span>Учитывать в общем балансе</span>
              <span
                className={`editor-switch ${included ? "is-on" : ""}`}
                aria-hidden="true"
              >
                <i />
              </span>
            </button>
          )}
        </div>
        {error && (
          <p className="editor-error" role="alert">
            {error}
          </p>
        )}
        {item.name && (
          <button className="editor-delete" type="button" onClick={onDelete}>
            Удалить
          </button>
        )}
      </form>
      {iconPicker && (
        <section
          className="icon-picker"
          role="dialog"
          aria-modal="true"
          aria-label="Выберите иконку"
        >
          <div
            className="icon-picker-panel"
            onTouchStart={(event) => {
              swipeStart.current = event.touches[0].clientX;
            }}
            onTouchEnd={(event) => {
              const delta =
                event.changedTouches[0].clientX - swipeStart.current;
              if (Math.abs(delta) > 45)
                setIconPage((current) =>
                  Math.max(
                    0,
                    Math.min(pageCount - 1, current + (delta < 0 ? 1 : -1)),
                  ),
                );
            }}
          >
            <div className="icon-picker-grid">
              {pageIcons.map((key) => {
                const ChoiceIcon = iconMap[key];
                return (
                  <button
                    type="button"
                    key={key}
                    className={key === icon ? "is-selected" : ""}
                    aria-label={`Иконка ${key}`}
                    aria-pressed={key === icon}
                    onClick={() => {
                      setIcon(key);
                      setIconPicker(false);
                    }}
                  >
                    <span>
                      <ChoiceIcon strokeWidth={1} />
                    </span>
                  </button>
                );
              })}
            </div>
            <div className="icon-picker-dots" aria-label="Страницы иконок">
              {Array.from({ length: pageCount }, (_, index) => (
                <button
                  type="button"
                  key={index}
                  className={index === iconPage ? "active" : ""}
                  aria-label={`Страница иконок ${index + 1}`}
                  aria-current={index === iconPage ? "page" : undefined}
                  onClick={() => setIconPage(index)}
                >
                  <i />
                </button>
              ))}
            </div>
            <button
              type="button"
              className="icon-picker-cancel"
              onClick={() => setIconPicker(false)}
            >
              Отмена
            </button>
          </div>
        </section>
      )}
      {currencyOpen && (
        <div
          className="editor-currency-overlay"
          role="dialog"
          aria-modal="true"
          aria-label="Валюта категории"
          onClick={() => setCurrencyOpen(false)}
        >
          <div
            className="editor-currency-dialog"
            onClick={(event) => event.stopPropagation()}
          >
            <h2>Валюта категории</h2>
            <button type="button" onClick={() => setCurrencyOpen(false)}>
              Российский рубль{" "}
              <span>
                ₽ <Check size={18} />
              </span>
            </button>
            <button type="button" onClick={() => setCurrencyOpen(false)}>
              Отмена
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
