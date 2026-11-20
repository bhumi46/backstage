# Backstage backend image (also serves the frontend through app-backend).
# Host build: run `yarn install --immutable && yarn tsc && yarn build:backend` first, then from the repo root:
#   docker build . -f packages/backend/Dockerfile -t ghcr.io/bhumi46/backstage:<sha>

FROM node:24-trixie-slim@sha256:af02d57b57719b9657a45199a79264a9437940cd55b3c7b3fc99615654f124a0

# libsqlite3-dev: better-sqlite3 fallback. python3 + venv: TechDocs builds docs in the pod
# (techdocs.generator.runIn: local), because there is no Docker inside the cluster.
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends libsqlite3-dev python3 python3-venv && \
    rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv "$VIRTUAL_ENV" && \
    "$VIRTUAL_ENV/bin/pip" install --no-cache-dir mkdocs-techdocs-core==1.7.1
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# From here on run as the unprivileged node user (uid 1000).
USER node
WORKDIR /app

COPY --chown=node:node .yarn ./.yarn
COPY --chown=node:node .yarnrc.yml ./
COPY --chown=node:node backstage.json ./

ENV NODE_ENV=production
# Default is 2G; keep the heap inside the pod's 1Gi memory limit.
ENV NODE_OPTIONS="--max-old-space-size=768"

# Package skeleton first, so dependency install is cached unless package.json files change.
COPY --chown=node:node yarn.lock package.json packages/backend/dist/skeleton.tar.gz ./
RUN tar xzf skeleton.tar.gz && rm skeleton.tar.gz

RUN --mount=type=cache,target=/home/node/.cache/yarn,sharing=locked,uid=1000,gid=1000 \
    yarn workspaces focus --all --production && rm -rf "$(yarn cache clean)"

# Backend bundle + config. app-config.local.yaml is excluded by .dockerignore (*.local.yaml).
COPY --chown=node:node packages/backend/dist/bundle.tar.gz app-config.yaml app-config.production.yaml ./
RUN tar xzf bundle.tar.gz && rm bundle.tar.gz

CMD ["node", "packages/backend", "--config", "app-config.yaml", "--config", "app-config.production.yaml"]
