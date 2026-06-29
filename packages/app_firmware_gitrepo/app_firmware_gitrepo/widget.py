"""UI for flashing firmware from Git repositories."""

from __future__ import annotations

import subprocess
import re
from pathlib import Path
from typing import Dict, List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QPlainTextEdit, QGroupBox, QListWidget,
    QProgressBar, QMessageBox, QLineEdit
)


class FirmwareGitRepoWidget(QWidget):
    """Главный виджет приложения"""
    
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        
        # Настройка репозитория
        self.repo_url = "https://github.com/your-org/firmware-repo.git"
        self.repo_path = Path.home() / ".introsat" / "firmware_repo"
        self.current_firmware_path = None
        self.device_connected = False
        
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        main_layout = QVBoxLayout()
        
        # --- Управление репозиторием ---
        repo_group = QGroupBox("Управление прошивками")
        repo_layout = QVBoxLayout()
        
        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Обновить прошивки из Git")
        self.refresh_btn.clicked.connect(self.refresh_firmware_list)
        btn_layout.addWidget(self.refresh_btn)
        
        self.repo_status = QLabel("Статус: готов")
        btn_layout.addWidget(self.repo_status)
        repo_layout.addLayout(btn_layout)
        
        # URL репозитория
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("URL:"))
        self.repo_url_edit = QLineEdit(self.repo_url)
        url_layout.addWidget(self.repo_url_edit)
        repo_layout.addLayout(url_layout)
        
        # Список прошивок
        repo_layout.addWidget(QLabel("Доступные прошивки:"))
        self.firmware_list = QListWidget()
        self.firmware_list.itemSelectionChanged.connect(self.on_firmware_selected)
        repo_layout.addWidget(self.firmware_list)
        
        repo_group.setLayout(repo_layout)
        main_layout.addWidget(repo_group)
        
        # --- Подключение устройства ---
        device_group = QGroupBox("Подключение устройства")
        device_layout = QVBoxLayout()
        
        connect_layout = QHBoxLayout()
        self.connect_btn = QPushButton("Подключить устройство")
        self.connect_btn.clicked.connect(self.connect_device)
        connect_layout.addWidget(self.connect_btn)
        
        self.device_status = QLabel("Устройство не подключено")
        connect_layout.addWidget(self.device_status)
        device_layout.addLayout(connect_layout)
        
        # Информация об устройстве
        self.device_info_text = QPlainTextEdit()
        self.device_info_text.setReadOnly(True)
        self.device_info_text.setMaximumHeight(80)
        device_layout.addWidget(self.device_info_text)
        
        device_group.setLayout(device_layout)
        main_layout.addWidget(device_group)
        
        # --- Прошивка ---
        flash_group = QGroupBox("Прошивка")
        flash_layout = QVBoxLayout()
        
        self.flash_btn = QPushButton("Прошить выбранную прошивку")
        self.flash_btn.setEnabled(False)
        self.flash_btn.clicked.connect(self.flash_device)
        flash_layout.addWidget(self.flash_btn)
        
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        flash_layout.addWidget(self.progress)
        
        flash_group.setLayout(flash_layout)
        main_layout.addWidget(flash_group)
        
        # --- Лог ---
        log_group = QGroupBox("Лог")
        log_layout = QVBoxLayout()
        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
        
        self.setLayout(main_layout)
        
        # Загружаем список прошивок при старте
        self.refresh_firmware_list()
    
    def refresh_firmware_list(self):
        """Обновляет список прошивок"""
        self.log("Обновление списка прошивок...")
        
        # Создаем тестовые данные для демонстрации
        self.firmware_list.clear()
        test_firmwares = [
            "firmware_v1.0.hex [STM32]",
            "firmware_v1.1.hex [STM32]",
            "firmware_v2.0.bin [ATmega]",
            "bootloader.hex [STM32]"
        ]
        
        for fw in test_firmwares:
            self.firmware_list.addItem(fw)
        
        self.log(f"✓ Найдено {len(test_firmwares)} тестовых прошивок")
        self.repo_status.setText("Статус: готово (тестовый режим)")
    
    def connect_device(self):
        """Подключается к устройству"""
        self.log("Подключение к устройству...")
        
        # Имитация подключения
        self.device_connected = True
        self.device_status.setText("✓ Устройство подключено (STM32F103)")
        self.device_info_text.clear()
        self.device_info_text.appendPlainText("Чип: STM32F103C8T6")
        self.device_info_text.appendPlainText("Core ID: 0x2BA01477")
        self.device_info_text.appendPlainText("Flash size: 64 KB")
        
        self.log("✓ Устройство подключено успешно (тестовый режим)")
    
    def on_firmware_selected(self):
        """Выбор прошивки"""
        selected = self.firmware_list.currentItem()
        if selected:
            self.flash_btn.setEnabled(True)
            self.current_firmware_path = selected.text()
            self.log(f"Выбрана прошивка: {selected.text()}")
    
    def flash_device(self):
        """Прошивает устройство"""
        if not self.current_firmware_path:
            return
        
        self.log(f"Начинаем прошивку: {self.current_firmware_path}")
        self.flash_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
        
        # Имитация процесса прошивки
        from PySide6.QtCore import QTimer
        QTimer.singleShot(3000, self.flash_complete)
    
    def flash_complete(self):
        """Завершение прошивки"""
        self.progress.setVisible(False)
        self.log("✓ Прошивка успешно завершена!")
        self.flash_btn.setEnabled(True)
        QMessageBox.information(self, "Успех", "Прошивка выполнена успешно!")
    
    def log(self, message: str):
        """Добавляет сообщение в лог"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.appendPlainText(f"[{timestamp}] {message}")