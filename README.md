# MeetMatch AI

**MeetMatch AI** — интеллектуальный сервис нетворкинга для конференций, хакатонов и профессиональных событий. Система помогает участникам находить релевантных собеседников, менторов, кофаундеров и работодателей на основе умного детерминированного мэтчинга навыков, интересов, опыта и целей.

---

## 📁 Структура репозитория

```text
MeetMatchAi/
├── backend/                  # Python / FastAPI микросервис
│   ├── app/                  # Исходный код приложения
│   │   ├── routes/           # Маршруты API (health, match, profile, feedback, telegram)
│   │   ├── services/         # Сервисный слой (логика Telegram и др.)
│   │   ├── config.py         # Настройки и чтение переменных окружения
│   │   ├── database.py       # Подключение к SQLite / SQLAlchemy
│   │   ├── errors.py         # Единые обработчики ошибок
│   │   ├── main.py           # Инициализация FastAPI приложения и CORS
│   │   ├── matching.py       # Алгоритм детерминированного мэтчинга (TF-IDF + Jaccard)
│   │   ├── models.py         # SQLAlchemy модели базы данных
│   │   ├── schemas.py        # Pydantic v2 схемы валидации
│   │   └── security.py       # Аутентификация (Supabase JWT / Bot API key)
│   ├── data/                 # Набор данных синтетических кандидатов (profiles.json)
│   ├── scripts/              # Вспомогательные скрипты (generate_profiles.py)
│   ├── tests/                # Тесты бэкенда (pytest)
│   ├── .dockerignore         # Исключения для сборки Docker
│   ├── .env.example          # Шаблон переменных окружения бэкенда
│   ├── Dockerfile            # Контейнеризация бэкенда
│   ├── BACKEND_SPEC.md       # Спецификация бэкенда
│   ├── README.md             # Документация бэкенда
│   └── requirements.txt      # Зависимости Python
│
├── frontend/                 # React 19 + TypeScript + Vite + Tailwind CSS
│   ├── public/               # Статические ресурсы (иконки, фавикон)
│   ├── src/                  # Исходный код интерфейса
│   │   ├── components/       # UI-компоненты (формы, карточки мэтчей, кольцо совместимости)
│   │   ├── contexts/         # React Context (AuthContext, MatchesContext)
│   │   ├── hooks/            # Пользовательские хуки (useAuth, useMatches, useI18n)
│   │   ├── i18n/             # Мультиязычность (RU, KK, EN)
│   │   ├── lib/              # Утилиты, валидация и чтение env
│   │   ├── pages/            # Страницы (Onboarding, Matches, Dashboard, Profile, Auth)
│   │   ├── services/         # API-клиент, интеграция с Supabase и mockApi
│   │   ├── styles/           # Tailwind CSS и глобальные стили
│   │   └── types/            # TypeScript интерфейсы и контракты
│   ├── .env.example          # Шаблон переменных окружения фронтенда
│   ├── FRONTEND_SPEC.md      # Спецификация фронтенда
│   ├── VERIFICATION.md       # Чек-лист проверки и критерии готовности
│   ├── README.md             # Документация фронтенда
│   └── package.json          # Зависимости и скрипты Node.js
│
├── .gitignore                # Согласованные правила игнорирования Git для всего проекта
└── README.md                 # Корневая документация
```

---

## ⚙️ Переменные окружения (.env)

### Бэкенд (`backend/.env`)

Создайте файл `backend/.env` на основе `backend/.env.example`:

```bash
cd backend
cp .env.example .env
```

| Переменная | Описание | Значение по умолчанию / Пример |
|---|---|---|
| `ENV` | Режим работы (`dev`, `test`, `prod`) | `dev` |
| `DATABASE_URL` | Строка подключения к базе данных SQLAlchemy | `sqlite:///./data/meetmatch.db` |
| `CORS_ORIGINS` | Разрешённые origins через запятую | `http://localhost:5173,http://127.0.0.1:5173` |
| `SUPABASE_JWT_SECRET` | Секретный ключ для проверки JWT токенов Supabase (HS256) | `replace-me` |
| `BOT_API_KEY` | API-ключ для авторизации Telegram-бота (`X-Bot-Key`) | `replace-me` |
| `DEV_AUTH_BYPASS` | Обход авторизации для разработки (только при `ENV=dev`) | `false` |
| `PROFILES_PATH` | Путь к JSON-файлу синтетических кандидатов | `data/profiles.json` |

### Фронтенд (`frontend/.env`)

Создайте файл `frontend/.env` на основе `frontend/.env.example`:

```bash
cd frontend
cp .env.example .env
```

| Переменная | Описание | Значение по умолчанию / Пример |
|---|---|---|
| `VITE_API_BASE_URL` | Базовый URL бэкенда (оставьте пустым для авто-mock демо) | `http://localhost:8000` |
| `VITE_API_URL` | Альтернативный алиас для базового URL бэкенда | `http://localhost:8000` |
| `VITE_USE_MOCK_API` | Принудительное включение/отключение mock-режима | `false` |
| `VITE_SUPABASE_URL` | URL инстанса Supabase Auth (опционально, для полной авторизации) | `https://xxxx.supabase.co` |
| `VITE_SUPABASE_ANON_KEY` | Публичный анонимный ключ Supabase | `eyJh...` |

