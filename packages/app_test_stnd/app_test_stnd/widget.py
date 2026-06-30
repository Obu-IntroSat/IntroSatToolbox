"""Minimal widget - replace the contents with your app's UI."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QWidget,
    QComboBox, QPushButton, QTextEdit, QFrame
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

    # === ОБРАБОТЧИКИ СОБЫТИЙ ===

    def on_check_connection(self):
        """Проверка подключения к МК или оснастке."""
        selected = self.connection_combo.currentText()
        self.output_text.clear()
        self.output_text.append(f"Проверка подключения: {selected}")
        self.output_text.append("")
        self.output_text.append("Выполняется проверка...")

        # ТУТ БУДЕТ ВЫЗОВ РЕАЛЬНОЙ ПРОВЕРКИ ПОДКЛЮЧЕНИЯ
        # Например: result = check_connection(selected)
        # self.output_text.append(result)

        self.output_text.append("")
        self.output_text.append("[ПРИМЕР] Проверка выполнена успешно")

    def on_request_firmware(self):
        """Запрос версии прошивки."""
        self.output_text.clear()
        self.output_text.append("Запрос версии прошивки...")
        self.output_text.append("")

        # ТУТ БУДЕТ ВЫЗОВ ЗАПРОСА ВЕРСИИ ПРОШИВКИ
        # Например: result = get_firmware_version()
        # self.output_text.append(result)

        self.output_text.append("[ПРИМЕР] Версия прошивки: v2.4.1")

    def on_request_stand_version(self):
        """Запрос версии стенда."""
        self.output_text.clear()
        self.output_text.append("Запрос версии стенда...")
        self.output_text.append("")

        # ТУТ БУДЕТ ВЫЗОВ ЗАПРОСА ВЕРСИИ СТЕНДА
        # Например: result = get_stand_version()
        # self.output_text.append(result)

        self.output_text.append("[ПРИМЕР] Версия стенда: 1.2.0")

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

        # ТУТ БУДЕТ ВЫЗОВ РЕАЛЬНОГО ТЕСТА
        # В зависимости от выбранного теста:
        # if "LIS2MDL" in test_name:
        #     result = run_test_lis2mdl()
        # elif "LSM6DS3" in test_name:
        #     result = run_test_lsm6ds3()
        # elif "CC1101" in test_name:
        #     result = run_test_cc1101()
        # else:
        #     result = run_test_full()
        # self.output_text.append(result)

        self.output_text.append("")
        self.output_text.append("[ПРИМЕР] Тест выполнен успешно")