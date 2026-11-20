// Ссылки на сказку: /s/<код>. Код целиком описывает сказку, сервер ничего не хранит.

export const SHARE_PREFIX = "/s/";

export function storyUrl(code) {
  return `${window.location.origin}${SHARE_PREFIX}${code}`;
}

/** Код сказки из адреса страницы, если открыта ссылка /s/<код>. */
export function codeFromLocation() {
  const { pathname } = window.location;
  if (!pathname.startsWith(SHARE_PREFIX)) return null;
  const code = decodeURIComponent(pathname.slice(SHARE_PREFIX.length)).replace(/\/+$/, "");
  return code || null;
}

export function setAddress(code) {
  const path = code ? `${SHARE_PREFIX}${code}` : "/";
  if (window.location.pathname !== path) window.history.replaceState(null, "", path);
}

/**
 * Системное меню «Поделиться» на телефоне, иначе — копирование ссылки.
 * Возвращает текст для уведомления или null, если человек сам закрыл меню.
 */
export async function shareStory(code, firstParagraph) {
  const url = storyUrl(code);
  if (navigator.share) {
    try {
      await navigator.share({ title: "Папина сказка", text: firstParagraph, url });
      return null;
    } catch (err) {
      if (err?.name === "AbortError") return null;
      // не получилось — пробуем скопировать
    }
  }
  try {
    await navigator.clipboard.writeText(url);
    return "Ссылка на сказку скопирована";
  } catch {
    return "Не получилось скопировать ссылку";
  }
}
