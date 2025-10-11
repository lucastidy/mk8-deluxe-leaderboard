FROM python:3.10-slim AS base

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

#default mode = prod (gunicorn)
ENV MODE=production

CMD ["gunicorn", "-b", "0.0.0.0:5000", "run:app"]