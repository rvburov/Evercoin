import { useLayoutEffect, useRef, useState, type ReactNode } from "react";
import { ChartPie, LayoutGrid, Mic, ScrollText, Settings } from "lucide-react";

export type NavTab = "home" | "feed" | "stats" | "settings";

// Геометрия островка как в клиенте Private Gateway: скругленная полоса
// с выступом-куполом под круглую кнопку помощника по центру.
const SIDE = 12;
const BAR_TOP = 44;
const BAR_HEIGHT = 60;
const CORNER = 24;
const DOME = 40;
const FILLET = 16;
export const NAV_HEIGHT = BAR_TOP + BAR_HEIGHT;

function round(value: number): number {
  return Math.round(value * 100) / 100;
}
function islandPath(width: number): string {
  const center = width / 2;
  const right = width - SIDE;
  const bottom = BAR_TOP + BAR_HEIGHT;
  // Скругление касается полосы и купола: от центра до его начала — reach.
  const reach = Math.sqrt((DOME + FILLET) ** 2 - FILLET ** 2);
  const share = DOME / (DOME + FILLET);
  const joinX = reach * share;
  const joinY = BAR_TOP - FILLET * share;
  return [
    `M${SIDE + CORNER} ${BAR_TOP}`,
    `H${round(center - reach)}`,
    `A${FILLET} ${FILLET} 0 0 0 ${round(center - joinX)} ${round(joinY)}`,
    `A${DOME} ${DOME} 0 0 1 ${round(center + joinX)} ${round(joinY)}`,
    `A${FILLET} ${FILLET} 0 0 0 ${round(center + reach)} ${BAR_TOP}`,
    `H${round(right - CORNER)}`,
    `A${CORNER} ${CORNER} 0 0 1 ${round(right)} ${BAR_TOP + CORNER}`,
    `V${bottom - CORNER}`,
    `A${CORNER} ${CORNER} 0 0 1 ${round(right - CORNER)} ${bottom}`,
    `H${SIDE + CORNER}`,
    `A${CORNER} ${CORNER} 0 0 1 ${SIDE} ${bottom - CORNER}`,
    `V${BAR_TOP + CORNER}`,
    `A${CORNER} ${CORNER} 0 0 1 ${SIDE + CORNER} ${BAR_TOP}`,
    "Z",
  ].join(" ");
}

interface BottomNavProps {
  active: NavTab;
  onSelect: (tab: NavTab) => void;
  onAssistant: () => void;
}
export default function BottomNav({
  active,
  onSelect,
  onAssistant,
}: BottomNavProps) {
  const navRef = useRef<HTMLElement>(null);
  const [width, setWidth] = useState(360);
  useLayoutEffect(() => {
    const nav = navRef.current;
    if (!nav) return;
    const update = () => setWidth(nav.clientWidth || 360);
    update();
    const observer = new ResizeObserver(update);
    observer.observe(nav);
    return () => observer.disconnect();
  }, []);
  function item(tab: NavTab, label: string, icon: ReactNode) {
    return (
      <button
        className="bottom-nav-item"
        aria-current={active === tab ? "page" : undefined}
        onClick={() => onSelect(tab)}
      >
        {icon}
        <span>{label}</span>
      </button>
    );
  }
  return (
    <nav className="bottom-nav" ref={navRef} aria-label="Основное меню">
      <svg
        className="bottom-nav-shape"
        viewBox={`0 0 ${width} ${NAV_HEIGHT}`}
        aria-hidden="true"
      >
        <path d={islandPath(width)} />
      </svg>
      <div className="bottom-nav-items">
        {item("home", "Главная", <LayoutGrid />)}
        {item("feed", "Лента", <ScrollText />)}
        <span className="bottom-nav-center-label" aria-hidden="true">
          Помощник
        </span>
        {item("stats", "Статистика", <ChartPie />)}
        {item("settings", "Настройки", <Settings />)}
      </div>
      <button
        className="bottom-nav-assistant"
        aria-label="Помощник"
        onClick={onAssistant}
      >
        <Mic />
      </button>
    </nav>
  );
}
