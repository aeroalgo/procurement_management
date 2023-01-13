#!/usr/bin/env sh

set -e

# Ожидаем запуска postgres
dockerize -wait tcp://${PSQL_HOST}:${PSQL_PORT}

# Миграция и синхронизация
./manage.py migrate --noinput
./manage.py sync_permissions
./manage.py sync_directions
./manage.py loaddata login/fixtures/dev.json
./manage.py users_generate 10

# Запуск команды
./manage.py runserver 0.0.0.0:${APP_PORT}