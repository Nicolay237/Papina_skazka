import { useEffect, useState } from "react";
import KidSwitch from "./KidSwitch";

export default function TopAppBar({ title, kidMode, onKidModeChange, children }) {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 4);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header className={`app-header${scrolled ? " app-header--scrolled" : ""}`}>
      <div className="md-top-app-bar">
        <p className="md-top-app-bar__title">{title}</p>
        <KidSwitch checked={kidMode} onChange={onKidModeChange} />
      </div>
      {children}
    </header>
  );
}
