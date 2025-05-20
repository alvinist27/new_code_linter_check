#!/bin/bash

# Импортируем env
set -aeuo pipefail
[ -f .env ] && source .env || true
set +a

# Устанавливаем значения по умолчанию
: "${APP_DIR:=.}"
: "${IS_LOCAL_LINTER_CHECK:=false}"

echo $APP_DIR
echo "APP_DIR: $APP_DIR"

# Проверяем и создаем директории
mkdir -p "${APP_DIR}/linter"

# Определяем пути
REPORT_PATH="${APP_DIR}/linter/ruff-report.json"
DIFF_PATH="${APP_DIR}/linter/current_diff.txt"
RUN_CHECK_SCRIPT_PATH="${APP_DIR}/linter/run_check.py"

# Переходим в директорию проекта
cd "$APP_DIR" || { echo "Ошибка перехода в ${APP_DIR}"; exit 1; }

# Обновляем ссылки на ветку master (только в локальном режиме)
if [ "$IS_LOCAL_LINTER_CHECK" = "true" ]; then
  echo "Обновление master"
  git fetch origin master:refs/remotes/origin/master || echo "Предупреждение: не удалось обновить master"
fi

# Генерируем ruff отчет
echo "Генерация ruff отчета..."
echo "REPORT_PATH: $REPORT_PATH"
ruff check . --output-format=json > "$REPORT_PATH" || true

echo "DIFF_PATH: $DIFF_PATH"
echo "IS_LOCAL_LINTER_CHECK: $IS_LOCAL_LINTER_CHECK"

# Записываем diff (только в локальном режиме)
if [ "$IS_LOCAL_LINTER_CHECK" = "true" ]; then
  echo "Генерация diff..."
  git diff origin/master...HEAD --unified=0 > "$DIFF_PATH" || true
fi

# Запускаем скрипт проверки
echo "Запуск проверки..."
python3 "$RUN_CHECK_SCRIPT_PATH"

# Возвращаемся в директорию проекта
cd "$APP_DIR"
echo "Скрипт завершен успешно"
