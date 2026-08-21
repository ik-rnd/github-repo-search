FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Copy env file if it doesn't exist at runtime
COPY .env.example .env

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
