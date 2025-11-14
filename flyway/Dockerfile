FROM flyway/flyway:10.11.0-alpine

RUN apk add --no-cache postgresql-client

COPY flyway-entrypoint.sh /flyway/
RUN chmod +x /flyway/flyway-entrypoint.sh

ENTRYPOINT ["/flyway/flyway-entrypoint.sh"]