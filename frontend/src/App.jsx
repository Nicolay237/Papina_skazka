import { useState } from "react";
import { generateRandomStory } from "./api";
import WelcomeScreen from "./components/WelcomeScreen";
import LoadingScreen from "./components/LoadingScreen";
import ErrorScreen from "./components/ErrorScreen";
import StoryPage from "./components/StoryPage";
import "./App.css";

const STAGE = {
  WELCOME: "welcome",
  GENERATING: "generating",
  STORY: "story",
  ERROR: "error",
};

export default function App() {
  const [stage, setStage] = useState(STAGE.WELCOME);
  const [story, setStory] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  async function handleGenerate() {
    setStage(STAGE.GENERATING);
    try {
      const generated = await generateRandomStory();
      setStory(generated);
      setStage(STAGE.STORY);
    } catch (err) {
      setErrorMessage(
        `Не удалось получить сказку. Проверьте, что бэкенд запущен (${err.message}).`
      );
      setStage(STAGE.ERROR);
    }
  }

  if (stage === STAGE.WELCOME) {
    return <WelcomeScreen onStart={handleGenerate} />;
  }

  if (stage === STAGE.GENERATING) {
    return <LoadingScreen />;
  }

  if (stage === STAGE.STORY) {
    return <StoryPage story={story} onRestart={handleGenerate} />;
  }

  return <ErrorScreen message={errorMessage} onRetry={handleGenerate} />;
}
