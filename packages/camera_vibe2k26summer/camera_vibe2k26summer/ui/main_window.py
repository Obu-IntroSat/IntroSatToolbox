"""Main window for camera application."""

from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QGroupBox, QComboBox, QGridLayout, QMessageBox,
    QProgressBar, QSpinBox, QCheckBox, QTabWidget, QFileDialog,
    QSplitter, QSlider, QDialog
)

from PIL import Image

from ..core.config import ConfigManager, CameraCommandConfig
from ..core.models import CameraState
from ..core.worker import CameraWorker
from .widgets import ZoomableImageLabel
from .dialogs import CreateConfigDialog


class CameraWidget(QWidget):
    """Главный виджет приложения"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.config_manager = ConfigManager()
        self.worker: Optional[CameraWorker] = None
        self.state = CameraState()
        self.image_data: Optional[bytes] = None
        
        self.setup_ui()
        self.load_configs()
        self.refresh_ports()
        self.add_log("🚀 Универсальная камера запущена")
        self.add_log("💡 Используйте колесико мыши для зума")
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)
        
        title = QLabel("📷 CAMERA VIBE2K26SUMMER")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("camera_title")
        main_layout.addWidget(title)
        
        control_panel = self._create_control_panel()
        main_layout.addWidget(control_panel)
        
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self._create_settings_panel())
        splitter.addWidget(self._create_tabs())
        splitter.setSizes([350, 350])
        main_layout.addWidget(splitter)
    
    def _create_control_panel(self) -> QWidget:
        panel = QWidget()
        layout = QHBoxLayout(panel)
        layout.setSpacing(10)
        
        config_group = QWidget()
        config_layout = QHBoxLayout(config_group)
        config_layout.setSpacing(5)
        config_layout.addWidget(QLabel("Профиль:"))
        
        self.config_combo = QComboBox()
        self.config_combo.setMinimumWidth(150)
        self.config_combo.currentIndexChanged.connect(self.on_config_changed)
        config_layout.addWidget(self.config_combo)
        
        self.add_config_btn = QPushButton("➕")
        self.add_config_btn.setToolTip("Создать конфигурацию")
        self.add_config_btn.clicked.connect(self.create_config)
        config_layout.addWidget(self.add_config_btn)
        
        self.load_config_btn = QPushButton("📂")
        self.load_config_btn.setToolTip("Загрузить конфигурацию")
        self.load_config_btn.clicked.connect(self.load_config_file)
        config_layout.addWidget(self.load_config_btn)
        
        layout.addWidget(config_group)
        layout.addStretch()
        
        conn_group = QWidget()
        conn_layout = QHBoxLayout(conn_group)
        conn_layout.setSpacing(5)
        
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(120)
        conn_layout.addWidget(QLabel("Порт:"))
        conn_layout.addWidget(self.port_combo)
        
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.clicked.connect(self.refresh_ports)
        conn_layout.addWidget(self.refresh_btn)
        
        self.connect_btn = QPushButton("🔌 Подключить")
        self.connect_btn.clicked.connect(self.toggle_connection)
        conn_layout.addWidget(self.connect_btn)
        
        layout.addWidget(conn_group)
        return panel
    
    def _create_settings_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(5)
        
        settings_group = QGroupBox("Настройки (применяются к следующему снимку)")
        settings_layout = QGridLayout(settings_group)
        settings_layout.setSpacing(8)
        
        settings_layout.addWidget(QLabel("Ширина:"), 0, 0)
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 1280)
        self.width_spin.setValue(640)
        settings_layout.addWidget(self.width_spin, 0, 1)
        
        settings_layout.addWidget(QLabel("Высота:"), 0, 2)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 1024)
        self.height_spin.setValue(480)
        settings_layout.addWidget(self.height_spin, 0, 3)
        
        self.set_size_btn = QPushButton("Применить")
        self.set_size_btn.clicked.connect(self.apply_resolution)
        settings_layout.addWidget(self.set_size_btn, 0, 4)
        
        settings_layout.addWidget(QLabel("vStart:"), 1, 0)
        self.v_start_spin = QSpinBox()
        self.v_start_spin.setRange(0, 1000)
        self.v_start_spin.setValue(0)
        settings_layout.addWidget(self.v_start_spin, 1, 1)
        
        settings_layout.addWidget(QLabel("hStart:"), 1, 2)
        self.h_start_spin = QSpinBox()
        self.h_start_spin.setRange(0, 1000)
        self.h_start_spin.setValue(0)
        settings_layout.addWidget(self.h_start_spin, 1, 3)
        
        self.set_crop_btn = QPushButton("Обрезать")
        self.set_crop_btn.clicked.connect(self.apply_crop)
        settings_layout.addWidget(self.set_crop_btn, 1, 4)
        
        settings_layout.addWidget(QLabel("Экспозиция:"), 2, 0)
        self.exposure_spin = QSpinBox()
        self.exposure_spin.setRange(0, 509)
        self.exposure_spin.setValue(0)
        settings_layout.addWidget(self.exposure_spin, 2, 1)
        
        self.auto_exp_check = QCheckBox("Авто")
        self.auto_exp_check.setChecked(True)
        self.auto_exp_check.toggled.connect(self.toggle_auto_exposure)
        settings_layout.addWidget(self.auto_exp_check, 2, 2)
        
        self.set_exp_btn = QPushButton("Установить")
        self.set_exp_btn.clicked.connect(self.apply_exposure)
        settings_layout.addWidget(self.set_exp_btn, 2, 3)
        
        settings_layout.addWidget(QLabel("Версия:"), 3, 0)
        self.version_label = QLabel("неизвестно")
        self.version_label.setObjectName("version_label")
        settings_layout.addWidget(self.version_label, 3, 1, 1, 2)
        
        hint = QLabel("ℹ️ Настройки применяются к следующему снимку")
        hint.setStyleSheet("color: #888; font-size: 10px; font-style: italic;")
        settings_layout.addWidget(hint, 3, 3, 1, 2)
        
        layout.addWidget(settings_group)
        
        action_layout = QHBoxLayout()
        action_layout.setSpacing(8)
        
        self.capture_btn = QPushButton("📸 Снимок")
        self.capture_btn.clicked.connect(self.capture_image)
        self.capture_btn.setEnabled(False)
        action_layout.addWidget(self.capture_btn)
        
        self.download_btn = QPushButton("⬇ Скачать")
        self.download_btn.clicked.connect(self.download_image)
        self.download_btn.setEnabled(False)
        action_layout.addWidget(self.download_btn)
        
        self.props_btn = QPushButton("ℹ Свойства")
        self.props_btn.clicked.connect(self.get_properties)
        self.props_btn.setEnabled(False)
        action_layout.addWidget(self.props_btn)
        
        self.save_btn = QPushButton("💾 Сохранить")
        self.save_btn.clicked.connect(self.save_image)
        self.save_btn.setEnabled(False)
        action_layout.addWidget(self.save_btn)
        
        self.clear_btn = QPushButton("🗑 Очистить")
        self.clear_btn.clicked.connect(self.clear_image)
        action_layout.addWidget(self.clear_btn)
        
        layout.addLayout(action_layout)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(20)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Готов к работе")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        return panel
    
    def _create_tabs(self) -> QTabWidget:
        tabs = QTabWidget()
        
        image_tab = QWidget()
        image_layout = QVBoxLayout(image_tab)
        image_layout.setContentsMargins(5, 5, 5, 5)
        
        zoom_widget = QWidget()
        zoom_layout = QHBoxLayout(zoom_widget)
        zoom_layout.setSpacing(5)
        zoom_layout.addWidget(QLabel("🔍"))
        
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setMinimum(10)
        self.zoom_slider.setMaximum(200)
        self.zoom_slider.setValue(100)
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)
        zoom_layout.addWidget(self.zoom_slider)
        
        self.zoom_label = QLabel("100%")
        self.zoom_label.setMinimumWidth(50)
        zoom_layout.addWidget(self.zoom_label)
        
        self.reset_zoom_btn = QPushButton("1:1")
        self.reset_zoom_btn.clicked.connect(self.reset_zoom)
        zoom_layout.addWidget(self.reset_zoom_btn)
        
        zoom_layout.addStretch()
        image_layout.addWidget(zoom_widget)
        
        self.image_label = ZoomableImageLabel()
        image_layout.addWidget(self.image_label)
        
        self.image_info = QLabel("")
        self.image_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_info.setObjectName("image_info")
        image_layout.addWidget(self.image_info)
        
        tabs.addTab(image_tab, "🖼 Изображение")
        
        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)
        log_layout.setContentsMargins(5, 5, 5, 5)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setObjectName("log_text")
        log_layout.addWidget(self.log_text)
        
        clear_log_btn = QPushButton("Очистить логи")
        clear_log_btn.clicked.connect(lambda: self.log_text.clear())
        log_layout.addWidget(clear_log_btn)
        
        tabs.addTab(log_tab, "📋 Логи")
        
        return tabs
    
    def load_configs(self):
        self.config_manager.load_from_folder()
        self.update_config_list()
    
    def update_config_list(self):
        self.config_combo.clear()
        for name in sorted(self.config_manager.configs.keys()):
            self.config_combo.addItem(name)
        if self.state.config_name in self.config_manager.configs:
            self.config_combo.setCurrentText(self.state.config_name)
    
    def on_config_changed(self):
        name = self.config_combo.currentText()
        config = self.config_manager.get(name)
        if config:
            self.state.config_name = name
            if self.worker:
                self.worker.set_config(config)
            self.add_log(f"📋 Профиль: {name}")
    
    def create_config(self):
        dialog = CreateConfigDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            config = dialog.get_config()
            if config.name in self.config_manager.configs:
                reply = QMessageBox.question(
                    self, "Конфигурация существует",
                    f"Конфигурация '{config.name}' уже существует. Перезаписать?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
            
            self.config_manager.update(config)
            self.update_config_list()
            self.config_combo.setCurrentText(config.name)
            self.add_log(f"✅ Создана конфигурация: {config.name}")
    
    def load_config_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Загрузить конфигурацию", "configs", "JSON Files (*.json)"
        )
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                config = CameraCommandConfig.from_dict(data)
                added = self.config_manager.add(config)
                if not added:
                    reply = QMessageBox.question(
                        self, "Конфигурация существует",
                        f"Конфигурация '{config.name}' уже существует. Перезаписать?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.No:
                        self.add_log(f"ℹ️ Импорт отменен: {config.name}")
                        return
                    self.config_manager.update(config)
                self.update_config_list()
                self.config_combo.setCurrentText(config.name)
                action = "Загружена" if added else "Обновлена"
                self.add_log(f"✅ {action} конфигурация: {config.name}")
            except Exception as e:
                self.add_log(f"❌ Ошибка: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))
    
    def refresh_ports(self):
        current = self.port_combo.currentText()
        self.port_combo.clear()
        try:
            import serial.tools.list_ports
            ports = [p.device for p in serial.tools.list_ports.comports()]
            self.port_combo.addItems(ports)
        except Exception:
            pass
        if current:
            idx = self.port_combo.findText(current)
            if idx >= 0:
                self.port_combo.setCurrentIndex(idx)
    
    def toggle_connection(self):
        if self.state.connected:
            self.disconnect()
        else:
            self.connect()
    
    def connect(self):
        port = self.port_combo.currentText()
        if not port:
            QMessageBox.warning(self, "Ошибка", "Выберите порт")
            return
        
        config = self.config_manager.get(self.state.config_name)
        if not config:
            config = CameraCommandConfig("CM 2.0")
        
        self.worker = CameraWorker(config)
        self._connect_signals()
        
        if self.worker.connect(port):
            self.state.connected = True
            self.connect_btn.setText("🔌 Отключить")
            self.status_label.setText("✅ Подключен")
            self.capture_btn.setEnabled(True)
            self.download_btn.setEnabled(True)
            self.props_btn.setEnabled(True)
            self.add_log(f"🔌 Подключено к {port}")
            self.worker.start_get_version()
        else:
            self.add_log("❌ Не удалось подключиться")
    
    def _connect_signals(self):
        self.worker.progress.connect(self.update_progress)
        self.worker.partial_image.connect(self.show_partial_image)
        self.worker.image_data.connect(self.display_image)
        self.worker.log.connect(self.add_log)
        self.worker.error.connect(self.show_error)
        self.worker.properties_received.connect(self.show_properties)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.capture_complete.connect(self.on_capture_complete)
        self.worker.version_received.connect(self.on_version_received)
    
    def disconnect(self):
        if self.worker:
            self.worker.stop()
            if self.worker.isRunning():
                self.worker.wait(3000)
            self.worker.disconnect()
            self.worker = None
        
        self.state.connected = False
        self.connect_btn.setText("🔌 Подключить")
        self.status_label.setText("⛔ Отключен")
        self.capture_btn.setEnabled(False)
        self.download_btn.setEnabled(False)
        self.props_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.version_label.setText("неизвестно")
    
    def on_version_received(self, version: str):
        self.state.firmware_version = version
        self.version_label.setText(version)
        self.add_log(f"📡 Версия прошивки: {version}")
        
        matches = self.config_manager.get_by_version(version)
        if len(matches) == 1:
            name, config = matches[0]
            self.config_combo.setCurrentText(name)
            if self.worker:
                self.worker.set_config(config)
            self.add_log(f"✅ Найден профиль: {name}")
        elif len(matches) > 1:
            name, config = matches[0]
            self.config_combo.setCurrentText(name)
            if self.worker:
                self.worker.set_config(config)
            self.add_log(f"⚠️ Найдено {len(matches)} профилей, выбран: {name}")
        else:
            self.add_log(f"⚠️ Профиль для версии {version} не найден")
            self.add_log("   Используется профиль по умолчанию")
        
        self.status_label.setText(f"✅ Подключен (v{version})")
    
    def capture_image(self):
        if self.worker and self.state.connected:
            self.capture_btn.setEnabled(False)
            self.download_btn.setEnabled(False)
            
            self.state.captured_width = self.state.width
            self.state.captured_height = self.state.height
            self.state.captured_v_start = self.state.v_start
            self.state.captured_h_start = self.state.h_start
            self.state.captured_exposure = self.state.exposure
            
            self.add_log("📸 Захват снимка...")
            self.worker.start_capture()
    
    def get_properties(self):
        if self.worker and self.state.connected:
            self.worker.start_properties()
    
    def download_image(self):
        if self.worker and self.state.connected:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.download_btn.setEnabled(False)
            self.capture_btn.setEnabled(False)
            self.props_btn.setEnabled(False)
            self.add_log("📥 Загрузка снимка...")
            self.worker.start_download()
    
    def apply_resolution(self):
        if self.worker and self.state.connected:
            w = self.width_spin.value()
            h = self.height_spin.value()
            self.state.width = w
            self.state.height = h
            self.worker.set_resolution(w, h)
            self.add_log(f"📐 Размер: {w}×{h} (применится к следующему снимку)")
    
    def apply_crop(self):
        self.state.v_start = self.v_start_spin.value()
        self.state.h_start = self.h_start_spin.value()
        if self.worker and self.state.connected:
            self.worker.set_crop(self.state.v_start, self.state.h_start)
            self.add_log(f"✂️ Обрезка: vStart={self.state.v_start}, hStart={self.state.h_start}")
    
    def apply_exposure(self):
        if self.worker and self.state.connected:
            exp = self.exposure_spin.value()
            self.state.exposure = exp
            self.worker.set_exposure(exp)
            self.add_log(f"🔆 Экспозиция: {'Авто' if exp == 0 else exp}")
    
    def toggle_auto_exposure(self, checked):
        self.exposure_spin.setEnabled(not checked)
        if checked:
            self.exposure_spin.setValue(0)
            self.state.exposure = 0
            if self.worker and self.state.connected:
                self.worker.set_exposure(0)
                self.add_log("🔆 Включен режим автоэкспозиции")
    
    def save_image(self):
        if not self.image_data:
            return
        
        save_dir = Path(__file__).parent.parent / "captures"
        save_dir.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        w = self.state.captured_width
        h = self.state.captured_height
        data = self.image_data[:w*h]
        
        try:
            img = Image.frombytes("L", (w, h), data)
            png_path = save_dir / f"capture_{ts}.png"
            img.save(png_path, "PNG")
            self.add_log(f"💾 Сохранено: {png_path.name}")
            QMessageBox.information(self, "Сохранено", f"Изображение сохранено:\n{png_path}")
        except Exception as e:
            self.add_log(f"❌ Ошибка: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))
    
    def clear_image(self):
        self.image_label.clear()
        self.image_info.setText("")
        self.image_data = None
        self.save_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.add_log("🗑 Очищено")
    
    def update_progress(self, value):
        self.progress_bar.setValue(value)
    
    def show_partial_image(self, data, w, h):
        try:
            expected = w * h
            show = data[:expected]
            if len(show) < expected:
                show += b'\x00' * (expected - len(show))
            img = QImage(show, w, h, w, QImage.Format_Grayscale8)
            pix = QPixmap.fromImage(img)
            self.image_label.set_image(pix)
            
            percent = int(min(100, (len(data) / expected) * 100)) if expected > 0 else 0
            self.image_info.setText(f"📥 Загрузка... {percent}% | {w}×{h} | {len(data)}/{expected} байт")
            self.progress_bar.setValue(percent)
        except Exception as e:
            self.add_log(f"⚠️ Ошибка отображения: {e}")
    
    def display_image(self, data):
        self.image_data = data
        w = self.state.captured_width
        h = self.state.captured_height
        try:
            img_data = data[:w*h]
            if len(img_data) < w*h:
                img_data += b'\x00' * (w*h - len(img_data))
            img = QImage(img_data, w, h, w, QImage.Format_Grayscale8)
            pix = QPixmap.fromImage(img)
            self.image_label.set_image(pix)
            
            self.image_info.setText(f"✅ {w}×{h} | vStart={self.state.captured_v_start} hStart={self.state.captured_h_start} | Эксп={self.state.captured_exposure}")
            self.save_btn.setEnabled(True)
            self.add_log(f"✅ Изображение загружено: {w}×{h}")
        except Exception as e:
            self.add_log(f"❌ Ошибка отображения: {e}")
    
    def show_properties(self, props):
        if props.get('chunks', 0) > 0:
            msg = f"📸 Параметры снимка:\n\n"
            msg += f"Размер: {props.get('width', 0)}×{props.get('height', 0)}\n"
            msg += f"Чанков: {props.get('chunks', 0)}\n"
            msg += f"vStart: {props.get('v_start', 0)}\n"
            msg += f"hStart: {props.get('h_start', 0)}\n"
            msg += f"Экспозиция: {props.get('exposure', 0)}"
            QMessageBox.information(self, "Свойства", msg)
        else:
            QMessageBox.information(self, "Свойства", "ℹ️ В памяти нет снимка")
    
    def on_capture_complete(self):
        self.capture_btn.setEnabled(True)
        self.download_btn.setEnabled(True)
        self.add_log("✅ Снимок создан! Нажмите 'Скачать'")
        self.status_label.setText("✅ Снимок готов к загрузке")
    
    def on_worker_finished(self):
        self.capture_btn.setEnabled(True)
        self.download_btn.setEnabled(True)
        self.props_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
    
    def show_error(self, msg):
        self.add_log(f"❌ {msg}")
        self.capture_btn.setEnabled(True)
        self.download_btn.setEnabled(True)
        self.props_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Ошибка", msg)
    
    def add_log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{ts}] {msg}")
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())
    
    def on_zoom_changed(self, value: int):
        zoom = value / 100.0
        self.image_label.set_zoom(zoom)
        self.zoom_label.setText(f"{value}%")
    
    def reset_zoom(self):
        self.zoom_slider.setValue(100)
        self.image_label.reset_zoom()