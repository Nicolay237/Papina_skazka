import Ornament from "./Ornament";
import "./SetupScreen.css";

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
    <div className="setup">
      <header className="setup__header">
        <p className="setup__eyebrow">Папина сказка</p>
        <h1 className="setup__title">Какую сказку сочиним?</h1>
        <Ornament className="setup__ornament" />
        <p className="setup__lead">
          Выберите, о чём будет сказка, и что в неё войдёт. Слова выпадут
          случайно из копилки в {meta.total.toLocaleString("ru-RU")} фраз — или выберите
          каждое сами.
        </p>
      </header>

      <section className="setup__section" aria-labelledby="themes-title">
        <div className="setup__section-head">
          <h2 id="themes-title" className="setup__section-title">О чём сказка</h2>
          <button
            type="button"
            className={`setup__link${allThemes ? " setup__link--on" : ""}`}
            onClick={() => onThemesChange([])}
            aria-pressed={allThemes}
          >
            {allThemes ? "Все темы сразу ✓" : "Выбрать все темы"}
          </button>
        </div>
        <div className="setup__themes">
          {meta.themes.map((theme) => {
            const active = themes.includes(theme.id);
            return (
              <button
                key={theme.id}
                type="button"
                className={`theme-card${active ? " theme-card--active" : ""}`}
                onClick={() => toggleTheme(theme.id)}
                aria-pressed={active}
              >
                <span className="theme-card__emoji" aria-hidden="true">{theme.emoji}</span>
                <span className="theme-card__name">{theme.name}</span>
                <span className="theme-card__desc">{theme.description}</span>
              </button>
            );
          })}
        </div>
      </section>

      <section className="setup__section" aria-labelledby="parts-title">
        <div className="setup__section-head">
          <h2 id="parts-title" className="setup__section-title">Что войдёт в сказку</h2>
        </div>
        <div className="setup__groups">
          {meta.groups.map((group) => (
            <div key={group.id} className="parts-group">
              <h3 className="parts-group__title">{group.title}</h3>
              <div className="parts-group__chips">
                {meta.slots
                  .filter((s) => s.group === group.id)
                  .map((slot) => {
                    const on = slot.required || optionalSlots.has(slot.id);
                    return (
                      <button
                        key={slot.id}
                        type="button"
                        className={`part-chip${on ? " part-chip--on" : ""}`}
                        onClick={() => !slot.required && toggleSlot(slot.id)}
                        aria-pressed={on}
                        disabled={slot.required}
                        title={slot.required ? "Без этого сказки не бывает" : undefined}
                      >
                        <span className="part-chip__mark" aria-hidden="true">{on ? "✓" : ""}</span>
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
        <button type="button" className="primary-button" onClick={onRandom}>
          Собери мне сказку
        </button>
        <button type="button" className="ghost-button" onClick={onPick}>
          Выберу сам
        </button>
      </div>
    </div>
  );
}
