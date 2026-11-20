import Icon from "./Icon";
import ThemePicker from "./ThemePicker";

export default function SetupScreen({
  meta,
  themes,
  onThemesChange,
  optionalSlots,
  onOptionalSlotsChange,
  onRandom,
  onPick,
}) {
  function toggleSlot(id) {
    const next = new Set(optionalSlots);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    onOptionalSlotsChange(next);
  }

  return (
    <section className="screen setup">
      <header className="setup__hero">
        <h1 className="md-display-small">Какую сказку сочиним?</h1>
        <p className="md-body-large setup__lead">В копилке {meta.total.toLocaleString("ru-RU")} фраз.</p>
      </header>

      <section className="setup__section" aria-labelledby="themes-title">
        <ThemePicker themes={meta.themes} selected={themes} onChange={onThemesChange} headingId="themes-title" />
      </section>

      <section className="setup__section" aria-labelledby="parts-title">
        <div className="section-head">
          <h2 id="parts-title" className="md-title-large">Что войдёт в сказку</h2>
        </div>
        <div className="parts-grid">
          {meta.groups.map((group) => (
            <div key={group.id} className="parts-group">
              <h3 className="md-label-large parts-group__title">{group.title}</h3>
              <div className="md-chip-set">
                {meta.slots
                  .filter((s) => s.group === group.id)
                  .map((slot) => {
                    const on = slot.required || optionalSlots.has(slot.id);
                    return (
                      <button
                        key={slot.id}
                        type="button"
                        className={`md-chip md-state${on ? " md-chip--selected" : ""}`}
                        onClick={() => toggleSlot(slot.id)}
                        aria-pressed={on}
                        disabled={slot.required}
                        title={slot.required ? "Без этого сказки не бывает" : undefined}
                      >
                        {on && <Icon name="check" />}
                        {slot.title}
                      </button>
                    );
                  })}
              </div>
            </div>
          ))}
        </div>
      </section>

      <div className="setup__actions">
        <button type="button" className="md-button md-button--filled md-button--large md-state" onClick={onRandom}>
          Собери мне сказку
        </button>
        <button type="button" className="md-button md-button--tonal md-button--large md-state" onClick={onPick}>
          Выберу сам
        </button>
      </div>
    </section>
  );
}
