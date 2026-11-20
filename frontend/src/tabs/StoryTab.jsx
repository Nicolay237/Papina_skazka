import { useCallback, useEffect, useMemo, useState } from "react";
import { continueStory, createStory, openStory } from "../api";
import SetupScreen from "../components/SetupScreen";
import PickScreen from "../components/PickScreen";
import LoadingScreen from "../components/LoadingScreen";
import ErrorScreen from "../components/ErrorScreen";
import StoryPage from "../components/StoryPage";

const STAGE = {
  SETUP: "setup",
  PICK: "pick",
  LOADING: "loading",
  STORY: "story",
  ERROR: "error",
};

export default function StoryTab({ meta, kid, notify, initialCode, onCodeChange }) {
  const [stage, setStage] = useState(initialCode ? STAGE.LOADING : STAGE.SETUP);
  const [error, setError] = useState(null); // { message, answers }; answers === null — повторять нечего

  const [themes, setThemes] = useState([]); // пусто = все темы
  const [optionalSlots, setOptionalSlots] = useState(
    () => new Set(meta.slots.filter((s) => !s.required).map((s) => s.id))
  );
  const [pickIndex, setPickIndex] = useState(0);
  const [answers, setAnswers] = useState({}); // slotId -> { text, label }

  const [result, setResult] = useState(null);
  const [continuing, setContinuing] = useState(false);

  const activeSlots = useMemo(
    () => meta.slots.filter((s) => s.required || optionalSlots.has(s.id)),
    [meta, optionalSlots]
  );
  const include = useMemo(() => activeSlots.map((s) => s.id), [activeSlots]);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [stage, pickIndex]);

  useEffect(() => {
    onCodeChange(stage === STAGE.STORY && result ? result.code : null);
  }, [stage, result, onCodeChange]);

  const showStory = useCallback((data) => {
    setResult(data);
    setStage(STAGE.STORY);
  }, []);

  const generate = useCallback(
    async (manualAnswers = {}) => {
      setStage(STAGE.LOADING);
      try {
        showStory(await createStory({ themes, include, answers: manualAnswers, kid }));
      } catch (err) {
        setError({ message: `Не удалось собрать сказку: ${err.message}.`, answers: manualAnswers });
        setStage(STAGE.ERROR);
      }
    },
    [themes, include, kid, showStory]
  );

  // открыта ссылка /s/<код>
  useEffect(() => {
    if (!initialCode) return;
    openStory(initialCode)
      .then(showStory)
      .catch((err) => {
        setError({ message: `${err.message}.`, answers: null });
        setStage(STAGE.ERROR);
      });
  }, [initialCode, showStory]);

  async function handleContinue() {
    setContinuing(true);
    try {
      setResult(await continueStory({ code: result.code, themes, include, kid }));
    } catch (err) {
      notify(`Не удалось продолжить: ${err.message}`);
    } finally {
      setContinuing(false);
    }
  }

  function startPicking() {
    setAnswers({});
    setPickIndex(0);
    setStage(STAGE.PICK);
  }

  function finishPicking() {
    generate(Object.fromEntries(Object.entries(answers).map(([slot, option]) => [slot, option.text])));
  }

  if (stage === STAGE.LOADING) return <LoadingScreen />;

  if (stage === STAGE.ERROR) {
    const canRetry = error.answers !== null; // ошибка ссылки повтором не лечится
    return (
      <ErrorScreen
        message={error.message}
        onRetry={canRetry ? () => generate(error.answers) : () => setStage(STAGE.SETUP)}
        retryLabel={canRetry ? "Попробовать снова" : "Собрать новую сказку"}
        onCancel={canRetry ? () => setStage(STAGE.SETUP) : undefined}
        cancelLabel="К настройкам"
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
        kid={kid}
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
        nextLabel={isLast ? "Дописать сказку" : "Дальше"}
      />
    );
  }

  if (stage === STAGE.STORY) {
    return (
      <StoryPage
        result={result}
        notify={notify}
        onContinue={handleContinue}
        continuing={continuing}
        onNew={() => generate({})}
        newLabel="Новая сказка"
        onSettings={() => setStage(STAGE.SETUP)}
        settingsLabel="Изменить темы"
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
