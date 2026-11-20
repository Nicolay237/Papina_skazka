import { useEffect, useRef, useState } from "react";
import { shareStory } from "../share";
import Icon from "./Icon";
import Ornament from "./Ornament";

/**
 * Страница готовой сказки.
 * credits — {slotId: имя игрока} для «Чепухи»; onContinue — дописать главу (если можно).
 */
export default function StoryPage({
  result,
  notify,
  credits = null,
  onContinue = null,
  continuing = false,
  onNew,
  newLabel,
  onSettings,
  settingsLabel,
}) {
  const [showPicks, setShowPicks] = useState(Boolean(credits));
  const chapterRefs = useRef([]);
  const shownChapters = useRef(result.chapters.length);

  // новая глава — плавно прокручиваем к ней
  useEffect(() => {
    if (result.chapters.length > shownChapters.current) {
      chapterRefs.current[result.chapters.length - 1]?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
    shownChapters.current = result.chapters.length;
  }, [result.chapters.length]);

  const firstParagraph = result.chapters[0][0];

  async function handleShare() {
    const message = await shareStory(result.code, firstParagraph);
    if (message) notify(message);
  }

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(result.story);
      notify("Сказка скопирована");
    } catch {
      notify("Не получилось скопировать");
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

  const manyChapters = result.chapters.length > 1;

  return (
    <section className="screen story">
      <article className="story__paper">
        <Ornament className="story__ornament" />
        {result.chapters.map((paragraphs, ci) => (
          <div key={ci} className="story__chapter" ref={(el) => (chapterRefs.current[ci] = el)}>
            {ci > 0 && <Ornament className="story__ornament story__ornament--divider" />}
            {paragraphs.map((paragraph, pi) =>
              ci === 0 && pi === 0 ? (
                <p key={pi} className="story__paragraph story__paragraph--first">
                  <span className="story__dropcap">{paragraph[0]}</span>
                  {paragraph.slice(1)}
                </p>
              ) : (
                <p key={pi} className="story__paragraph">
                  {paragraph}
                </p>
              )
            )}
          </div>
        ))}
        <Ornament className="story__ornament story__ornament--bottom" />
      </article>

      <div className="story__actions">
        {onContinue && result.can_continue && (
          <button
            type="button"
            className="md-button md-button--filled md-state"
            onClick={onContinue}
            disabled={continuing}
          >
            {continuing ? "Пишем продолжение…" : "Продолжить сказку"}
          </button>
        )}
        <button
          type="button"
          className={`md-button ${onContinue && result.can_continue ? "md-button--tonal" : "md-button--filled"} md-state`}
          onClick={handleShare}
        >
          <Icon name="share" />
          Поделиться
        </button>
      </div>

      <div className="story__actions story__actions--secondary">
        <button type="button" className="md-button md-button--outlined md-state" onClick={onNew}>
          {newLabel}
        </button>
        <button type="button" className="md-button md-button--text md-state" onClick={onSettings}>
          {settingsLabel}
        </button>
        <button type="button" className="md-icon-button md-state" onClick={handleCopy} aria-label="Копировать текст" title="Копировать текст">
          <Icon name="content_copy" />
        </button>
        <button type="button" className="md-icon-button md-state" onClick={handleDownload} aria-label="Скачать .txt" title="Скачать .txt">
          <Icon name="download" />
        </button>
      </div>

      <div className="md-card md-card--outlined story__picks">
        <button
          type="button"
          className="story__picks-header md-state"
          onClick={() => setShowPicks((v) => !v)}
          aria-expanded={showPicks}
        >
          <span className="md-title-medium">{credits ? "Кто что выбрал" : "Из чего сложилась сказка"}</span>
          <Icon name="expand_more" className={`story__chevron${showPicks ? " story__chevron--open" : ""}`} />
        </button>
        {showPicks && (
          <>
            <hr className="md-divider" />
            <ul className="md-list">
              {result.picks.map((pick, i) => (
                <li key={`${pick.chapter}-${pick.slot}`}>
                  {manyChapters && (i === 0 || result.picks[i - 1].chapter !== pick.chapter) && (
                    <p className="md-list-subheader">Глава {pick.chapter}</p>
                  )}
                  <div className="md-list-item">
                    <span className="md-list-item__content">
                      <span className="md-list-item__overline">{pick.title}</span>
                      <span className="md-list-item__headline">{pick.label}</span>
                    </span>
                    {credits?.[pick.slot] && <span className="md-list-item__trailing">{credits[pick.slot]}</span>}
                  </div>
                </li>
              ))}
            </ul>
          </>
        )}
      </div>
    </section>
  );
}
