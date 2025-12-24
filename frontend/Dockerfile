FROM node:18-alpine

WORKDIR /app

# Устанавливаем curl для health check
RUN apk add --no-cache curl

# Копируем package.json
COPY package.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем весь код приложения
COPY . .

# Expose порт
EXPOSE 5173

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=3 --start-period=15s \
  CMD curl -f http://localhost:5173/ || exit 1

# Запуск dev сервера
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
