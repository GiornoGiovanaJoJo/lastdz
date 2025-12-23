# 🚀 Quickstart Guide

## Пререквизиты

- Python 3.9+ для backend
- Node.js 16+ для frontend
- pip и npm установлены

---

## 1️⃣ Terminal 1: Запустите Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Ожидаемые вывод:
```
INFO:     Application startup complete
INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

## 2️⃣ Terminal 2: Запустите Frontend

```bash
cd frontend
npm install
npm run dev
```

Окно браузера наотрится автоматически:
```
➡️  Local:   http://localhost:5173/
```

---

## 3️⃣ Откройте фронтенд

Перейдите по адресу: **http://localhost:5173**

---

## 4️⃣ Лодите тест GraphML

1. Нажмите **"Choose File"** кнопку
2. Выберите файл: `backend/sample.graphml`
3. Ожидайте и граф визуализируется

---

## 🎉 Готово!

Вы должны на экране увидеть:
- 📊 микросервисную архитектуру
- 🗐️ рабочие фильтры
- 🎯 интерактивные тултипы

---

## 🐛 Ошибки?

### Порты заняты

```bash
# Найти процесс на порте 8000
lsof -i :8000

# Остановить (максOS/Linux)
kill -9 <PID>
```

### CORS ошибка

- Проверьте, что backend работает на http://localhost:8000
- Проверьте Network tab в DevTools (F12)

### Проблемы с анализом

- Остановите оба сервера (Ctrl+C)
- Очистите кэш:
  ```bash
  rm -rf frontend/node_modules frontend/dist
  rm -rf backend/__pycache__ backend/*.pyc
  ```
- Переустановите и запустите снова

---

## 🏕️ Настройка (опционально)

### Письма в файлах скриптов

**backend/start.sh** (макос/Linux):
```bash
#!/bin/bash
cd backend
pip install -r requirements.txt 2>/dev/null || true
uvicorn main:app --reload --port 8000
```

**frontend/start.sh** (макос/Linux):
```bash
#!/bin/bash
cd frontend
npm install --legacy-peer-deps 2>/dev/null || true
npm run dev
```

После сохранения:
```bash
chmod +x backend/start.sh frontend/start.sh
```

---

## 📑 Дополнительно

- [📄 Полные README](./README.md)
- [💻 Тестовые API](http://localhost:8000/docs)
- [📍 GraphML спецификация](http://graphml.graphdrawing.org/)
