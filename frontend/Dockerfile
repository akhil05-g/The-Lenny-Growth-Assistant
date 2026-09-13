# Multi-stage production build for React + Vite frontend
FROM node:20-alpine AS build

WORKDIR /app

COPY frontend/package.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# Production server using lightweight Nginx
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html

# Nginx reverse proxy configuration for /api to backend
RUN echo 'server { \
    listen 80; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html index.htm; \
        try_files $uri $uri/ /index.html; \
    } \
    location /api/ { \
        proxy_pass http://backend:8000/api/; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_buffering off; \
        proxy_read_timeout 300s; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
