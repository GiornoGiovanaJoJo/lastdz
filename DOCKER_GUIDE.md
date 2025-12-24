# 🐳 Docker Compose Guide

Полное руководство по запуску проекта через Docker Compose.

## Предварительные требования

- **Docker**: [Скачать и установить](https://www.docker.com/products/docker-desktop)
- **Docker Compose**: Обычно идёт в комплекте с Docker Desktop
- **OS**: macOS, Linux или Windows (с WSL 2)

### Проверка установки

```bash
docker --version
docker compose version
```

## 🚀 Быстрый старт

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/GiornoGiovanaJoJo/lastdz.git
cd lastdz
```

### 2. Создайте `.env` файлы (опционально)

```bash
# Frontend
cp frontend/.env.example frontend/.env

# Backend (если нужно)
echo "PYTHONUNBUFFERED=1" > backend/.env
```

### 3. Запустите приложение

```bash
docker compose up
```

### 4. Откройте в браузере

- **Frontend**: http://localhost:5173
- **Backend API Docs**: http://localhost:8000/docs
- **Backend Swagger**: http://localhost:8000/docs

## 📋 Основные команды

### Запуск в фоновом режиме

```bash
docker compose up -d
```

### Просмотр логов

```bash
# Все сервисы
docker compose logs -f

# Конкретный сервис
docker compose logs -f backend
docker compose logs -f frontend

# Последние 100 строк
docker compose logs --tail=100
```

### Остановка приложения

```bash
# Остановить контейнеры (данные сохранены)
docker compose stop

# Остановить и удалить контейнеры
docker compose down

# Остановить, удалить контейнеры и очистить volumes
docker compose down -v
```

### Перестройка образов

```bash
# Полная пересборка без кеша
docker compose up --build --no-cache

# Пересборка с кешем
docker compose up --build
```

### Запуск определённого сервиса

```bash
# Только backend
docker compose up backend

# Только frontend
docker compose up frontend
```

### Доступ к контейнеру

```bash
# Backend (Python shell)
docker compose exec backend /bin/bash

# Frontend (Node shell)
docker compose exec frontend /bin/sh

# Запуск команды в контейнере
docker compose exec backend python -V
docker compose exec frontend npm --version
```

## 🔍 Проверка статуса

### Просмотр запущенных контейнеров

```bash
docker compose ps
```

**Вывод:**
```
NAME              COMMAND                 SERVICE     STATUS
graphml-backend   python main.py          backend     Up 2 minutes (healthy)
graphml-frontend  npm run dev             frontend    Up 2 minutes (healthy)
```

### Проверка использования ресурсов

```bash
docker compose stats
```

## 🔧 Устранение проблем

### Backend не запускается

```bash
# Проверьте логи
docker compose logs backend

# Очистите и пересборите
docker compose down -v
docker compose build --no-cache backend
docker compose up backend
```

### Frontend не может подключиться к Backend

1. Убедитесь, что backend запущен:
```bash
docker compose ps
```

2. Проверьте, доступен ли backend на http://localhost:8000/docs

3. Проверьте CORS настройки в `backend/main.py`

### Порты уже заняты

```bash
# Если 8000 или 5173 уже заняты, измените в docker-compose.yml
# Например, вместо 8000:8000 используйте 8001:8000
```

### Нужно очистить всё и начать заново

```bash
# Удаляет контейнеры, образы и volumes
docker compose down -v
docker system prune -a

# Затем снова запустите
docker compose up
```

## 📦 Структура проекта в контейнерах

```
Containers:
├── graphml-backend
│   ├── Python 3.11
│   ├── FastAPI
│   └── /app (backend код)
│
└── graphml-frontend
    ├── Node.js 18
    ├── Vite
    └── /app (frontend код)
```

## 🌐 Сетевая конфигурация

### Внутренняя сеть

- Сервисы доступны друг другу по имени хоста
- Frontend → Backend: `http://backend:8000`
- Backend → Frontend: `http://frontend:5173`

### Внешний доступ

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

## 📝 Примеры использования

### Разработка в контейнерах

```bash
# Запустить и сразу видеть изменения
docker compose up

# В другом терминале — редактируйте файлы
# Код будет перезагружаться автоматически
```

### Деплой на сервер

```bash
# На удалённом сервере
git clone https://github.com/GiornoGiovanaJoJo/lastdz.git
cd lastdz

# Запустить в продакшене
docker compose up -d

# Проверить статус
docker compose ps

# Просмотреть логи
docker compose logs -f
```

## 📊 Мониторинг

### Просмотр использования памяти и CPU

```bash
# Режиме реального времени
docker compose stats

# Один раз
docker compose stats --no-stream
```

### Проверка health status

```bash
docker compose ps
# Смотрим колонку STATUS
```

## 🔐 Security

### Использовать `.env` для секретов

```bash
# .env
BACKEND_SECRET_KEY=your-secret-key
FRONTEND_API_KEY=your-api-key
```

### Не коммитить `.env` в git

```bash
# .gitignore
.env
.env.local
```

## 📚 Дополнительные ресурсы

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Vite Documentation](https://vitejs.dev/)

## 🎯 Что дальше?

1. ✅ Запустили приложение через Docker Compose
2. 📝 Создайте `.env` файлы для конфигурации
3. 🧪 Протестируйте API через http://localhost:8000/docs
4. 🎨 Откройте Frontend на http://localhost:5173
5. 🚀 Готово к разработке!

---

**Вопросы?** Смотрите логи или проверьте раздел "Устранение проблем" выше.
