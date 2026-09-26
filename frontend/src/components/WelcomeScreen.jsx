import Ornament from "./Ornament";
import "./WelcomeScreen.css";

export default function WelcomeScreen({ onStart }) {
  return (
    <div className="welcome-screen">
      <p className="welcome-screen__eyebrow">Папина сказка</p>
      <h1 className="welcome-screen__title">Сказка из случайных слов</h1>
      <Ornament className="welcome-screen__ornament" />
      <p className="welcome-screen__lead">
        Никаких вопросов — просто нажми кнопку. Фразы выпадут случайно
        из копилки семейной «Чепухи», а сказка сама сложится в единую
        (хоть и абсурдную) историю.
      </p>
      <button type="button" className="primary-button" onClick={onStart}>
        Собери мне сказку
      </button>
    </div>
  );
}
