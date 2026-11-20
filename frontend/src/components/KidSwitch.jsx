import Icon from "./Icon";

// Переключатель Material 3 с иконкой на ползунке: галочка — включено, крестик — выключено.
export default function KidSwitch({ checked, onChange }) {
  return (
    <label className={`kid-switch${checked ? " kid-switch--on" : ""}`}>
      <span className="kid-switch__label">
        <span className="kid-switch__label-long">Детский режим</span>
        <span className="kid-switch__label-short">Детский</span>
      </span>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        aria-label="Детский режим"
        className="md-switch"
        onClick={() => onChange(!checked)}
      >
        <span className="md-switch__handle md-state">
          <Icon name={checked ? "check" : "close"} />
        </span>
      </button>
    </label>
  );
}
