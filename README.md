# GraphML Visualizer

🎯 **Визуализация GraphML графов** с полной валидацией на бэкенде и интерактивным отображением на фронтенде.

![Status](https://img.shields.io/badge/status-complete-brightgreen)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![React](https://img.shields.io/badge/React-18+-61dafb)
![License](https://img.shields.io/badge/license-MIT-green)

## 🚀 Быстрый старт

### Backend (FastAPI)

```bash
cd backend

# Установка зависимостей
pip install -r requirements.txt

# Запуск сервера (порт 8000)
uvicorn main:app --reload --port 8000
```

### Frontend (React + TypeScript)

```bash
cd frontend

# Установка зависимостей
npm install

# Запуск dev сервера (порт 5173)
npm run dev
```

**Откройте браузер:** http://localhost:5173

---

## 📁 Структура проекта

```
lastdz/
├── backend/
│   ├── main.py                 # FastAPI приложение
│   ├── requirements.txt         # Python зависимости
│   └── sample.graphml          # Пример GraphML файла
├── frontend/
│   ├── src/
│   │   ├── main.tsx            # Entry point
│   │   ├── App.tsx             # Главный компонент
│   │   ├── GraphView.tsx        # Компонент визуализации
│   │   └── styles.css          # Глобальные стили
│   ├── index.html              # HTML шаблон
│   ├── package.json            # Node зависимости
│   ├── vite.config.ts          # Vite конфиг
│   └── tsconfig.json           # TypeScript конфиг
├── .gitignore
└── README.md
```

---

## ✨ Функционал

### 🔧 Backend

✅ **FastAPI + networkx**
- Парсинг GraphML файлов
- Валидация XML структуры
- Проверка обязательных полей
- Валидация типов и значений
- CORS поддержка

✅ **Валидация включает:**
```
• node.type ∈ {service, db, cache, queue, external}
• edge.kind ∈ {sync, async, stream}
• edge.criticality ∈ {low, medium, high}
• Проверка существования узлов для каждого ребра
• Проверка расширения файла (.graphml)
```

### 🎨 Frontend

✅ **React + TypeScript + vis-network**
- Загрузка и отправка GraphML файлов
- Интерактивная визуализация графа
- Force-directed layout (автоматический)
- Поддержка фиксированных координат (x, y)

✅ **Фильтрация:**
- По окружению (env): prod/stage/dev
- По типу узла: service/db/cache/queue/external
- По критичности ребра: high/medium/low
- По тегам (поиск по строке)

✅ **Интерактивность:**
- 🎯 Тултипы при наведении
- 🖱️ Drag & drop узлов
- 🔍 Zoom и pan
- ⌨️ Клавиатурные сокращения
- 🎨 Цветовая кодировка по типам и критичности
- ➡️ Стрелки, указывающие направление
- 📊 Легенда с объяснением цветов

---

## 📡 API

### POST `/api/graphml-to-json`

**Запрос:**
```bash
curl -X POST http://localhost:8000/api/graphml-to-json \
  -F "file=@backend/sample.graphml"
```

**Ответ (200):**
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

**Ошибка (400):**
```json
{
  "detail": "Node 'api-gateway' missing required field: label"
}
```

---

## 📋 Требования к GraphML

### Обязательные поля узла:
```xml
<node id="service-1">
  <data key="label">Service Name</data>
  <data key="type">service</data>
</node>
```

**Допустимые типы:** `service | db | cache | queue | external`

### Обязательные поля ребра:
```xml
<edge source="service-1" target="service-2">
  <data key="label">API Call</data>
  <data key="kind">sync</data>
  <data key="criticality">high</data>
</edge>
```

**Допустимые значения:**
- `kind`: `sync | async | stream`
- `criticality`: `low | medium | high`

### Опциональные поля:
```xml
<node id="service-1">
  <data key="env">prod</data>
  <data key="domain">platform</data>
  <data key="tier">edge</data>
  <data key="tags">entrypoint,auth,rate-limit</data>
  <data key="x">0</data>
  <data key="y">0</data>
</node>

<edge source="service-1" target="service-2">
  <data key="protocol">http</data>
  <data key="weight">2.0</data>
  <data key="env">prod</data>
  <data key="tags">auth,entry</data>
</edge>
```

---

## 🧪 Пример использования

1. **Откройте фронтенд:** http://localhost:5173
2. **Нажмите "Choose File"** и выберите `backend/sample.graphml`
3. **Граф загрузится и визуализируется** с микросервисной архитектурой
4. **Используйте фильтры** для фильтрации по env, type, criticality
5. **Наведите на узлы/ребра** для просмотра деталей
6. **Перетащите узлы** для перестановки (physics будет работать)

---

## 🛠️ Технологический стек

### Backend
- **Python 3.9+**
- **FastAPI** — современный веб-фреймворк
- **networkx** — парсинг GraphML
- **lxml** — XML валидация
- **uvicorn** — ASGI сервер

### Frontend
- **React 18** — UI библиотека
- **TypeScript** — типизация
- **Vite** — сборщик
- **vis-network** — визуализация графов
- **Axios** — HTTP клиент

---

## 📝 Валидация

Backend проверяет:

✅ **XML валидность** — парсится ли файл как корректный XML
✅ **Обязательные поля:**
  - Узлы: `label`, `type`
  - Ребра: `label`, `kind`, `criticality`

✅ **Допустимые значения:**
  - `node.type` из {service, db, cache, queue, external}
  - `edge.kind` из {sync, async, stream}
  - `edge.criticality` из {low, medium, high}

✅ **Целостность графа:**
  - Все `source` и `target` ребер существуют в узлах
  - Расширение файла `.graphml`

---

## 🐛 Решение проблем

### Backend не запускается
```bash
# Проверьте Python версию
python --version  # Должно быть 3.9+

# Переустановите зависимости
rm -rf venv
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows
pip install -r requirements.txt
```

### Frontend не загружается
```bash
# Очистите кэш и переустановите
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### CORS ошибка при загрузке файла
- ✅ Backend имеет CORS middleware
- ✅ Убедитесь, что backend запущен на http://localhost:8000
- ✅ Frontend должен быть на http://localhost:5173

### Граф не отображается после загрузки
- Проверьте console (F12) на ошибки
- Убедитесь, что GraphML файл валиден
- Проверьте response в Network tab

---

## 📊 Пример sample.graphml

Файл содержит микросервисную архитектуру:
- **API Gateway** → EntryPoint (edge)
- **Auth Service** → Security (core)
- **Orders Service** → Business logic (core)
- **Billing Service** → Payments (core)
- **PostgreSQL** → Data storage
- **Redis Cache** → Session storage
- **Kafka** → Event streaming
- **Analytics Worker** → ETL processing
- **External Payments** → Third-party integration

---

## 🎓 Для разработчиков

### Добавить новый тип узла

1. **Backend** (`backend/main.py`):
   ```python
   ALLOWED_NODE_TYPES = {"service", "db", "cache", "queue", "external", "new_type"}
   ```

2. **Frontend** (`frontend/src/GraphView.tsx`):
   ```typescript
   const typeColors: { [key: string]: string } = {
     // ...
     new_type: '#ffffff',
   };
   ```

### Кастомизировать визуализацию

Отредактируйте `GraphView.tsx`:
- `typeColors` — цвета узлов
- `criticalityColors` — цвета ребер
- `options` в `Network` — параметры физики и отображения

---

## 📄 Лицензия

MIT

---

## 📞 Контакты

Создано как тестовое задание по визуализации GraphML графов.

Стек: Python FastAPI + React TypeScript + vis-network
