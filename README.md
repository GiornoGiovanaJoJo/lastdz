# GraphML Visualizer

Приложение для визуализации и валидации GraphML файлов графов.

## 🚀 Быстрый старт

```bash
# Запуск через Docker Compose
docker compose up
```

## 📌 Доступ

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/docs

## 📦 Структура

```
├── backend/           # FastAPI приложение
│   ├── main.py        # REST API, GraphML обработка
│   ├── requirements.txt
│   ├── Dockerfile
│   └── sample.graphml
├── frontend/          # Vite + TypeScript
│   ├── src/           # React компоненты
│   ├── index.html
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml # Оркестрация сервисов
└── README.md
```

## 🛠 Локальная разработка

### Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## 🔧 Технологии

- **Backend**: FastAPI, NetworkX, Colorama
- **Frontend**: React, TypeScript, Vite
- **DevOps**: Docker, Docker Compose

## 📝 API

Полная документация: http://localhost:8000/docs

### Основные endpoints

- `POST /upload` - Загрузка GraphML файла
- `GET /graph` - Получение данных графа
- `GET /docs` - Swagger документация

## ✅ Функционал

- ✓ Загрузка и парсинг GraphML файлов
- ✓ Визуализация графов
- ✓ Валидация структуры
- ✓ API документация
- ✓ Docker поддержка
