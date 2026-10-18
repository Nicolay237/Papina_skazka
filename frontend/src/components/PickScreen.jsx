import { useEffect, useRef, useState } from "react";
import { getOptions } from "../api";
import Icon from "./Icon";

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
  const [round, setRound] = useState(0); // растёт при каждом «Показать другие»
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

  // выбранный вариант не пропадает после «Показать другие»
  const shown =
    selected && !options.some((o) => o.text === selected.text) ? [selected, ...options] : options;
  const percent = Math.round((index / total) * 100);

  return (
    <section className="screen pick">
      <div className="pick__progress">
        <span className="md-label-large pick__step">
          Шаг {index} из {total} · {slot.title}
        </span>
        <div
          className="md-linear-progress"
          role="progressbar"
          aria-valuenow={index}
          aria-valuemin={1}
          aria-valuemax={total}
          aria-label="Прогресс"
        >
          <div className="md-linear-progress__bar" style={{ width: `${percent}%` }} />
        </div>
      </div>

      <h1 className="md-headline-medium pick__question">{slot.question}</h1>

      {error && (
        <p className="md-body-medium pick__error">
          <Icon name="error" className="md-icon--small" />
          Не удалось получить варианты: {error}
        </p>
      )}

      <div className={`md-chip-set pick__options${loading ? " pick__options--loading" : ""}`} aria-busy={loading}>
        {shown.map((option) => {
          const active = selected?.text === option.text;
          return (
            <button
              key={option.text}
              type="button"
              className={`md-chip md-chip--phrase md-state${active ? " md-chip--selected" : ""}`}
              onClick={() => (active ? onClear() : onSelect(option))}
              aria-pressed={active}
            >
              {active && <Icon name="check" />}
              {option.label}
            </button>
          );
        })}
      </div>

      <div className="pick__tools">
        <button type="button" className="md-button md-button--text md-state" onClick={reshuffle} disabled={loading}>
          <Icon name="refresh" />
          Показать другие
        </button>
        {totalInPool > 0 && (
          <span className="md-body-small pick__count">Всего вариантов: {totalInPool}</span>
        )}
      </div>

      <footer className="pick__nav">
        <button type="button" className="md-button md-button--text md-state" onClick={onBack}>
          <Icon name="arrow_back" />
          Назад
        </button>
        {selected ? (
          <button type="button" className="md-button md-button--filled md-state" onClick={onNext}>
            {isLast ? "Дописать сказку" : "Дальше"}
            <Icon name={isLast ? "auto_stories" : "arrow_forward"} />
          </button>
        ) : (
          <button type="button" className="md-button md-button--tonal md-state" onClick={onNext}>
            <Icon name="casino" />
            Пусть решит случай
          </button>
        )}
      </footer>
    </section>
  );
}
