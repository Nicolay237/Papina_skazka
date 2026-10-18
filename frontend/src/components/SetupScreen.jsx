import Icon from "./Icon";

export default function SetupScreen({
  meta,
  themes,
  onThemesChange,
  optionalSlots,
  onOptionalSlotsChange,
  onRandom,
  onPick,
}) {
  const allThemes = themes.length === 0;

  function toggleTheme(id) {
    onThemesChange(themes.includes(id) ? themes.filter((t) => t !== id) : [...themes, id]);
  }

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
        <p className="md-body-large setup__lead">
          Выберите темы и части сказки. Слова выпадут случайно из копилки
          в {meta.total.toLocaleString("ru-RU")} фраз — или выберите каждое сами.
        </p>
      </header>

      <section className="setup__section" aria-labelledby="themes-title">
        <div className="section-head">
          <h2 id="themes-title" className="md-title-large">Темы</h2>
          <button
            type="button"
            className={`md-chip md-state${allThemes ? " md-chip--selected" : ""}`}
            onClick={() => onThemesChange([])}
            aria-pressed={allThemes}
          >
            {allThemes && <Icon name="check" />}
            Все темы
          </button>
        </div>
        <div className="theme-grid">
          {meta.themes.map((theme) => {
            const selected = themes.includes(theme.id);
            return (
              <button
                key={theme.id}
                type="button"
                className={`md-card md-card--outlined theme-card md-state${selected ? " theme-card--selected" : ""}`}
                onClick={() => toggleTheme(theme.id)}
                aria-pressed={selected}
              >
                <span className="theme-card__icon">
                  <Icon name={theme.icon} filled={selected} />
                </span>
                <span className="theme-card__text">
                  <span className="md-title-medium">{theme.name}</span>
                  <span className="md-body-medium theme-card__desc">{theme.description}</span>
                </span>
                {selected && <Icon name="check" className="theme-card__check" />}
              </button>
            );
          })}
        </div>
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
          <Icon name="auto_awesome" />
          Собери мне сказку
        </button>
        <button type="button" className="md-button md-button--tonal md-button--large md-state" onClick={onPick}>
          <Icon name="touch_app" />
          Выберу сам
        </button>
      </div>
    </section>
  );
}
