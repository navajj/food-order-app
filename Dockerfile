FROM python:3.11-slim

# Install Node.js for Tailwind build
RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Node deps and build Tailwind
COPY package.json package-lock.json ./
RUN npm install
COPY tailwind.config.js ./
COPY templates/ ./templates/
COPY static/ ./static/
RUN npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify

# Copy the rest of the app
COPY . .

# Run migrations and start server
RUN python manage.py migrate

EXPOSE 8000
CMD ["uvicorn", "food_order_project.asgi:application", "--host", "0.0.0.0", "--port", "8000"]