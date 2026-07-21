#!/bin/bash

echo "🚀 Запуск CI тестов для cam-introsat"
echo "========================================"

# Установка зависимостей
echo "📦 Установка зависимостей..."
pip install -e ".[test]"

# Запуск линтеров
echo "🔍 Проверка стиля кода..."
flake8 cam_introsat --max-line-length=120 --exclude=__pycache__,*.pyc

# Запуск проверки типов
echo "📝 Проверка типов..."
mypy cam_introsat --ignore-missing-imports

# Запуск тестов
echo "🧪 Запуск тестов..."
pytest -v --cov=cam_introsat --cov-report=term --cov-report=xml

# Проверка результата
if [ $? -eq 0 ]; then
    echo "✅ Все тесты пройдены успешно!"
    echo "📊 Отчет о покрытии создан: coverage.xml"
else
    echo "❌ Некоторые тесты не прошли!"
    exit 1
fi

echo "========================================"
echo "🎉 CI процесс завершен!"
