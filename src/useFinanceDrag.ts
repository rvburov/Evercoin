import {
  useEffect,
  useRef,
  useState,
  type PointerEvent as ReactPointerEvent,
} from "react";
import type { OperationDraft } from "./data";
export interface DragSource {
  kind: "income" | "account";
  id: string;
  name: string;
}
export interface DragState extends DragSource {
  x: number;
  y: number;
}
export function useFinanceDrag(
  onDraft: (draft: Partial<OperationDraft>) => void,
  notify: (message: string) => void,
) {
  const [drag, setDrag] = useState<DragState | null>(null);
  const active = useRef<DragState | null>(null);
  const suppressedUntil = useRef(0);
  const cleanupRef = useRef<() => void>(() => {});
  useEffect(() => () => cleanupRef.current(), []);
  function beginDrag(event: ReactPointerEvent, source: DragSource) {
    if (event.button !== 0) return;
    cleanupRef.current();
    const timer = setTimeout(() => {
      active.current = { ...source, x: event.clientX, y: event.clientY };
      setDrag(active.current);
      navigator.vibrate?.(15);
    }, 230);
    function cleanup() {
      clearTimeout(timer);
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", end);
      window.removeEventListener("pointercancel", cancel);
      document
        .querySelectorAll(".drop-hover")
        .forEach((element) => element.classList.remove("drop-hover"));
    }
    function move(pointer: PointerEvent) {
      if (!active.current) {
        if (
          Math.hypot(
            pointer.clientX - event.clientX,
            pointer.clientY - event.clientY,
          ) > 8
        )
          clearTimeout(timer);
        return;
      }
      pointer.preventDefault();
      active.current = { ...source, x: pointer.clientX, y: pointer.clientY };
      setDrag(active.current);
      document
        .querySelectorAll(".drop-hover")
        .forEach((element) => element.classList.remove("drop-hover"));
      const target = document
        .elementFromPoint(pointer.clientX, pointer.clientY)
        ?.closest<HTMLElement>("[data-drop]");
      if (
        target?.dataset.drop ===
        (source.kind === "income" ? "account" : "expense")
      )
        target.classList.add("drop-hover");
    }
    function cancel() {
      cleanup();
      active.current = null;
      setDrag(null);
    }
    function end(pointer: PointerEvent) {
      const isActive = active.current;
      const target = document
        .elementFromPoint(pointer.clientX, pointer.clientY)
        ?.closest<HTMLElement>("[data-drop]");
      cancel();
      if (!isActive) return;
      suppressedUntil.current = Date.now() + 450;
      if (source.kind === "income" && target?.dataset.drop === "account")
        onDraft({ sourceId: source.id, targetId: target.dataset.id });
      else if (source.kind === "account" && target?.dataset.drop === "expense")
        onDraft({ sourceId: source.id, targetId: target.dataset.id });
      else
        notify(
          source.kind === "income"
            ? "Перенесите доход на счет"
            : "Перенесите счет на расход",
        );
    }
    window.addEventListener("pointermove", move, { passive: false });
    window.addEventListener("pointerup", end);
    window.addEventListener("pointercancel", cancel);
    cleanupRef.current = cleanup;
  }
  function allowClick() {
    return Date.now() > suppressedUntil.current;
  }
  return { drag, beginDrag, allowClick };
}
