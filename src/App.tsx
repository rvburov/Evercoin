import { useCallback, useEffect, useRef, useState } from "react";
import {
  ChevronDown,
  ChevronRight,
  Mail,
  Pencil,
  RefreshCw,
  ScrollText,
  Settings2,
  UserRound,
  Plus,
} from "lucide-react";
import Home from "./Home";
import Feed from "./Feed";
import Settings from "./Settings";
import Profile from "./Profile";
import Assistant from "./Assistant";
import ItemEditor from "./ItemEditor";
import Calendar from "./Calendar";
import OperationComposer from "./OperationComposer";
import {
  accountBalance,
  createInitialState,
  defaultDraft,
  loadState,
  newId,
  saveState,
  type Entry,
  type FinanceItem,
  type FinanceState,
  type ItemKind,
  type OperationDraft,
  type ReportKind,
} from "./data";
import { ActionSheet, ScreenHeader } from "./ui";

type Screen = "home" | "feed" | "settings" | "profile" | "assistant" | "help";
export default function App() {
  const [state, setState] = useState<FinanceState>(loadState);
  const [screen, setScreen] = useState<Screen>("home");
  const [period, setPeriod] = useState("2026-11");
  const [filterId, setFilterId] = useState<string | null>(null);
  const [report, setReport] = useState<ReportKind | undefined>();
  const [menu, setMenu] = useState(false);
  const [profileSwitcher, setProfileSwitcher] = useState(false);
  const [editing, setEditing] = useState(false);
  const [editor, setEditor] = useState<FinanceItem | null>(null);
  const [operation, setOperation] = useState<OperationDraft | null>(null);
  const [editingEntryId, setEditingEntryId] = useState<string | null>(null);
  const [calendar, setCalendar] = useState(false);
  const [pendingDelete, setPendingDelete] = useState<FinanceItem | null>(null);
  const [resetConfirm, setResetConfirm] = useState(false);
  const [toast, setToast] = useState("");
  const saveLock = useRef(false);
  const notify = useCallback((message: string) => setToast(message), []);

  useEffect(() => {
    if (!toast) return;
    const timer = setTimeout(() => setToast(""), 3200);
    return () => clearTimeout(timer);
  }, [toast]);
  useEffect(() => {
    document.documentElement.dataset.theme = "light";
  }, []);
  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if (event.key !== "Escape") return;
      if (calendar) setCalendar(false);
      else if (pendingDelete) setPendingDelete(null);
      else if (resetConfirm) setResetConfirm(false);
      else if (operation) setOperation(null);
      else if (editor) setEditor(null);
      else if (menu) setMenu(false);
      else {
        setScreen("home");
        setEditing(false);
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [calendar, pendingDelete, resetConfirm, operation, editor, menu]);

  function updateState(next: FinanceState) {
    setState(next);
    if (!saveState(next))
      notify("Изменения сохранены до закрытия этой вкладки");
  }
  function navigate(next: Screen) {
    setScreen(next);
    setMenu(false);
    window.scrollTo({ top: 0 });
  }
  function openFeed(id?: string, kind?: "expense" | "income" | "balance") {
    setFilterId(id || null);
    setReport(kind);
    navigate("feed");
  }
  function openOperation(
    values: Partial<OperationDraft> = {},
    entryId: string | null = null,
  ) {
    const fallbackAccount = state.items.find(
      (item) => item.kind === "account" && !item.archived,
    );
    const fallbackExpense = state.items.find(
      (item) => item.kind === "expense" && !item.archived,
    );
    const initial = {
      ...defaultDraft(),
      sourceId: fallbackAccount?.id || "",
      targetId: fallbackExpense?.id || "",
      ...values,
    };
    if (!initial.sourceId || !initial.targetId) {
      notify("Сначала добавьте счет и категорию расхода");
      return;
    }
    setOperation(initial);
    setEditingEntryId(entryId);
    saveLock.current = false;
    setMenu(false);
  }
  function saveOperation(draft: OperationDraft) {
    if (saveLock.current) return;
    saveLock.current = true;
    const entry: Entry = {
      ...draft,
      id: editingEntryId || newId(),
      amount: Math.round(Number(draft.amount.replace(",", ".")) * 100),
    };
    const entries = editingEntryId
      ? state.entries.map((previous) =>
          previous.id === editingEntryId ? entry : previous,
        )
      : [entry, ...state.entries];
    updateState({ ...state, entries });
    setPeriod(entry.date.slice(0, 7));
    setOperation(null);
    setEditingEntryId(null);
    notify(editingEntryId ? "Операция изменена" : "Операция записана");
  }
  function addItem(kind: ItemKind) {
    setEditor({
      id: newId(),
      kind,
      name: "",
      icon:
        kind === "account" ? "wallet" : kind === "expense" ? "cart" : "money",
      opening: 0,
      budget: 0,
      included: true,
      goal: false,
    });
  }
  function saveItem(item: FinanceItem, desiredBalance?: number) {
    const original = state.items.find((previous) => previous.id === item.id);
    const saved = { ...item };
    if (item.kind === "account" && desiredBalance !== undefined)
      saved.opening =
        item.opening + desiredBalance - accountBalance(item, state.entries);
    updateState({
      ...state,
      items: original
        ? state.items.map((previous) =>
            previous.id === item.id ? saved : previous,
          )
        : [...state.items, saved],
    });
    setEditor(null);
    notify("Изменения сохранены");
  }
  function deleteItem(item: FinanceItem) {
    if (!state.items.some((previous) => previous.id === item.id)) {
      setEditor(null);
      return;
    }
    setPendingDelete(item);
  }
  function confirmDelete() {
    if (!pendingDelete) return;
    updateState({
      ...state,
      items: state.items.map((item) =>
        item.id === pendingDelete.id
          ? { ...item, archived: true, included: false }
          : item,
      ),
    });
    setPendingDelete(null);
    setEditor(null);
    notify("Удалено с главного экрана");
  }
  function exportEntries() {
    const blob = new Blob([JSON.stringify(state, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "evercoin-finances.json";
    anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    notify("Данные экспортированы");
  }

  const activeScreen = operation ? (
    <OperationComposer
      key={editingEntryId || "new-operation"}
      state={state}
      initialDraft={operation}
      onSave={saveOperation}
      onClose={() => setOperation(null)}
    />
  ) : editor ? (
    <ItemEditor
      key={editor.id}
      item={editor}
      balance={accountBalance(editor, state.entries)}
      onSave={saveItem}
      onDelete={() => deleteItem(editor)}
      onCancel={() => setEditor(null)}
    />
  ) : (
    <>
      {screen === "home" && (
        <Home
          state={state}
          period={period}
          editing={editing}
          onMenu={() => setMenu(true)}
          onFeed={openFeed}
          onEditor={setEditor}
          onAdd={addItem}
          onRemove={deleteItem}
          onDone={() => setEditing(false)}
          onDraft={openOperation}
          onToggleIncome={() =>
            updateState({
              ...state,
              preferences: {
                ...state.preferences,
                incomeVisible: !state.preferences.incomeVisible,
              },
            })
          }
          onAssistant={() => navigate("assistant")}
          notify={notify}
        />
      )}
      {screen === "feed" && (
        <Feed
          key={`${filterId || "all"}-${report || "default"}`}
          state={state}
          period={period}
          filterId={filterId}
          initialReport={report}
          onFilter={(id) => {
            setFilterId(id);
            setReport(undefined);
          }}
          onPeriod={setPeriod}
          onBack={() => navigate("home")}
          onEdit={(id) => {
            const item = state.items.find((item) => item.id === id);
            if (item) setEditor(item);
          }}
          onSelectEntry={(entry) =>
            openOperation(
              { ...entry, amount: String(entry.amount / 100) },
              entry.id,
            )
          }
          onCalendar={() => setCalendar(true)}
        />
      )}
      {screen === "settings" && (
        <Settings
          preferences={state.preferences}
          onChange={(preferences) => updateState({ ...state, preferences })}
          onBack={() => navigate("home")}
          onExport={exportEntries}
          onReset={() => setResetConfirm(true)}
          notify={notify}
        />
      )}
      {screen === "profile" && (
        <Profile
          profileName={state.profileName}
          onSave={(profileName) => {
            updateState({ ...state, profileName });
            navigate("home");
            notify("Демонстрационный профиль сохранен");
          }}
          onBack={() => navigate("home")}
        />
      )}
      {screen === "assistant" && (
        <Assistant
          state={state}
          period={period}
          onReview={openOperation}
          notify={notify}
          onBack={() => navigate("home")}
        />
      )}
      {screen === "help" && (
        <div className="help-screen">
          <ScreenHeader title="Помощь" onBack={() => navigate("home")} />
          <section>
            <h2>Как записать операцию</h2>
            <p>
              Зажмите источник дохода и перенесите на счет. Чтобы записать
              расход, перенесите счет на категорию. Введите сумму и подтвердите
              галочкой.
            </p>
            <button className="full-button" onClick={() => openOperation()}>
              Добавить операцию
            </button>
            <h2>Как изменить счета и категории</h2>
            <p>
              В меню нажмите карандаш внизу. Выберите значок карандаша у
              категории или счета. Страницы категорий и счетов переключаются
              смахиванием и точками.
            </p>
            <h2>Финансовый помощник</h2>
            <p>
              Значок микрофона открывает помощника. В макете доступны демопример
              голосовой записи и ответы по вашим операциям.
            </p>
            <button
              className="full-button"
              onClick={() => navigate("assistant")}
            >
              Открыть помощника
            </button>
          </section>
        </div>
      )}
    </>
  );
  return (
    <div
      className={`app-shell ${state.preferences.largeFonts ? "large-fonts" : ""} ${menu ? "menu-open" : ""}`}
    >
      <div className="app-content">{activeScreen}</div>
      {menu && (
        <div className="menu-overlay" onClick={() => setMenu(false)}>
          <aside
            className="side-menu"
            aria-label="Меню приложения"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="menu-profile">
              <UserRound />
              <button onClick={() => setProfileSwitcher(!profileSwitcher)}>
                {state.profileName || "Профиль"}
              </button>
              <button
                className="icon-button"
                aria-label="Изменить профиль"
                onClick={() => navigate("profile")}
              >
                <Pencil size={16} />
              </button>
              <button
                className="icon-button"
                aria-label="Показать профили"
                onClick={() => setProfileSwitcher(!profileSwitcher)}
              >
                <ChevronDown size={16} />
              </button>
            </div>
            {profileSwitcher && (
              <div className="profile-switcher">
                <button
                  className="add-profile full-button"
                  onClick={() => navigate("profile")}
                >
                  ДОБАВИТЬ ПРОФИЛЬ
                </button>
              </div>
            )}
            <div className="menu-links">
              <button
                className="menu-row"
                onClick={() => {
                  setFilterId(null);
                  setReport(undefined);
                  navigate("feed");
                }}
              >
                <ScrollText />
                <span>ЛЕНТА</span>
                <ChevronRight />
              </button>
              <button className="menu-row" onClick={() => navigate("settings")}>
                <Settings2 />
                <span>НАСТРОЙКИ</span>
                <ChevronRight />
              </button>
              <button className="menu-row" onClick={() => navigate("help")}>
                <Mail />
                <span>ПОМОЩЬ</span>
                <ChevronRight />
              </button>
            </div>
            <div className="menu-bottom">
              <button
                onClick={() => notify("Демоданные сохранены в этом браузере")}
              >
                <RefreshCw />
                <span>Сегодня, 19:56</span>
              </button>
              <button
                className="icon-button"
                aria-label="Добавить операцию"
                onClick={() => openOperation()}
              >
                <Plus />
              </button>
              <button
                className="icon-button"
                aria-label="Редактировать главный экран"
                onClick={() => {
                  setEditing(true);
                  setMenu(false);
                }}
              >
                <Pencil />
              </button>
            </div>
          </aside>
        </div>
      )}
      {calendar && (
        <Calendar
          selectedDate={`${period}-25`}
          onClose={() => setCalendar(false)}
          onSelect={(date) => {
            setPeriod(date.slice(0, 7));
            setCalendar(false);
          }}
        />
      )}
      {pendingDelete && (
        <ActionSheet
          title={`Удалить «${pendingDelete.name}»?`}
          onClose={() => setPendingDelete(null)}
        >
          <p className="sheet-description">
            Значок будет убран с главного экрана. История операций сохранится.
          </p>
          <button className="sheet-option danger" onClick={confirmDelete}>
            Удалить
          </button>
        </ActionSheet>
      )}
      {resetConfirm && (
        <ActionSheet
          title="Вернуть исходные данные?"
          onClose={() => setResetConfirm(false)}
        >
          <p className="sheet-description">
            Добавленные операции и настройки этого макета будут сброшены.
          </p>
          <button
            className="sheet-option danger"
            onClick={() => {
              updateState(createInitialState());
              setPeriod("2026-11");
              setResetConfirm(false);
              notify("Исходные данные восстановлены");
            }}
          >
            Сбросить
          </button>
        </ActionSheet>
      )}
      {toast && (
        <div className="toast" role="status">
          {toast}
        </div>
      )}
    </div>
  );
}
