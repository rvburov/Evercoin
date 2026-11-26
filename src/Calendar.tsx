import { useEffect, useMemo, useRef, useState } from "react";
import { CalendarDays, Check, ChevronRight, X } from "lucide-react";
import { isValidDate, today, type RepeatRule } from "./data";
import "./calendar.css";

interface CalendarProps {
  selectedDate: string;
  onSelect: (date: string) => void;
  onClose: () => void;
}

function isoDate(year: number, month: number, day: number) {
  return `${year}-${String(month + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
}

export default function Calendar({
  selectedDate,
  onSelect,
  onClose,
}: CalendarProps) {
  const initialDate = isValidDate(selectedDate) ? selectedDate : today;
  const [viewMonth, setViewMonth] = useState(initialDate.slice(0, 7));
  const scrollRef = useRef<HTMLDivElement>(null);
  const selectedMonthRef = useRef<HTMLElement>(null);
  const baseYear = Number(viewMonth.slice(0, 4));
  const months = useMemo(
    () =>
      Array.from({ length: 24 }, (_, index) => {
        const date = new Date(baseYear, index, 1);
        return {
          year: date.getFullYear(),
          month: date.getMonth(),
          key: isoDate(date.getFullYear(), date.getMonth(), 1).slice(0, 7),
        };
      }),
    [baseYear],
  );

  useEffect(() => {
    if (!scrollRef.current || !selectedMonthRef.current) return;
    scrollRef.current.scrollTop =
      selectedMonthRef.current.offsetTop - scrollRef.current.offsetTop;
  }, [viewMonth]);

  return (
    <section
      className="calendar-sheet"
      role="dialog"
      aria-modal="true"
      aria-label="Выберите дату"
    >
      <header className="calendar-toolbar">
        <button
          className="icon-button"
          aria-label="Закрыть календарь"
          onClick={onClose}
        >
          <X />
        </button>
        <label className="calendar-month-jump">
          <CalendarDays size={18} />
          <input
            type="month"
            aria-label="Перейти к месяцу"
            value={viewMonth}
            onChange={(event) => {
              if (event.target.value) setViewMonth(event.target.value);
            }}
          />
        </label>
      </header>
      <div className="calendar-weekdays" aria-hidden="true">
        {["пн", "вт", "ср", "чт", "пт", "сб", "вс"].map((day) => (
          <span key={day}>{day}</span>
        ))}
      </div>
      <div className="calendar-scroll" ref={scrollRef}>
        {months.map(({ year, month, key }) => {
          const firstDay = (new Date(year, month, 1).getDay() + 6) % 7;
          const count = new Date(year, month + 1, 0).getDate();
          return (
            <section
              className="calendar-month"
              key={key}
              ref={key === viewMonth ? selectedMonthRef : undefined}
            >
              <h2>
                {new Intl.DateTimeFormat("ru-RU", {
                  month: "long",
                  year: "numeric",
                })
                  .format(new Date(year, month, 1))
                  .replace(" г.", "")}
              </h2>
              <div className="calendar-days">
                {Array.from({ length: firstDay }, (_, index) => (
                  <span key={`blank-${index}`} />
                ))}
                {Array.from({ length: count }, (_, index) => {
                  const date = isoDate(year, month, index + 1);
                  return (
                    <button
                      key={date}
                      className={`${date === selectedDate ? "is-selected" : ""} ${date === today ? "is-today" : ""}`}
                      aria-label={new Intl.DateTimeFormat("ru-RU", {
                        day: "numeric",
                        month: "long",
                        year: "numeric",
                      }).format(new Date(year, month, index + 1))}
                      aria-pressed={date === selectedDate}
                      onClick={() => onSelect(date)}
                    >
                      {index + 1}
                    </button>
                  );
                })}
              </div>
            </section>
          );
        })}
      </div>
    </section>
  );
}

interface RepeatPickerProps {
  value: RepeatRule | null;
  onSave: (value: RepeatRule | null) => void;
  onClose: () => void;
}

const unitLabels: Record<RepeatRule["unit"], string> = {
  day: "день",
  week: "неделю",
  month: "месяц",
  year: "год",
};
const unitShort: Record<RepeatRule["unit"], string> = {
  day: "День",
  week: "Неделя",
  month: "Месяц",
  year: "Год",
};

export function RepeatPicker({ value, onSave, onClose }: RepeatPickerProps) {
  const [every, setEvery] = useState(value?.every || 1);
  const [unit, setUnit] = useState<RepeatRule["unit"]>(value?.unit || "month");
  const [until, setUntil] = useState(value?.until || "");
  const [dateOpen, setDateOpen] = useState(false);
  const [error, setError] = useState("");
  function save() {
    if (until && !isValidDate(until)) {
      setError("Выберите корректную дату окончания");
      return;
    }
    onSave({ every, unit, until });
  }
  return (
    <section
      className="repeat-sheet"
      role="dialog"
      aria-modal="true"
      aria-labelledby="repeat-title"
    >
      <header className="repeat-header">
        <button
          className="icon-button"
          aria-label="Отменить повторение"
          onClick={onClose}
        >
          <X />
        </button>
        <h1 id="repeat-title">Повторение</h1>
        <button
          className="icon-button"
          aria-label="Сохранить повторение"
          onClick={save}
        >
          <Check />
        </button>
      </header>
      <div className="repeat-summary">
        <span>Повторять каждый</span>
        <strong>
          {every} {unitShort[unit]}
        </strong>
      </div>
      <div className="repeat-wheel" aria-label="Периодичность">
        <label className="repeat-number">
          Количество
          <span className="repeat-wheel-values" aria-hidden="true">
            {[-2, -1, 0, 1, 2].map((offset) => (
              <span key={offset} className={offset === 0 ? "selected" : ""}>
                {every + offset > 0 && every + offset <= 31
                  ? every + offset
                  : "\u00a0"}
              </span>
            ))}
          </span>
          <select
            aria-label="Количество периодов"
            value={every}
            onChange={(event) => setEvery(Number(event.target.value))}
          >
            {Array.from({ length: 31 }, (_, index) => (
              <option key={index + 1} value={index + 1}>
                {index + 1}
              </option>
            ))}
          </select>
        </label>
        <label className="repeat-unit">
          Период
          <span className="repeat-wheel-values" aria-hidden="true">
            {[-2, -1, 0, 1, 2].map((offset) => {
              const options: RepeatRule["unit"][] = [
                "day",
                "week",
                "month",
                "year",
              ];
              const candidate = options[options.indexOf(unit) + offset];
              return (
                <span key={offset} className={offset === 0 ? "selected" : ""}>
                  {candidate ? unitLabels[candidate] : "\u00a0"}
                </span>
              );
            })}
          </span>
          <select
            aria-label="Единица повторения"
            value={unit}
            onChange={(event) =>
              setUnit(event.target.value as RepeatRule["unit"])
            }
          >
            {(["day", "week", "month", "year"] as const).map((value) => (
              <option key={value} value={value}>
                {unitLabels[value]}
              </option>
            ))}
          </select>
        </label>
      </div>
      <button className="repeat-until" onClick={() => setDateOpen(true)}>
        <span>Повторять до</span>
        <span>
          {until
            ? new Date(until + "T12:00:00").toLocaleDateString("ru-RU")
            : "Не выбрано"}
          <ChevronRight size={17} />
        </span>
      </button>
      {dateOpen && (
        <label className="repeat-date-field">
          Дата окончания
          <input
            type="date"
            aria-label="Повторять до даты"
            value={until}
            onChange={(event) => setUntil(event.target.value)}
          />
          <button onClick={() => setDateOpen(false)}>Готово</button>
        </label>
      )}
      {error && (
        <p className="repeat-error" role="alert">
          {error}
        </p>
      )}
      <button className="repeat-none" onClick={() => onSave(null)}>
        Без повторения
      </button>
    </section>
  );
}
