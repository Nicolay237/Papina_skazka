import Icon from "./Icon";

// Разделы сайта — сегментированные кнопки Material 3 (по смыслу это вкладки).
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
    <div className="md-segmented" role="tablist" aria-label="Разделы" onKeyDown={onKeyDown}>
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
            className={`md-segment md-state${selected ? " md-segment--selected" : ""}`}
            onClick={() => onChange(tab.id)}
          >
            {selected && <Icon name="check" />}
            {tab.label}
          </button>
        );
      })}
    </div>
  );
}
