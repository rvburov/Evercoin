import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type CSSProperties,
  type PointerEvent as ReactPointerEvent,
  type ReactNode,
} from "react";
import {
  CalendarDays,
  ChartNoAxesCombined,
  ChartPie,
  Check,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  Plus,
  Minus,
  Search,
  X,
} from "lucide-react";
import {
  accountBalance,
  colorCss,
  compactMoney,
  dateLabel,
  entriesForPeriod,
  iconMap,
  isValidDate,
  money,
  monthLabel,
  today,
  type Entry,
  type FinanceItem,
  type FinanceState,
  type ReportKind,
} from "./data";
import { Icon } from "./ui";
import "./feed.css";

interface FeedProps {
  // feed — операции по дням, stats — графики и отчеты.
  view: "feed" | "stats";
  state: FinanceState;
  period: string;
  filterId: string | null;
  initialReport?: ReportKind;
  onFilter: (id: string | null) => void;
  onPeriod: (period: string) => void;
  onBack: () => void;
  onSelectEntry: (entry: Entry) => void;
  onCalendar: () => void;
}
const reportOptions: Array<{ id: ReportKind; label: string }> = [
  { id: "both", label: "Расходы и доходы" },
  { id: "expense", label: "Расходы" },
  { id: "income", label: "Доходы" },
  { id: "balance", label: "В наличии" },
  { id: "capital", label: "Накопленный капитал" },
];
// Цвета рядов — палитра AI Capper.
const chartColors = [
  "var(--s1)",
  "var(--s2)",
  "var(--s3)",
  "var(--s4)",
  "var(--s5)",
  "var(--s6)",
  "var(--s7)",
  "var(--s8)",
];

