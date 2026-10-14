# Папина сказка

Генератор сказок в духе семейной «Чепухи»: выбираете темы (Сказочные, Мультики,
Космос, Школа, Страшилки…) и что войдёт в сказку (герой, спутник, место, время,
занятие, слова людей, концовка) — слова выпадают случайно или выбираются вручную.
В копилке больше 2000 фраз, герой согласуется с глаголами по роду и числу.

- `backend/` — FastAPI, банки фраз в `backend/app/data/*.txt`
- `frontend/` — React + Vite

## Запуск для разработки

Терминал 1:
```bash
cd backend
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
```

Терминал 2:
```bash
cd frontend
npm install
npm run dev
```

Откройте http://localhost:5173 (запросы `/api` Vite сам проксирует на порт 8000).

## Выкладка в прод (один процесс)

```bash
cd frontend && npm ci && npm run build      # появится frontend/dist
cd ../backend && pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Если `frontend/dist` существует, FastAPI отдаёт и сайт, и API с одного адреса — CORS
не нужен. Если фронтенд живёт на другом домене, задайте `ALLOWED_ORIGINS=https://ваш-домен`
для бэкенда и `VITE_API_BASE_URL=https://адрес-api` перед `npm run build`.
Перед uvicorn стоит поставить nginx или Caddy с HTTPS.

## Проверки

```bash
cd backend
python -m pytest                  # тесты генератора и API
python scripts/check_bank.py      # структура и орфография банков фраз
```

Формат банков и правила добавления фраз — в `backend/README.md`.
