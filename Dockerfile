 FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Playwright browsers
RUN playwright install --with-deps chromium

COPY . .
RUN chmod +x run.sh

CMD ["python", "main.py"]