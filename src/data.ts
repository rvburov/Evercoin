import type { LucideIcon } from "lucide-react";
import {
  Baby,
  Bath,
  BedDouble,
  Tent,
  Trees,
  Truck,
  Umbrella,
  Watch,
  Wrench,
  Zap,
  Scissors,
  Dog,
  Hospital,
  Lamp,
  Sofa,
  Refrigerator,
  CircleDollarSign,
  HandCoins,
  Headphones,
  PiggyBank,
  Ticket,
  Sailboat,
  Compass,
  Croissant,
  Cookie,
  Pizza,
  Gem,
  Palette,
  Mountain,
  KeyRound,
  Cloud,
  Luggage,
} from "lucide-react";
import {
  Banknote,
  BriefcaseBusiness,
  CreditCard,
  UserRound,
  Wallet,
  ShoppingCart,
  Sandwich,
  Radio,
  House,
  Fuel,
  CarFront,
  TramFront,
  Film,
  Globe2,
  GraduationCap,
  Monitor,
  Hammer,
  Speaker,
  Shirt,
  BriefcaseMedical,
  PawPrint,
  Gift,
  Calculator,
  Percent,
  Plane,
  AtSign,
  Bandage,
  Landmark,
  Presentation,
  Martini,
  SprayCan,
  Beer,
  Bike,
  BookOpen,
  Book,
  ChartNoAxesColumn,
  Camera,
  Building2,
  Coffee,
  Gamepad2,
  Scale,
  Dices,
  Drama,
  Dumbbell,
  Flower2,
  Utensils,
  Music,
  Smartphone,
  Heart,
  Star,
  Target,
} from "lucide-react";

export type ItemKind = "income" | "account" | "expense";
export type ReportKind = "both" | "expense" | "income" | "balance" | "capital";
export interface FinanceItem {
  id: string;
  kind: ItemKind;
  name: string;
  icon: string;
  budget: number;
  opening: number;
  included: boolean;
  goal: boolean;
  archived?: boolean;
}
export interface RepeatRule {
  every: number;
  unit: "day" | "week" | "month" | "year";
  until: string;
}
export interface Entry {
  id: string;
  sourceId: string;
  targetId: string;
  amount: number;
  date: string;
  note: string;
  tags: string[];
  repeat: RepeatRule | null;
  origin?: "assistant";
}
export interface OperationDraft {
  sourceId: string;
  targetId: string;
  amount: string;
  date: string;
  note: string;
  tags: string[];
  repeat: RepeatRule | null;
  origin?: "assistant";
}
export interface Preferences {
  incomeVisible: boolean;
  showBudget: boolean;
  colorOverspend: boolean;
  notifications: boolean;
  password: boolean;
  gracePeriod: boolean;
  sounds: boolean;
  dailyReports: boolean;
  largeFonts: boolean;
  news: boolean;
  period: "month" | "week" | "year";
  startDate: string;
}
export interface FinanceState {
  version: 2;
  items: FinanceItem[];
  entries: Entry[];
  preferences: Preferences;
  profileName: string;
}
export const today = "2026-11-25";
export const iconMap: Record<string, LucideIcon> = {
  money: Banknote,
  work: BriefcaseBusiness,
  card: CreditCard,
  person: UserRound,
  wallet: Wallet,
  cart: ShoppingCart,
  cafe: Sandwich,
  radio: Radio,
  home: House,
  fuel: Fuel,
  car: CarFront,
  transit: TramFront,
  film: Film,
  globe: Globe2,
  study: GraduationCap,
  monitor: Monitor,
  hammer: Hammer,
  speaker: Speaker,
  shirt: Shirt,
  health: BriefcaseMedical,
  paw: PawPrint,
  gift: Gift,
  calculator: Calculator,
  percent: Percent,
  plane: Plane,
  at: AtSign,
  bandage: Bandage,
  bank: Landmark,
  presentation: Presentation,
  cocktail: Martini,
  spray: SprayCan,
  beer: Beer,
  bike: Bike,
  book: BookOpen,
  notebook: Book,
  chart: ChartNoAxesColumn,
  camera: Camera,
  building: Building2,
  coffee: Coffee,
  game: Gamepad2,
  scale: Scale,
  dice: Dices,
  drama: Drama,
  dumbbell: Dumbbell,
  flower: Flower2,
  food: Utensils,
  music: Music,
  phone: Smartphone,
  heart: Heart,
  star: Star,
  target: Target,
  baby: Baby,
  bath: Bath,
  bed: BedDouble,
  tent: Tent,
  trees: Trees,
  truck: Truck,
  umbrella: Umbrella,
  watch: Watch,
  wrench: Wrench,
  electricity: Zap,
  scissors: Scissors,
  dog: Dog,
  hospital: Hospital,
  lamp: Lamp,
  sofa: Sofa,
  fridge: Refrigerator,
  dollar: CircleDollarSign,
  coins: HandCoins,
  headphones: Headphones,
  piggy: PiggyBank,
  ticket: Ticket,
  boat: Sailboat,
  compass: Compass,
  croissant: Croissant,
  cookie: Cookie,
  pizza: Pizza,
  gem: Gem,
  palette: Palette,
  mountain: Mountain,
  key: KeyRound,
  cloud: Cloud,
  luggage: Luggage,
};
export const iconChoices = Object.keys(iconMap);
export function money(kopeks: number): string {
  return (
    new Intl.NumberFormat("ru-RU", {
      maximumFractionDigits: kopeks % 100 ? 2 : 0,
    }).format(kopeks / 100) + " ₽"
  );
}
export function compactMoney(kopeks: number): string {
  return Math.abs(kopeks) >= 100000000
    ? new Intl.NumberFormat("ru-RU", { maximumFractionDigits: 0 }).format(
        kopeks / 100000,
      ) + "к ₽"
    : money(kopeks);
}
export const monthLabel = (period: string) =>
  new Intl.DateTimeFormat("ru-RU", { month: "long", year: "numeric" })
    .format(new Date(period + "-15T12:00:00"))
    .replace(" г.", "");
