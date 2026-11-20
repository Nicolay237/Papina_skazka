export default function ErrorScreen({ message, onRetry, retryLabel = "Попробовать снова", onCancel, cancelLabel }) {
  return (
    <section className="screen screen--center" role="alert">
      <p className="md-body-large status-text">{message}</p>
      <div className="screen__buttons">
        <button type="button" className="md-button md-button--filled md-state" onClick={onRetry}>
          {retryLabel}
        </button>
        {onCancel && (
          <button type="button" className="md-button md-button--text md-state" onClick={onCancel}>
            {cancelLabel}
          </button>
        )}
      </div>
    </section>
  );
}
