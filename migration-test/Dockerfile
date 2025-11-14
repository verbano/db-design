FROM postgres:13-alpine

RUN apk add --no-cache \
    bash \
    diffutils \
    grep \
    sed

WORKDIR /app

COPY test_migrations.sh /app/test_migrations.sh

RUN chmod +x /app/test_migrations.sh

CMD ["/bin/bash", "/app/test_migrations.sh"]