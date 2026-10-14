import { useEffect, useRef, useState } from "react";
import { getOptions } from "../api";
import Ornament from "./Ornament";
import ProgressRail from "./ProgressRail";
import "./PickScreen.css";

export default function PickScreen({
  slot,
  themes,
  index,
  total,
  selected,
  onSelect,
  onClear,
  onBack,
  onNext,
  isLast,
}) {
  const [options, setOptions] = useState([]);
  const [totalInPool, setTotalInPool] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [round, setRound] = useState(0); // растёт при каждом «Перемешать»
  const seen = useRef([]);

  useEffect(() => {
    let cancelled = false;
    getOptions({ slot: slot.id, themes, exclude: seen.current })
      .then((data) => {
        if (cancelled) return;
        setOptions(data.options);
        setTotalInPool(data.total);
        seen.current = [...seen.current, ...data.options.map((o) => o.text)].slice(-200);
      })
      .catch((err) => !cancelled && setError(err.message))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [slot.id, themes, round]);

  function reshuffle() {
    setLoading(true);
    setError("");
    setRound((r) => r + 1);
  }

  // выбранная плитка не пропадает после «Перемешать»
  const shown =
    selected && !options.some((o) => o.text === selected.text) ? [selected, ...options] : options;

  return (
    <div className="pick">
      <Ornament className="pick__ornament" />

      <h1 className="pick__text">{slot.question}</h1>

      <div className="pick__options" aria-busy={loading}>
        {error && <p className="pick__error">Не удалось получить варианты: {error}</p>}
        {shown.map((option) => {
          const active = selected?.text === option.text;
          return (
            <button
              key={option.text}
              type="button"
              className={`word-tile${active ? " word-tile--active" : ""}${loading ? " word-tile--dim" : ""}`}
              onClick={() => onSelect(option)}
              aria-pressed={active}
            >
              {option.label}
            </button>
          );
        })}
      </div>

      <div className="pick__tools">
        <button type="button" className="ghost-button" onClick={reshuffle} disabled={loading}>
          ↻ Показать другие
        </button>
        {totalInPool > 0 && <span className="pick__count">всего вариантов: {totalInPool}</span>}
      </div>

      <div className="pick__nav">
        <button type="button" className="ghost-button" onClick={onBack}>
          Назад
        </button>
        {selected ? (
          <button type="button" className="primary-button" onClick={onNext}>
            {isLast ? "Дописать сказку" : "Дальше"}
          </button>
        ) : (
          <button type="button" className="primary-button" onClick={onNext}>
            Пусть решит случай
          </button>
        )}
      </div>
      {selected && (
        <button type="button" className="setup__link pick__reset" onClick={onClear}>
          Снять выбор — пусть решит случай
        </button>
      )}

      <ProgressRail current={index} total={total} />
    </div>
  );
}
