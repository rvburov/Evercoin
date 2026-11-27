import { useState } from "react";
import {
  ArrowLeft,
  CalendarDays,
  Check,
  ChevronRight,
  Divide,
  Equal,
  MessageCircle,
  Minus,
  MoreHorizontal,
  Percent,
  Plus,
  Repeat2,
  X,
} from "lucide-react";
import {
  isValidDate,
  today,
  type FinanceState,
  type OperationDraft,
} from "./data";
import Calendar, { RepeatPicker } from "./Calendar";
import { ActionSheet } from "./ui";
import "./operation.css";

interface Props {
  state: FinanceState;
  initialDraft: OperationDraft;
  onSave: (draft: OperationDraft) => void;
  onClose: () => void;
}
export default function OperationComposer({
  state,
  initialDraft,
  onSave,
  onClose,
}: Props) {
  const [draft, setDraft] = useState<OperationDraft>(initialDraft);
  const [panel, setPanel] = useState<
    "source" | "target" | "tags" | "calendar" | "repeat" | null
  >(null);
  const [noteMode, setNoteMode] = useState(false);
  const [note, setNote] = useState(draft.note);
  const [error, setError] = useState("");
  const [operand, setOperand] = useState<number | null>(null);
  const [operator, setOperator] = useState<string | null>(null);
  const source = state.items.find((item) => item.id === draft.sourceId);
  const target = state.items.find((item) => item.id === draft.targetId);
  // Метки — из уже записанных операций, встроенных подкатегорий нет.
  const tags = Array.from(
    new Set(state.entries.flatMap((entry) => entry.tags)),
  );
  const [customTag, setCustomTag] = useState("");
  const availableTags = Array.from(new Set([...tags, ...draft.tags]));
  function updateAmount(value: string) {
    setDraft((previous) => ({ ...previous, amount: value }));
    setError("");
  }
  function calculate(): number | null {
    const current = Number(draft.amount.replace(",", ".") || "0");
    if (operand === null || !operator) return current;
    const result =
      operator === "+"
        ? operand + current
        : operator === "−"
          ? operand - current
          : operator === "×"
            ? operand * current
            : current !== 0
              ? operand / current
              : NaN;
    if (!Number.isFinite(result)) {
      setError("Деление на ноль невозможно");
      return null;
    }
    return Math.round(result * 100) / 100;
  }
  function chooseOperator(next: string) {
    const value = calculate();
    if (value === null) return;
    setOperand(value);
    setOperator(next);
    updateAmount("");
  }
  function equals() {
    const result = calculate();
    if (result === null) return;
    updateAmount(String(result));
    setOperand(null);
    setOperator(null);
  }
  function save() {
    const value = calculate();
    if (value === null) return;
    const amount = String(value);
    const kopeks = Math.round(value * 100);
    if (
      !/^\d+(\.\d{1,2})?$/.test(amount) ||
      !Number.isSafeInteger(kopeks) ||
      kopeks <= 0 ||
      kopeks > 99999999999
    ) {
      setError("Укажите сумму больше нуля, до 999 999 999,99 ₽");
      return;
    }
    if (
      !source ||
      !target ||
      source.id === target.id ||
      source.kind === "expense" ||
      target.kind === "income" ||
      (source.kind === "income" && target.kind !== "account")
    ) {
      setError("Выберите счет и назначение операции");
      return;
    }
    if (!isValidDate(draft.date)) {
      setError("Выберите дату");
      return;
    }
    onSave({ ...draft, amount, note: noteMode ? note : draft.note });
  }
  function key(value: string) {
    if (value === "back") {
      updateAmount(draft.amount.slice(0, -1));
      return;
    }
    if (value === ",") {
      if (!/[.,]/.test(draft.amount)) updateAmount((draft.amount || "0") + ",");
      return;
    }
    if (draft.amount.length < 14)
      updateAmount(draft.amount === "0" ? value : draft.amount + value);
  }
  function selectItem(id: string) {
    const item = state.items.find((candidate) => candidate.id === id)!;
    if (panel === "source") {
      const targetId =
        item.kind === "income" && target?.kind !== "account"
          ? state.items.find(
              (candidate) =>
                candidate.kind === "account" && !candidate.archived,
            )?.id || ""
          : draft.targetId;
      setDraft({
        ...draft,
        sourceId: id,
        targetId:
          targetId === id
            ? state.items.find(
                (candidate) =>
                  candidate.kind === "expense" && !candidate.archived,
              )?.id || ""
            : targetId,
      });
    } else setDraft({ ...draft, targetId: id });
    setPanel(null);
  }
  const selections = state.items.filter(
    (item) =>
      !item.archived &&
      (panel === "source"
        ? item.kind !== "expense"
        : item.kind !== "income" &&
          item.id !== draft.sourceId &&
          (source?.kind !== "income" || item.kind === "account")),
  );
  return (
    <div className="operation-screen">
      <header className="operation-header">
        <button
          className="icon-button"
          aria-label="Отменить операцию"
          onClick={onClose}
        >
          <X />
        </button>
        <button
          className="operation-party"
          aria-label="Откуда"
          onClick={() => setPanel("source")}
        >
          {source?.name || "Откуда"}
        </button>
        <ChevronRight />
        <button
          className="operation-party"
          aria-label="Куда"
          onClick={() => setPanel("target")}
        >
          {target?.name || "Куда"}
        </button>
        <button
          className="icon-button"
          aria-label="Сохранить операцию"
          onClick={save}
        >
          <Check />
        </button>
      </header>
      <div className="operation-tags">
        {availableTags.slice(0, 2).map((tag) => (
          <button
            key={tag}
            className={draft.tags.includes(tag) ? "selected" : ""}
            onClick={() =>
              setDraft({
                ...draft,
                tags: draft.tags.includes(tag)
                  ? draft.tags.filter((value) => value !== tag)
                  : [...draft.tags, tag],
              })
            }
          >
            {tag}
          </button>
        ))}
        <button
          className="icon-button"
          aria-label="Выбрать метки"
          onClick={() => setPanel("tags")}
        >
          <MoreHorizontal />
        </button>
      </div>
      <div className="operation-amount">
        {operator && (
          <small>
            {operand} {operator}
          </small>
        )}
        <input
          aria-label="Сумма операции"
          inputMode="decimal"
          value={draft.amount}
          placeholder=""
          onChange={(event) => {
            if (/^\d{0,10}([.,]\d{0,2})?$/.test(event.target.value))
              updateAmount(event.target.value);
          }}
        />
        <span>₽</span>
      </div>
      {error && (
        <p className="operation-error" role="alert">
          {error}
        </p>
      )}
      {draft.origin === "assistant" && (
        <p className="operation-demo">Черновик помощника · проверьте данные</p>
      )}
      {noteMode ? (
        <div className="operation-note">
          <textarea
            aria-label="Заметка"
            placeholder="Заметка"
            value={note}
            onChange={(event) => setNote(event.target.value)}
            autoFocus
            maxLength={1000}
          />
          <div>
            <button
              className="icon-button"
              aria-label="Отменить заметку"
              onClick={() => {
                setNote(draft.note);
                setNoteMode(false);
              }}
            >
              <X />
            </button>
            <button
              className="icon-button"
              aria-label="Сохранить заметку"
              onClick={() => {
                setDraft({ ...draft, note });
                setNoteMode(false);
              }}
            >
              <Check />
            </button>
          </div>
        </div>
      ) : (
        <>
          <div className="calculator-tools">
            <button
              className={draft.note ? "chosen" : ""}
              aria-label="Добавить заметку"
              onClick={() => setNoteMode(true)}
            >
              <MessageCircle />
            </button>
            <button
              className={draft.repeat ? "chosen" : ""}
              aria-label="Повторение"
              onClick={() => setPanel("repeat")}
            >
              <Repeat2 />
            </button>
            <button
              aria-label="Процент"
              onClick={() =>
                updateAmount(
                  String(
                    Math.round(Number(draft.amount.replace(",", ".") || 0)) /
                      100,
                  ),
                )
              }
            >
              <Percent />
            </button>
            <button aria-label="Прибавить" onClick={() => chooseOperator("+")}>
              <Plus />
            </button>
          </div>
          <div className="calculator-keys">
            {[
              ["1", "2", "3", "−"],
              ["4", "5", "6", "×"],
              ["7", "8", "9", "÷"],
              [",", "0", "back", "="],
            ].map((row, rowIndex) =>
              row.map((value, column) => (
                <button
                  key={`${rowIndex}-${column}`}
                  className={column === 3 ? "operator-key" : ""}
                  aria-label={
                    value === "back"
                      ? "Стереть цифру"
                      : value === "="
                        ? "Равно"
                        : value
                  }
                  onClick={() =>
                    value === "="
                      ? equals()
                      : ["−", "×", "÷"].includes(value)
                        ? chooseOperator(value)
                        : key(value)
                  }
                >
                  {value === "back" ? (
                    <ArrowLeft />
                  ) : value === "÷" ? (
                    <Divide />
                  ) : value === "−" ? (
                    <Minus />
                  ) : value === "=" ? (
                    <Equal />
                  ) : (
                    value
                  )}
                </button>
              )),
            )}
          </div>
          <footer className="operation-date">
            <button
              onClick={() => setDraft({ ...draft, date: "2026-11-24" })}
              className={draft.date === "2026-11-24" ? "selected" : ""}
            >
              Вчера
            </button>
            <button
              onClick={() => setDraft({ ...draft, date: today })}
              className={draft.date === today ? "selected" : ""}
            >
              {draft.date === today || draft.date === "2026-11-24"
                ? "Сегодня"
                : new Date(draft.date + "T12:00:00").toLocaleDateString(
                    "ru-RU",
                  )}
            </button>
            <button
              aria-label="Дата операции"
              onClick={() => setPanel("calendar")}
            >
              <CalendarDays />
            </button>
          </footer>
        </>
      )}
      {(panel === "source" || panel === "target") && (
        <ActionSheet
          title={panel === "source" ? "Откуда" : "Куда"}
          onClose={() => setPanel(null)}
        >
          {selections.map((item) => (
            <button
              className="sheet-option"
              key={item.id}
              onClick={() => selectItem(item.id)}
            >
              {item.name}
            </button>
          ))}
        </ActionSheet>
      )}
      {panel === "tags" && (
        <ActionSheet title="Метки операции" onClose={() => setPanel(null)}>
          {availableTags.map((tag) => (
            <button
              className="sheet-option tag-option"
              key={tag}
              onClick={() =>
                setDraft({
                  ...draft,
                  tags: draft.tags.includes(tag)
                    ? draft.tags.filter((value) => value !== tag)
                    : [...draft.tags, tag],
                })
              }
            >
              <span>{tag}</span>
              {draft.tags.includes(tag) && <Check size={18} />}
            </button>
          ))}
          <form
            className="custom-tag"
            onSubmit={(event) => {
              event.preventDefault();
              const value = customTag.trim();
              if (value) {
                setDraft({
                  ...draft,
                  tags: Array.from(new Set([...draft.tags, value])),
                });
                setCustomTag("");
              }
            }}
          >
            <input
              aria-label="Новая метка"
              placeholder="Новая метка"
              value={customTag}
              onChange={(event) => setCustomTag(event.target.value)}
            />
            <button aria-label="Добавить метку">
              <Plus />
            </button>
          </form>
          <button className="sheet-option" onClick={() => setPanel(null)}>
            Готово
          </button>
        </ActionSheet>
      )}
      {panel === "calendar" && (
        <Calendar
          selectedDate={draft.date}
          onSelect={(date) => {
            setDraft({ ...draft, date });
            setPanel(null);
          }}
          onClose={() => setPanel(null)}
        />
      )}
      {panel === "repeat" && (
        <RepeatPicker
          value={draft.repeat}
          onSave={(repeat) => {
            setDraft({ ...draft, repeat });
            setPanel(null);
          }}
          onClose={() => setPanel(null)}
        />
      )}
    </div>
  );
}