export const dateLabel = (date: string) =>
  (date === today ? "СЕГОДНЯ, " : "") +
  new Intl.DateTimeFormat("ru-RU", {
    day: "numeric",
    month: "long",
    year: "numeric",
  })
    .format(new Date(date + "T12:00:00"))
    .replace(" г.", "");
export function isValidDate(value: string): boolean {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const date = new Date(value + "T12:00:00Z");
  return (
    Number.isFinite(date.getTime()) && date.toISOString().slice(0, 10) === value
  );
}
export function newId(): string {
  return (
    globalThis.crypto?.randomUUID?.() || `item-${Date.now()}-${Math.random()}`
  );
}
export function itemTotal(id: string, entries: Entry[]): number {
  return entries.reduce(
    (total, entry) => total + (entry.targetId === id ? entry.amount : 0),
    0,
  );
}
export function accountBalance(item: FinanceItem, entries: Entry[]): number {
  return (
    item.opening +
    entries.reduce(
      (total, entry) =>
        total +
        (entry.targetId === item.id ? entry.amount : 0) -
        (entry.sourceId === item.id ? entry.amount : 0),
      0,
    )
  );
}
export function totalBalance(state: FinanceState): number {
  return state.items
    .filter(
      (item) => item.kind === "account" && item.included && !item.archived,
    )
    .reduce((total, item) => total + accountBalance(item, state.entries), 0);
}
export function entriesForPeriod(entries: Entry[], period: string): Entry[] {
  return entries.filter((entry) => entry.date.startsWith(period));
}
export function totals(state: FinanceState, period: string) {
  const entries = entriesForPeriod(state.entries, period);
  const byId = new Map(state.items.map((item) => [item.id, item]));
  const income = entries
    .filter((entry) => byId.get(entry.sourceId)?.kind === "income")
    .reduce((total, entry) => total + entry.amount, 0);
  const expense = entries
    .filter((entry) => byId.get(entry.targetId)?.kind === "expense")
    .reduce((total, entry) => total + entry.amount, 0);
  const planned = state.items
    .filter((item) => item.kind === "expense" && !item.archived)
    .reduce(
      (total, item) =>
        total + Math.max(0, item.budget - itemTotal(item.id, entries)),
      0,
    );
  return { income, expense, planned };
}
export function defaultDraft(): OperationDraft {
  return {
    sourceId: "sber",
    targetId: "food",
    amount: "",
    date: today,
    note: "",
    tags: [],
    repeat: null,
  };
}

