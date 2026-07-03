"""UI for flashing firmware from Git repositories."""

from __future__ import annotations

import json
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from PySide6.QtCore import Qt, QTimer, QThread, Signal, QObject
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QPlainTextEdit, QGroupBox, QListWidget,
    QListWidgetItem, QProgressBar, QMessageBox, QLineEdit,
    QCheckBox, QComboBox, QSplitter, QFileDialog, QScrollArea
)
from PySide6.QtCore import QThreadPool, QRunnable

# Импортируем наши модули
from .github_release_manager import GitHubReleaseManager
from .stlink_client import STLinkClient


class FlashWorkerSignals(QObject):
    """Сигналы для FlashWorker."""
    progress = Signal(str)
    finished = Signal(bool, str)


class FlashWorker(QRunnable):
    """Worker для прошивки в отдельном потоке."""
    
    def __init__(self, stlink: STLinkClient, firmware_path: str, verify: bool):
        super().__init__()
        self.stlink = stlink
        self.firmware_path = firmware_path
        self.verify = verify
        self.signals = FlashWorkerSignals()
    
    def run(self):
        """Запускает прошивку."""
        self.signals.progress.emit("Начинаем прошивку...")
        success, message = self.stlink.flash(self.firmware_path, self.verify)
        self.signals.finished.emit(success, message)


