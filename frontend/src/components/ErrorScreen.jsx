import Icon from "./Icon";

export default function ErrorScreen({ message, onRetry }) {
  return (
    <section className="screen screen--center" role="alert">
      <div className="error-badge">
        <Icon name="error" />
      </div>
      <h1 className="md-headline-small">Сказка не сложилась</h1>
      <p className="md-body-medium status-text">{message}</p>
      <button type="button" className="md-button md-button--filled md-state" onClick={onRetry}>
        <Icon name="refresh" />
        Попробовать снова
      </button>
    </section>
  );
}
