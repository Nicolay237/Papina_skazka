// Иконка Material Symbols Rounded. Набор иконок подгружается в index.html —
// новую иконку нужно дописать в параметр icon_names (по алфавиту).
export default function Icon({ name, filled = false, className = "" }) {
  return (
    <span
      className={`md-icon${filled ? " md-icon--filled" : ""}${className ? ` ${className}` : ""}`}
      aria-hidden="true"
    >
      {name}
    </span>
  );
}
