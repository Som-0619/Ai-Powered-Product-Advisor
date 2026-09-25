FROM node:20-alpine AS base

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"
ENV INTERNAL_API_URL "http://backend:8000"

# Production build: no on-demand page compilation, minified/optimized
# bundles, and no React Strict Mode double-invoke of effects -- all of
# which made dev mode noticeably slower to navigate and, for the double-
# invoke case, actually doubled some network requests.
RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "start"]
