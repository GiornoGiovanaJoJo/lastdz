FROM node:18-alpine AS build

WORKDIR /app

# Копируем package.json
COPY package.json package-lock.json ./

# Устанавливаем зависимости
RUN npm ci

# Копируем код приложения
COPY . .

# Стадия разработки
FROM node:18-alpine AS dev

WORKDIR /app

# Копируем зависимости из билд-стеджа
COPY --from=build /app .

# Устанавливаем curl для health check
RUN apk add --no-cache curl

# Expose порт
EXPOSE 5173

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=3 --start-period=15s \
  CMD curl -f http://localhost:5173/ || exit 1

# Запуск dev сервера
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
