.PHONY: test test-verbose test-coverage test-html test-fast clean help

# Default target
help:
	@echo "📋 Доступные команды:"
	@echo "  make test           - Запуск всех тестов"
	@echo "  make test-verbose   - Запуск всех тестов с подробным выводом"
	@echo "  make test-coverage  - Запуск тестов с отчетом о покрытии (терминал)"
	@echo "  make test-html      - Запуск тестов с HTML отчетом о покрытии"
	@echo "  make test-fast      - Запуск быстрых тестов (без UI)"
	@echo "  make clean          - Очистка временных файлов"
	@echo "  make help           - Показать эту справку"

test:
	pytest -v

test-verbose:
	pytest -vv --tb=long

test-coverage:
	pytest --cov=cam_introsat --cov-report=term

test-html:
	pytest --cov=cam_introsat --cov-report=html --cov-report=term
	@echo "📄 HTML отчет: htmlcov/index.html"
	@open htmlcov/index.html 2>/dev/null || echo "Откройте htmlcov/index.html в браузере"

test-fast:
	pytest -k "not test_ui" -v

test-integration:
	pytest -m integration -v

test-unit:
	pytest -k "not integration and not test_ui" -v

clean:
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .mypy_cache/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "🧹 Очистка завершена"
