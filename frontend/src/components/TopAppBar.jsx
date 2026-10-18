import { useEffect, useState } from "react";
import Icon from "./Icon";

export default function TopAppBar({ title, onBack, backLabel = "Назад" }) {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 4);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header className={`md-top-app-bar${scrolled ? " md-top-app-bar--scrolled" : ""}`}>
      <div className="md-top-app-bar__slot">
        {onBack && (
          <button type="button" className="md-icon-button md-state" onClick={onBack} aria-label={backLabel} title={backLabel}>
            <Icon name="arrow_back" />
          </button>
        )}
      </div>
      <p className="md-top-app-bar__title">{title}</p>
      <div className="md-top-app-bar__slot" />
    </header>
  );
}
