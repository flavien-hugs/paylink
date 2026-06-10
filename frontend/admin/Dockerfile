# syntax=docker/dockerfile:1

# build: compile the SvelteKit app (adapter-node bundles deps into build/)

FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY . .
RUN npm run build

# run: distroless (node only, non-root, no shell/npm/node_modules)
# build/ is self-contained, so no runtime node_modules are required.

FROM gcr.io/distroless/nodejs20-debian12:nonroot AS run
WORKDIR /app
ENV NODE_ENV=production \
    PORT=4173 \
    HOST=0.0.0.0
COPY --from=build /app/build ./build
EXPOSE 4173
CMD ["build"]
