FROM nginx:1.31-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY web/ /usr/share/nginx/html/

# Fail the image build if setup.py has not produced the application entry points.
RUN test -s /usr/share/nginx/html/index.html && \
    test -s /usr/share/nginx/html/layout.html && \
    test -s /usr/share/nginx/html/layout.loader.js && nginx -t

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -q -O /dev/null http://127.0.0.1/ || exit 1
