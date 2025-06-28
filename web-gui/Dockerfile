# Multi-stage Dockerfile for NPCEngine Frontend
# Optimized for production deployment

# Build stage
FROM node:18-alpine as builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && npm cache clean --force

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine as production

# Install curl for health checks
RUN apk add --no-cache curl

# Copy built app from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Add non-root user
RUN addgroup -g 1001 -S npcengine && \
    adduser -S npcengine -u 1001

# Set correct permissions
RUN chown -R npcengine:npcengine /usr/share/nginx/html && \
    chown -R npcengine:npcengine /var/cache/nginx && \
    chown -R npcengine:npcengine /var/log/nginx && \
    chown -R npcengine:npcengine /etc/nginx/conf.d

# Switch to non-root user
USER npcengine

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"] 