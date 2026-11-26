import { useEffect, useRef, type ReactNode } from "react";
import { ChevronLeft, X } from "lucide-react";
import { iconMap } from "./data";

export function Icon({ name, size = 24 }: { name: string; size?: number }) {
  const Component = iconMap[name] || iconMap.money;
  return <Component size={size} strokeWidth={1} aria-hidden="true" />;
}
export function ScreenHeader({
  title,
  onBack,
  action,
}: {
  title: string;
  onBack: () => void;
  action?: ReactNode;
}) {
  return (
    <header className="screen-topbar">
      <button className="icon-button" aria-label="Назад" onClick={onBack}>
        <ChevronLeft />
      </button>
      <h1>{title}</h1>
      <span className="topbar-action">{action}</span>
    </header>
  );
}
export function ActionSheet({
  title,
  children,
  onClose,
}: {
  title?: string;
  children: ReactNode;
  onClose: () => void;
}) {
  const sheetRef = useRef<HTMLElement>(null);
  const onCloseRef = useRef(onClose);
  onCloseRef.current = onClose;
  useEffect(() => {
    const previousFocus = document.activeElement as HTMLElement | null;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    sheetRef.current?.focus();
    function handleKey(event: KeyboardEvent) {
      if (event.key === "Escape") {
        event.stopPropagation();
        onCloseRef.current();
      }
      if (event.key !== "Tab") return;
      const controls = sheetRef.current?.querySelectorAll<HTMLElement>(
        "button, input, select, textarea",
      );
      if (!controls?.length) return;
      const first = controls[0];
      const last = controls[controls.length - 1];
      if (
        event.shiftKey &&
        (document.activeElement === first ||
          document.activeElement === sheetRef.current)
      ) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }
    window.addEventListener("keydown", handleKey, true);
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", handleKey, true);
      previousFocus?.focus();
    };
  }, []);
  return (
    <div className="sheet-backdrop" onClick={onClose}>
      <section
        className="action-sheet"
        ref={sheetRef}
        tabIndex={-1}
        role="dialog"
        aria-modal="true"
        aria-label={title || "Выберите действие"}
        onClick={(event) => event.stopPropagation()}
      >
        <div className="sheet-group">
          {title && <h2>{title}</h2>}
          {children}
        </div>
        <button className="sheet-option cancel" onClick={onClose}>
          Отмена
        </button>
      </section>
    </div>
  );
}

export function CloseButton({ onClick }: { onClick: () => void }) {
  return (
    <button className="icon-button" aria-label="Закрыть" onClick={onClick}>
      <X />
    </button>
  );
}
