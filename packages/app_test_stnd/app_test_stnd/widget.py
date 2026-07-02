"""Minimal widget - replace the contents with your app's UI."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QWidget,
    QComboBox, QPushButton, QTextEdit, QFrame
)

from .test_controller import (
    create_controller,
    execute_connection_check,
    execute_firmware_version,
    execute_stand_version,
    execute_i2c_test,
    execute_spi_test
)


class TemplateWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # Основной вертикальный layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # === ВЕРХНЯЯ ПОЛОВИНА ===
        top_container = QWidget()
        top_layout = QHBoxLayout(top_container)
        top_layout.setSpacing(30)

        # === ЛЕВАЯ ЧАСТЬ: надписи с выпадающими меню ===
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setSpacing(25)

        # Ряд 1: Проверка подключения
        conn_row = QWidget()
        conn_layout = QHBoxLayout(conn_row)
        conn_layout.setSpacing(15)

        label_conn = QLabel("Проверка подключения")
        label_conn.setStyleSheet("font-weight: bold; font-size: 14px; min-width: 180px;")
        conn_layout.addWidget(label_conn)

        self.connection_combo = QComboBox()
        self.connection_combo.setMinimumWidth(180)
        self.connection_combo.setMaximumWidth(180)
        self.connection_combo.addItems(["МК", "Оснастка"])
        conn_layout.addWidget(self.connection_combo)

        check_conn_btn = QPushButton("Проверить")
        check_conn_btn.clicked.connect(self.on_check_connection)
        conn_layout.addWidget(check_conn_btn)
        conn_layout.addStretch()

        left_layout.addWidget(conn_row)

        # Ряд 2: Тестирование
        test_row = QWidget()
        test_layout = QHBoxLayout(test_row)
        test_layout.setSpacing(15)

        label_test = QLabel("Тестирование")
        label_test.setStyleSheet("font-weight: bold; font-size: 14px; min-width: 180px;")
        test_layout.addWidget(label_test)

        self.test_combo = QComboBox()
        self.test_combo.setMinimumWidth(180)
        self.test_combo.setMaximumWidth(180)
        self.test_combo.addItems([
            "Выберите тест...",
            "ICT - LIS2MDL (I2C)",
            "ICT - LSM6DS3 (I2C)",
            "ICT - CC1101 (SPI)",
            "FCT - Полное тестирование"
        ])
        test_layout.addWidget(self.test_combo)

        test_btn = QPushButton("Проверить")
        test_btn.clicked.connect(self.on_run_test)
        test_layout.addWidget(test_btn)

        test_layout.addStretch()
        left_layout.addWidget(test_row)

        top_layout.addWidget(left_container)

        # === ПРАВАЯ ЧАСТЬ: блок с кнопками версий ===
        right_container = QFrame()
        right_container.setObjectName("version_frame")
        right_container.setStyleSheet("""
            QFrame#version_frame {
                background-color: rgba(117, 245, 234, 0.15);
                border: 2px solid #75f5ea;
                border-radius: 12px;
                padding: 10px;
            }
        """)
        right_layout = QVBoxLayout(right_container)
        right_layout.setSpacing(15)
        right_layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок блока
        version_label = QLabel("Запрос версии")
        version_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #75f5ea;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(version_label)

        # Кнопка запроса версии прошивки
        firmware_btn = QPushButton("Версия прошивки")
        firmware_btn.clicked.connect(self.on_request_firmware)
        firmware_btn.setMinimumWidth(180)
        right_layout.addWidget(firmware_btn)

        # Кнопка запроса версии стенда
        stand_btn = QPushButton("Версия стенда")
        stand_btn.clicked.connect(self.on_request_stand_version)
        stand_btn.setMinimumWidth(180)
        right_layout.addWidget(stand_btn)

        top_layout.addWidget(right_container)

        # Растягиваем правую часть по вертикали
        right_container.setSizePolicy(
            right_container.sizePolicy().horizontalPolicy(),
            left_container.sizePolicy().verticalPolicy()
        )

        main_layout.addWidget(top_container)

        # === РАЗДЕЛИТЕЛЬ ===
        separator = QFrame()
        separator.setObjectName("separator")
        separator.setStyleSheet("""
            QFrame#separator {
                background-color: #75f5ea;
                max-height: 2px;
                min-height: 2px;
                border: none;
            }
        """)
        separator.setFrameShape(QFrame.HLine)
        main_layout.addWidget(separator)

        # === НИЖНЯЯ ПОЛОВИНА: поле вывода ===
        output_container = QWidget()
        output_layout = QVBoxLayout(output_container)
        output_layout.setContentsMargins(0, 10, 0, 0)

        output_label = QLabel("Результаты тестирования:")
        output_label.setStyleSheet("color: #75f5ea; font-weight: bold; font-size: 14px;")
        output_layout.addWidget(output_label)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumHeight(200)
        # Черный фон для поля вывода
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: black;
                color: white;
                border: 2px solid #75f5ea;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        output_layout.addWidget(self.output_text)

        main_layout.addWidget(output_container)

        # Создаем контроллер
        self.controller = create_controller(port="COM15", baudrate=9600)

    # === ОБРАБОТЧИКИ СОБЫТИЙ ===

    def on_check_connection(self):
        """Проверка подключения к МК или оснастке."""
        selected = self.connection_combo.currentText()
        result = execute_connection_check(self.controller, selected)
        self.output_text.clear()
        self.output_text.append(result)

    def on_request_firmware(self):
        """Запрос версии прошивки."""
        result = execute_firmware_version(self.controller)
        self.output_text.clear()
        self.output_text.append(result)

    def on_request_stand_version(self):
        """Запрос версии стенда."""
        result = execute_stand_version(self.controller)
        self.output_text.clear()
        self.output_text.append(result)

    def on_run_test(self):
        """Запуск выбранного теста."""
        test_name = self.test_combo.currentText()

        if test_name == "Выберите тест...":
            self.output_text.clear()
            self.output_text.append("ОШИБКА: Не выбран тест!")
            self.output_text.append("")
            self.output_text.append("Доступные тесты:")
            self.output_text.append("  • ICT - LIS2MDL (I2C)")
            self.output_text.append("  • ICT - LSM6DS3 (I2C)")
            self.output_text.append("  • ICT - CC1101 (SPI)")
            self.output_text.append("  • FCT - Полное тестирование")
            return

        self.output_text.clear()
        self.output_text.append(f"Запуск теста: {test_name}")
        self.output_text.append("")
        self.output_text.append("Выполнение теста...")
        self.output_text.append("")

        # Выполняем соответствующий тест
        if "LIS2MDL" in test_name:
            result = execute_i2c_test(self.controller, "LIS2MDL", 0x1E)
        elif "LSM6DS3" in test_name:
            result = execute_i2c_test(self.controller, "LSM6DS3", 0x6A)
        elif "CC1101" in test_name:
            result = execute_spi_test(self.controller)
        else:  # FCT - Полное тестирование
            result = self.run_full_test()

        self.output_text.append(result)

    def run_full_test(self) -> str:
        """Полное функциональное тестирование."""
        lines = []
        lines.append("=== FCT - Полное тестирование ===")
        lines.append("")

        # Счетчики для отслеживания результатов
        total_tests = 0
        passed_tests = 0
        failed_tests = 0

        # Тест 1: Проверка подключения
        total_tests += 1
        lines.append(f"Тест {total_tests}: Проверка подключения")
        result = execute_connection_check(self.controller, "МК")
        lines.append(result)
        lines.append("")
        if "Ошибка" not in result:
            passed_tests += 1
        else:
            failed_tests += 1

        # Если подключение не удалось, остальные тесты не имеют смысла
        if failed_tests > 0:
            lines.append("")
            lines.append("=" * 50)
            lines.append("   ТЕСТИРОВАНИЕ ОСТАНОВЛЕНО!")
            lines.append("   Не удалось подключиться к стенду.")
            lines.append("   Проверьте:")
            lines.append("     1. Подключен ли стенд по USB")
            lines.append("     2. Правильный ли COM-порт (сейчас COM15)")
            lines.append("     3. Запущен ли эмулятор (emulator.py)")
            lines.append("=" * 50)
            return "\n".join(lines)

        # Тест 2: Версия прошивки
        total_tests += 1
        lines.append(f"Тест {total_tests}: Версия прошивки")
        result = execute_firmware_version(self.controller)
        lines.append(result)
        lines.append("")
        if "Ошибка" not in result:
            passed_tests += 1
        else:
            failed_tests += 1

        # Тест 3: Версия стенда
        total_tests += 1
        lines.append(f"Тест {total_tests}: Версия стенда")
        result = execute_stand_version(self.controller)
        lines.append(result)
        lines.append("")
        if "Ошибка" not in result:
            passed_tests += 1
        else:
            failed_tests += 1

        # Тест 4: I2C тест LIS2MDL
        total_tests += 1
        lines.append(f"Тест {total_tests}: LIS2MDL (I2C)")
        result = execute_i2c_test(self.controller, "LIS2MDL", 0x1E)
        lines.append(result)
        lines.append("")
        if "Ошибка" not in result:
            passed_tests += 1
        else:
            failed_tests += 1

        # Тест 5: I2C тест LSM6DS3
        total_tests += 1
        lines.append(f"Тест {total_tests}: LSM6DS3 (I2C)")
        result = execute_i2c_test(self.controller, "LSM6DS3", 0x6A)
        lines.append(result)
        lines.append("")
        if "Ошибка" not in result:
            passed_tests += 1
        else:
            failed_tests += 1

        # Тест 6: SPI тест CC1101
        total_tests += 1
        lines.append(f"Тест {total_tests}: CC1101 (SPI)")
        result = execute_spi_test(self.controller)
        lines.append(result)
        lines.append("")
        if "Ошибка" not in result:
            passed_tests += 1
        else:
            failed_tests += 1

        # Итоговый отчет
        lines.append("=" * 50)
        lines.append("    ИТОГОВЫЙ ОТЧЕТ:")
        lines.append(f"   Всего тестов: {total_tests}")
        lines.append(f"   Пройдено: {passed_tests}")
        lines.append(f"   Провалено: {failed_tests}")

        if failed_tests == 0:
            lines.append("")
            lines.append("ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        else:
            lines.append("")
            lines.append("ЕСТЬ ПРОВАЛЕННЫЕ ТЕСТЫ!")
            lines.append("   Проверьте подключение и повторите попытку.")
        lines.append("=" * 50)

        return "\n".join(lines)