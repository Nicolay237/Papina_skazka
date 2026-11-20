// Текстовое поле Material 3 (outlined) с видимой подписью.
export default function TextField({ id, label, value, onChange, maxLength = 30, trailing = null }) {
  return (
    <div className="md-text-field">
      <input
        id={id}
        className="md-text-field__input"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        maxLength={maxLength}
        placeholder=" "
        autoComplete="off"
      />
      <label htmlFor={id} className="md-text-field__label">{label}</label>
      {trailing && <span className="md-text-field__trailing">{trailing}</span>}
    </div>
  );
}
