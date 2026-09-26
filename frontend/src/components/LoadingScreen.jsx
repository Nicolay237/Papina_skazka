import Ornament from "./Ornament";
import "./LoadingScreen.css";

export default function LoadingScreen() {
  return (
    <div className="loading-screen">
      <div className="loading-screen__thread" aria-hidden="true" />
      <p className="loading-screen__text">Сказка сплетается из слов…</p>
      <Ornament className="loading-screen__ornament" />
    </div>
  );
}
