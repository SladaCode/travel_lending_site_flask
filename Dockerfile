# 1. Базовый образ Python
FROM python:3.12-slim

# 2. Рабочая папка внутри контейнера
WORKDIR /app

# 3. Копируем зависимости
COPY requirements.txt .

# 4. Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# 5. Копируем весь код
COPY . .

# 6. Открываем порт
EXPOSE 8000

# 7. Запускаем через gunicorn
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "explore:create_app()"]