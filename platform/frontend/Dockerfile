FROM node:22-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (using lock file for reproducible builds)
RUN npm ci

# Copy source files
COPY . .

# Build the application
RUN npm run build

# Production stage - serve with nginx
FROM nginx:alpine

# Used by the compose healthcheck; nginx:alpine does not guarantee curl across
# base-image updates.
RUN apk add --no-cache curl

# Copy built files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy pre-built wiki and download binaries if they exist in the build context.
# On a fresh clone without wiki/ or binaries/, the build creates empty placeholder
# dirs via the .dockerignore-safe pattern below. If the dirs exist, their contents
# are copied into the image.
# Wiki content is a single namespaced tree: wiki/range/<slug>/, wiki/course/<slug>/,
# and wiki/index.html. One COPY bakes it all in. The [i] glob keeps the build from
# failing on a fresh clone without the wiki/ dir.
# The workbook wiki lives in the wiki_data volume built by the wiki-builder
# service. Keep only a placeholder here so nginx has a file to serve before the
# first build.
RUN mkdir -p /usr/share/nginx/wiki /usr/share/nginx/downloads && \
    printf '%s\n' '<!doctype html><title>Workbook wiki</title><p>The workbook wiki has not been built yet. Run scripts/build-wiki.sh.</p>' > /usr/share/nginx/wiki/index.html
COPY binaries/ /usr/share/nginx/downloads/

# Copy nginx configuration (HTTP default + SSL variant)
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY nginx-ssl.conf /etc/nginx/conf.d/nginx-ssl.conf

# Entrypoint auto-detects TLS certs and swaps config
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 80 443

ENTRYPOINT ["/docker-entrypoint.sh"]

