import { useState } from "react";
import Ornament from "./Ornament";
import "./StoryPage.css";

export default function StoryPage({ result, onAgain, onSettings }) {
  const [copied, setCopied] = useState(false);
  const [showPicks, setShowPicks] = useState(false);
  const [firstParagraph, ...restParagraphs] = result.paragraphs;
  const firstLetter = firstParagraph?.[0] ?? "";
  const restOfFirst = firstParagraph?.slice(1) ?? "";

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(result.story);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // буфер обмена недоступен — молча игнорируем
    }
  }

  function handleDownload() {
    const blob = new Blob([result.story], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "moya-skazka.txt";
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="story-page">
      <div className="story-page__book">
        <Ornament className="story-page__ornament" />
        <p className="story-page__paragraph story-page__paragraph--first">
          <span className="story-page__dropcap">{firstLetter}</span>
          {restOfFirst}
        </p>
        {restParagraphs.map((paragraph, i) => (
          <p key={i} className="story-page__paragraph">
            {paragraph}
          </p>
        ))}
        <Ornament className="story-page__ornament story-page__ornament--bottom" />
      </div>

      <div className="story-page__actions">
        <button type="button" className="primary-button" onClick={onAgain}>
          Ещё одну!
        </button>
        <button type="button" className="ghost-button" onClick={onSettings}>
          Изменить темы
        </button>
        <button type="button" className="ghost-button" onClick={handleCopy}>
          {copied ? "Скопировано" : "Скопировать"}
        </button>
        <button type="button" className="ghost-button" onClick={handleDownload}>
          Скачать .txt
        </button>
      </div>

      <div className="story-page__picks">
        <button
          type="button"
          className="story-page__picks-toggle"
          onClick={() => setShowPicks((v) => !v)}
          aria-expanded={showPicks}
        >
          {showPicks ? "Спрятать, из чего сложилась сказка" : "Из чего сложилась сказка"}
        </button>
        {showPicks && (
          <dl className="story-page__picks-list">
            {result.picks.map((pick) => (
              <div key={pick.slot} className="story-page__pick">
                <dt>{pick.title}</dt>
                <dd>{pick.label}</dd>
              </div>
            ))}
          </dl>
        )}
      </div>
    </div>
  );
}