function periodBefore(period: string, offset: number): string {
  const date = new Date(period + "-15T12:00:00");
  date.setMonth(date.getMonth() - offset);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`;
}
function shortPeriod(period: string): string {
  return (
    new Intl.DateTimeFormat("ru-RU", { month: "short" })
      .format(new Date(period + "-15T12:00:00"))
      .replace(".", "")
      .toUpperCase() +
    "’" +
    period.slice(2, 4)
  );
}

// Один знак минуса во всей ленте: «−1 223к ₽», «−370 ₽», «+25 000 ₽».
const minus = (text: string) => text.replace("-", "−");
function signed(value: number): string {
  return (value < 0 ? "−" : value > 0 ? "+" : "") + money(Math.abs(value));
}
const capital = (text: string) => text.charAt(0).toUpperCase() + text.slice(1);
function shiftDays(date: string, days: number): string {
  const day = new Date(date + "T12:00:00Z");
  day.setUTCDate(day.getUTCDate() + days);
  return day.toISOString().slice(0, 10);
}
function daysBetween(start: string, end: string): number {
  return Math.round(
    (Date.parse(end + "T12:00:00Z") - Date.parse(start + "T12:00:00Z")) /
      86400000,
  );
}
// Неделя с понедельника.
function weekRange(date: string): [string, string] {
  const shift = (new Date(date + "T12:00:00Z").getUTCDay() + 6) % 7;
  const start = shiftDays(date, -shift);
  return [start, shiftDays(start, 6)];
}
function monthRange(month: string): [string, string] {
  const [year, index] = month.split("-").map(Number);
  const days = new Date(Date.UTC(year, index, 0)).getUTCDate();
  return [month + "-01", `${month}-${String(days).padStart(2, "0")}`];
}
// «9 ноября», «23 – 29 ноября», «10 ноября – 17 декабря»; год — при переходе через год.
function rangeLabel([start, end]: [string, string]): string {
  const format = (date: string, withYear: boolean) =>
    new Intl.DateTimeFormat("ru-RU", {
      day: "numeric",
      month: "long",
      ...(withYear ? { year: "numeric" as const } : {}),
    })
      .format(new Date(date + "T12:00:00"))
      .replace(" г.", "");
  const crossYear = start.slice(0, 4) !== end.slice(0, 4);
  if (start === end) return format(start, false);
  if (start.slice(0, 7) === end.slice(0, 7))
    return `${Number(start.slice(8))} – ${format(end, false)}`;
  return `${format(start, crossYear)} – ${format(end, crossYear)}`;
}
const DATE_TEMPLATE = "дд.мм.гггг";
const dots = (date: string) =>
  `${date.slice(8, 10)}.${date.slice(5, 7)}.${date.slice(0, 4)}`;
function parseDots(text: string): string | null {
  const match = text.match(/^(\d{2})\.(\d{2})\.(\d{4})$/);
  if (!match) return null;
  const value = `${match[3]}-${match[2]}-${match[1]}`;
  return isValidDate(value) ? value : null;
}
// Цифры сами разбиваются точками: 10112026 → 10.11.2026.
function maskDate(text: string): string {
  const digits = text.replace(/\D/g, "").slice(0, 8);
  return [digits.slice(0, 2), digits.slice(2, 4), digits.slice(4)]
    .filter(Boolean)
    .join(".");
}
function operationsWord(count: number): string {
  const last = count % 10;
  const lastTwo = count % 100;
  if (last === 1 && lastTwo !== 11) return "операция";
  if (last >= 2 && last <= 4 && (lastTwo < 12 || lastTwo > 14))
    return "операции";
  return "операций";
}
type Step = "week" | "month" | "year";
const steps: Array<[Step, string]> = [
  ["week", "Неделя"],
  ["month", "Месяц"],
  ["year", "Год"],
];

export default function Feed({
  view,
  state,
  period,
  filterId,
  initialReport,
  onFilter,
  onPeriod,
  onBack,
  onSelectEntry,
  onCalendar,
}: FeedProps) {
  const selectedItem = state.items.find((item) => item.id === filterId);
  const defaultReport: ReportKind =
    initialReport ||
    (selectedItem?.kind === "income"
      ? "income"
      : selectedItem?.kind === "expense"
        ? "expense"
        : selectedItem?.kind === "account"
          ? "balance"
          : "both");
  const [report, setReport] = useState<ReportKind>(defaultReport);
  const [chartMode, setChartMode] = useState<"line" | "donut">("line");
  const [reportOpen, setReportOpen] = useState(false);
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [periodOpen, setPeriodOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [showAll, setShowAll] = useState(false);
  const [showPercent, setShowPercent] = useState(true);
  const [showBudget, setShowBudget] = useState(true);
  const [chartMonths, setChartMonths] = useState(4);
  // Лента: шаг листания плашки, свой период, окна и фильтры поиска.
  const [step, setStep] = useState<Step>("month");
  const [anchor, setAnchor] = useState(today);
  const [custom, setCustom] = useState<[string, string] | null>(null);
  const [sheet, setSheet] = useState<"none" | "period" | "step">("none");
  const [pick, setPick] = useState<{ start: string; end: string | null }>({
    start: "",
    end: null,
  });
  const [calMonth, setCalMonth] = useState(period);
  const [fromText, setFromText] = useState("");
  const [toText, setToText] = useState("");
  const [typeFilter, setTypeFilter] = useState<"all" | "expense" | "income">(
    "all",
  );
  const [amountFrom, setAmountFrom] = useState("");
  const [amountTo, setAmountTo] = useState("");
  const [allCategories, setAllCategories] = useState(false);
  const sheetDrag = useRef<{ y: number; dy: number } | null>(null);
  const [sheetShift, setSheetShift] = useState(0);
  const isFeed = view === "feed";
  const itemsById = useMemo(
    () => new Map(state.items.map((item) => [item.id, item])),
    [state.items],
  );

  useEffect(() => {
    setReport(defaultReport);
    setShowAll(false);
    // В ленте категорию выбирают в панели поиска — панель остается открытой.
    if (view !== "feed") {
      setQuery("");
      setFiltersOpen(false);
    }
  }, [filterId, defaultReport, view]);

  useEffect(() => {
    if (!reportOpen && !filtersOpen && sheet === "none") return;
    const previousOverflow = document.body.style.overflow;
    if (reportOpen || sheet !== "none") document.body.style.overflow = "hidden";
    const close = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setReportOpen(false);
        setFiltersOpen(false);
        setSheet("none");
      }
    };
    window.addEventListener("keydown", close);
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", close);
    };
  }, [reportOpen, filtersOpen, sheet]);

  const filteredEntries = state.entries.filter(
    (entry) =>
      !filterId || entry.sourceId === filterId || entry.targetId === filterId,
  );
  // Отрезок ленты: свой период из календаря, неделя или год, иначе месяц.
  const range: [string, string] | null = !isFeed
    ? null
    : (custom ??
      (step === "week"
        ? weekRange(anchor)
        : step === "year"
          ? [anchor.slice(0, 4) + "-01-01", anchor.slice(0, 4) + "-12-31"]
          : null));
  const periodEntries = range
    ? filteredEntries.filter(
        (entry) => entry.date >= range[0] && entry.date <= range[1],
      )
    : entriesForPeriod(filteredEntries, period);
  const isIncome = (entry: Entry) =>
    itemsById.get(entry.sourceId)?.kind === "income";
  const isExpense = (entry: Entry) =>
    itemsById.get(entry.targetId)?.kind === "expense";
  const sumIncome = (entries: Entry[]) =>
    entries.filter(isIncome).reduce((value, entry) => value + entry.amount, 0);
  const sumExpense = (entries: Entry[]) =>
    entries.filter(isExpense).reduce((value, entry) => value + entry.amount, 0);
  const totalIncome = sumIncome(periodEntries);
  const totalExpense = sumExpense(periodEntries);
  const matchesReport = (entry: Entry) =>
    report === "income"
      ? isIncome(entry)
      : report === "expense"
        ? isExpense(entry)
        : true;
  // Поиск по всей информации операции: категория, счет, заметка, метки,
  // сумма (с пробелами и без), дата и тип.
  const searchText = (entry: Entry) =>
    [
      itemsById.get(entry.sourceId)?.name,
      itemsById.get(entry.targetId)?.name,
      entry.note,
      ...entry.tags,
      money(entry.amount),
      String(entry.amount / 100),
      dateLabel(entry.date),
      isIncome(entry) ? "доход" : isExpense(entry) ? "расход" : "",
    ]
      .join(" ")
      .toLowerCase();
  const matchesQuery = (entry: Entry) => {
    const needle = query.trim().toLowerCase();
    if (!needle) return true;
    const text = searchText(entry);
    return (
      text.includes(needle) ||
      text.replace(/\s/g, "").includes(needle.replace(/\s/g, ""))
    );
  };
  const amountMin =
    Number(amountFrom.replace(/\s/g, "").replace(",", ".")) * 100 || 0;
  const amountMax =
    Number(amountTo.replace(/\s/g, "").replace(",", ".")) * 100 || Infinity;
  const matchesSearch = (entry: Entry) =>
    (typeFilter === "all" ||
      (typeFilter === "income" ? isIncome(entry) : isExpense(entry))) &&
    entry.amount >= amountMin &&
    entry.amount <= amountMax;
  const visibleEntries = periodEntries
    .filter(
      (entry) =>
        matchesReport(entry) && matchesQuery(entry) && matchesSearch(entry),
    )
    .sort((left, right) => right.date.localeCompare(left.date));
  const dates = [...new Set(visibleEntries.map((entry) => entry.date))];
  const accountItems =
    selectedItem?.kind === "account"
      ? [selectedItem]
      : state.items.filter((item) => item.kind === "account" && item.included);
  function balanceAt(date: string): number {
    const entries = state.entries.filter((entry) => entry.date <= date);
    return accountItems.reduce(
      (value, item) => value + accountBalance(item, entries),
      0,
    );
  }
  const endDate = period + "-31";
  const periods = Array.from({ length: chartMonths }, (_, index) =>
    periodBefore(period, chartMonths - index - 1),
  );
  // Больше шести подписей месяцев не помещается в ширину телефона.
  const monthLabelStep = Math.ceil(periods.length / 6);
  const currentBalance =
    (report === "balance" || report === "capital") && !showBudget
      ? Math.round(
          periods.reduce(
            (total, month) => total + balanceAt(month + "-31"),
            0,
          ) / periods.length,
        )
      : balanceAt(endDate);
  const totalValue =
    report === "income"
      ? totalIncome
      : report === "expense"
        ? totalExpense
        : currentBalance;
  const categoryKind = report === "income" ? "income" : "expense";
  const breakdown = state.items
    .filter((item) => item.kind === categoryKind)
    .map((item) => ({
      item,
      amount: periodEntries
        .filter((entry) =>
          categoryKind === "income"
            ? entry.sourceId === item.id
            : entry.targetId === item.id,
        )
        .reduce((value, entry) => value + entry.amount, 0),
    }))
    .filter((row) => row.amount > 0)
    .sort((left, right) => right.amount - left.amount);
  const breakdownTotal = breakdown.reduce(
    (value, row) => value + row.amount,
    0,
  );
  let angle = 0;
  const donutStops = breakdown.map((row, index) => {
    const from = angle;
    angle += breakdownTotal ? (row.amount / breakdownTotal) * 100 : 0;
    return `${chartColors[index % chartColors.length]} ${from}% ${angle}%`;
  });
  const chartPoints = periods.map((value) => {
    const entries = entriesForPeriod(filteredEntries, value);
    return {
      period: value,
      income: sumIncome(entries),
      expense: sumExpense(entries),
      balance: balanceAt(value + "-31"),
    };
  });
  const values = chartPoints.flatMap((point) =>
    report === "both"
      ? [point.income, point.expense]
      : [
          report === "income"
            ? point.income
            : report === "expense"
              ? point.expense
              : point.balance,
        ],
  );
  const maxValue = Math.max(100, ...values.map(Math.abs));
  const negativeChart =
    (report === "balance" || report === "capital") && currentBalance < 0;
  const chartHeight = 170;
  const chartWidth = 360;
  const yFor = (value: number) =>
    negativeChart
      ? 18 + (Math.abs(value) / maxValue) * (chartHeight - 38)
      : chartHeight - 19 - (Math.max(0, value) / maxValue) * (chartHeight - 38);
  function linePath(key: "income" | "expense" | "balance"): string {
    return chartPoints
      .map(
        (point, index) =>
          `${index ? "L" : "M"} ${(index * chartWidth) / Math.max(1, chartPoints.length - 1)} ${yFor(point[key])}`,
      )
      .join(" ");
  }
  function chooseFilter(item: FinanceItem | null) {
    onFilter(item?.id || null);
    setFiltersOpen(false);
    setQuery("");
  }
  function dailyChange(entries: Entry[]): number {
    if (selectedItem?.kind === "account") {
      return entries.reduce(
        (value, entry) =>
          value +
          (entry.targetId === selectedItem.id ? entry.amount : 0) -
          (entry.sourceId === selectedItem.id ? entry.amount : 0),
        0,
      );
    }
    return sumIncome(entries) - sumExpense(entries);
  }
  function toggleChart() {
    if (report !== "income" && report !== "expense") setReport("expense");
    setChartMode(chartMode === "line" ? "donut" : "line");
  }

  // ----- Плашка: период и шаг листания -----
  const periodName = capital(monthLabel(period));
  const weekAnchor =
    step === "week"
      ? anchor
      : period === today.slice(0, 7)
        ? today
        : period + "-01";
  const plateTitle = custom
    ? rangeLabel(custom)
    : step === "week"
      ? rangeLabel(weekRange(anchor))
      : step === "year"
        ? anchor.slice(0, 4) + " год"
        : periodName;
  // Серым в окне «Листать по» — то, что появится в плашке.
  const stepValues: Record<Step, string> = {
    week: rangeLabel(weekRange(weekAnchor)),
    month:
      step === "month" || custom
        ? periodName
        : capital(monthLabel(anchor.slice(0, 7))),
    year: (step === "year" ? anchor.slice(0, 4) : period.slice(0, 4)) + " год",
  };
  const arrowLabels = custom
    ? ["Предыдущий отрезок", "Следующий отрезок"]
    : step === "week"
      ? ["Предыдущая неделя", "Следующая неделя"]
      : step === "year"
        ? ["Предыдущий год", "Следующий год"]
        : ["Предыдущий месяц", "Следующий месяц"];
  // Стрелки листают выбранный шаг, свой период сдвигается на свою длину.
  function shiftPeriod(direction: 1 | -1) {
    if (custom) {
      const length = daysBetween(custom[0], custom[1]) + 1;
      setCustom([
        shiftDays(custom[0], direction * length),
        shiftDays(custom[1], direction * length),
      ]);
    } else if (step === "week") setAnchor(shiftDays(anchor, direction * 7));
    else if (step === "year")
      setAnchor(String(Number(anchor.slice(0, 4)) + direction) + anchor.slice(4));
    else onPeriod(periodBefore(period, -direction));
  }
  function chooseStep(next: Step) {
    if (next === "week") setAnchor(weekAnchor);
    if (next === "year" && step !== "year") setAnchor(period + "-01");
    if (next === "month" && (step !== "month" || custom))
      onPeriod((custom ? custom[0] : anchor).slice(0, 7));
    setStep(next);
    setCustom(null);
    setSheet("none");
  }

  // ----- Окно «Период»: календарь и поля дат -----
  function setPickRange(start: string, end: string | null) {
    setPick({ start, end });
    setFromText(start ? dots(start) : "");
    setToText(end ? dots(end) : "");
  }
  function openPeriod() {
    const current = range ?? monthRange(period);
    setPickRange(current[0], current[1]);
    setCalMonth(
      current[0] <= today && today <= current[1]
        ? today.slice(0, 7)
        : current[0].slice(0, 7),
    );
    setSheet("period");
  }
  // Первое нажатие — начало, второе — конец; то же число дважды — один день.
  function tapDay(value: string) {
    if (!pick.start || pick.end) setPickRange(value, null);
    else if (value < pick.start) setPickRange(value, pick.start);
    else setPickRange(pick.start, value);
  }
  function typeFrom(text: string) {
    const masked = maskDate(text);
    setFromText(masked);
    const value = parseDots(masked);
    if (!value) return;
    setPick((previous) => ({
      start: value,
      end: previous.end && previous.end >= value ? previous.end : null,
    }));
    setCalMonth(value.slice(0, 7));
  }
  function typeTo(text: string) {
    const masked = maskDate(text);
    setToText(masked);
    const value = parseDots(masked);
    if (value && pick.start && value >= pick.start)
      setPick((previous) => ({ ...previous, end: value }));
  }
  function applyPick() {
    if (!pick.start || !pick.end) return;
    const month = pick.start.slice(0, 7);
    const whole = monthRange(month);
    if (pick.start === whole[0] && pick.end === whole[1]) {
      onPeriod(month);
      setStep("month");
      setCustom(null);
    } else setCustom([pick.start, pick.end]);
    setSheet("none");
  }
  // Окно закрывается свайпом вниз за верхнюю часть или нажатием вне окна.
  const sheetStyle: CSSProperties | undefined = sheetShift
    ? { transform: `translateY(${sheetShift}px)`, transition: "none" }
    : undefined;
  const sheetSwipe = {
    onPointerDown(event: ReactPointerEvent<HTMLDivElement>) {
      if ((event.target as HTMLElement).closest("button, input, label")) return;
      sheetDrag.current = { y: event.clientY, dy: 0 };
      event.currentTarget.setPointerCapture(event.pointerId);
    },
    onPointerMove(event: ReactPointerEvent<HTMLDivElement>) {
      if (!sheetDrag.current) return;
      sheetDrag.current.dy = Math.max(0, event.clientY - sheetDrag.current.y);
      setSheetShift(sheetDrag.current.dy);
    },
    onPointerUp() {
      const shift = sheetDrag.current?.dy || 0;
      sheetDrag.current = null;
      setSheetShift(0);
      if (shift > 80) setSheet("none");
    },
    onPointerCancel() {
      sheetDrag.current = null;
      setSheetShift(0);
    },
  };
  // Поле даты: точки шаблона видны сразу, цифры встают на место букв.
  function dateField(
    id: string,
    label: string,
    text: string,
    onText: (value: string) => void,
    next: boolean,
  ) {
    return (
      <label className={`feed-date ${next ? "is-next" : ""}`}>
        <span className="feed-date-box">
          <span className="feed-date-size" aria-hidden="true">
            00.00.0000
          </span>
          <span className="feed-date-ghost" aria-hidden="true">
            <span>{text}</span>
            {DATE_TEMPLATE.slice(text.length)}
          </span>
          <input
            id={id}
            aria-label={label}
            inputMode="numeric"
            autoComplete="off"
            value={text}
            onChange={(event) => onText(event.target.value)}
          />
        </span>
      </label>
    );
  }
  function periodSheet() {
    const [year, month] = calMonth.split("-").map(Number);
    const days = new Date(Date.UTC(year, month, 0)).getUTCDate();
    const offset = (new Date(Date.UTC(year, month - 1, 1)).getUTCDay() + 6) % 7;
    const last = pick.end || pick.start;
    const cells: ReactNode[] = [];
    for (let index = 0; index < offset; index++)
      cells.push(<span key={"empty" + index} className="feed-cal-day" />);
    for (let day = 1; day <= days; day++) {
      const column = (offset + day - 1) % 7;
      const value = `${calMonth}-${String(day).padStart(2, "0")}`;
      const inside = !!pick.start && value >= pick.start && value <= last;
      cells.push(
        <button
          key={day}
          type="button"
          aria-label={dots(value)}
          aria-pressed={inside}
          onClick={() => tapDay(value)}
          className={[
            "feed-cal-day",
            inside ? "in" : "",
            value === pick.start ? "start" : "",
            value === last ? "end" : "",
            column === 0 ? "row-start" : "",
            column === 6 ? "row-end" : "",
            value === today ? "today" : "",
            inside && day === days && value < last ? "cont-right" : "",
            inside && day === 1 && value > pick.start ? "cont-left" : "",
          ].join(" ")}
        >
          <b>{day}</b>
        </button>,
      );
    }
    return (
      <>
        <div className="feed-cal-nav">
          <button
            aria-label="Предыдущий месяц"
            onClick={() => setCalMonth(periodBefore(calMonth, 1))}
          >
            <ChevronLeft size={22} />
          </button>
          <strong>{capital(monthLabel(calMonth))}</strong>
          <button
            aria-label="Следующий месяц"
            onClick={() => setCalMonth(periodBefore(calMonth, -1))}
          >
            <ChevronRight size={22} />
          </button>
        </div>
        <div className="feed-cal-grid">
          {["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"].map((label) => (
            <span key={label} className="feed-cal-weekday">
              {label}
            </span>
          ))}
          {cells}
        </div>
        <div className="feed-dates">
          {dateField("period-from", "Начало периода", fromText, typeFrom, false)}
          <span aria-hidden="true">–</span>
          {dateField(
            "period-to",
            "Конец периода",
            toText,
            typeTo,
            !!pick.start && !pick.end,
          )}
        </div>
        <button
          className="feed-sheet-primary"
          disabled={!pick.end}
          onClick={applyPick}
        >
          {pick.end
            ? "Показать " + rangeLabel([pick.start, pick.end])
            : "Выберите конец периода"}
        </button>
      </>
    );
  }
  function renderSheet() {
    if (sheet === "none") return null;
    const title = sheet === "period" ? "Период" : "Листать по";
    return (
      <div className="feed-sheet-backdrop" onClick={() => setSheet("none")}>
        <div
          className="feed-sheet"
          role="dialog"
          aria-modal="true"
          aria-label={title}
          style={sheetStyle}
          {...sheetSwipe}
          onClick={(event) => event.stopPropagation()}
        >
          <div className="feed-sheet-grip" />
          <h2 className="feed-sheet-title">{title}</h2>
          {sheet === "period" ? (
            periodSheet()
          ) : (
            <div className="feed-steps">
              {steps.map(([id, label]) => (
                <button
                  key={id}
                  role="radio"
                  aria-checked={!custom && step === id}
                  className={!custom && step === id ? "is-on" : ""}
                  onClick={() => chooseStep(id)}
                >
                  <span className="feed-step-radio" />
                  <span>
                    <strong>{label}</strong>
                    <small>{stepValues[id]}</small>
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }

  // ----- Панель поиска: тип, категория, счет, сумма -----
  const needle = query.trim().toLowerCase();
  const searchRows = (kind: FinanceItem["kind"]) =>
    state.items
      .filter(
        (item) =>
          item.kind === kind &&
          !item.archived &&
          item.name.toLowerCase().includes(needle),
      )
      .map((item) => ({
        item,
        count: periodEntries.filter(
          (entry) => entry.sourceId === item.id || entry.targetId === item.id,
        ).length,
      }))
      .sort((left, right) => right.count - left.count);
  function searchChip({ item }: { item: FinanceItem }) {
    return (
      <button
        key={item.id}
        className={`feed-search-chip ${item.id === filterId ? "is-on" : ""}`}
        style={{ "--chip": colorCss(item.color) } as CSSProperties}
        aria-pressed={item.id === filterId}
        onClick={() => onFilter(item.id === filterId ? null : item.id)}
      >
        <i aria-hidden="true" />
        {item.name}
      </button>
    );
  }
  function renderSearchPanel() {
    const categories = searchRows("expense");
    const accounts = searchRows("account");
    const shown = allCategories
      ? categories
      : categories.filter((row) => row.count > 0).slice(0, 8);
    const hidden = categories.length - shown.length;
    const found = visibleEntries.length;
    return (
      <div className="feed-search" role="dialog" aria-label="Поиск и фильтр">
        <p className="feed-search-label">Тип</p>
        <div className="feed-search-types" role="radiogroup" aria-label="Тип">
          {(
            [
              ["all", "Все"],
              ["expense", "Расходы"],
              ["income", "Доходы"],
            ] as const
          ).map(([id, label]) => (
            <button
              key={id}
              role="radio"
              aria-checked={typeFilter === id}
              className={typeFilter === id ? "is-on" : ""}
              onClick={() => setTypeFilter(id)}
            >
              {label}
            </button>
          ))}
        </div>
        <p className="feed-search-label">Категория</p>
        <div className="feed-search-chips">
          {shown.map(searchChip)}
          {hidden > 0 && (
            <button
              className="feed-search-chip is-more"
              onClick={() => setAllCategories(true)}
            >
              Еще {hidden}
            </button>
          )}
          {!categories.length && (
            <span className="feed-search-empty">Нет таких категорий</span>
          )}
        </div>
        {accounts.length > 0 && (
          <>
            <p className="feed-search-label">Счет</p>
            <div className="feed-search-chips">{accounts.map(searchChip)}</div>
          </>
        )}
        <p className="feed-search-label">Сумма, ₽</p>
        <div className="feed-search-amounts">
          <input
            id="amount-from"
            aria-label="Сумма от"
            inputMode="decimal"
            placeholder="от"
            value={amountFrom}
            onChange={(event) => setAmountFrom(event.target.value)}
          />
          <span aria-hidden="true">–</span>
          <input
            id="amount-to"
            aria-label="Сумма до"
            inputMode="decimal"
            placeholder="до"
            value={amountTo}
            onChange={(event) => setAmountTo(event.target.value)}
          />
        </div>
        <div className="feed-search-actions">
          <button
            className="feed-search-reset"
            onClick={() => {
              setTypeFilter("all");
              setAmountFrom("");
              setAmountTo("");
              setQuery("");
              setAllCategories(false);
              onFilter(null);
            }}
          >
            Сбросить
          </button>
          <button
            className="feed-search-apply"
            onClick={() => setFiltersOpen(false)}
          >
            Показать {found} {operationsWord(found)}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`feed-screen view-${view}`}>
      {isFeed && (
        <div className="feed-plate">
          <div className="feed-plate-row">
            <button aria-label={arrowLabels[0]} onClick={() => shiftPeriod(-1)}>
              <ChevronLeft size={22} />
            </button>
            <button
              className="feed-plate-title"
              aria-haspopup="dialog"
              onClick={() => setSheet("step")}
            >
              {plateTitle}
            </button>
            <button aria-label={arrowLabels[1]} onClick={() => shiftPeriod(1)}>
              <ChevronRight size={22} />
            </button>
          </div>
          <div className="feed-plate-sums">
            <div>
              <small>Доходы</small>
              <b>{signed(totalIncome)}</b>
            </div>
            <div>
              <small>Расходы</small>
              <b>{signed(-totalExpense)}</b>
            </div>
            <div>
              <small>Итого</small>
              <b>{signed(totalIncome - totalExpense)}</b>
            </div>
          </div>
        </div>
      )}
      <header className="feed-header">
        {!isFeed && (
          <button
            className="icon-button"
            aria-label="На главный экран"
            onClick={onBack}
          >
            <ChevronLeft size={25} />
          </button>
        )}
        <div className="feed-filter-box">
          <Search size={16} className="feed-search-icon" aria-hidden="true" />
          {selectedItem && (
            <button
              className="feed-filter-chip"
              style={{ "--chip": colorCss(selectedItem.color) } as CSSProperties}
              onClick={() => setFiltersOpen(true)}
            >
              <span className="feed-chip-dot" aria-hidden="true">
                <Icon name={selectedItem.icon} size={12} />
              </span>
              <span className="feed-chip-name">{selectedItem.name}</span>
              <X
                size={14}
                aria-label="Убрать фильтр"
                onClick={(event) => {
                  event.stopPropagation();
                  chooseFilter(null);
                }}
              />
            </button>
          )}
          <input
            aria-label={isFeed ? "Поиск и фильтр" : "Добавить фильтр"}
            placeholder={
              selectedItem ? "" : isFeed ? "Поиск и фильтр" : "Добавить фильтр"
            }
            value={query}
            onFocus={() => setFiltersOpen(true)}
            onChange={(event) => {
              setQuery(event.target.value);
              setFiltersOpen(true);
            }}
          />
          {query && (
            <button
              className="feed-clear"
              aria-label="Очистить поиск"
              onClick={() => setQuery("")}
            >
              <X size={12} />
            </button>
          )}
        </div>
        <button
          className="icon-button"
          aria-label={isFeed ? "Выбрать период" : "Открыть календарь"}
          onClick={isFeed ? openPeriod : onCalendar}
        >
          <CalendarDays size={28} />
        </button>
        {isFeed && filtersOpen && renderSearchPanel()}
      </header>
      {isFeed && filtersOpen && (
        <div
          className="feed-search-dim"
          onClick={() => setFiltersOpen(false)}
        />
      )}
      {!isFeed && filtersOpen && (
        <div className="feed-filter-panel">
          <div className="feed-filter-panel-head">
            <Search size={16} />
            <span>Категория или счет</span>
            <button
              className="icon-button"
              aria-label="Закрыть фильтры"
              onClick={() => setFiltersOpen(false)}
            >
              <X size={18} />
            </button>
          </div>
          <button
            className="feed-filter-option"
            onClick={() => chooseFilter(null)}
          >
            Все операции{!filterId && <Check size={16} />}
          </button>
          {state.items
            .filter((item) =>
              item.name.toLowerCase().includes(query.toLowerCase()),
            )
            .map((item) => {
              const ItemIcon = iconMap[item.icon];
              return (
                <button
                  key={item.id}
                  className="feed-filter-option"
                  onClick={() => chooseFilter(item)}
                >
                  <ItemIcon size={18} />
                  <span>{item.name}</span>
                  {item.id === filterId && <Check size={16} />}
                </button>
              );
            })}
        </div>
      )}
      {view === "stats" && (
        <>
          <div className="feed-report-heading">
            <button onClick={() => setReportOpen(true)}>
              {reportOptions.find((option) => option.id === report)!.label}
              <ChevronDown size={15} />
            </button>
            <button
              className="icon-button"
              aria-label={
                chartMode === "line" ? "Круговая диаграмма" : "Линейный график"
              }
              onClick={toggleChart}
            >
              {chartMode === "line" ? (
                <ChartPie size={27} />
              ) : (
                <ChartNoAxesCombined size={27} />
              )}
            </button>
          </div>
          {chartMode === "donut" &&
          (report === "income" || report === "expense") ? (
            <div className="feed-donut-region">
              <div
                className="feed-donut"
                role="img"
                aria-label={`${report === "income" ? "Доходы" : "Расходы"} ${money(breakdownTotal)}. Подробности ниже.`}
                style={{
                  background: breakdownTotal
                    ? `conic-gradient(${donutStops.join(",")})`
                    : "var(--surface-3)",
                }}
              >
                <div>
                  <span>{shortPeriod(period)}</span>
                  <strong>{money(breakdownTotal)}</strong>
                </div>
              </div>
              <div className="feed-donut-labels">
                {breakdown.slice(0, 4).map((row, index) => (
                  <span key={row.item.id} style={{ color: chartColors[index] }}>
                    {Math.round((row.amount / breakdownTotal) * 100)}%
                  </span>
                ))}
              </div>
            </div>
          ) : (
            <div className="feed-line-region">
              <div className="feed-chart-ticks">
                {[4, 3, 2, 1, 0].map((tick, index) => (
                  <span key={tick}>
                    {money(((negativeChart ? -index : tick) * maxValue) / 4)}
                  </span>
                ))}
              </div>
              <svg
                className="feed-line-chart"
                viewBox={`0 0 ${chartWidth} ${chartHeight}`}
                preserveAspectRatio="none"
                role="img"
                aria-label={`График за ${chartMonths} месяца. ${report === "both" ? `Расходы ${money(totalExpense)}, доходы ${money(totalIncome)}` : money(totalValue)}`}
              >
                {[0, 1, 2, 3, 4].map((value) => (
                  <line
                    key={value}
                    x1="0"
                    x2={chartWidth}
                    y1={18 + (value * (chartHeight - 37)) / 4}
                    y2={18 + (value * (chartHeight - 37)) / 4}
                    className="feed-gridline"
                  />
                ))}
                {report === "balance" || report === "capital" ? (
                  <>
                    <line
                      x1={chartWidth / 2}
                      x2={chartWidth / 2}
                      y1="0"
                      y2={chartHeight}
                      className="feed-axis"
                    />
                    <rect
                      x={chartWidth / 2 - 52}
                      width="51"
                      y={negativeChart ? 18 : yFor(currentBalance)}
                      height={Math.max(
                        1,
                        Math.abs(
                          yFor(currentBalance) -
                            (negativeChart ? 18 : chartHeight - 19),
                        ),
                      )}
                      style={{ fill: "var(--account)" }}
                    />
                  </>
                ) : (
                  <>
                    {report !== "expense" && report !== "both" && (
                      <path
                        d={`${linePath("income")} L ${chartWidth} ${chartHeight - 19} L 0 ${chartHeight - 19} Z`}
                        style={{ fill: "var(--good)" }}
                        opacity=".9"
                      />
                    )}
                    {report === "both" && (
                      <path
                        d={linePath("income")}
                        style={{ stroke: "var(--good)" }}
                        strokeWidth="3.5"
                        fill="none"
                        strokeLinejoin="round"
                      />
                    )}
                    {report !== "income" && (
                      <path
                        d={linePath("expense")}
                        style={{ stroke: "var(--bad)" }}
                        strokeWidth="3.5"
                        fill="none"
                        strokeLinejoin="round"
                      />
                    )}
                  </>
                )}
              </svg>
              <div className="feed-chart-zoom">
                <button
                  aria-label="Увеличить график"
                  disabled={chartMonths <= 2}
                  onClick={() => setChartMonths((value) => Math.max(2, value - 1))}
                >
                  <Plus size={20} />
                </button>
                <button
                  aria-label="Уменьшить график"
                  disabled={chartMonths >= 12}
                  onClick={() => setChartMonths((value) => Math.min(12, value + 1))}
                >
                  <Minus size={20} />
                </button>
              </div>
              <div className="feed-chart-months">
                {periods.map((value, index) =>
                  (periods.length - 1 - index) % monthLabelStep === 0 ? (
                    <span key={value}>{shortPeriod(value)}</span>
                  ) : null,
                )}
              </div>
            </div>
          )}
          <div className="feed-chart-controls">
            {(report === "income" || report === "expense") && (
              <button
                onClick={() => {
                  setShowAll(!showAll);
                }}
              >
                категории
              </button>
            )}
            <button
              onClick={() =>
                chartMode === "donut"
                  ? setShowPercent(!showPercent)
                  : setShowBudget(!showBudget)
              }
            >
              {chartMode === "donut"
                ? showPercent
                  ? "проценты"
                  : "суммы"
                : report === "balance" || report === "capital"
                  ? showBudget
                    ? "среднее"
                    : "остаток"
                  : showBudget
                    ? "бюджет"
                    : "без бюджета"}
            </button>
            <button onClick={() => setPeriodOpen(!periodOpen)}>ваш период</button>
          </div>
          {periodOpen && (
            <label className="feed-period-input">
              Выберите месяц
              <input
                aria-label="Месяц отчета"
                type="month"
                value={period}
                onChange={(event) => {
                  if (event.target.value) onPeriod(event.target.value);
                }}
              />
            </label>
          )}
          <button className="feed-show-all" onClick={() => setShowAll(!showAll)}>
            {showAll ? "Свернуть" : "Показать все"}
            <ChevronDown size={18} className={showAll ? "up" : ""} />
          </button>
          {report === "both" ? (
            <div className="feed-summary">
              <button
                onClick={() => {
                  setReport("expense");
                }}
              >
                <span className="expense-text">Расходы</span>
                <ChevronRight size={18} />
                <small>
                  {showBudget
                    ? money(
                        state.items
                          .filter((item) => item.kind === "expense")
                          .reduce((value, item) => value + item.budget, 0),
                      )
                    : ""}
                </small>
                <strong>{money(totalExpense)}</strong>
              </button>
              <button
                onClick={() => {
                  setReport("income");
                }}
              >
                <span className="income-text">Доходы</span>
                <ChevronRight size={18} />
                <small>
                  {showBudget
                    ? money(
                        state.items
                          .filter((item) => item.kind === "income")
                          .reduce((value, item) => value + item.budget, 0),
                      )
                    : ""}
                </small>
                <strong>{money(totalIncome)}</strong>
              </button>
            </div>
          ) : (
            <div className="feed-total-row">
              <span>ВСЕГО</span>
              <small>
                {chartMode === "donut" && showPercent
                  ? "100%"
                  : report === "balance" || report === "capital"
                    ? money(currentBalance)
                    : showBudget && selectedItem
                      ? money(selectedItem.budget)
                      : ""}
              </small>
              <strong>{money(totalValue)}</strong>
            </div>
          )}
          {showAll && (
            <div className="feed-breakdown">
              {breakdown.map((row, index) => (
                <button key={row.item.id} onClick={() => chooseFilter(row.item)}>
                  <i
                    style={{ background: chartColors[index % chartColors.length] }}
                  />
                  <span>{row.item.name}</span>
                  <small>
                    {showPercent && breakdownTotal
                      ? `${Math.round((row.amount / breakdownTotal) * 100)}%`
                      : ""}
                  </small>
                  <strong>{money(row.amount)}</strong>
                </button>
              ))}
            </div>
          )}
        </>
      )}
      {view === "feed" && (
        <>
          {dates.map((date) => {
            const dayEntries = visibleEntries.filter(
              (entry) => entry.date === date,
            );
            const net = dailyChange(dayEntries);
            const dayIncome = sumIncome(dayEntries);
            const dayExpense = sumExpense(dayEntries);
            return (
              <section className="feed-day" key={date}>
                <h2>{dateLabel(date)}</h2>
                {dayEntries.map((entry) => {
                  const source = itemsById.get(entry.sourceId)!;
                  const target = itemsById.get(entry.targetId)!;
                  const positive =
                    isIncome(entry) ||
                    (selectedItem?.kind === "account" &&
                      entry.targetId === selectedItem.id);
                  const negative =
                    isExpense(entry) ||
                    (selectedItem?.kind === "account" &&
                      entry.sourceId === selectedItem.id);
                  // Крупно — на что или откуда деньги, мелко — счет.
                  const main = isIncome(entry) ? source : target;
                  const via = isIncome(entry) ? target : source;
                  const meta = [
                    ...entry.tags.map((value) => "#" + value),
                    entry.note,
                  ]
                    .filter(Boolean)
                    .join(" · ");
                  return (
                    <button
                      key={entry.id}
                      className="feed-operation"
                      onClick={() => onSelectEntry(entry)}
                    >
                      <span
                        className={`feed-op-icon is-${main.kind}`}
                        aria-hidden="true"
                      >
                        <Icon name={main.icon} size={20} />
                      </span>
                      <div className="feed-operation-names">
                        <strong>{main.name}</strong>
                        <small>{via.name}</small>
                      </div>
                      <div className="feed-operation-values">
                        <strong
                          className={
                            positive
                              ? "income-text"
                              : negative
                                ? "expense-text"
                                : ""
                          }
                        >
                          {positive ? "+" : negative ? "−" : ""}
                          {money(entry.amount)}
                        </strong>
                        {meta && <small>{meta}</small>}
                      </div>
                    </button>
                  );
                })}
                <div className="feed-day-total">
                  <span>
                    <small>Баланс</small>
                    <b className="balance-text">
                      {minus(compactMoney(balanceAt(date)))}
                    </b>
                  </span>
                  <span>
                    <small>Доход</small>
                    <b className={dayIncome ? "income-text" : "zero-text"}>
                      {signed(dayIncome)}
                    </b>
                  </span>
                  <span>
                    <small>Расход</small>
                    <b className={dayExpense ? "expense-text" : "zero-text"}>
                      {signed(-dayExpense)}
                    </b>
                  </span>
                  <span>
                    <small>Итог дня</small>
                    <b
                      className={
                        net > 0
                          ? "income-text"
                          : net < 0
                            ? "expense-text"
                            : "zero-text"
                      }
                    >
                      {signed(net)}
                    </b>
                  </span>
                </div>
              </section>
            );
          })}
          {!visibleEntries.length && (
            <p className="feed-empty">За этот период операций нет</p>
          )}
          {state.preferences.news && (
            <section className="feed-news">
              <h3>Новости Evercoin</h3>
              <p>
                Все операции под рукой. Записывайте расходы сразу после покупки.
              </p>
            </section>
          )}
        </>
      )}
      {isFeed && renderSheet()}
      {reportOpen && (
        <div
          className="report-sheet"
          role="dialog"
          aria-modal="true"
          aria-label="Вид отчета"
          onClick={() => setReportOpen(false)}
        >
          <div onClick={(event) => event.stopPropagation()}>
            <div className="report-sheet-options">
              {reportOptions.map((option) => (
                <button
                  key={option.id}
                  onClick={() => {
                    setReport(option.id);
                    if (
                      option.id === "both" ||
                      option.id === "balance" ||
                      option.id === "capital"
                    )
                      setChartMode("line");
                    setReportOpen(false);
                  }}
                >
                  {option.label}
                </button>
              ))}
            </div>
            <button
              className="report-sheet-cancel"
              onClick={() => setReportOpen(false)}
            >
              Отмена
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
