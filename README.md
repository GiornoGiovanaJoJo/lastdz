# GraphML Visualizer

Визуализация GraphML графов с валидацией на бэкенде и интерактивным отображением на фронтенде.

## Структура проекта

```
lastdz/
├── backend/          # FastAPI сервер
│   ├── main.py
│   ├── requirements.txt
│   └── sample.graphml
├── frontend/         # React + TypeScript
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── GraphView.tsx
│   │   └── styles.css
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
└── README.md
```

## Быстрый старт

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Backend запустится на **http://localhost:8000**

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend запустится на **http://localhost:5173**

## Функционал

✅ **Загрузка GraphML файлов**
✅ **Валидация на бэкенде:**
- XML валидация
- Проверка обязательных полей (label, type, kind, criticality)
- Проверка допустимых значений
- Проверка существования узлов в рёбрах

✅ **Визуализация графа:**
- Интерактивный граф с использованием vis-network
- Автоматический layout (force-directed)
- Использование x/y координат если присутствуют

✅ **Фильтрация:**
- По окружению (env: prod/stage/dev)
- По типу узла (service/db/cache/queue/external)
- По критичности ребра (high/medium/low)
- По тегам (поиск по строке)

✅ **Визуальные улучшения:**
- Тултипы при наведении
- Цветовая кодировка по типу узла
- Толщина и цвет ребра по критичности
- Стрелки, указывающие направление связи

## API

### POST `/api/graphml-to-json`

**Параметры:**
- `file` (multipart/form-data): GraphML файл

**Ответ:**
```json
{
  "nodes": [
    {
      "id": "api-gateway",
      "label": "API Gateway",
      "type": "service",
      "env": "prod",
      "domain": "platform",
      "tags": ["entrypoint", "auth", "rate-limit"],
      "tier": "edge",
      "x": 0,
      "y": 0
    }
  ],
  "edges": [
    {
      "id": "e1",
      "source": "api-gateway",
      "target": "auth-service",
      "label": "login/refresh",
      "kind": "sync",
      "protocol": "http",
      "criticality": "high",
      "weight": 2.0,
      "env": "prod",
      "tags": ["auth", "entry"]
    }
  ]
}
```

## Требования к GraphML

**Обязательные поля узлов:**
- `id` — уникальный идентификатор
- `label` — отображаемое имя
- `type` — тип узла (service, db, cache, queue, external)

**Обязательные поля рёбер:**
- `source` — ID исходящего узла
- `target` — ID целевого узла
- `label` — название связи
- `kind` — тип связи (sync, async, stream)
- `criticality` — критичность (low, medium, high)

**Опциональные поля:**
- `env` — окружение (prod, stage, dev)
- `domain`, `tier`, `protocol`, `weight`, `tags`, `x`, `y`

## Примеры использования

1. Откройте фронтенд на **http://localhost:5173**
2. Нажмите "Загрузить .graphml"
3. Выберите файл `backend/sample.graphml`
4. Граф визуализируется
5. Используйте фильтры для фильтрации по env, type, criticality, tags

## Валидация

Backend проверяет:
- ✅ Валидность XML
- ✅ Обязательные поля (label, type для nodes; kind, criticality для edges)
- ✅ Допустимые значения типов
- ✅ Существование узлов для каждого ребра
- ✅ Расширение файла (.graphml)

Если валидация не пройдена, возвращается ошибка 400 с описанием.

## Технологический стек

**Backend:**
- Python 3.9+
- FastAPI
- networkx (парсинг GraphML)
- lxml (XML валидация)

**Frontend:**
- React 18+ с TypeScript
- Vite
- vis-network (визуализация)
- axios (HTTP клиент)

## Лицензия

MIT