> 💡 **Примечание**: Если `VITE_API_BASE_URL` (или `VITE_API_URL`) не задан или пуст, фронтенд автоматически работает в демонстрационном офлайн-режиме с баннером **DEMO**. Для прямого подключения к работающему бэкенду укажите `VITE_API_BASE_URL=http://localhost:8000` и `VITE_USE_MOCK_API=false`.

---

## 🚀 Быстрый запуск

### 1. Запуск бэкенда (FastAPI)

Требуется Python 3.11+.

```bash
# Переходим в директорию бэкенда
cd backend

# Создаём и активируем виртуальное окружение
# Windows (PowerShell):
python -m venv .venv
.venv\Scripts\Activate.ps1
# Linux / macOS:
# python3 -m venv .venv
# source .venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt

# Создаём .env файл
cp .env.example .env

# (Опционально) Регенерируем детерминированный синтетический датасет (180 профилей, seed 42)
python scripts/generate_profiles.py --out data/profiles.json

# Запускаем сервер FastAPI
uvicorn app.main:app --reload --port 8000
```

Сервер бэкенда будет доступен по адресу:
- API & Health: [http://localhost:8000/api/health](http://localhost:8000/api/health)
- Интерактивная Swagger-документация: [http://localhost:8000/docs](http://localhost:8000/docs)
- OpenAPI JSON: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

### 2. Запуск фронтенда (React + Vite)

Требуется Node.js 18+ (рекомендуется Node.js 20+).

```bash
# В отдельном терминале переходим в директорию фронтенда
cd frontend

# Устанавливаем зависимости
npm install

# Создаём .env файл
cp .env.example .env
# Для работы с реальным локальным бэкендом раскомментируйте или укажите:
# VITE_API_BASE_URL=http://localhost:8000
# VITE_USE_MOCK_API=false

# Запускаем dev-сервер Vite
npm run dev
```

Интерфейс будет доступен по адресу: [http://localhost:5173](http://localhost:5173) (или [http://127.0.0.1:5173](http://127.0.0.1:5173)).

---

## 🔗 Интеграция и согласованность API

В объединённом проекте обеспечена полная взаимная совместимость между фронтендом и бэкендом:

1. **Базовый URL и CORS**:
   - Фронтенд поддерживает как `VITE_API_BASE_URL`, так и `VITE_API_URL`.
   - Бэкенд по умолчанию разрешает CORS-запросы с `http://localhost:5173` и `http://127.0.0.1:5173` с передачей credentials.
2. **Эндпоинт `/api/match`**:
   - Бэкенд принимает как канонические имена (`skills`, `experience_years`, `bio`), так и алиасы фронтенда (`stack`, `experience`, `about`) через Pydantic `AliasChoices`.
   - Поддерживаются и взаимно маппятся все цели:
     - `find_job` ↔ `hire`
     - `find_mentor` ↔ `be_mentor` / `offer_mentorship`
     - `find_cofounder` ↔ `find_investor` / `exchange_experience`
   - Валидатор фронтенда корректно нормализует цели из ответа бэкенда.
3. **Эндпоинт `/api/feedback`**:
   - Бэкенд принимает как `like`/`dislike`, так и `met`/`not_fit`.
   - Фронтенд транслирует действия пользователя и сохраняет статус карточек.
4. **Эндпоинт `/api/profile/me` (`GET`, `PUT`)**:
   - Бэкенд сохраняет и возвращает персональные данные (`email`, `phone`, `age`, `city`) и профессиональные поля.
   - Клиент фронтенда адаптирует структуру профиля (`personal` + `professional`).
5. **Эндпоинт `/api/telegram/link`**:
   - Бэкенд генерирует одноразовый 8-значный код (`XXXX-XXXX`) со сроком жизни 10 минут и возвращает поля `code`, `expires_in` и `expires_in_seconds`.
6. **Единый формат ошибок**:
   - Ошибки валидации (422) и HTTP-ошибки содержат как структурированный блок `error: {code, message, details}`, так и поле `detail` для совместимости со стандартными клиентами FastAPI.

---

## 🧪 Тестирование

### Тесты бэкенда
```bash
cd backend
python -m pytest
```
*Запускает 11 тестов: проверка healthcheck, валидации контракта ошибок, ранжирования топ-5 кандидатов, детерминированности, конфиденциальности персональных данных и генератора датасета.*

### Тесты и сборка фронтенда
```bash
cd frontend
# Запуск unit-тестов
npm test

# Проверка TypeScript и production-сборка
npm run build
```
*Запускает 21 тест (Vitest) на валидацию шагов анкеты, контракт API, обработку сетевых ошибок и демо-режим.*

---

## 🐳 Запуск в Docker

Для быстрого запуска всего проекта (и бэкенда на `http://localhost:8000`, и фронтенда на `http://localhost:5173`) одной командой используйте `docker-compose.yml`:

```bash
docker compose up --build
```

Для изолированного запуска только бэкенда можно использовать `backend/Dockerfile`:

```bash
cd backend
docker build -t meetmatch-backend .
docker run -p 8000:8000 -e CORS_ORIGINS="http://localhost:5173,http://127.0.0.1:5173" meetmatch-backend
```
