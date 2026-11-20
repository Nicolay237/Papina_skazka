import Icon from "./Icon";

// Выбор тем: пустой список значит «все темы».
export default function ThemePicker({ themes, selected, onChange, headingId }) {
  const allThemes = selected.length === 0;

  function toggle(id) {
    onChange(selected.includes(id) ? selected.filter((t) => t !== id) : [...selected, id]);
  }

  return (
    <>
      <div className="section-head">
        <h2 id={headingId} className="md-title-large">Темы</h2>
        <button
          type="button"
          className={`md-chip md-state${allThemes ? " md-chip--selected" : ""}`}
          onClick={() => onChange([])}
          aria-pressed={allThemes}
        >
          {allThemes && <Icon name="check" />}
          Все темы
        </button>
      </div>
      <div className="theme-grid">
        {themes.map((theme) => {
          const on = selected.includes(theme.id);
          return (
            <button
              key={theme.id}
              type="button"
              className={`md-card md-card--outlined theme-card md-state${on ? " theme-card--selected" : ""}`}
              onClick={() => toggle(theme.id)}
              aria-pressed={on}
            >
              <span className="theme-card__text">
                <span className="md-title-medium">{theme.name}</span>
                {theme.description && <span className="md-body-medium theme-card__desc">{theme.description}</span>}
              </span>
              {on && <Icon name="check" className="theme-card__check" />}
            </button>
          );
        })}
      </div>
    </>
  );
}
