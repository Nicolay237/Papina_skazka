import Ornament from "./Ornament";
import ProgressRail from "./ProgressRail";
import "./QuestionScreen.css";

export default function QuestionScreen({
  question,
  index,
  total,
  selected,
  onSelect,
  onNext,
  onBack,
  isFirst,
}) {
  return (
    <div className="question-screen">
      <Ornament className="question-screen__ornament" />

      <h1 className="question-screen__text">{question.text}</h1>

      <div className="question-screen__options">
        {question.options.map((word) => {
          const isActive = word === selected;
          return (
            <button
              key={word}
              type="button"
              className={`word-tile${isActive ? " word-tile--active" : ""}`}
              onClick={() => onSelect(word)}
              aria-pressed={isActive}
            >
              {word}
            </button>
          );
        })}
      </div>

      <div className="question-screen__nav">
        <button
          type="button"
          className="ghost-button"
          onClick={onBack}
          disabled={isFirst}
        >
          Назад
        </button>
        <button
          type="button"
          className="primary-button"
          onClick={onNext}
          disabled={!selected}
        >
          {index === total ? "Дописать сказку" : "Дальше"}
        </button>
      </div>

      <ProgressRail current={index} total={total} />
    </div>
  );
}
