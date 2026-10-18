export default function LoadingScreen() {
  return (
    <section className="screen screen--center" role="status" aria-live="polite">
      <svg className="md-circular-progress" viewBox="0 0 48 48" aria-hidden="true">
        <circle cx="24" cy="24" r="20" />
      </svg>
      <p className="md-body-large status-text">Сказка сплетается из слов…</p>
    </section>
  );
}
