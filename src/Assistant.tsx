import { useEffect, useRef, useState } from "react";
import {
  ArrowLeft,
  AudioLines,
  Check,
  ChevronRight,
  LoaderCircle,
  Mic,
  Send,
  X,
} from "lucide-react";
import {
  accountBalance,
  entriesForPeriod,
  iconMap,
  itemTotal,
  money,
  monthLabel,
  today,
  totalBalance,
  totals,
  type FinanceItem,
  type FinanceState,
  type OperationDraft,
} from "./data";
import "./assistant.css";

interface AssistantProps {
  state: FinanceState;
  period: string;
  onReview: (draft: OperationDraft) => void;
  notify: (message: string) => void;
  onBack: () => void;
}
interface Message {
  id: number;
  role: "user" | "assistant";
  text: string;
}
interface SpeechResultEvent {
  results: ArrayLike<ArrayLike<{ transcript: string }>>;
}
interface Recognition {
  lang: string;
  interimResults: boolean;
  onresult: ((event: SpeechResultEvent) => void) | null;
  onerror: (() => void) | null;
  onend: (() => void) | null;
  start(): void;
  stop(): void;
}
type SpeechWindow = Window & {
  SpeechRecognition?: new () => Recognition;
  webkitSpeechRecognition?: new () => Recognition;
};
const waveHeights = [
  8, 17, 26, 12, 34, 22, 24, 37, 19, 31, 24, 15, 33, 22, 17, 28, 12,
];
const normalize = (text: string) =>
  text.toLowerCase().replaceAll("\u0451", "е");

function matchItem(
  items: FinanceItem[],
  text: string,
): FinanceItem | undefined {
  const exact = items.find((item) => text.includes(normalize(item.name)));
  if (exact) return exact;
  const keywords: Record<string, RegExp> = {
    food: /продукт|вкусвилл|пятерочк|перекрест/,
    cafe: /кафе|кофе|круассан|ресторан|обед/,
    transport: /транспорт|такси|метро|автобус|проезд/,
    fuel: /топлив|бензин|заправ/,
    home: /жкх|квартир|коммунал/,
    programs: /программ|подписк|хостинг|сервис|хранилищ/,
    clothes: /одежд|обувь/,
    health: /здоров|аптек|лекарств|врач/,
    salary: /зарплат/,
    bonus: /преми/,
    freelance: /фриланс|заработ/,
    sber: /сбер/,
    vtb: /втб/,
    tbank: /тбанк|тинькоф/,
    ozon: /озон/,
    loan: /михаил/,
    macbook: /макбук|macbook/,
    "mom-debt": /долг мам/,
  };
  return (
    items.find((item) => keywords[item.id]?.test(text)) ||
    items.find((item) => text.includes(normalize(item.name).slice(0, 5)))
  );
}

function makeProposal(
  text: string,
  state: FinanceState,
): OperationDraft | null {
  const normalized = normalize(text);
  const match = normalized.match(/\d[\d\s]*(?:[.,]\d{1,2})?/);
  if (!match) return null;
  let rubles = Number(match[0].replace(/\s/g, "").replace(",", "."));
  if (
    /^\s*(тыс|тысяч)/.test(
      normalized.slice((match.index || 0) + match[0].length),
    )
  )
    rubles *= 1000;
  const amount = Math.round(rubles * 100);
  if (!Number.isSafeInteger(amount) || amount <= 0 || amount > 99999999999)
    return null;

  const income = /получил|поступил|зарплат|преми|заработал|доход/.test(
    normalized,
  );
  const categoryItems = state.items.filter(
    (item) => !item.archived && item.kind === (income ? "income" : "expense"),
  );
  const accountItems = state.items.filter(
    (item) => !item.archived && item.kind === "account",
  );
  const category = matchItem(categoryItems, normalized);
  const account = matchItem(accountItems, normalized) || accountItems[0];
  if (!account || !category) return null;
  return {
    sourceId: income ? category.id : account.id,
    targetId: income ? account.id : category.id,
    amount: (amount / 100).toString(),
    date: /вчера/.test(normalized) ? "2026-11-24" : today,
    note: text.trim(),
    tags: [],
    repeat: null,
    origin: "assistant",
  };
}

