const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function handleResponse(response) {
  if (!response.ok) {
    let detail = `Ошибка сервера (${response.status})`;
    try {
      const data = await response.json();
      if (data?.detail) detail = data.detail;
    } catch {
      // ответ без тела — оставляем сообщение по умолчанию
    }
    throw new Error(detail);
  }
  return response.json();
}

export async function generateRandomStory() {
  const response = await fetch(`${API_BASE}/api/generate/random`, {
    method: "POST",
  });
  const data = await handleResponse(response);
  return data.story;
}
