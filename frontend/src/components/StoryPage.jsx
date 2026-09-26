import { useState } from "react";
import Ornament from "./Ornament";
import "./StoryPage.css";

export default function StoryPage({ story, onRestart }) {
  const [copied, setCopied] = useState(false);
  const paragraphs = story.split("\n\n").filter(Boolean);
  const [firstParagraph, ...restParagraphs] = paragraphs;
  const firstLetter = firstParagraph?.[0] ?? "";
  const restOfFirst = firstParagraph?.slice(1) ?? "";

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(story);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // буфер обмена недоступен — молча игнорируем
    }
  }

  function handleDownload() {
    const blob = new Blob([story], { type: "text/plain;charset=utf-8" });
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
        <button type="button" className="ghost-button" onClick={handleCopy}>
          {copied ? "Скопировано" : "Скопировать текст"}
        </button>
        <button type="button" className="ghost-button" onClick={handleDownload}>
          Скачать .txt
        </button>
        <button type="button" className="primary-button" onClick={onRestart}>
          Ещё одну!
        </button>
      </div>
    </div>
  );
}
