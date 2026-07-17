"""Minimal widget - replace the contents with your app's UI."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QWidget,
    QComboBox, QPushButton, QTextEdit, QFrame
)

from satcore.serial_io import available_ports

from .test_controller import (
    create_controller,
    execute_connection_check,
    execute_firmware_version,
    execute_stand_version,
    execute_i2c_test,
    execute_spi_test,
    execute_uart_test
)

BAUD_RATES = ["9600", "19200", "38400", "57600", "115200", "230400"]


class TemplateWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # Основной вертикальный layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # === СТРОКА ВЫБОРА ПОРТА И СКОРОСТИ ===
        port_row = QWidget()
        port_layout = QHBoxLayout(port_row)
        port_layout.setSpacing(15)

        label_port = QLabel("Порт:")
        label_port.setStyleSheet("font-weight: bold; font-size: 14px; color: white; background: transparent;")
        port_layout.addWidget(label_port)

        self.port_box = QComboBox()
        self.port_box.setMinimumWidth(150)
        self.port_box.setMaximumWidth(200)
        port_layout.addWidget(self.port_box)

        label_baud = QLabel("Скорость:")
        label_baud.setStyleSheet("font-weight: bold; font-size: 14px; color: white; background: transparent;")
        port_layout.addWidget(label_baud)

        self.baud_box = QComboBox()
        self.baud_box.addItems(BAUD_RATES)
        self.baud_box.setCurrentText("9600")
        self.baud_box.setMinimumWidth(100)
        self.baud_box.setMaximumWidth(120)
        port_layout.addWidget(self.baud_box)

        refresh_btn = QPushButton("Обновить порты")
        refresh_btn.clicked.connect(self.refresh_ports)
        port_layout.addWidget(refresh_btn)
        port_layout.addStretch()

        main_layout.addWidget(port_row)

        # === РАЗДЕЛИТЕЛЬ ПОСЛЕ СТРОКИ ВЫБОРА ПОРТА ===
        separator_port = QFrame()
        separator_port.setObjectName("separator_port")
        separator_port.setStyleSheet("""
            QFrame#separator_port {
                background-color: #75f5ea;
                max-height: 2px;
                min-height: 2px;
                border: none;
            }
        """)
        separator_port.setFrameShape(QFrame.HLine)
        main_layout.addWidget(separator_port)

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
        label_conn.setStyleSheet("font-weight: bold; font-size: 14px; min-width: 180px; color: white; background: transparent;")
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
        label_test.setStyleSheet("font-weight: bold; font-size: 14px; min-width: 180px; color: white; background: transparent;")
        test_layout.addWidget(label_test)

        self.test_combo = QComboBox()
        self.test_combo.setMinimumWidth(180)
        self.test_combo.setMaximumWidth(180)
        self.test_combo.addItems([
            "Выберите тест...",
            "ICT - LIS2MDL (I2C)",
            "ICT - LSM6DS3 (I2C)",
            "ICT - CC1101 (SPI)",
            "UART тест",
            "FCT - Полное тестирование"
        ])
        test_layout.addWidget(self.test_combo)

        test_btn = QPushButton("Проверить")
        test_btn.clicked.connect(self.on_run_test)
        test_layout.addWidget(test_btn)

        test_layout.addStretch()
        left_layout.addWidget(test_row)

        top_layout.addWidget(left_container, alignment=Qt.AlignmentFlag.AlignCenter)

        # === ПРАВАЯ ЧАСТЬ: блок с информацией о подключении ===
        right_container = QFrame()
        right_container.setObjectName("info_frame")
        right_container.setStyleSheet("""
            QFrame#info_frame {
                background-color: rgba(117, 245, 234, 0.15);
                border: 2px solid #75f5ea;
                border-radius: 12px;
                padding: 10px;
            }
            QLabel {
                background: transparent;
                color: white;
                font-size: 12px;
            }
        """)
        right_layout = QVBoxLayout(right_container)
        right_layout.setSpacing(10)
        right_layout.setContentsMargins(20, 20, 20, 20)

        # Кнопка подключения
        connect_btn = QPushButton("Подключить стенд")
        connect_btn.clicked.connect(self.on_connect_stand)
        connect_btn.setMinimumWidth(180)
        right_layout.addWidget(connect_btn)

        # Разделитель
        separator_info = QFrame()
        separator_info.setStyleSheet("""
            QFrame {
                background-color: #75f5ea;
                max-height: 1px;
                min-height: 1px;
                border: none;
            }
        """)
        right_layout.addWidget(separator_info)

        # Информация о подключении
        self.port_info_label = QLabel("Открыт порт: ")
        self.port_info_label.setStyleSheet("color: white; font-size: 12px; background: transparent; padding: 4px 0;")
        right_layout.addWidget(self.port_info_label)

        self.stand_info_label = QLabel("Данные о стенде: ")
        self.stand_info_label.setStyleSheet("color: white; font-size: 12px; background: transparent; padding: 4px 0;")
        right_layout.addWidget(self.stand_info_label)

        self.fixture_info_label = QLabel("Данные об оснастке: ")
        self.fixture_info_label.setStyleSheet("color: white; font-size: 12px; background: transparent; padding: 4px 0;")
        right_layout.addWidget(self.fixture_info_label)

        right_layout.addStretch()

        top_layout.addWidget(right_container, alignment=Qt.AlignmentFlag.AlignCenter)

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
        output_label.setStyleSheet("color: #75f5ea; font-weight: bold; font-size: 14px; background: transparent;")
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
        self.controller = None

        # Заполняем список портов
        self.refresh_ports()

        # Очищаем информационные поля
        self.clear_info_labels()

    def clear_info_labels(self):
        """Очищает информационные метки."""
        self.port_info_label.setText("Открыт порт: ")
        self.stand_info_label.setText("Данные о стенде: ")
        self.fixture_info_label.setText("Данные об оснастке: ")

    def refresh_ports(self) -> None:
        """Обновляет список доступных COM-портов."""
        current = self.port_box.currentText()
        self.port_box.clear()
        ports = available_ports()
        self.port_box.addItems(ports)
        if current in ports:
            self.port_box.setCurrentText(current)
        elif ports:
            self.port_box.setCurrentIndex(0)

    def get_controller(self):
        """Создает или обновляет контроллер с текущими настройками порта и скорости."""
        port = self.port_box.currentText()
        if not port:
            self.output_text.clear()
            self.output_text.append("Ошибка: Нет доступных COM-портов!")
            return None

        baudrate = int(self.baud_box.currentText())
        self.controller = create_controller(port=port, baudrate=baudrate)
        return self.controller

    # === НОВЫЙ ОБРАБОТЧИК: Подключение стенда ===
    def on_connect_stand(self):
        """Подключение к стенду и получение информации."""
        controller = self.get_controller()
        if controller is None:
            return

        self.output_text.clear()
        self.output_text.append("Подключение к стенду...")
        self.output_text.append("")

        # Шаг 1: Подключение к порту
        if not controller.connect():
            self.output_text.append("Ошибка: Не удалось открыть порт!")
            self.clear_info_labels()
            return

        self.output_text.append("Порт открыт")

        # Шаг 2: Запрос версии прошивки
        result = controller.execute_command("GetVersion", {})
        firmware_ok = False
        if result['success'] and result['response_code'] == 200:
            data = result['response_data']
            version = f"v{data.get('major', 0)}.{data.get('minor', 0)}.{data.get('patch', 0)}"
            self.stand_info_label.setText(f"Данные о стенде: {version}")
            self.output_text.append(f"Версия прошивки: {version}")
            firmware_ok = True
        else:
            self.stand_info_label.setText("Данные о стенде: Ошибка получения")
            self.output_text.append("Ошибка получения версии прошивки")

        # Шаг 3: Запрос данных об оснастке
        result = controller.execute_command("I2cProbe", {"address": 0x1E})
        if result['success'] and result['response_code'] == 207:
            present = result['response_data'].get('present', False)
            if present:
                self.fixture_info_label.setText("Данные об оснастке: LIS2MDL обнаружен")
                self.output_text.append("Оснастка: LIS2MDL обнаружен")
            else:
                self.fixture_info_label.setText("Данные об оснастке: Не обнаружена")
                self.output_text.append("Оснастка: LIS2MDL не обнаружен")
        else:
            self.fixture_info_label.setText("Данные об оснастке: Ошибка проверки")
            self.output_text.append("Ошибка проверки оснастки")

        # Обновляем порт
        self.port_info_label.setText(f"Открыт порт: {controller.port}")

        # Итоговый результат
        if firmware_ok:
            self.output_text.append("")
            self.output_text.append("Подключение выполнено успешно!")
        else:
            self.output_text.append("")
            self.output_text.append("Подключение выполнено с ошибками!")

    # === ОБРАБОТЧИКИ СОБЫТИЙ ===

    def on_check_connection(self):
        """Проверка подключения к МК или оснастке."""
        controller = self.get_controller()
        if controller is None:
            return

        selected = self.connection_combo.currentText()
        result = execute_connection_check(controller, selected)
        self.output_text.clear()
        self.output_text.append(result)

    def on_request_firmware(self):
        """Запрос версии прошивки (устарело, оставлено для совместимости)."""
        self.output_text.clear()
        self.output_text.append("Используйте кнопку 'Подключить стенд' для получения информации.")

    def on_request_stand_version(self):
        """Запрос версии стенда (устарело, оставлено для совместимости)."""
        self.output_text.clear()
        self.output_text.append("Используйте кнопку 'Подключить стенд' для получения информации.")

    def on_run_test(self):
        """Запуск выбранного теста."""
        controller = self.get_controller()
        if controller is None:
            return

        test_name = self.test_combo.currentText()

        if test_name == "Выберите тест...":
            self.output_text.clear()
            self.output_text.append("ОШИБКА: Не выбран тест!")
            self.output_text.append("")
            self.output_text.append("Доступные тесты:")
            self.output_text.append("  • ICT - LIS2MDL (I2C)")
            self.output_text.append("  • ICT - LSM6DS3 (I2C)")
            self.output_text.append("  • ICT - CC1101 (SPI)")
            self.output_text.append("  • ICT - тест UART")
            self.output_text.append("  • FCT - Полное тестирование")
            return

        self.output_text.clear()
        self.output_text.append(f"Запуск теста: {test_name}")
        self.output_text.append("")
        self.output_text.append("Выполнение теста...")
        self.output_text.append("")

        # Выполняем соответствующий тест
        if "LIS2MDL" in test_name:
            result = execute_i2c_test(controller, "LIS2MDL", 0x1E)
        elif "LSM6DS3" in test_name:
            result = execute_i2c_test(controller, "LSM6DS3", 0x6A)
        elif "CC1101" in test_name:
            result = execute_spi_test(controller)
        elif "UART тест" in test_name:
            result = execute_uart_test(controller, "../scenarios/test_uart.yaml")
        else:  # FCT - Полное тестирование
            result = self.run_full_test()

        self.output_text.append(result)

    def run_full_test(self) -> str:
        """Полное функциональное тестирование."""
        controller = self.get_controller()
        if controller is None:
            return "Ошибка: Нет доступных COM-портов!"

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
        result = execute_connection_check(controller, "МК")
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
            lines.append("     2. Правильный ли COM-порт")
            lines.append("     3. Запущен ли эмулятор (emulator.py)")
            lines.append("=" * 50)
            return "\n".join(lines)

        # Тест 2: Версия прошивки
        total_tests += 1
        lines.append(f"Тест {total_tests}: Версия прошивки")
        result = execute_firmware_version(controller)
        lines.append(result)
        lines.append("")
        if "Ошибка" not in result:
            passed_tests += 1
        else:
            failed_tests += 1

        # Тест 3: Версия стенда
        total_tests += 1
        lines.append(f"Тест {total_tests}: Версия стенда")
        result = execute_stand_version(controller)
        lines.append(result)
        lines.append("")
        if "Ошибка" not in result:
            passed_tests += 1
        else:
            failed_tests += 1

        # Тест 4: I2C тест LIS2MDL
        total_tests += 1
        lines.append(f"Тест {total_tests}: LIS2MDL (I2C)")
        result = execute_i2c_test(controller, "LIS2MDL", 0x1E)
        lines.append(result)
        lines.append("")
        if "Ошибка" not in result:
            passed_tests += 1
        else:
            failed_tests += 1

        # Тест 5: I2C тест LSM6DS3
        total_tests += 1
        lines.append(f"Тест {total_tests}: LSM6DS3 (I2C)")
        result = execute_i2c_test(controller, "LSM6DS3", 0x6A)
        lines.append(result)
        lines.append("")
        if "Ошибка" not in result:
            passed_tests += 1
        else:
            failed_tests += 1

        # Тест 6: SPI тест CC1101
        total_tests += 1
        lines.append(f"Тест {total_tests}: CC1101 (SPI)")
        result = execute_spi_test(controller)
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