export default function Assistant({
  state,
  period,
  onReview,
  notify,
  onBack,
}: AssistantProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [proposal, setProposal] = useState<OperationDraft | null>(null);
  const [listening, setListening] = useState(false);
  const [demoPlaying, setDemoPlaying] = useState(false);
  const recognitionRef = useRef<Recognition | null>(null);
  const demoTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const messageCounter = useRef(0);
  const threadEndRef = useRef<HTMLDivElement>(null);
  const entries = entriesForPeriod(state.entries, period);
  const summary = totals(state, period);
  const activeItems = state.items.filter((item) => !item.archived);
  const account =
    activeItems.find((item) => item.id === "sber" && item.kind === "account") ||
    activeItems.find((item) => item.kind === "account");
  const expense =
    activeItems.find((item) => item.id === "food" && item.kind === "expense") ||
    activeItems.find((item) => item.kind === "expense");
  const income =
    activeItems.find((item) => item.id === "bonus" && item.kind === "income") ||
    activeItems.find((item) => item.kind === "income");

  useEffect(() => {
    if (!messages.length && !proposal && !listening && !demoPlaying) return;
    const reducedMotion = window.matchMedia(
      "(prefers-reduced-motion: reduce)",
    ).matches;
    threadEndRef.current?.scrollIntoView({
      behavior: reducedMotion ? "auto" : "smooth",
      block: "end",
    });
  }, [messages, proposal, listening, demoPlaying]);
  useEffect(() => setProposal(null), [state.entries]);
  useEffect(
    () => () => {
      if (demoTimerRef.current) clearTimeout(demoTimerRef.current);
      const recognition = recognitionRef.current;
      if (recognition) {
        recognition.onresult = null;
        recognition.onerror = null;
        recognition.onend = null;
        recognition.stop();
      }
    },
    [],
  );

  function addMessage(role: Message["role"], text: string) {
    const id = ++messageCounter.current;
    setMessages((previous) => [...previous, { id, role, text }]);
  }

  function answerQuestion(text: string): string {
    const normalized = normalize(text);
    if (/баланс|в наличии|капитал/.test(normalized)) {
      const matchedAccount = matchItem(
        state.items.filter((item) => item.kind === "account"),
        normalized,
      );
      return matchedAccount
        ? `На счете «${matchedAccount.name}» сейчас ${money(accountBalance(matchedAccount, state.entries))}.`
        : `Общий баланс счетов, включенных в расчет, — ${money(totalBalance(state))}.`;
    }
    const category = matchItem(
      state.items.filter((item) => item.kind !== "account"),
      normalized,
    );
    if (category) {
      const amount =
        category.kind === "income"
          ? entries
              .filter((entry) => entry.sourceId === category.id)
              .reduce((total, entry) => total + entry.amount, 0)
          : itemTotal(category.id, entries);
      const plan = category.budget ? ` План — ${money(category.budget)}.` : "";
      return `За период «${monthLabel(period)}» в категории «${category.name}» — ${money(amount)}.${plan}`;
    }
    if (
      /доход|заработ|получил/.test(normalized) &&
      !/расход|потрат/.test(normalized)
    ) {
      return `За период «${monthLabel(period)}» доходы составили ${money(summary.income)}.`;
    }
    const top = state.items
      .filter((item) => item.kind === "expense")
      .sort(
        (left, right) =>
          itemTotal(right.id, entries) - itemTotal(left.id, entries),
      )[0];
    if (!top || !summary.expense)
      return `За период «${monthLabel(period)}» расходов пока нет. Доходы — ${money(summary.income)}.`;
    const topAmount = itemTotal(top.id, entries);
    return `За период «${monthLabel(period)}» расходы — ${money(summary.expense)}, доходы — ${money(summary.income)}. Больше всего ушло на «${top.name}» — ${money(topAmount)}, ${Math.round((topAmount / summary.expense) * 100)}% расходов.`;
  }

  function sendMessage(text: string) {
    const trimmed = text.trim();
    if (!trimmed) return;
    addMessage("user", trimmed);
    setInput("");
    setProposal(null);
    if (/^(сколько|какие|какой|покажи|на что|где|как|разбер)/i.test(trimmed)) {
      addMessage("assistant", answerQuestion(trimmed));
      return;
    }
    const candidate = makeProposal(trimmed, state);
    if (!candidate) {
      addMessage(
        "assistant",
        "Укажите сумму цифрами и название существующей категории. Например, «Потратил 640 рублей на продукты со Сбера». В демо используются простые правила разбора.",
      );
      return;
    }
    addMessage(
      "assistant",
      "Подготовил операцию. Проверьте сумму, категорию и счет перед сохранением.",
    );
    setProposal(candidate);
  }

  function playDemo() {
    if (demoPlaying || listening) return;
    if (!account || !expense) {
      notify("Сначала создайте счет и категорию расхода");
      return;
    }
    setDemoPlaying(true);
    demoTimerRef.current = setTimeout(() => {
      setDemoPlaying(false);
      sendMessage(
        `Потратил 640 рублей на ${expense.name} со счета ${account.name}`,
      );
    }, 1200);
  }

  function toggleMicrophone() {
    if (listening) {
      recognitionRef.current?.stop();
      setListening(false);
      return;
    }
    const speechWindow = window as SpeechWindow;
    const Constructor =
      speechWindow.SpeechRecognition || speechWindow.webkitSpeechRecognition;
    if (!Constructor) {
      notify(
        "Голосовой ввод недоступен в этом браузере. Используйте текст или демопример",
      );
      return;
    }
    const recognition = new Constructor();
    recognitionRef.current = recognition;
    recognition.lang = "ru-RU";
    recognition.interimResults = false;
    recognition.onresult = (event) => {
      const transcript = event.results[0]?.[0]?.transcript;
      if (transcript) sendMessage(transcript);
    };
    recognition.onerror = () => {
      setListening(false);
      notify(
        "Не удалось распознать речь. Проверьте доступ к микрофону или попробуйте демопример",
      );
    };
    recognition.onend = () => setListening(false);
    try {
      recognition.start();
      setListening(true);
    } catch {
      setListening(false);
      notify("Микрофон недоступен. Попробуйте текст или демопример");
    }
  }

  const proposalSource =
    proposal && state.items.find((item) => item.id === proposal.sourceId);
  const proposalTarget =
    proposal && state.items.find((item) => item.id === proposal.targetId);
  const ProposalIcon = proposalTarget ? iconMap[proposalTarget.icon] : Check;

  return (
    <section className="assistant-screen">
      <header className="screen-topbar">
        <button className="icon-button" aria-label="Назад" onClick={onBack}>
          <ArrowLeft size={23} />
        </button>
        <h1>Помощник</h1>
        <span className="assistant-demo-label">Демо</span>
      </header>
      <div className="assistant-content">
        <p className="assistant-introduction">
          Запишите доход или расход голосом.
          <br />
          Или спросите о своих финансах.
        </p>
        <button
          className="assistant-demo-button"
          onClick={playDemo}
          disabled={demoPlaying || listening}
        >
          {demoPlaying ? (
            <LoaderCircle size={20} className="assistant-spin" />
          ) : (
            <AudioLines size={20} />
          )}
          <span>
            {demoPlaying
              ? "Показываю пример..."
              : "Попробовать голосовой пример"}
          </span>
          <ChevronRight size={18} />
        </button>
        <p className="assistant-demo-note">
          В макете фразы разбираются по простым правилам.
          <br />
          ИИ-сервис подключим после согласования.
        </p>
        <div className="assistant-suggestions">
          <button onClick={() => sendMessage("Сколько потратил на кафе?")}>
            Расходы на кафе
          </button>
          <button onClick={() => sendMessage("На что я трачу больше всего?")}>
            Основные расходы
          </button>
          {income && account && (
            <button
              onClick={() =>
                sendMessage(
                  `Получил ${income.name} 5000 рублей на ${account.name}`,
                )
              }
            >
              Записать доход
            </button>
          )}
        </div>
        <div className="assistant-messages" aria-live="polite">
          {messages.map((message) => (
            <div
              className={`assistant-message ${message.role}`}
              key={message.id}
            >
              <span>{message.role === "user" ? "Вы" : "Помощник"}</span>
              <p>{message.text}</p>
            </div>
          ))}
          {proposal && proposalSource && proposalTarget && (
            <div className="assistant-proposal">
              <div className="assistant-proposal-heading">
                <ProposalIcon size={21} />
                <span>Проверьте операцию</span>
              </div>
              <div className="assistant-proposal-route">
                <span>{proposalSource.name}</span>
                <ChevronRight size={16} />
                <span>{proposalTarget.name}</span>
              </div>
              <strong>
                {money(Math.round(Number(proposal.amount) * 100))}
              </strong>
              <div className="assistant-proposal-actions">
                <button onClick={() => setProposal(null)}>
                  <X size={18} />
                  Отменить
                </button>
                <button onClick={() => onReview(proposal)}>
                  <Check size={18} />
                  Проверить и сохранить
                </button>
              </div>
            </div>
          )}
          {(listening || demoPlaying) && (
            <div className="assistant-listening" role="status">
              <div className="assistant-waveform" aria-hidden="true">
                {waveHeights.map((height, index) => (
                  <i
                    key={index}
                    style={{ height, animationDelay: `${index * 0.06}s` }}
                  />
                ))}
              </div>
              <span>
                {demoPlaying
                  ? "Демонстрация голосовой записи"
                  : "Слушаю вас..."}
              </span>
            </div>
          )}
          <div ref={threadEndRef} className="assistant-thread-end" />
        </div>
      </div>
      <div className="assistant-composer-container">
        <form
          className="assistant-composer"
          onSubmit={(event) => {
            event.preventDefault();
            sendMessage(input);
          }}
        >
          <input
            aria-label="Сообщение помощнику"
            placeholder="Напишите или скажите"
            value={input}
            maxLength={1000}
            onChange={(event) => setInput(event.target.value)}
          />
          <button
            type="button"
            className={listening ? "recording" : ""}
            aria-label={listening ? "Остановить запись" : "Включить микрофон"}
            onClick={toggleMicrophone}
            disabled={demoPlaying}
          >
            <Mic size={23} />
          </button>
          <button
            type="submit"
            aria-label="Отправить сообщение"
            disabled={!input.trim()}
          >
            <Send size={21} />
          </button>
        </form>
        <p>Микрофон использует распознавание браузера</p>
      </div>
    </section>
  );
}
