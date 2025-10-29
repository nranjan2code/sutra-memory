# Multi-stage Dockerfile for Sutra Explorer Frontend

# Stage 1: Build stage
FROM node:20-alpine as builder

WORKDIR /build

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build arguments
ARG VITE_API_URL=http://localhost:8100
ENV VITE_API_URL=$VITE_API_URL

# Build application
RUN npm run build

# Stage 2: Runtime stage (Nginx)
FROM nginx:alpine

# Copy built assets from builder
COPY --from=builder /build/dist /usr/share/nginx/html

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# Run nginx
CMD ["nginx", "-g", "daemon off;"]
