import { useEffect, useMemo, useState } from "react";
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
  compactMoney,
  dateLabel,
  entriesForPeriod,
  iconMap,
  money,
  type Entry,
  type FinanceItem,
  type FinanceState,
  type ReportKind,
} from "./data";
import "./feed.css";

interface FeedProps {
  state: FinanceState;
  period: string;
  filterId: string | null;
  initialReport?: ReportKind;
  onFilter: (id: string | null) => void;
  onPeriod: (period: string) => void;
  onBack: () => void;
  onEdit: (id: string) => void;
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
const chartColors = [
  "#e51b51",
  "#ffa742",
  "#f96451",
  "#f6c947",
  "#77748f",
  "#b0cf77",
  "#358c83",
  "#4c89a5",
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

export default function Feed({
  state,
  period,
  filterId,
  initialReport,
  onFilter,
  onPeriod,
  onBack,
  onEdit,
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
  const itemsById = useMemo(
    () => new Map(state.items.map((item) => [item.id, item])),
    [state.items],
  );

  useEffect(() => {
    setReport(defaultReport);
    setShowAll(false);
    setQuery("");
    setFiltersOpen(false);
  }, [filterId, defaultReport]);

  useEffect(() => {
    if (!reportOpen && !filtersOpen) return;
    const previousOverflow = document.body.style.overflow;
    if (reportOpen) document.body.style.overflow = "hidden";
    const close = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setReportOpen(false);
        setFiltersOpen(false);
      }
    };
    window.addEventListener("keydown", close);
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", close);
    };
  }, [reportOpen, filtersOpen]);

  const filteredEntries = state.entries.filter(
    (entry) =>
      !filterId || entry.sourceId === filterId || entry.targetId === filterId,
  );
  const periodEntries = entriesForPeriod(filteredEntries, period);
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
  const matchesQuery = (entry: Entry) =>
    `${itemsById.get(entry.sourceId)?.name} ${itemsById.get(entry.targetId)?.name} ${entry.note} ${entry.tags.join(" ")}`
      .toLowerCase()
      .includes(query.toLowerCase());
  const visibleEntries = periodEntries
    .filter((entry) => matchesReport(entry) && matchesQuery(entry))
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

  return (
    <div className="feed-screen">
      <header className="feed-header">
        <button
          className="icon-button"
          aria-label="На главный экран"
          onClick={onBack}
        >
          <ChevronLeft size={25} />
        </button>
        <div className="feed-filter-box">
          {selectedItem && (
            <button
              className={`feed-filter-chip ${selectedItem.kind}`}
              onClick={() => setFiltersOpen(true)}
            >
              {selectedItem.name}
              <X
                size={14}
                onClick={(event) => {
                  event.stopPropagation();
                  chooseFilter(null);
                }}
              />
            </button>
          )}
          <input
            aria-label="Добавить фильтр"
            placeholder={selectedItem ? "" : "Добавить фильтр"}
            value={query}
            onFocus={() => setFiltersOpen(true)}
            onChange={(event) => {
              setQuery(event.target.value);
              setFiltersOpen(true);
            }}
          />
          {(query || selectedItem) && (
            <button
              className="feed-clear"
              aria-label="Сбросить фильтр"
              onClick={() => {
                setQuery("");
                chooseFilter(null);
              }}
            >
              <X size={12} />
            </button>
          )}
        </div>
        <button
          className="icon-button"
          aria-label="Открыть календарь"
          onClick={onCalendar}
        >
          <CalendarDays size={28} />
        </button>
      </header>
      {filtersOpen && (
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
      {selectedItem && (
        <div className="feed-edit-row">
          <button onClick={() => onEdit(selectedItem.id)}>Изменить</button>
        </div>
      )}
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
                : "#dedee2",
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
                  fill="#ca1b55"
                />
              </>
            ) : (
              <>
                {report !== "expense" && report !== "both" && (
                  <path
                    d={`${linePath("income")} L ${chartWidth} ${chartHeight - 19} L 0 ${chartHeight - 19} Z`}
                    fill="#c91e55"
                    opacity=".95"
                  />
                )}
                {report === "both" && (
                  <path
                    d={linePath("income")}
                    stroke="#08a47b"
                    strokeWidth="3.5"
                    fill="none"
                    strokeLinejoin="round"
                  />
                )}
                {report !== "income" && (
                  <path
                    d={linePath("expense")}
                    stroke={report === "both" ? "#d8313b" : "#c91e55"}
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
            {periods.map((value) => (
              <span key={value}>{shortPeriod(value)}</span>
            ))}
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
      {dates.map((date) => {
        const dayEntries = visibleEntries.filter(
          (entry) => entry.date === date,
        );
        const net = dailyChange(dayEntries);
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
              const tag = [
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
                  <div className="feed-operation-names">
                    <small>{source.name}</small>
                    <strong>{target.name}</strong>
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
                      {positive ? "+ " : negative ? "− " : ""}
                      {money(entry.amount)}
                    </strong>
                    {tag && <small>{tag}</small>}
                  </div>
                </button>
              );
            })}
            <div className="feed-day-total">
              <div>
                <strong>{compactMoney(balanceAt(date))}</strong>
                <span>баланс</span>
              </div>
              <div>
                <strong className={net >= 0 ? "income-text" : "expense-text"}>
                  {net < 0 ? "− " : net > 0 ? "+ " : ""}
                  {money(Math.abs(net))}
                </strong>
                <span>всего</span>
              </div>
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
