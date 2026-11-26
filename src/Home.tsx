import {
  useRef,
  useState,
  type PointerEvent as ReactPointerEvent,
} from "react";
import {
  ChevronDown,
  ChevronUp,
  Menu,
  Mic,
  Pencil,
  Plus,
  X,
} from "lucide-react";
import {
  accountBalance,
  compactMoney,
  entriesForPeriod,
  itemTotal,
  money,
  totalBalance,
  totals,
  type FinanceItem,
  type FinanceState,
  type ItemKind,
  type OperationDraft,
} from "./data";
import { Icon } from "./ui";
import { useFinanceDrag } from "./useFinanceDrag";

interface HomeProps {
  state: FinanceState;
  period: string;
  editing: boolean;
  onMenu: () => void;
  onFeed: (filter?: string, report?: "expense" | "income" | "balance") => void;
  onEditor: (item: FinanceItem) => void;
  onAdd: (kind: ItemKind) => void;
  onRemove: (item: FinanceItem) => void;
  onDone: () => void;
  onDraft: (draft: Partial<OperationDraft>) => void;
  onToggleIncome: () => void;
  onAssistant: () => void;
  notify: (message: string) => void;
}
export default function Home({
  state,
  period,
  editing,
  onMenu,
  onFeed,
  onEditor,
  onAdd,
  onRemove,
  onDone,
  onDraft,
  onToggleIncome,
  onAssistant,
  notify,
}: HomeProps) {
  const [expensePage, setExpensePage] = useState(0);
  const [incomePage, setIncomePage] = useState(0);
  const [accountPage, setAccountPage] = useState(0);
  const expenseRef = useRef<HTMLDivElement>(null);
  const incomeRef = useRef<HTMLDivElement>(null);
  const accountRef = useRef<HTMLDivElement>(null);
  const startTouch = useRef<{ x: number; y: number } | null>(null);
  const { drag, beginDrag, allowClick } = useFinanceDrag(onDraft, notify);
  const monthlyEntries = entriesForPeriod(state.entries, period);
  const summary = totals(state, period);
  const incomes = state.items.filter(
    (item) => item.kind === "income" && !item.archived,
  );
  const accounts = state.items.filter(
    (item) => item.kind === "account" && !item.archived,
  );
  const expenses = state.items.filter(
    (item) => item.kind === "expense" && !item.archived,
  );
  const incomePages = Math.max(1, Math.ceil((incomes.length + 1) / 4));
  const expensePages = Math.max(1, Math.ceil((expenses.length + 1) / 20));
  const accountPages = Math.max(1, Math.ceil((accounts.length + 1) / 4));
  function selectPage(kind: "expense" | "account" | "income", index: number) {
    const ref =
      kind === "expense"
        ? expenseRef
        : kind === "income"
          ? incomeRef
          : accountRef;
    ref.current?.scrollTo({
      left: index * ref.current.clientWidth,
      behavior: "smooth",
    });
    if (kind === "expense") setExpensePage(index);
    else if (kind === "income") setIncomePage(index);
    else setAccountPage(index);
  }
  function swipeEnd(
    event: ReactPointerEvent,
    kind: "expense" | "account" | "income",
  ) {
    const start = startTouch.current;
    startTouch.current = null;
    if (!start || drag) return;
    const distance = start.x - event.clientX;
    if (Math.abs(distance) < 45 || Math.abs(event.clientY - start.y) > 60)
      return;
    const current =
      kind === "expense"
        ? expensePage
        : kind === "income"
          ? incomePage
          : accountPage;
    const count =
      kind === "expense"
        ? expensePages
        : kind === "income"
          ? incomePages
          : accountPages;
    selectPage(
      kind,
      Math.max(0, Math.min(count - 1, current + (distance > 0 ? 1 : -1))),
    );
  }
  function tile(item: FinanceItem) {
    const amount =
      item.kind === "account"
        ? accountBalance(item, state.entries)
        : item.kind === "income"
          ? monthlyEntries
              .filter((entry) => entry.sourceId === item.id)
              .reduce((total, entry) => total + entry.amount, 0)
          : itemTotal(item.id, monthlyEntries);
    const isOver =
      state.preferences.colorOverspend &&
      item.kind === "expense" &&
      item.budget > 0 &&
      amount > item.budget;
    const circleClass =
      item.kind !== "expense"
        ? item.kind
        : amount === 0
          ? "expense idle"
          : isOver
            ? "expense over"
            : "expense under";
    const fill = item.budget
      ? Math.min(100, (amount / item.budget) * 100)
      : 100;
    return (
      <div className="finance-tile" key={item.id}>
        <button
          className={`tile-button ${item.kind !== "expense" && !editing ? "draggable" : ""}`}
          aria-label={item.name}
          data-drop={
            item.kind === "account"
              ? "account"
              : item.kind === "expense"
                ? "expense"
                : undefined
          }
          data-id={item.id}
          onPointerDown={(event) => {
            if (item.kind !== "expense" && !editing)
              beginDrag(event, {
                kind: item.kind,
                id: item.id,
                name: item.name,
              });
          }}
          onClick={() => {
            if (!allowClick()) return;
            if (editing) onEditor(item);
            else onFeed(item.id);
          }}
        >
          <span className="tile-name">{item.name}</span>
          <span
            className={`circle-icon ${circleClass}`}
            style={
              item.kind === "expense" && amount > 0 && !isOver
                ? {
                    background: `linear-gradient(to top, var(--positive) ${fill}%, var(--idle) ${fill}%)`,
                  }
                : undefined
            }
          >
            <Icon name={item.icon} size={30} />
          </span>
          <span
            className={`tile-value ${item.kind === "expense" ? (isOver ? "over-value" : "under-value") : item.kind + "-value"}`}
          >
            {compactMoney(amount)}
          </span>
          {item.kind !== "account" && state.preferences.showBudget && (
            <span className="tile-budget">
              {item.budget > 0
                ? money(item.budget).replace(" ₽", "")
                : "\u00a0"}
            </span>
          )}
        </button>
        {editing && (
          <>
            <button
              className="tile-delete"
              aria-label={`Удалить ${item.name}`}
              onClick={() => onRemove(item)}
            >
              <X size={15} />
            </button>
            <button
              className="tile-edit"
              aria-label={`Изменить ${item.name}`}
              onClick={() => onEditor(item)}
            >
              <Pencil size={12} />
            </button>
          </>
        )}
      </div>
    );
  }
  function addTile(kind: ItemKind) {
    return (
      <div className="finance-tile add-tile">
        <button
          className="tile-button"
          aria-label={`Добавить ${kind === "income" ? "доход" : kind === "account" ? "счет" : "расход"}`}
          onClick={() => onAdd(kind)}
        >
          <span className="tile-name">&nbsp;</span>
          <span className="circle-icon add-circle">
            <Plus size={27} />
          </span>
        </button>
      </div>
    );
  }
  return (
    <div
      className={`home-screen ${editing ? "home-editing" : ""} ${drag ? "dragging-mode" : ""}`}
    >
      {!editing && (
        <header className="overview-header">
          <button
            className="icon-button"
            aria-label="Открыть меню"
            onClick={onMenu}
          >
            <Menu />
          </button>
          <button onClick={() => onFeed(undefined, "balance")}>
            <span>Баланс</span>
            <strong data-testid="total-balance">
              {compactMoney(totalBalance(state))}
            </strong>
          </button>
          <button onClick={() => onFeed(undefined, "expense")}>
            <span>Расходы</span>
            <strong>{money(summary.expense)}</strong>
          </button>
          <button onClick={() => onFeed(undefined, "expense")}>
            <span>В планах</span>
            <strong>{money(summary.planned)}</strong>
          </button>
          <button
            className="icon-button"
            aria-label="Свернуть доходы"
            onClick={onToggleIncome}
          >
            {state.preferences.incomeVisible ? <ChevronUp /> : <ChevronDown />}
          </button>
        </header>
      )}
      <section
        className="income-band"
        aria-label="Доходы"
        onPointerDown={(event) => {
          startTouch.current = { x: event.clientX, y: event.clientY };
        }}
        onPointerUp={(event) => swipeEnd(event, "income")}
      >
        {state.preferences.incomeVisible ? (
          <>
            <div
              className="income-pages"
              ref={incomeRef}
              onScroll={(event) =>
                setIncomePage(
                  Math.round(
                    event.currentTarget.scrollLeft /
                      event.currentTarget.clientWidth,
                  ),
                )
              }
            >
              {Array.from({ length: incomePages }, (_, page) => (
                <div className="income-page item-grid" key={page}>
                  {incomes.slice(page * 4, page * 4 + 4).map(tile)}
                  {page === incomePages - 1 && addTile("income")}
                </div>
              ))}
            </div>
            {(editing || incomes.length > 4) && (
              <div className="income-page-control">
                {Array.from({ length: incomePages }, (_, page) => (
                  <button
                    key={page}
                    aria-label={`Доходы, страница ${page + 1}`}
                    aria-current={incomePage === page}
                    onClick={() => selectPage("income", page)}
                  >
                    <i />
                  </button>
                ))}
              </div>
            )}
          </>
        ) : (
          <div className="item-grid">{addTile("income")}</div>
        )}
      </section>
      <section
        className="account-band"
        aria-label="Счета"
        onPointerDown={(event) => {
          startTouch.current = { x: event.clientX, y: event.clientY };
        }}
        onPointerUp={(event) => swipeEnd(event, "account")}
      >
        <div
          className={`account-pages ${drag?.kind === "income" ? "targets-active" : ""}`}
          ref={accountRef}
          onScroll={(event) =>
            setAccountPage(
              Math.round(
                event.currentTarget.scrollLeft /
                  event.currentTarget.clientWidth,
              ),
            )
          }
        >
          {Array.from({ length: accountPages }, (_, page) => (
            <div className="account-page item-grid" key={page}>
              {accounts.slice(page * 4, page * 4 + 4).map(tile)}
              {page === accountPages - 1 &&
                accounts.length % 4 !== 0 &&
                addTile("account")}
              {page === accountPages - 1 &&
                accounts.length % 4 === 0 &&
                addTile("account")}
            </div>
          ))}
        </div>
        <div className="account-page-control" aria-label="Страницы счетов">
          {Array.from({ length: accountPages }, (_, page) => (
            <button
              key={page}
              aria-label={`Счета, страница ${page + 1}`}
              aria-current={accountPage === page}
              onClick={() => selectPage("account", page)}
            >
              <i />
            </button>
          ))}
        </div>
      </section>
      <section
        className="expense-band"
        aria-label="Расходы"
        onPointerDown={(event) => {
          startTouch.current = { x: event.clientX, y: event.clientY };
        }}
        onPointerUp={(event) => swipeEnd(event, "expense")}
      >
        <div
          className={`expense-pages ${drag?.kind === "account" ? "targets-active" : ""}`}
          ref={expenseRef}
          onScroll={(event) =>
            setExpensePage(
              Math.round(
                event.currentTarget.scrollLeft /
                  event.currentTarget.clientWidth,
              ),
            )
          }
        >
          {Array.from({ length: expensePages }, (_, page) => (
            <div className="expense-page item-grid" key={page}>
              {expenses.slice(page * 20, page * 20 + 20).map(tile)}
              {page === expensePages - 1 && addTile("expense")}
            </div>
          ))}
        </div>
      </section>
      <footer className="home-footer">
        <div className="page-dots">
          {Array.from({ length: expensePages }, (_, page) => (
            <button
              key={page}
              aria-label={`Расходы, страница ${page + 1}`}
              aria-current={expensePage === page}
              onClick={() => selectPage("expense", page)}
            >
              <i />
            </button>
          ))}
        </div>
        {editing ? (
          <button className="home-edit-done" onClick={onDone}>
            Готово
          </button>
        ) : (
          <button
            className="assistant-fab"
            aria-label="Финансовый помощник"
            onClick={onAssistant}
          >
            <Mic size={20} />
          </button>
        )}
      </footer>
      {drag && (
        <>
          <div className="drag-instruction">
            {drag.kind === "income"
              ? "Перенесите на счет"
              : "Перенесите на расход"}
          </div>
          <div className="drag-ghost" style={{ left: drag.x, top: drag.y }}>
            {drag.name}
          </div>
        </>
      )}
    </div>
  );
}
