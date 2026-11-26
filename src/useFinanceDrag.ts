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
// Зона у края списка расходов, в которой он сам прокручивается при переносе.
const SCROLL_EDGE = 56;
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
    let scrollFrame = 0;
    const timer = setTimeout(() => {
      active.current = { ...source, x: event.clientX, y: event.clientY };
      setDrag(active.current);
      navigator.vibrate?.(15);
    }, 230);
    function cleanup() {
      clearTimeout(timer);
      cancelAnimationFrame(scrollFrame);
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", end);
      window.removeEventListener("pointercancel", cancel);
      document
        .querySelectorAll(".drop-hover")
        .forEach((element) => element.classList.remove("drop-hover"));
    }
    function highlight(x: number, y: number) {
      document
        .querySelectorAll(".drop-hover")
        .forEach((element) => element.classList.remove("drop-hover"));
      const target = document
        .elementFromPoint(x, y)
        ?.closest<HTMLElement>("[data-drop]");
      if (
        target?.dataset.drop ===
        (source.kind === "income" ? "account" : "expense")
      )
        target.classList.add("drop-hover");
    }
    // Список расходов длиннее экрана: у верхнего и нижнего края он
    // прокручивается сам, пока палец держит счет.
    function autoScroll() {
      scrollFrame = 0;
      const point = active.current;
      const area = document.querySelector<HTMLElement>("[data-autoscroll]");
      if (!point || source.kind !== "account" || !area) return;
      const box = area.getBoundingClientRect();
      const visibleBottom =
        box.bottom - (parseFloat(getComputedStyle(area).paddingBottom) || 0);
      let step = 0;
      if (point.y > visibleBottom - SCROLL_EDGE)
        step = Math.min(14, (point.y - visibleBottom + SCROLL_EDGE) / 5);
      else if (point.y < box.top + SCROLL_EDGE && point.y > box.top - 40)
        step = -Math.min(14, (box.top + SCROLL_EDGE - point.y) / 5);
      if (!step) return;
      const before = area.scrollTop;
      area.scrollTop += step;
      if (area.scrollTop === before) return;
      highlight(point.x, point.y);
      scrollFrame = requestAnimationFrame(autoScroll);
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
      highlight(pointer.clientX, pointer.clientY);
      if (!scrollFrame) scrollFrame = requestAnimationFrame(autoScroll);
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
