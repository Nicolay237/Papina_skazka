// Пусто = тот же адрес, с которого открыт сайт (прокси Vite в dev, FastAPI в проде).
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

async function request(path, options) {
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, options);
  } catch {
    throw new Error("нет связи с сервером");
  }
  if (!response.ok) {
    let detail = `ошибка сервера (${response.status})`;
    try {
      const data = await response.json();
      if (typeof data?.detail === "string") detail = data.detail;
    } catch {
      // ответ без тела — оставляем сообщение по умолчанию
    }
    throw new Error(detail);
  }
  return response.json();
}

function post(path, body) {
  return request(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export const getMeta = () => request("/api/meta");

export const getOptions = ({ slot, themes, exclude = [], limit = 12 }) =>
  post("/api/options", { slot, themes, exclude, limit });

export const createStory = ({ themes, include, answers = {} }) =>
  post("/api/story", { themes, include, answers });
