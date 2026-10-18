import { useEffect, useState } from "react";
import Icon from "./Icon";
import Ornament from "./Ornament";

const SLOT_ICONS = {
  kto: "person",
  s_kem: "group",
  gde: "place",
  kogda: "schedule",
  chto_delali: "directions_run",
  lyudi_skazali: "forum",
  delo_konchilos: "flag",
};

export default function StoryPage({ result, onAgain, onSettings }) {
  const [snackbar, setSnackbar] = useState("");
  const [showPicks, setShowPicks] = useState(false);
  const [firstParagraph, ...restParagraphs] = result.paragraphs;
  const firstLetter = firstParagraph?.[0] ?? "";
  const restOfFirst = firstParagraph?.slice(1) ?? "";

  useEffect(() => {
    if (!snackbar) return undefined;
    const timer = setTimeout(() => setSnackbar(""), 2500);
    return () => clearTimeout(timer);
  }, [snackbar]);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(result.story);
      setSnackbar("Сказка скопирована");
    } catch {
      setSnackbar("Не получилось скопировать");
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
    <section className="screen story">
      <article className="story__paper">
        <Ornament className="story__ornament" />
        <p className="story__paragraph story__paragraph--first">
          <span className="story__dropcap">{firstLetter}</span>
          {restOfFirst}
        </p>
        {restParagraphs.map((paragraph, i) => (
          <p key={i} className="story__paragraph">
            {paragraph}
          </p>
        ))}
        <Ornament className="story__ornament story__ornament--bottom" />
      </article>

      <div className="story__actions">
        <button type="button" className="md-button md-button--filled md-state" onClick={onAgain}>
          <Icon name="autorenew" />
          Ещё одну
        </button>
        <button type="button" className="md-button md-button--tonal md-state" onClick={onSettings}>
          <Icon name="tune" />
          Изменить темы
        </button>
        <button type="button" className="md-button md-button--outlined md-state" onClick={handleCopy}>
          <Icon name="content_copy" />
          Копировать
        </button>
        <button type="button" className="md-button md-button--outlined md-state" onClick={handleDownload}>
          <Icon name="download" />
          Скачать
        </button>
      </div>

      <div className="md-card md-card--outlined story__picks">
        <button
          type="button"
          className="story__picks-header md-state"
          onClick={() => setShowPicks((v) => !v)}
          aria-expanded={showPicks}
        >
          <span className="md-title-medium">Из чего сложилась сказка</span>
          <Icon name="expand_more" className={`story__chevron${showPicks ? " story__chevron--open" : ""}`} />
        </button>
        {showPicks && (
          <>
            <hr className="md-divider" />
            <ul className="md-list">
              {result.picks.map((pick) => (
                <li key={pick.slot} className="md-list-item">
                  <Icon name={SLOT_ICONS[pick.slot] ?? "auto_stories"} className="md-list-item__icon" />
                  <span>
                    <span className="md-list-item__overline">{pick.title}</span>
                    <span className="md-list-item__headline">{pick.label}</span>
                  </span>
                </li>
              ))}
            </ul>
          </>
        )}
      </div>

      {snackbar && (
        <div className="md-snackbar" role="status">
          {snackbar}
        </div>
      )}
    </section>
  );
}
