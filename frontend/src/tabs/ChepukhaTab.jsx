import { useEffect, useMemo, useState } from "react";
import { createStory } from "../api";
import Icon from "../components/Icon";
import TextField from "../components/TextField";
import ThemePicker from "../components/ThemePicker";
import PickScreen from "../components/PickScreen";
import LoadingScreen from "../components/LoadingScreen";
import ErrorScreen from "../components/ErrorScreen";
import StoryPage from "../components/StoryPage";

// Игра «Чепуха»: каждый отвечает на свой вопрос, не видя чужих ответов,
// и передаёт телефон дальше. В конце все вместе читают, что получилось.

const STAGE = {
  SETUP: "setup",
  HANDOFF: "handoff",
  QUESTION: "question",
  READY: "ready",
  LOADING: "loading",
  STORY: "story",
  ERROR: "error",
};

const MIN_PLAYERS = 2;

let nextPlayerId = 1;
const newPlayer = () => ({ id: nextPlayerId++, name: "" });

export default function ChepukhaTab({ meta, kid, notify }) {
  const slots = useMemo(
    () => meta.chepukha_slots.map((id) => meta.slots.find((s) => s.id === id)),
    [meta]
  );
  const maxPlayers = slots.length;

  const [stage, setStage] = useState(STAGE.SETUP);
  const [players, setPlayers] = useState(() => [newPlayer(), newPlayer(), newPlayer()]);
  const [themes, setThemes] = useState([]);
  const [turn, setTurn] = useState(0);
  const [answers, setAnswers] = useState({}); // slotId -> { text, label }
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [stage, turn]);

  const nameOf = (i) => players[i].name.trim() || `Игрок ${i + 1}`;
  const playerFor = (slotIndex) => slotIndex % players.length;
  const credits = Object.fromEntries(slots.map((s, i) => [s.id, nameOf(playerFor(i))]));

  function updatePlayer(id, name) {
    setPlayers((ps) => ps.map((p) => (p.id === id ? { ...p, name } : p)));
  }

  function startRound() {
    setAnswers({});
    setTurn(0);
    setResult(null);
    setStage(STAGE.HANDOFF);
  }

  function nextTurn() {
    if (turn === slots.length - 1) setStage(STAGE.READY);
    else {
      setTurn(turn + 1);
      setStage(STAGE.HANDOFF);
    }
  }

  async function reveal() {
    setStage(STAGE.LOADING);
    try {
      const data = await createStory({
        themes,
        include: slots.map((s) => s.id),
        answers: Object.fromEntries(Object.entries(answers).map(([slot, o]) => [slot, o.text])),
        kid,
      });
      setResult(data);
      setStage(STAGE.STORY);
    } catch (err) {
      setError(`Не удалось собрать сказку: ${err.message}.`);
      setStage(STAGE.ERROR);
    }
  }

  if (stage === STAGE.LOADING) return <LoadingScreen />;

  if (stage === STAGE.ERROR) {
    return <ErrorScreen message={error} onRetry={reveal} onCancel={() => setStage(STAGE.SETUP)} cancelLabel="К настройкам" />;
  }

  if (stage === STAGE.HANDOFF) {
    return (
      <section className="screen screen--center handoff">
        <p className="md-label-large handoff__step">
          Вопрос {turn + 1} из {slots.length}
        </p>
        <h1 className="md-display-small">{nameOf(playerFor(turn))}</h1>
        <p className="md-body-large status-text">Ваш ход. Остальные не подглядывают.</p>
        <button type="button" className="md-button md-button--filled md-button--large md-state" onClick={() => setStage(STAGE.QUESTION)}>
          Показать вопрос
        </button>
      </section>
    );
  }

  if (stage === STAGE.QUESTION) {
    const slot = slots[turn];
    return (
      <PickScreen
        key={`${slot.id}-${turn}`}
        slot={slot}
        themes={themes}
        kid={kid}
        index={turn + 1}
        total={slots.length}
        stepLabel={`Вопрос ${turn + 1} из ${slots.length}, отвечает ${nameOf(playerFor(turn))}`}
        selected={answers[slot.id] ?? null}
        onSelect={(option) => setAnswers((a) => ({ ...a, [slot.id]: option }))}
        onClear={() =>
          setAnswers((a) => {
            const { [slot.id]: _removed, ...rest } = a;
            return rest;
          })
        }
        onNext={nextTurn}
        nextLabel="Ответить"
      />
    );
  }

  if (stage === STAGE.READY) {
    return (
      <section className="screen screen--center">
        <h1 className="md-display-small">Все ответили</h1>
        <p className="md-body-large status-text">Соберитесь вместе и прочитайте сказку вслух.</p>
        <button type="button" className="md-button md-button--filled md-button--large md-state" onClick={reveal}>
          Читать сказку
        </button>
      </section>
    );
  }

  if (stage === STAGE.STORY) {
    return (
      <StoryPage
        result={result}
        notify={notify}
        credits={credits}
        onNew={startRound}
        newLabel="Сыграть ещё"
        onSettings={() => setStage(STAGE.SETUP)}
        settingsLabel="Сменить игроков"
      />
    );
  }

  return (
    <section className="screen setup">
      <header className="setup__hero">
        <h1 className="md-display-small">Чепуха</h1>
        <p className="md-body-large setup__lead">
          Каждый отвечает на свой вопрос и передаёт телефон следующему. Чужих ответов не видно до самого конца.
        </p>
      </header>

      <section className="setup__section" aria-labelledby="players-title">
        <div className="section-head">
          <h2 id="players-title" className="md-title-large">Игроки</h2>
        </div>
        <div className="players">
          {players.map((player, i) => (
            <TextField
              key={player.id}
              id={`player-${player.id}`}
              label={`Игрок ${i + 1}`}
              value={player.name}
              onChange={(name) => updatePlayer(player.id, name)}
              trailing={
                players.length > MIN_PLAYERS && (
                  <button
                    type="button"
                    className="md-icon-button md-state"
                    onClick={() => setPlayers((ps) => ps.filter((p) => p.id !== player.id))}
                    aria-label={`Убрать игрока ${i + 1}`}
                    title="Убрать игрока"
                  >
                    <Icon name="close" />
                  </button>
                )
              }
            />
          ))}
        </div>
        {players.length < maxPlayers && (
          <button
            type="button"
            className="md-button md-button--text md-state players__add"
            onClick={() => setPlayers((ps) => [...ps, newPlayer()])}
          >
            Добавить игрока
          </button>
        )}
      </section>

      <section className="setup__section" aria-labelledby="chepukha-themes-title">
        <ThemePicker themes={meta.themes} selected={themes} onChange={setThemes} headingId="chepukha-themes-title" />
      </section>

      <div className="setup__actions">
        <button type="button" className="md-button md-button--filled md-button--large md-state" onClick={startRound}>
          Начать игру
        </button>
      </div>
    </section>
  );
}
