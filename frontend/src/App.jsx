import { useCallback, useEffect, useState } from "react";
import { getMeta } from "./api";
import { codeFromLocation, setAddress } from "./share";
import TopAppBar from "./components/TopAppBar";
import Tabs from "./components/Tabs";
import LoadingScreen from "./components/LoadingScreen";
import ErrorScreen from "./components/ErrorScreen";
import StoryTab from "./tabs/StoryTab";
import ChepukhaTab from "./tabs/ChepukhaTab";

const TABS = [
  { id: "story", label: "Сказка" },
  { id: "chepukha", label: "Чепуха" },
];

const KID_MODE_KEY = "papina-skazka:kid-mode";

function readKidMode() {
  try {
    return window.localStorage.getItem(KID_MODE_KEY) !== "off"; // по умолчанию включён
  } catch {
    return true;
  }
}

export default function App() {
  const [meta, setMeta] = useState(null);
  const [metaError, setMetaError] = useState("");
  const [tab, setTab] = useState("story");
  const [kidMode, setKidMode] = useState(readKidMode);
  const [snackbar, setSnackbar] = useState(null); // { text, id }
  const [initialCode] = useState(codeFromLocation);
  const [storyCode, setStoryCode] = useState(null);

  const loadMeta = useCallback(() => {
    setMetaError("");
    getMeta()
      .then(setMeta)
      .catch((err) => setMetaError(`Не удалось загрузить копилку слов: ${err.message}.`));
  }, []);

  useEffect(() => {
    loadMeta();
  }, [loadMeta]);

  // адрес страницы — ссылка на открытую сказку
  useEffect(() => {
    setAddress(tab === "story" ? storyCode : null);
  }, [tab, storyCode]);

  useEffect(() => {
    if (!snackbar) return undefined;
    const timer = setTimeout(() => setSnackbar(null), 3000);
    return () => clearTimeout(timer);
  }, [snackbar]);

  const notify = useCallback((text) => setSnackbar({ text, id: Date.now() }), []);

  function changeKidMode(on) {
    setKidMode(on);
    try {
      window.localStorage.setItem(KID_MODE_KEY, on ? "on" : "off");
    } catch {
      // хранилище недоступно — режим просто не запомнится
    }
    notify(on ? "Детский режим включён" : "Детский режим выключен, возможны шутки для взрослых");
  }

  function changeTab(id) {
    setTab(id);
    window.scrollTo(0, 0);
  }

  let content;
  if (metaError) content = <ErrorScreen message={metaError} onRetry={loadMeta} />;
  else if (!meta) content = <LoadingScreen />;
  else {
    content = (
      <>
        <div id="panel-story" role="tabpanel" aria-labelledby="tab-story" className="tab-panel" hidden={tab !== "story"}>
          <StoryTab meta={meta} kid={kidMode} notify={notify} initialCode={initialCode} onCodeChange={setStoryCode} />
        </div>
        <div id="panel-chepukha" role="tabpanel" aria-labelledby="tab-chepukha" className="tab-panel" hidden={tab !== "chepukha"}>
          <ChepukhaTab meta={meta} kid={kidMode} notify={notify} />
        </div>
      </>
    );
  }

  return (
    <>
      <TopAppBar title="Папина сказка" kidMode={kidMode} onKidModeChange={changeKidMode}>
        <Tabs tabs={TABS} active={tab} onChange={changeTab} />
      </TopAppBar>
      <main className="app-main">{content}</main>
      {snackbar && (
        <div key={snackbar.id} className="md-snackbar" role="status">
          {snackbar.text}
        </div>
      )}
    </>
  );
}
