import "./ErrorScreen.css";

export default function ErrorScreen({ message, onRetry }) {
  return (
    <div className="error-screen">
      <p className="error-screen__title">Сказка не сложилась</p>
      <p className="error-screen__message">{message}</p>
      <button type="button" className="primary-button" onClick={onRetry}>
        Попробовать снова
      </button>
    </div>
  );
}
