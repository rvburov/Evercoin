import { useState, type ReactNode } from "react";
import {
  ArrowDownToLine,
  ArrowRight,
  Bell,
  CalendarDays,
  ChevronLeft,
  ChevronRight,
  Clock3,
  Coins,
  KeyRound,
  MessageCircle,
  Palette,
  PiggyBank,
  Radio,
  RefreshCw,
  RotateCcw,
  ScrollText,
  Timer,
  Type,
  Volume2,
  X,
} from "lucide-react";
import type { Preferences } from "./data";
import "./settings.css";

interface SettingsProps {
  preferences: Preferences;
  onChange: (preferences: Preferences) => void;
  onBack: () => void;
  onExport: () => void;
  onReset: () => void;
  notify: (message: string) => void;
}

function Toggle({ checked }: { checked: boolean }) {
  return (
    <span
      className={`settings-toggle ${checked ? "is-on" : ""}`}
      aria-hidden="true"
    >
      <i />
    </span>
  );
}

function SettingsRow({
  icon,
  color,
  label,
  children,
  onClick,
  checked,
}: {
  icon: ReactNode;
  color: string;
  label: string;
  children?: ReactNode;
  onClick?: () => void;
  checked?: boolean;
}) {
  return (
    <button
      className="settings-row"
      onClick={onClick}
      role={typeof checked === "boolean" ? "switch" : undefined}
      aria-checked={checked}
    >
      <span className="settings-row-icon" style={{ background: color }}>
        {icon}
      </span>
      <span className="settings-row-content">
        <span>{label}</span>
        {children}
      </span>
    </button>
  );
}

