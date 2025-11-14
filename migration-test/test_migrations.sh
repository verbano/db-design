#!/bin/bash
set -e

# export PGHOST=${PGHOST}
export PGHOST=${POSTGRES_HOST}
export PGUSER=${POSTGRES_USER}
export PGPASSWORD=${POSTGRES_PASSWORD}
export PGDATABASE=${POSTGRES_DB}

if ! psql -c "SELECT 1" > /dev/null; then
  echo "Cannot connect to database"
  exit 1
fi

psql -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

for up_file in /migrations/V*.sql; do
  base_name=$(basename "$up_file" | sed 's/^V[0-9]\+__//')
  version=$(echo "$up_file" | grep -oP 'V\K\d+')
  down_file="/migrations/R${version}__${base_name}"
  
  if [ ! -f "$down_file" ]; then
    echo "Down file $(basename "$down_file") not found in /migrations!"
    echo "Expected path: $down_file"
    exit 1
  fi
  
  echo "Testing version ${version}..."
  
  echo "1. Applying UP: $(basename "$up_file")"
  psql -f "$up_file"
  
  pg_dump --schema-only > /tmp/schema1.sql

  echo "2. Applying DOWN: $(basename "$down_file")"
  psql -f "$down_file"
  
  echo "3. Re-applying UP: $(basename "$up_file")"
  psql -f "$up_file"
  
  pg_dump --schema-only > /tmp/schema2.sql

  echo "4. Comparing schemas..."
  if diff -u /tmp/schema1.sql /tmp/schema2.sql; then
    echo "Version ${version} passed (schemas identical)"
  else
    echo "Version ${version} FAILED (schemas differ!)"
    exit 1
  fi
  
done

echo "All migrations passed successfully!"