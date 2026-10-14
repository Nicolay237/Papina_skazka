import { useCallback, useEffect, useMemo, useState } from "react";
import { createStory, getMeta } from "./api";
import SetupScreen from "./components/SetupScreen";
import PickScreen from "./components/PickScreen";
import LoadingScreen from "./components/LoadingScreen";
import ErrorScreen from "./components/ErrorScreen";
import StoryPage from "./components/StoryPage";
import "./App.css";

const STAGE = {
  LOADING_META: "loading-meta",
  SETUP: "setup",
  PICK: "pick",
  GENERATING: "generating",
  STORY: "story",
  ERROR: "error",
};

export default function App() {
  const [stage, setStage] = useState(STAGE.LOADING_META);
  const [meta, setMeta] = useState(null);
  const [error, setError] = useState({ message: "", answers: null }); // answers === null — ошибка загрузки копилки

  // настройки сказки
  const [themes, setThemes] = useState([]); // пусто = все темы
  const [optionalSlots, setOptionalSlots] = useState(new Set()); // включённые необязательные части
  // ручной выбор
  const [pickIndex, setPickIndex] = useState(0);
  const [answers, setAnswers] = useState({}); // slotId -> { text, label }

  const [result, setResult] = useState(null);

  const loadMeta = useCallback(async () => {
    setStage(STAGE.LOADING_META);
    try {
      const data = await getMeta();
      setMeta(data);
      setOptionalSlots(new Set(data.slots.filter((s) => !s.required).map((s) => s.id)));
      setStage(STAGE.SETUP);
    } catch (err) {
      setError({ message: `Не удалось загрузить копилку слов: ${err.message}.`, answers: null });
      setStage(STAGE.ERROR);
    }
  }, []);

  useEffect(() => {
    loadMeta();
  }, [loadMeta]);

  // новый экран всегда открывается с начала страницы
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [stage, pickIndex]);

  const activeSlots = useMemo(
    () => (meta ? meta.slots.filter((s) => s.required || optionalSlots.has(s.id)) : []),
    [meta, optionalSlots]
  );

  const generate = useCallback(
    async (manualAnswers = {}) => {
      setStage(STAGE.GENERATING);
      try {
        const data = await createStory({
          themes,
          include: activeSlots.map((s) => s.id),
          answers: manualAnswers,
        });
        setResult(data);
        setStage(STAGE.STORY);
      } catch (err) {
        setError({ message: `Не удалось собрать сказку: ${err.message}.`, answers: manualAnswers });
        setStage(STAGE.ERROR);
      }
    },
    [themes, activeSlots]
  );

  function startPicking() {
    setAnswers({});
    setPickIndex(0);
    setStage(STAGE.PICK);
  }

  function finishPicking() {
    const manual = Object.fromEntries(
      Object.entries(answers).map(([slot, option]) => [slot, option.text])
    );
    generate(manual);
  }

  if (stage === STAGE.LOADING_META || stage === STAGE.GENERATING) {
    return <LoadingScreen />;
  }

  if (stage === STAGE.ERROR) {
    return (
      <ErrorScreen
        message={error.message}
        onRetry={() => (error.answers === null ? loadMeta() : generate(error.answers))}
      />
    );
  }

  if (stage === STAGE.PICK) {
    const slot = activeSlots[pickIndex];
    const isLast = pickIndex === activeSlots.length - 1;
    return (
      <PickScreen
        key={slot.id}
        slot={slot}
        themes={themes}
        index={pickIndex + 1}
        total={activeSlots.length}
        selected={answers[slot.id] ?? null}
        onSelect={(option) => setAnswers((a) => ({ ...a, [slot.id]: option }))}
        onClear={() =>
          setAnswers((a) => {
            const { [slot.id]: _removed, ...rest } = a;
            return rest;
          })
        }
        onBack={() => (pickIndex === 0 ? setStage(STAGE.SETUP) : setPickIndex(pickIndex - 1))}
        onNext={() => (isLast ? finishPicking() : setPickIndex(pickIndex + 1))}
        isLast={isLast}
      />
    );
  }

  if (stage === STAGE.STORY) {
    return (
      <StoryPage
        result={result}
        onAgain={() => generate({})}
        onSettings={() => setStage(STAGE.SETUP)}
      />
    );
  }

  return (
    <SetupScreen
      meta={meta}
      themes={themes}
      onThemesChange={setThemes}
      optionalSlots={optionalSlots}
      onOptionalSlotsChange={setOptionalSlots}
      onRandom={() => generate({})}
      onPick={startPicking}
    />
  );
}