export default function Settings({
  preferences,
  onChange,
  onBack,
  onExport,
  onReset,
  notify,
}: SettingsProps) {
  const [breakDialog, setBreakDialog] = useState(false);
  const [breakDate, setBreakDate] = useState(preferences.startDate);
  const [periodDialog, setPeriodDialog] = useState(false);
  const [dateDialog, setDateDialog] = useState(false);
  function toggle(key: keyof Preferences) {
    onChange({ ...preferences, [key]: !preferences[key] });
  }
  const dateText = new Date(
    preferences.startDate + "T12:00:00",
  ).toLocaleDateString("ru-RU");
  return (
    <section className="settings-screen">
      <header className="screen-topbar">
        <button className="icon-button" aria-label="Назад" onClick={onBack}>
          <ChevronLeft />
        </button>
        <h1>Настройки</h1>
        <span />
      </header>
      <div className="settings-scroll">
        <div className="settings-group">
          <SettingsRow
            icon={<Coins />}
            color="var(--s3)"
            label="Валюта по умолчанию"
            onClick={() => notify("В макете используется рубль RUB")}
          >
            <span className="settings-row-value">RUB</span>
          </SettingsRow>
          <SettingsRow
            icon={<MessageCircle />}
            color="var(--s1)"
            label="Язык"
            onClick={() => notify("Язык макета — русский")}
          >
            <span className="settings-row-value">Русский</span>
          </SettingsRow>
          <SettingsRow
            icon={<ArrowDownToLine />}
            color="var(--s4)"
            label="Экспорт"
            onClick={onExport}
          >
            <ChevronRight />
          </SettingsRow>
          <SettingsRow
            icon={<Bell />}
            color="var(--s5)"
            label="Уведомления"
            checked={preferences.notifications}
            onClick={() => toggle("notifications")}
          >
            <Toggle checked={preferences.notifications} />
          </SettingsRow>
          <SettingsRow
            icon={<KeyRound />}
            color="var(--s8)"
            label="Пароль"
            checked={preferences.password}
            onClick={() => toggle("password")}
          >
            <Toggle checked={preferences.password} />
          </SettingsRow>
          <SettingsRow
            icon={<Timer />}
            color="var(--s7)"
            label="3 мин. без пароля"
            checked={preferences.gracePeriod}
            onClick={() => toggle("gracePeriod")}
          >
            <Toggle checked={preferences.gracePeriod} />
          </SettingsRow>
        </div>
        <h2 className="settings-section-title">ОТЧЕТНЫЙ ПЕРИОД</h2>
        <div className="settings-group">
          <SettingsRow
            icon={<CalendarDays />}
            color="var(--warn)"
            label="Период"
            onClick={() => setPeriodDialog(true)}
          >
            <span className="settings-row-value">
              {preferences.period === "month"
                ? "Месяц"
                : preferences.period === "week"
                  ? "Неделя"
                  : "Год"}
            </span>
          </SettingsRow>
          <SettingsRow
            icon={<ArrowRight />}
            color="var(--s2)"
            label="Начало"
            onClick={() => setDateDialog(true)}
          >
            <span className="settings-row-value">{dateText}</span>
          </SettingsRow>
        </div>
        <h2 className="settings-section-title">ПЕРСОНАЛЬНЫЕ</h2>
        <div className="settings-group">
          <SettingsRow
            icon={<PiggyBank />}
            color="var(--s3)"
            label="Показывать бюджет"
            checked={preferences.showBudget}
            onClick={() => toggle("showBudget")}
          >
            <Toggle checked={preferences.showBudget} />
          </SettingsRow>
          <SettingsRow
            icon={<Palette />}
            color="var(--s5)"
            label="Цветные перерасходы"
            checked={preferences.colorOverspend}
            onClick={() => toggle("colorOverspend")}
          >
            <Toggle checked={preferences.colorOverspend} />
          </SettingsRow>
          <SettingsRow
            icon={<Volume2 />}
            color="var(--s7)"
            label="Звуки"
            checked={preferences.sounds}
            onClick={() => toggle("sounds")}
          >
            <Toggle checked={preferences.sounds} />
          </SettingsRow>
          <SettingsRow
            icon={<ScrollText />}
            color="var(--s2)"
            label="Ежедневные отчеты"
            checked={preferences.dailyReports}
            onClick={() => toggle("dailyReports")}
          >
            <Toggle checked={preferences.dailyReports} />
          </SettingsRow>
          <SettingsRow
            icon={<Type />}
            color="var(--accent)"
            label="Увеличенные шрифты"
            checked={preferences.largeFonts}
            onClick={() => toggle("largeFonts")}
          >
            <Toggle checked={preferences.largeFonts} />
          </SettingsRow>
          <SettingsRow
            icon={<Radio />}
            color="var(--s7)"
            label="Источники доходов"
            checked={preferences.incomeVisible}
            onClick={() => toggle("incomeVisible")}
          >
            <Toggle checked={preferences.incomeVisible} />
          </SettingsRow>
          <SettingsRow
            icon={<MessageCircle />}
            color="var(--s1)"
            label="Новости в Ленте"
            checked={preferences.news}
            onClick={() => toggle("news")}
          >
            <Toggle checked={preferences.news} />
          </SettingsRow>
        </div>
        <h2 className="settings-section-title">ПОМОЩНИКИ</h2>
        <div className="settings-group">
          <SettingsRow
            icon={<Clock3 />}
            color="var(--s2)"
            label="Долгий перерыв в учете"
            onClick={() => setBreakDialog(true)}
          >
            <ChevronRight />
          </SettingsRow>
          <SettingsRow
            icon={<RefreshCw />}
            color="var(--s8)"
            label="Пересчитать балансы"
            onClick={() =>
              notify("Балансы пересчитаны по сохраненным операциям")
            }
          >
            <ChevronRight />
          </SettingsRow>
        </div>
        <button className="settings-reset" onClick={onReset}>
          <RotateCcw size={15} />
          Восстановить демоданные
        </button>
      </div>
      {periodDialog && (
        <div
          className="settings-dialog-backdrop"
          onClick={() => setPeriodDialog(false)}
        >
          <section
            className="settings-dialog"
            role="dialog"
            aria-modal="true"
            aria-label="Отчетный период"
            onClick={(event) => event.stopPropagation()}
          >
            <h2>Отчетный период</h2>
            {(["week", "month", "year"] as const).map((value) => (
              <button
                key={value}
                onClick={() => {
                  onChange({ ...preferences, period: value });
                  setPeriodDialog(false);
                }}
              >
                {value === "week"
                  ? "Неделя"
                  : value === "month"
                    ? "Месяц"
                    : "Год"}
              </button>
            ))}
            <button onClick={() => setPeriodDialog(false)}>Отмена</button>
          </section>
        </div>
      )}
      {dateDialog && (
        <div
          className="settings-dialog-backdrop"
          onClick={() => setDateDialog(false)}
        >
          <section
            className="settings-dialog"
            role="dialog"
            aria-modal="true"
            aria-label="Начало учета"
            onClick={(event) => event.stopPropagation()}
          >
            <h2>Начало учета</h2>
            <label>
              Дата
              <input
                type="date"
                aria-label="Начало учета"
                value={preferences.startDate}
                onChange={(event) => {
                  if (event.target.value)
                    onChange({ ...preferences, startDate: event.target.value });
                }}
              />
            </label>
            <button onClick={() => setDateDialog(false)}>Готово</button>
          </section>
        </div>
      )}
      {breakDialog && (
        <div
          className="settings-dialog-backdrop"
          onClick={() => setBreakDialog(false)}
        >
          <section
            className="settings-dialog"
            role="dialog"
            aria-modal="true"
            aria-label="Долгий перерыв в учете"
            onClick={(event) => event.stopPropagation()}
          >
            <button
              className="settings-dialog-close"
              aria-label="Закрыть"
              onClick={() => setBreakDialog(false)}
            >
              <X size={20} />
            </button>
            <h2>Долгий перерыв в учете</h2>
            <p>
              Укажите дату, с которой продолжаете учет. Балансы можно изменить в
              параметрах каждого счета.
            </p>
            <label>
              Продолжить с даты
              <input
                type="date"
                value={breakDate}
                onChange={(event) => setBreakDate(event.target.value)}
              />
            </label>
            <button
              onClick={() => {
                if (!breakDate) return;
                onChange({ ...preferences, startDate: breakDate });
                setBreakDialog(false);
                notify("Дата начала учета обновлена");
              }}
            >
              Сохранить
            </button>
          </section>
        </div>
      )}
    </section>
  );
}
