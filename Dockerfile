FROM python:3.12-slim

ARG FINTRA_VERSION=dev
ARG SOURCE_URL=https://github.com/OWNER/fintra

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FINTRA_VERSION=${FINTRA_VERSION}

LABEL org.opencontainers.image.title="Fintra" \
      org.opencontainers.image.description="Self-hosted personal finance tracker" \
      org.opencontainers.image.source="${SOURCE_URL}" \
      org.opencontainers.image.version="${FINTRA_VERSION}"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

RUN mkdir -p /app/data /app/app/static/vendor

# Chart.js is downloaded once while the container image is built.
# The running Fintra container needs no external frontend resources.
ADD https://cdn.jsdelivr.net/npm/chart.js@4.5.1/dist/chart.umd.min.js /app/app/static/vendor/chart.umd.min.js

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD ["python","-c","import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=3).read()"]

CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8080"]
