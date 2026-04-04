FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY environment/ ./environment/
COPY server/ ./server/
COPY app.py .

EXPOSE 7860

# Run the server app
CMD ["python", "-c", "from server.app import main; main()"]
