# Генератор сказок

Полноценное веб-приложение: нажимаешь 1 кнопку и получаешь связную сказку, на основе игры в чепуху.

- `backend/` — FastAPI + pymorphy3, банки слов в JSON, вся морфология
- `frontend/` — React (Vite), пошаговый интерфейс и книжная страница
  с итоговой сказкой

## Быстрый запуск

Терминал 1:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Терминал 2:
```bash
cd frontend
npm install
npm run dev
```

Откройте адрес, который выведет Vite (обычно http://localhost:5173).

Подробности — в README внутри каждой папки.
