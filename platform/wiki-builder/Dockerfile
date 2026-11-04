FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Pinned to the toolchain used by the platform's docs build. Keep these in
# step with platform/backend/requirements-dev.txt.
RUN pip install --no-cache-dir \
    mkdocs==1.6.1 \
    mkdocs-material==9.8.0 \
    PyYAML==6.0.3

WORKDIR /builder
COPY build_wiki.py /builder/build_wiki.py

ENTRYPOINT ["python", "/builder/build_wiki.py"]
