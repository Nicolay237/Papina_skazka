export default function ErrorScreen({ message, onRetry }) {
  return (
    <section className="screen screen--center" role="alert">
      <p className="md-body-large status-text">{message}</p>
      <button type="button" className="md-button md-button--filled md-state" onClick={onRetry}>
        Попробовать снова
      </button>
    </section>
  );
}
