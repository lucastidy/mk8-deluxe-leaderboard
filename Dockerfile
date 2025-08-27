FROM python:3.10-slim AS base

COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

#default mode = prod (gunicorn)
ENV MODE=production

CMD if [ "$MODE" = "development" ]; then \
        flask run --host=0.0.0.0 --reload; \
    else \
        gunicorn -b 0.0.0.0:5000 app:app --workers=4 --threads=2; \
    fi
