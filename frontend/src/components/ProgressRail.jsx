import "./ProgressRail.css";

export default function ProgressRail({ current, total }) {
  const percent = Math.round((current / total) * 100);
  return (
    <div className="progress-rail" role="progressbar" aria-valuenow={current} aria-valuemin={1} aria-valuemax={total}>
      <div className="progress-rail__label">
        Шаг {current} из {total}
      </div>
      <div className="progress-rail__track">
        <div className="progress-rail__fill" style={{ width: `${percent}%` }} />
        <div className="progress-rail__spark" style={{ left: `${percent}%` }} />
      </div>
    </div>
  );
}
