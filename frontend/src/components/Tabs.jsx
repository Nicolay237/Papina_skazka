// Основные вкладки Material 3.
export default function Tabs({ tabs, active, onChange }) {
  function onKeyDown(event) {
    const index = tabs.findIndex((t) => t.id === active);
    const step = event.key === "ArrowRight" ? 1 : event.key === "ArrowLeft" ? -1 : 0;
    if (!step) return;
    event.preventDefault();
    const next = tabs[(index + step + tabs.length) % tabs.length];
    onChange(next.id);
    document.getElementById(`tab-${next.id}`)?.focus();
  }

  return (
    <div className="md-tabs" role="tablist" onKeyDown={onKeyDown}>
      {tabs.map((tab) => {
        const selected = tab.id === active;
        return (
          <button
            key={tab.id}
            id={`tab-${tab.id}`}
            type="button"
            role="tab"
            aria-selected={selected}
            aria-controls={`panel-${tab.id}`}
            tabIndex={selected ? 0 : -1}
            className={`md-tab md-state${selected ? " md-tab--active" : ""}`}
            onClick={() => onChange(tab.id)}
          >
            <span className="md-tab__label">
              {tab.label}
              <span className="md-tab__indicator" />
            </span>
          </button>
        );
      })}
    </div>
  );
}
