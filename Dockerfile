FROM python:3.12-slim

# Рабочая директория внутри контейнера
WORKDIR /app

# Копируем зависимости и устанавливаем
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY . .

# trends.db и feeds.json будут монтироваться как volume —
# при запуске они не перезаписываются из образа
CMD ["python", "bot.py"]
