"""UI for flashing firmware from Git repositories."""

from __future__ import annotations

import json
import subprocess
import re
import sys
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

from .github_release_manager import GitHubReleaseManager
from .stlink_client import STLinkClient


class FlashWorkerSignals(QObject):
    progress = Signal(str)
    finished = Signal(bool, str)


class FlashWorker(QRunnable):
    
    def __init__(self, stlink: STLinkClient, firmware_path: str):
        super().__init__()
        self.stlink = stlink
        self.firmware_path = firmware_path
        self.signals = FlashWorkerSignals()
    
    def run(self):
        self.signals.progress.emit("Начинаем прошивку...")
        success, message = self.stlink.flash(self.firmware_path)
        self.signals.finished.emit(success, message)


class FirmwareGitRepoWidget(QWidget):
    
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        
        self.config_file = self._find_config_file()
        self.storage_path = Path.home() / ".introsat" / "firmware"
        self.token_file = Path.home() / ".introsat" / ".github_token"
        
        self.github_token = self._load_github_token()
        
        self.release_manager = GitHubReleaseManager(
            self.config_file, 
            self.storage_path,
            token=self.github_token
        )
        self.stlink = STLinkClient()
        
        self.all_firmware = []
        self.devices = {}
        self.selected_device = None
        self.current_firmware_path = None
        self.is_flashing = False
        self.device_connected = False
        
        self.threadpool = QThreadPool()
        
        self.init_ui()
        self.check_stlink_status()
        self.refresh_firmware_list()
    
    def _find_config_file(self) -> Path:
        """Find firmware_repositories.json in multiple possible locations."""
        if getattr(sys, 'frozen', False):
            app_dir = Path(sys.executable).parent
            possible_paths = [
                app_dir / "firmware_repositories.json",
                app_dir / ".." / "firmware_repositories.json",
                app_dir / "packages" / "app_firmware_gitrepo" / "firmware_repositories.json",
                app_dir.parent / "firmware_repositories.json",
                app_dir.parent / ".." / "firmware_repositories.json",
                app_dir / "packages" / "app_firmware_gitrepo" / "app_firmware_gitrepo" / ".." / "firmware_repositories.json",
            ]
            for path in possible_paths:
                if path.exists():
                    print(f"[DEBUG] Config found at: {path}")
                    return path
        
        local_path = Path(__file__).parent.parent / "firmware_repositories.json"
        if local_path.exists():
            print(f"[DEBUG] Config found at: {local_path}")
            return local_path
        
        user_path = Path.home() / ".introsat" / "firmware_repositories.json"
        if user_path.exists():
            print(f"[DEBUG] Config found at: {user_path}")
            return user_path
        
        print(f"[WARNING] Config file not found! Using default path.")
        return Path(__file__).parent.parent / "firmware_repositories.json"
    
    def _load_github_token(self) -> Optional[str]:
        if self.token_file.exists():
            try:
                with open(self.token_file, 'r', encoding='utf-8') as f:
                    token = f.read().strip()
                    if token:
                        return token
            except Exception:
                pass
        return None
    
    def _save_github_token(self, token: str):
        self.token_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.token_file, 'w', encoding='utf-8') as f:
                f.write(token.strip())
            return True
        except Exception:
            return False
    
    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(5)
        
        repo_group = QGroupBox("Управление прошивками")
        repo_layout = QVBoxLayout()
        repo_layout.setSpacing(3)
        
        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Обновить прошивки")
        self.refresh_btn.clicked.connect(self.refresh_firmware_list)
        btn_layout.addWidget(self.refresh_btn)
        
        self.repo_status = QLabel("Готов")
        btn_layout.addWidget(self.repo_status)
        btn_layout.addStretch()
        repo_layout.addLayout(btn_layout)
        
        token_layout = QHBoxLayout()
        token_layout.setSpacing(3)
        
        token_label = QLabel("Token:")
        token_layout.addWidget(token_label)
        
        self.token_edit = QLineEdit()
        self.token_edit.setPlaceholderText("Введите токен")
        self.token_edit.setMinimumWidth(700)
        self.token_edit.setEchoMode(QLineEdit.Password)
        if self.github_token:
            self.token_edit.setText(self.github_token)
        self.token_edit.textChanged.connect(self.on_token_changed)
        token_layout.addWidget(self.token_edit)
        
        self.toggle_visibility_btn = QPushButton("👁")
        self.toggle_visibility_btn.setToolTip("Показать/скрыть токен")
        self.toggle_visibility_btn.clicked.connect(self.toggle_token_visibility)
        token_layout.addWidget(self.toggle_visibility_btn)
        
        self.token_file_btn = QPushButton("Обзор...")
        self.token_file_btn.setToolTip("Выбрать файл с токеном")
        self.token_file_btn.clicked.connect(self.select_token_file)
        token_layout.addWidget(self.token_file_btn)
        
        self.token_status = QLabel()
        if self.github_token:
            self.token_status.setText("Токен загружен")
            self.token_status.setStyleSheet("color: green;")
        else:
            self.token_status.setText("Токен не найден")
            self.token_status.setStyleSheet("color: orange;")
        token_layout.addWidget(self.token_status)
        
        token_layout.addStretch()
        repo_layout.addLayout(token_layout)
        
        devices_layout = QHBoxLayout()
        devices_layout.setSpacing(5)
        
        devices_group = QGroupBox("Устройства")
        devices_group_layout = QVBoxLayout()
        devices_group_layout.setContentsMargins(5, 5, 5, 5)
        
        self.devices_list = QListWidget()
        self.devices_list.setMinimumHeight(150)
        self.devices_list.setMaximumHeight(200)
        self.devices_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.devices_list.itemSelectionChanged.connect(self.on_device_selected)
        devices_group_layout.addWidget(self.devices_list)
        
        devices_group.setLayout(devices_group_layout)
        devices_layout.addWidget(devices_group, 1)
        
        firmware_group = QGroupBox("Прошивки")
        firmware_group_layout = QVBoxLayout()
        firmware_group_layout.setContentsMargins(5, 5, 5, 5)
        
        count_layout = QHBoxLayout()
        count_layout.addStretch()
        self.firmware_count_label = QLabel("Найдено: 0")
        count_layout.addWidget(self.firmware_count_label)
        firmware_group_layout.addLayout(count_layout)
        
        self.firmware_list = QListWidget()
        self.firmware_list.setMinimumHeight(150)
        self.firmware_list.setMaximumHeight(200)
        self.firmware_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.firmware_list.itemSelectionChanged.connect(self.on_firmware_selected)
        self.firmware_list.itemDoubleClicked.connect(self.on_firmware_double_click)
        firmware_group_layout.addWidget(self.firmware_list)
        
        firmware_group.setLayout(firmware_group_layout)
        devices_layout.addWidget(firmware_group, 2)
        
        repo_layout.addLayout(devices_layout)
        
        repo_group.setLayout(repo_layout)
        main_layout.addWidget(repo_group)
        
        device_group = QGroupBox("Подключение устройства")
        device_layout = QVBoxLayout()
        device_layout.setSpacing(3)
        
        stlink_layout = QHBoxLayout()
        self.stlink_status_label = QLabel("ST-Link: проверка...")
        stlink_layout.addWidget(self.stlink_status_label)
        stlink_layout.addStretch()
        device_layout.addLayout(stlink_layout)
        
        connect_layout = QHBoxLayout()
        self.connect_btn = QPushButton("Подключить устройство")
        self.connect_btn.clicked.connect(self.connect_device)
        connect_layout.addWidget(self.connect_btn)
        
        self.device_status = QLabel("Устройство не подключено")
        connect_layout.addWidget(self.device_status)
        connect_layout.addStretch()
        device_layout.addLayout(connect_layout)
        
        self.device_info_text = QPlainTextEdit()
        self.device_info_text.setReadOnly(True)
        self.device_info_text.setMinimumHeight(100)
        self.device_info_text.setMaximumHeight(200)
        self.device_info_text.setPlaceholderText("Информация об устройстве появится здесь после подключения")
        device_layout.addWidget(self.device_info_text)
        
        device_group.setLayout(device_layout)
        main_layout.addWidget(device_group)
        
        flash_group = QGroupBox("Прошивка")
        flash_layout = QVBoxLayout()
        flash_layout.setSpacing(3)
        
        flash_btn_layout = QHBoxLayout()
        self.flash_btn = QPushButton("Прошить выбранную прошивку")
        self.flash_btn.setEnabled(False)
        self.flash_btn.clicked.connect(self.flash_device)
        flash_btn_layout.addWidget(self.flash_btn)
        flash_btn_layout.addStretch()
        flash_layout.addLayout(flash_btn_layout)
        
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        flash_layout.addWidget(self.progress)
        
        flash_group.setLayout(flash_layout)
        main_layout.addWidget(flash_group)
        
        log_group = QGroupBox("Лог операций")
        log_layout = QVBoxLayout()
        log_layout.setSpacing(3)
        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumBlockCount(1000)
        self.log_text.setMinimumHeight(300)
        
        log_btn_layout = QHBoxLayout()
        clear_log_btn = QPushButton("Очистить лог")
        clear_log_btn.clicked.connect(lambda: self.log_text.clear())
        log_btn_layout.addWidget(clear_log_btn)
        log_btn_layout.addStretch()
        log_layout.addLayout(log_btn_layout)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
        
        main_layout.addStretch()
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setWidget(main_widget)
        
        base_layout = QVBoxLayout(self)
        base_layout.setContentsMargins(0, 0, 0, 0)
        base_layout.addWidget(scroll)
    
    def toggle_token_visibility(self):
        if self.token_edit.echoMode() == QLineEdit.Password:
            self.token_edit.setEchoMode(QLineEdit.Normal)
            self.toggle_visibility_btn.setText("🙈")
            self.toggle_visibility_btn.setToolTip("Скрыть токен")
        else:
            self.token_edit.setEchoMode(QLineEdit.Password)
            self.toggle_visibility_btn.setText("👁")
            self.toggle_visibility_btn.setToolTip("Показать токен")
    
    def select_token_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл с GitHub токеном",
            str(Path.home() / ".introsat"),
            "Токен файлы (.github_token);;Текстовые файлы (*.txt);;Все файлы (*)"
        )
        
        if file_path:
            token = self._load_github_token(Path(file_path))
            if token:
                self.token_edit.setText(token)
                self.token_file = Path(file_path)
                self.token_status.setText(f"Токен загружен из {Path(file_path).name}")
                self.token_status.setStyleSheet("color: green;")
                self.log(f"Токен загружен из файла: {file_path}")
            else:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    f"Не удалось прочитать токен из файла:\n{file_path}\n\n"
                    "Убедитесь, что файл содержит только токен в первой строке."
                )

    def on_token_changed(self, text: str):
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
        info = self.stlink.get_stlink_info()
        if info["available"]:
            self.stlink_status_label.setText(f"ST-Link: доступен (версия {info['version']})")
            if info["connected"]:
                self.stlink_status_label.setText("ST-Link: устройство уже подключено")
        else:
            self.stlink_status_label.setText("ST-Link: не найден")
    
    def refresh_firmware_list(self):
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
            
            repos_dict = {}
            for repo in self.release_manager.repositories:
                repos_dict[repo.get('name')] = repo.get('device', 'Unknown')
            
            self.devices = {}
            for fw in firmware_list:
                device = fw.get('device', '')
                if not device or device == 'Unknown':
                    repo_name = fw.get('repo', '')
                    device = repos_dict.get(repo_name, 'Unknown')
                    fw['device'] = device
                
                repo = fw.get('repo', '')
                device_name = f"{device} ({repo})" if repo else device
                if device_name not in self.devices:
                    self.devices[device_name] = []
                self.devices[device_name].append(fw)
            
            self.devices_list.clear()
            
            def sort_key(name):
                if 'STM32' in name:
                    return (0, name)
                elif 'ATmega' in name:
                    return (1, name)
                else:
                    return (2, name)
            
            for device_name in sorted(self.devices.keys(), key=sort_key):
                count = len(self.devices[device_name])
                self.devices_list.addItem(f"{device_name} ({count})")
            
            if self.devices_list.count() > 0:
                self.devices_list.setCurrentRow(0)
            
            self.log(f"Найдено {len(self.all_firmware)} прошивок в {len(self.devices)} устройствах")
            self.repo_status.setText(f"Готово ({len(self.all_firmware)} прошивок)")
            
        except Exception as e:
            self.log(f"Ошибка загрузки: {str(e)}")
            self.repo_status.setText("Ошибка загрузки")
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить прошивки:\n{str(e)}")
        
        self.refresh_btn.setEnabled(True)
    
    def on_device_selected(self):
        selected = self.devices_list.currentItem()
        if not selected:
            return
        
        device_name = selected.text()
        if ' (' in device_name:
            device_name = device_name[:device_name.rfind(' (')]
        
        self.selected_device = device_name
        self.display_firmware_for_device(device_name)
    
    def display_firmware_for_device(self, device_name: str):
        self.firmware_list.clear()
        
        if device_name not in self.devices:
            return
        
        firmwares = self.devices[device_name]
        
        if self.device_connected:
            device_chip = self.device_info_text.toPlainText()
            if 'STM32' in device_name:
                firmwares = [f for f in firmwares if f.get('device') == 'STM32']
            elif 'ATmega' in device_name:
                firmwares = [f for f in firmwares if f.get('device') == 'ATmega']
        
        for fw in firmwares:
            version = fw.get('version', '')
            item_text = f"{fw['name']}"
            if version and version != "unknown":
                if not version.startswith("v"):
                    item_text += f" (v{version})"
                else:
                    item_text += f" ({version})"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, fw.get("path", ""))
            
            tooltip = f"Файл: {fw['name']}\n"
            tooltip += f"Версия: {version}\n"
            tooltip += f"Устройство: {fw.get('device', 'Unknown')}\n"
            tooltip += f"Репозиторий: {fw.get('repo', '')}\n"
            if fw.get('published_at'):
                tooltip += f"Опубликовано: {fw['published_at']}\n"
            if fw.get('size'):
                tooltip += f"Размер: {fw['size']} байт"
            
            item.setToolTip(tooltip)
            self.firmware_list.addItem(item)
        
        self.firmware_count_label.setText(f"Найдено: {len(firmwares)}")
    
    def connect_device(self):
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
            
            if self.selected_device:
                self.display_firmware_for_device(self.selected_device)
            
            QMessageBox.information(self, "Успех", "Устройство успешно подключено!")
        else:
            self.log(f"{message}")
            self.device_connected = False
            self.device_status.setText("Ошибка подключения")
            self.device_info_text.clear()
            self.device_info_text.appendPlainText("Не удалось подключиться к устройству\n")
            self.device_info_text.appendPlainText("Проверьте:")
            self.device_info_text.appendPlainText("  1. Подключен ли программатор ST-Link")
            self.device_info_text.appendPlainText("  2. Установлены ли драйверы")
            self.device_info_text.appendPlainText("  3. Установлен ли st-link (st-info, st-flash)")
            self.device_info_text.appendPlainText("  4. Подключено ли питание к устройству")
            QMessageBox.warning(self, "Ошибка", message)
        
        self.connect_btn.setEnabled(True)
    
    def on_firmware_selected(self):
        selected = self.firmware_list.currentItem()
        if selected and selected.data(Qt.UserRole):
            self.flash_btn.setEnabled(True)
            self.current_firmware_path = selected.data(Qt.UserRole)
            self.log(f"Выбрана прошивка: {selected.text()}")
        else:
            self.flash_btn.setEnabled(False)
    
    def on_firmware_double_click(self, item):
        if item and item.data(Qt.UserRole):
            self.current_firmware_path = item.data(Qt.UserRole)
            self.flash_device()
    
    def flash_device(self):
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
            self.current_firmware_path
        )
        worker.signals.progress.connect(self.log)
        worker.signals.finished.connect(self.flash_finished)
        self.threadpool.start(worker)
    
    def flash_finished(self, success: bool, message: str):
        self.progress.setVisible(False)
        self.progress.setRange(0, 100)
        self.progress.setFormat("%p%")
        
        if success:
            self.log(f"{message}")
            QMessageBox.information(
                self, 
                "Успех", 
                "Прошивка выполнена успешно!"
            )
        else:
            self.log(f"Ошибка: {message}")
            QMessageBox.critical(self, "Ошибка", f"Прошивка не удалась:\n{message}")
        
        self.is_flashing = False
        self.flash_btn.setEnabled(True)
        self.connect_btn.setEnabled(True)
        self.refresh_btn.setEnabled(True)
    
    def log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.appendPlainText(f"[{timestamp}] {message}")