class FirmwareGitRepoWidget(QWidget):
    """Главный виджет приложения для прошивки из Git."""
    
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        
        # Путь к файлу конфигурации с репозиториями
        self.config_file = Path(__file__).parent.parent / "firmware_repositories.json"
        self.storage_path = Path.home() / ".introsat" / "firmware"
        
        # Токен для доступа к GitHub (из переменных окружения или файла)
        self.github_token = self._load_github_token()
        
        # Создаем менеджеры
        self.release_manager = GitHubReleaseManager(
            self.config_file, 
            self.storage_path,
            token=self.github_token
        )
        self.stlink = STLinkClient()
        
        # Состояние
        self.all_firmware = []
        self.current_firmware_path = None
        self.is_flashing = False
        self.device_connected = False
        
        self.threadpool = QThreadPool()
        
        self.init_ui()
        self.check_stlink_status()
        self.refresh_firmware_list()
    
    def _load_github_token(self) -> Optional[str]:
        """Загружает GitHub токен из файла или переменных окружения."""
        # 1. Пробуем из файла .github_token в папке пользователя
        token_file = Path.home() / ".introsat" / ".github_token"
        if token_file.exists():
            try:
                with open(token_file, 'r') as f:
                    token = f.read().strip()
                    if token:
                        return token
            except Exception:
                pass
        
        # 2. Пробуем из переменной окружения
        import os
        token = os.environ.get('GITHUB_TOKEN')
        if token:
            return token
        
        # 3. Пробуем из файла рядом с приложением
        token_file_local = Path(__file__).parent.parent / ".github_token"
        if token_file_local.exists():
            try:
                with open(token_file_local, 'r') as f:
                    token = f.read().strip()
                    if token:
                        return token
            except Exception:
                pass
        
        return None
    
    def _save_github_token(self, token: str):
        """Сохраняет GitHub токен в файл."""
        token_file = Path.home() / ".introsat" / ".github_token"
        token_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(token_file, 'w') as f:
                f.write(token.strip())
            return True
        except Exception:
            return False
    
    def init_ui(self):
        """Инициализация интерфейса."""
        # Создаем главный виджет с прокруткой
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # --- Управление прошивками ---
        repo_group = QGroupBox("Управление прошивками")
        repo_layout = QVBoxLayout()
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Обновить прошивки")
        self.refresh_btn.setMinimumHeight(30)
        self.refresh_btn.clicked.connect(self.refresh_firmware_list)
        btn_layout.addWidget(self.refresh_btn)
        
        self.repo_status = QLabel("Готов")
        btn_layout.addWidget(self.repo_status)
        btn_layout.addStretch()
        repo_layout.addLayout(btn_layout)
        
        # Токен (опционально, для приватных репозиториев)
        token_layout = QHBoxLayout()
        token_layout.addWidget(QLabel("GitHub Token:"))
        self.token_edit = QLineEdit()
        self.token_edit.setPlaceholderText("Введите токен для доступа к приватным репозиториям")
        self.token_edit.setEchoMode(QLineEdit.Password)
        if self.github_token:
            self.token_edit.setText(self.github_token)
        self.token_edit.textChanged.connect(self.on_token_changed)
        token_layout.addWidget(self.token_edit)
        
        self.token_status = QLabel()
        if self.github_token:
            self.token_status.setText("Токен загружен")
            self.token_status.setStyleSheet("color: green;")
        else:
            self.token_status.setText("Токен не найден")
            self.token_status.setStyleSheet("color: orange;")
        token_layout.addWidget(self.token_status)
        repo_layout.addLayout(token_layout)
        
        # Список прошивок с фильтром
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Фильтр:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Все", "STM32", "ATmega"])
        self.filter_combo.currentTextChanged.connect(self.filter_firmware_list)
        filter_layout.addWidget(self.filter_combo)
        
        self.firmware_count_label = QLabel("Найдено: 0")
        filter_layout.addWidget(self.firmware_count_label)
        filter_layout.addStretch()
        repo_layout.addLayout(filter_layout)
        
        # Список прошивок с ползунком
        self.firmware_list = QListWidget()
        self.firmware_list.setMinimumHeight(200)
        self.firmware_list.setMaximumHeight(300)
        self.firmware_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.firmware_list.itemSelectionChanged.connect(self.on_firmware_selected)
        self.firmware_list.itemDoubleClicked.connect(self.on_firmware_double_click)
        repo_layout.addWidget(self.firmware_list)
        
        repo_group.setLayout(repo_layout)
        main_layout.addWidget(repo_group)
        
        # --- Подключение устройства ---
        device_group = QGroupBox("Подключение устройства")
        device_layout = QVBoxLayout()
        
        # Информация о ST-Link
        stlink_layout = QHBoxLayout()
        self.stlink_status_label = QLabel("ST-Link: проверка...")
        stlink_layout.addWidget(self.stlink_status_label)
        stlink_layout.addStretch()
        device_layout.addLayout(stlink_layout)
        
        # Кнопка подключения
        connect_layout = QHBoxLayout()
        self.connect_btn = QPushButton("Подключить устройство")
        self.connect_btn.setMinimumHeight(30)
        self.connect_btn.clicked.connect(self.connect_device)
        connect_layout.addWidget(self.connect_btn)
        
        self.device_status = QLabel("Устройство не подключено")
        connect_layout.addWidget(self.device_status)
        connect_layout.addStretch()
        device_layout.addLayout(connect_layout)
        
        # Информация об устройстве
        self.device_info_text = QPlainTextEdit()
        self.device_info_text.setReadOnly(True)
        self.device_info_text.setMinimumHeight(120)
        self.device_info_text.setMaximumHeight(180)
        self.device_info_text.setPlaceholderText("Информация об устройстве появится здесь после подключения")
        device_layout.addWidget(self.device_info_text)
        
        device_group.setLayout(device_layout)
        main_layout.addWidget(device_group)
        
        # --- Прошивка ---
        flash_group = QGroupBox("Прошивка")
        flash_layout = QVBoxLayout()
        
        flash_btn_layout = QHBoxLayout()
        self.flash_btn = QPushButton("Прошить выбранную прошивку")
        self.flash_btn.setEnabled(False)
        self.flash_btn.setMinimumHeight(35)
        self.flash_btn.clicked.connect(self.flash_device)
        flash_btn_layout.addWidget(self.flash_btn)
        flash_btn_layout.addStretch()
        flash_layout.addLayout(flash_btn_layout)
        
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        flash_layout.addWidget(self.progress)
        
        flash_group.setLayout(flash_layout)
        main_layout.addWidget(flash_group)
        
        # --- Лог ---
        log_group = QGroupBox("Лог операций")
        log_layout = QVBoxLayout()
        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumBlockCount(1000)
        
        # Кнопки управления логом
        log_btn_layout = QHBoxLayout()
        clear_log_btn = QPushButton("Очистить лог")
        clear_log_btn.clicked.connect(lambda: self.log_text.clear())
        log_btn_layout.addWidget(clear_log_btn)
        log_btn_layout.addStretch()
        log_layout.addLayout(log_btn_layout)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
        
        # Добавляем растяжение в конце
        main_layout.addStretch()
        
        # Оборачиваем все в QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setWidget(main_widget)
        
        # Основной layout виджета
        base_layout = QVBoxLayout(self)
        base_layout.setContentsMargins(0, 0, 0, 0)
        base_layout.addWidget(scroll)

    def on_token_changed(self, text: str):
        """Обработчик изменения токена."""
        if text.strip():
            self.token_status.setText("Токен установлен")
            self.token_status.setStyleSheet("color: green;")
            self._save_github_token(text)
            self.github_token = text
            self.release_manager.token = text
        else:
            self.token_status.setText("Токен не установлен")
            self.token_status.setStyleSheet("color: orange;")
            self.github_token = None
            self.release_manager.token = None
    
    def check_stlink_status(self):
        """Проверяет доступность ST-Link."""
        info = self.stlink.get_stlink_info()
        if info["available"]:
            self.stlink_status_label.setText(f"ST-Link: доступен (версия {info['version']})")
            if info["connected"]:
                self.stlink_status_label.setText("ST-Link: устройство уже подключено")
        else:
            self.stlink_status_label.setText("ST-Link: не найден")
    
    def refresh_firmware_list(self):
        """Обновляет список прошивок из GitHub Releases."""
        self.refresh_btn.setEnabled(False)
        self.repo_status.setText("Загрузка из GitHub...")
        self.log("Начинаем загрузку прошивок из GitHub Releases...")
        
        try:
            firmware_list = self.release_manager.get_all_releases(self.log)
            cached = self.release_manager.get_cached_firmware()
            
            all_paths = {fw['path'] for fw in firmware_list}
            for fw in cached:
                if fw['path'] not in all_paths:
                    firmware_list.append(fw)
                    all_paths.add(fw['path'])
            
            self.all_firmware = firmware_list
            self.display_firmware_list()
            
            self.log(f"Найдено {len(self.all_firmware)} прошивок")
            self.repo_status.setText(f"Готово ({len(self.all_firmware)} прошивок)")
            
        except Exception as e:
            self.log(f"Ошибка загрузки: {str(e)}")
            self.repo_status.setText("Ошибка загрузки")
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить прошивки:\n{str(e)}")
        
        self.refresh_btn.setEnabled(True)
    
    def display_firmware_list(self, filter_device: str = "Все"):
        """Отображает список прошивок с фильтрацией."""
        self.firmware_list.clear()
        
        filtered = self.all_firmware
        if filter_device != "Все":
            filtered = [f for f in self.all_firmware if f.get("device", "Unknown") == filter_device]
        
        if self.device_connected:
            device_chip = self.device_info_text.toPlainText()
            if "STM32" in device_chip:
                filtered = [f for f in filtered if f.get("device") == "STM32"]
            elif "ATmega" in device_chip or "MEGA" in device_chip:
                filtered = [f for f in filtered if f.get("device") == "ATmega"]
        
        for fw in filtered:
            version = fw.get('version', '')
            device = fw.get('device', 'Unknown')
            repo = fw.get('repo', '')
            
            item_text = f"{fw['name']}"
            if version and version != "unknown":
                item_text += f" ({version})"
            item_text += f" [{device}]"
            if repo:
                item_text += f" [{repo}]"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, fw.get("path", ""))
            
            tooltip = f"Файл: {fw['name']}\n"
            tooltip += f"Версия: {version}\n"
            tooltip += f"Устройство: {device}\n"
            tooltip += f"Репозиторий: {repo}\n"
            if fw.get('published_at'):
                tooltip += f"Опубликовано: {fw['published_at']}\n"
            if fw.get('size'):
                tooltip += f"Размер: {fw['size']} байт"
            
            item.setToolTip(tooltip)
            self.firmware_list.addItem(item)
        
        self.firmware_count_label.setText(f"Найдено: {len(filtered)}")
    
    def filter_firmware_list(self):
        """Фильтрует список по выбранному типу."""
        self.display_firmware_list(self.filter_combo.currentText())
    
    def connect_device(self):
        """Подключается к устройству через ST-Link."""
        self.connect_btn.setEnabled(False)
        self.log("Подключение к устройству через ST-Link...")
        
        success, message = self.stlink.connect()
        
        if success:
            info = self.stlink.get_device_info()
            self.device_info_text.clear()
            self.device_info_text.appendPlainText("Информация об устройстве:")
            self.device_info_text.appendPlainText(f"  Чип: {info.get('chip', 'Неизвестно')}")
            self.device_info_text.appendPlainText(f"  Chip ID: {info.get('chipid', 'Неизвестно')}")
            self.device_info_text.appendPlainText(f"  Серийный номер: {info.get('serial', 'Неизвестно')}")
            self.device_info_text.appendPlainText(f"  Flash: {info.get('flash_size', 'Неизвестно')}")
            self.device_info_text.appendPlainText(f"  SRAM: {info.get('sram_size', 'Неизвестно')}")
            
            self.device_connected = True
            self.log(f"{message}")
            self.device_status.setText("Устройство подключено")
            self.filter_firmware_list()
            QMessageBox.information(self, "Успех", "Устройство успешно подключено!")
        else:
            self.log(f"{message}")
            self.device_connected = False
            self.device_status.setText("Ошибка подключения")
            self.device_info_text.clear()
            self.device_info_text.appendPlainText("Не удалось подключиться к устройству\n\n")
            self.device_info_text.appendPlainText("Проверьте:")
            self.device_info_text.appendPlainText("  1. Подключен ли программатор ST-Link")
            self.device_info_text.appendPlainText("  2. Установлены ли драйверы")
            self.device_info_text.appendPlainText("  3. Установлен ли st-link (st-info, st-flash)")
            self.device_info_text.appendPlainText("  4. Подключено ли питание к устройству")
            QMessageBox.warning(self, "Ошибка", message)
        
        self.connect_btn.setEnabled(True)
    
    def on_firmware_selected(self):
        """Выбор прошивки из списка."""
        selected = self.firmware_list.currentItem()
        if selected and selected.data(Qt.UserRole):
            self.flash_btn.setEnabled(True)
            self.current_firmware_path = selected.data(Qt.UserRole)
            self.log(f"Выбрана прошивка: {selected.text()}")
        else:
            self.flash_btn.setEnabled(False)
    
    def on_firmware_double_click(self, item):
        """Двойной клик для быстрой прошивки."""
        if item and item.data(Qt.UserRole):
            self.current_firmware_path = item.data(Qt.UserRole)
            self.flash_device()
    
    def flash_device(self):
        """Прошивает устройство в отдельном потоке."""
        if self.is_flashing:
            return
            
        if not self.current_firmware_path:
            QMessageBox.warning(self, "Ошибка", "Прошивка не выбрана")
            return
            
        if not self.device_connected:
            QMessageBox.warning(self, "Ошибка", "Устройство не подключено")
            return
        
        if not Path(self.current_firmware_path).exists():
            QMessageBox.warning(self, "Ошибка", f"Файл прошивки не найден:\n{self.current_firmware_path}")
            return
        
        self.is_flashing = True
        self.flash_btn.setEnabled(False)
        self.connect_btn.setEnabled(False)
        self.refresh_btn.setEnabled(False)
        
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
        self.progress.setFormat("Прошивка...")
        
        self.log(f"Начинаем прошивку: {Path(self.current_firmware_path).name}")
        
        worker = FlashWorker(
            self.stlink,
            self.current_firmware_path,
            True
        )
        worker.signals.progress.connect(self.log)
        worker.signals.finished.connect(self.flash_finished)
        self.threadpool.start(worker)
    
    def flash_finished(self, success: bool, message: str):
        """Обработчик завершения прошивки."""
        self.progress.setVisible(False)
        self.progress.setRange(0, 100)
        self.progress.setFormat("%p%")
        
        if success:
            self.log(f"{message}")
            QMessageBox.information(
                self, 
                "Успех", 
                "Прошивка выполнена успешно!\n\n"
                "Если светодиод не мигает — отключите и снова подключите питание устройства."
            )
        else:
            self.log(f"Ошибка: {message}")
            QMessageBox.critical(self, "Ошибка", f"Прошивка не удалась:\n{message}")
        
        self.is_flashing = False
        self.flash_btn.setEnabled(True)
        self.connect_btn.setEnabled(True)
        self.refresh_btn.setEnabled(True)
    
    def log(self, message: str):
        """Добавляет сообщение в лог."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.appendPlainText(f"[{timestamp}] {message}")