const incomeItems: Array<[string, string, string, number]> = [
  ["salary", "Зарплата", "money", 150000],
  ["bonus", "Премия", "money", 40000],
  ["freelance", "Заработок", "money", 0],
  ["loan-income", "Займы доходы", "money", 10000],
];
const accountItems: Array<[string, string, string, number]> = [
  ["sber", "Сбер кредитка", "card", -1208000],
  ["vtb", "ВТБ кредитка", "card", -76340],
  ["tbank", "Тбанк кредитка", "card", -2950],
  ["ozon", "Озон кредитка", "wallet", -5600],
  ["loan", "Займ Михаил", "money", 500000],
  ["macbook", "Кредит MacBook", "money", -130000],
  ["mom-debt", "Долг мама", "person", -300000],
];
const expenseItems: Array<[string, string, string, number, number]> = [
  ["food", "Продукты", "cart", 24170, 14000],
  ["cafe", "Кафе и рестораны", "cafe", 18880, 12000],
  ["connection", "Связь", "radio", 0, 1920],
  ["home", "ЖКХ", "home", 13100, 6500],
  ["fuel", "Топливо", "fuel", 9570, 3000],
  ["service", "Обслуживание", "car", 1980, 5425],
  ["transport", "Транспорт", "transit", 0, 2400],
  ["fun", "Развлечение", "film", 6800, 2000],
  ["travel", "Путешествия", "globe", 0, 8333],
  ["study", "Обучение", "study", 0, 100],
  ["programs", "Программы", "monitor", 25270, 1934],
  ["household", "Дом. хозяйство", "hammer", 5810, 1200],
  ["tech", "Техника", "speaker", 2560, 1000],
  ["clothes", "Одежда", "shirt", 0, 2000],
  ["health", "Здоровье", "health", 3000, 2000],
  ["cat", "Кошка", "paw", 1090, 2000],
  ["polina", "Полина", "person", 42040, 8000],
  ["mom", "Мама", "person", 0, 500],
  ["dad", "Папа", "person", 0, 500],
  ["gifts", "Подарки", "gift", 5000, 1000],
  ["credit", "Кредит %", "calculator", 13900, 3100],
  ["tax", "Налоги", "percent", 820, 0],
];
export function createInitialState(): FinanceState {
  const items: FinanceItem[] = [
    ...incomeItems.map(([id, name, icon, budget]) => ({
      id,
      name,
      icon,
      budget: budget * 100,
      kind: "income" as const,
      opening: 0,
      included: true,
      goal: false,
    })),
    ...accountItems.map(([id, name, icon, balance]) => ({
      id,
      name,
      icon,
      budget: 0,
      kind: "account" as const,
      opening: balance * 100,
      included: true,
      goal: false,
    })),
    ...expenseItems.map(([id, name, icon, , budget]) => ({
      id,
      name,
      icon,
      budget: budget * 100,
      kind: "expense" as const,
      opening: 0,
      included: true,
      goal: false,
    })),
  ];
  const expenseEntry = (
    id: string,
    targetId: string,
    amount: number,
    date: string,
    note = "",
    tags: string[] = [],
  ): Entry => ({
    id,
    sourceId: "sber",
    targetId,
    amount: amount * 100,
    date,
    note,
    tags,
    repeat: null,
  });
  const entries: Entry[] = [
    expenseEntry("e1", "programs", 1190, today, "", ["Хостинг «Программы»"]),
    expenseEntry("e2", "cafe", 370, today, "", [
      "Бизнес ланч «Кафе и рестораны»",
    ]),
    expenseEntry("e3", "cafe", 660, today, "", [
      "Бизнес ланч «Кафе и рестораны»",
    ]),
    expenseEntry("e4", "programs", 3000, "2026-11-24", "", [
      "Claude «Программы»",
    ]),
    expenseEntry("e5", "fuel", 2940, "2026-11-24"),
    expenseEntry("e6", "cafe", 1820, "2026-11-24", "", [
      "Бизнес ланч «Кафе и рестораны»",
    ]),
    expenseEntry("e7", "cafe", 640, "2026-11-23"),
    expenseEntry("e8", "cafe", 380, "2026-11-23"),
    expenseEntry("e9", "polina", 1000, "2026-11-22", "", [
      "Здоровье и красота",
    ]),
    expenseEntry("e10", "credit", 500, "2026-11-22", "", ["Тинькоф"]),
    expenseEntry("e11", "food", 2280, "2026-11-22", "", [
      "Продукты первой необходимости",
    ]),
  ];
  for (const [id, , , amount] of expenseItems) {
    const remainder = amount * 100 - itemTotal(id, entries);
    if (remainder > 0)
      entries.push({
        ...expenseEntry(`seed-${id}`, id, remainder / 100, "2026-11-10"),
        note: "Операции за месяц",
      });
  }
  entries.push({
    id: "income1",
    sourceId: "salary",
    targetId: "sber",
    amount: 6250000,
    date: "2026-11-05",
    note: "",
    tags: [],
    repeat: null,
  });
  entries.push({
    id: "income2",
    sourceId: "bonus",
    targetId: "sber",
    amount: 2500000,
    date: "2026-11-13",
    note: "",
    tags: [],
    repeat: null,
  });
  // Демонстрационная история дает графикам четыре реальных месячных среза.
  for (const [month, income, expense, bonus] of [
    ["2026-08", 130000, 185000, 10000],
    ["2026-09", 127000, 198000, 18000],
    ["2026-10", 125000, 210000, 20000],
  ] as const) {
    const historicalDate = month + "-15";
    entries.push({
      id: "salary-" + month,
      sourceId: "salary",
      targetId: "sber",
      amount: (income - bonus) * 100,
      date: historicalDate,
      note: "Демонстрационная история",
      tags: [],
      repeat: null,
    });
    entries.push({
      id: "bonus-" + month,
      sourceId: "bonus",
      targetId: "sber",
      amount: bonus * 100,
      date: historicalDate,
      note: "Демонстрационная история",
      tags: [],
      repeat: null,
    });
    let assigned = 0;
    const activeCategories = expenseItems.filter((item) => item[3] > 0);
    activeCategories.forEach(([id, , , value], index) => {
      const amount =
        index === activeCategories.length - 1
          ? expense * 100 - assigned
          : Math.round((expense * 100 * value) / 173990);
      assigned += amount;
      entries.push({
        id: id + "-" + month,
        sourceId: "sber",
        targetId: id,
        amount,
        date: historicalDate,
        note: "Демонстрационная история",
        tags: [],
        repeat: null,
      });
    });
  }
  const sber = items.find((item) => item.id === "sber")!;
  sber.opening -= accountBalance({ ...sber, opening: 0 }, entries);
  return {
    version: 2,
    items,
    entries,
    preferences: {
      incomeVisible: true,
      showBudget: true,
      colorOverspend: true,
      notifications: false,
      password: false,
      gracePeriod: false,
      sounds: false,
      dailyReports: false,
      largeFonts: false,
      news: false,
      period: "month",
      startDate: "2024-01-01",
    },
    profileName: "romanburov89@gmail.com",
  };
}
const storageKey = "evercoin-screenshot-mockup-v2";
export function loadState(): FinanceState {
  try {
    const value: unknown = JSON.parse(
      localStorage.getItem(storageKey) || "null",
    );
    const state = value as FinanceState | null;
    if (
      state?.version !== 2 ||
      !Array.isArray(state.items) ||
      !Array.isArray(state.entries) ||
      !state.preferences ||
      typeof state.profileName !== "string"
    )
      return createInitialState();
    const ids = new Set(state.items.map((item) => item.id));
    if (
      !state.items.every(
        (item) =>
          typeof item.id === "string" &&
          typeof item.name === "string" &&
          ["income", "account", "expense"].includes(item.kind) &&
          !!iconMap[item.icon] &&
          Number.isSafeInteger(item.opening) &&
          Number.isSafeInteger(item.budget) &&
          item.budget >= 0,
      )
    )
      return createInitialState();
    if (
      !state.entries.every(
        (entry) =>
          Number.isSafeInteger(entry.amount) &&
          entry.amount > 0 &&
          ids.has(entry.sourceId) &&
          ids.has(entry.targetId) &&
          typeof entry.date === "string" &&
          isValidDate(entry.date) &&
          typeof entry.note === "string" &&
          Array.isArray(entry.tags),
      )
    )
      return createInitialState();
    return state;
  } catch {
    return createInitialState();
  }
}
export function saveState(state: FinanceState): boolean {
  try {
    localStorage.setItem(storageKey, JSON.stringify(state));
    return true;
  } catch {
    return false;
  }
}
