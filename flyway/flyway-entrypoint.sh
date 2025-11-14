#!/bin/sh
set -e

until pg_isready -h haproxy -U ${POSTGRES_USER} -d postgres -t 30; do
  echo "Waiting for primary database to be ready..."
  sleep 5
done

psql -h haproxy -U ${POSTGRES_USER} -d postgres -c \
  "SELECT 'CREATE DATABASE ${DB_NAME}' WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = '${DB_NAME}')" | \
  grep 'CREATE DATABASE' | psql -h haproxy -U ${POSTGRES_USER} -d postgres

psql -h haproxy -U ${POSTGRES_USER} -d postgres -c \
  "DO \$\$ 
   DECLARE
       analyst_name text;
   BEGIN
       IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'analytic') THEN
           CREATE ROLE analytic;
       END IF;
       
       FOREACH analyst_name IN ARRAY string_to_array('${ANALYST_NAMES}', ',') 
       LOOP
           IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = analyst_name) THEN
               EXECUTE format('CREATE USER %I WITH PASSWORD %L', 
                             analyst_name, 
                             analyst_name || '_123');
               EXECUTE format('GRANT analytic TO %I', analyst_name);
           END IF;
       END LOOP;
   END \$\$;"

psql -h haproxy -U ${POSTGRES_USER} -d postgres -c \
  "DO \$\$ 
   BEGIN 
     IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${MIGRATION_USER}') THEN
       CREATE USER ${MIGRATION_USER} WITH PASSWORD '${FLYWAY_PASSWORD}' CREATEDB;
     END IF;
   END
   \$\$;"

psql -h haproxy -U ${POSTGRES_USER} -d postgres -c \
  "GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${MIGRATION_USER};"

psql -h haproxy -U ${POSTGRES_USER} -d ${DB_NAME} -c \
  "GRANT ALL PRIVILEGES ON SCHEMA public TO ${MIGRATION_USER};"

flyway migrate