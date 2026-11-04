FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY app.py /app/app.py

# The target is intentionally small and dependency-free. Run it unprivileged
# and read-only; the compose file drops every capability as well.
RUN useradd --create-home --uid 10001 --shell /usr/sbin/nologin appuser

USER 10001
EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/', timeout=2)" || exit 1

CMD ["python", "/app/app.py"]
