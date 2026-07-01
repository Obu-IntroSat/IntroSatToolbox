"""UI for camera application."""

from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QGroupBox, QLineEdit,
    QComboBox, QGridLayout, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QImage

class CameraWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Создание интерфейса приложения."""
        main_layout = QVBoxLayout(self)
        
        # ===== Заголовок =====
        title = QLabel("CAMERA VIBE2K26SUMMER")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold;
            padding: 10px;
            background-color: #2d2d2d;
            color: white;
            border-radius: 5px;
        """)
        main_layout.addWidget(title)
        
        # ===== Основной контент =====
        content_layout = QHBoxLayout()
        
        # ---- Левая панель: настройки ----
        left_panel = QVBoxLayout()
        
        # Группа: Настройки камеры
        settings_group = QGroupBox("Настройки камеры")
        settings_layout = QVBoxLayout(settings_group)
        
        # Выбор камеры
        cam_layout = QHBoxLayout()
        cam_layout.addWidget(QLabel("Камера:"))
        self.camera_combo = QComboBox()
        self.camera_combo.addItems(["Камера 1", "Камера 2", "Камера 3"])
        cam_layout.addWidget(self.camera_combo)
        settings_layout.addLayout(cam_layout)
        
        # Разрешение
        res_layout = QHBoxLayout()
        res_layout.addWidget(QLabel("Разрешение:"))
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["640x480", "1280x720", "1920x1080"])
        res_layout.addWidget(self.resolution_combo)
        settings_layout.addLayout(res_layout)
        
        # Частота кадров
        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel("FPS:"))
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["15", "30", "60"])
        fps_layout.addWidget(self.fps_combo)
        settings_layout.addLayout(fps_layout)
        
        left_panel.addWidget(settings_group)
        
        # Группа: Управление
        control_group = QGroupBox("Управление")
        control_layout = QVBoxLayout(control_group)
        
        self.start_btn = QPushButton("▶ Запустить камеру")
        self.start_btn.clicked.connect(self.start_camera)
        self.start_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        control_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹ Остановить")
        self.stop_btn.clicked.connect(self.stop_camera)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("background-color: #f44336; color: white;")
        control_layout.addWidget(self.stop_btn)
        
        self.capture_btn = QPushButton("📸 Сделать снимок")
        self.capture_btn.clicked.connect(self.capture_image)
        self.capture_btn.setEnabled(False)
        control_layout.addWidget(self.capture_btn)
        
        left_panel.addWidget(control_group)
        
        # Группа: Информация
        info_group = QGroupBox("Информация")
        info_layout = QVBoxLayout(info_group)
        
        self.status_label = QLabel("Статус: Не подключена")
        info_layout.addWidget(self.status_label)
        
        self.info_label = QLabel("Кадров: 0")
        info_layout.addWidget(self.info_label)
        
        left_panel.addWidget(info_group)
        left_panel.addStretch()
        
        # ---- Правая панель: видео и логи ----
        right_panel = QVBoxLayout()
        
        # Видео область
        video_group = QGroupBox("Видео")
        video_layout = QVBoxLayout(video_group)
        
        self.video_label = QLabel("Нет видео")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setMinimumHeight(400)
        self.video_label.setStyleSheet("""
            background-color: #1a1a1a;
            color: #666;
            border: 2px solid #333;
            border-radius: 5px;
        """)
        video_layout.addWidget(self.video_label)
        
        right_panel.addWidget(video_group)
        
        # Логи
        log_group = QGroupBox("Логи")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        self.log_text.setStyleSheet("""
            background-color: #1e1e1e;
            color: #d4d4d4;
            font-family: 'Courier New', monospace;
            font-size: 11px;
        """)
        log_layout.addWidget(self.log_text)
        
        right_panel.addWidget(log_group)
        
        # ---- Собираем всё вместе ----
        content_layout.addLayout(left_panel, 1)
        content_layout.addLayout(right_panel, 3)
        main_layout.addLayout(content_layout)
        
        # ===== Таймер для симуляции видео =====
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_video)
        self.frame_count = 0
        
        # Лог начального сообщения
        self.add_log("Приложение CAMERA_VIBE2K26SUMMER запущено")
        self.add_log("Готово к работе")
    
    # ===== Методы управления =====
    
    def start_camera(self):
        """Запуск камеры."""
        try:
            camera = self.camera_combo.currentText()
            resolution = self.resolution_combo.currentText()
            fps = self.fps_combo.currentText()
            
            self.add_log(f"Запуск камеры: {camera}")
            self.add_log(f"Разрешение: {resolution}, FPS: {fps}")
            
            # Здесь должна быть реальная логика подключения к камере
            # Пока симулируем
            
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.capture_btn.setEnabled(True)
            self.status_label.setText("Статус: Запущена")
            self.status_label.setStyleSheet("color: #4CAF50;")
            
            self.timer.start(1000 // int(fps))  # Таймер с частотой FPS
            
            self.add_log("✅ Камера успешно запущена")
            
        except Exception as e:
            self.add_log(f"❌ Ошибка запуска: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось запустить камеру:\n{str(e)}")
    
    def stop_camera(self):
        """Остановка камеры."""
        self.timer.stop()
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.capture_btn.setEnabled(False)
        self.status_label.setText("Статус: Остановлена")
        self.status_label.setStyleSheet("color: #f44336;")
        
        self.video_label.setText("Нет видео")
        self.video_label.setStyleSheet("""
            background-color: #1a1a1a;
            color: #666;
            border: 2px solid #333;
            border-radius: 5px;
        """)
        
        self.add_log("⏹ Камера остановлена")
        self.frame_count = 0
        self.info_label.setText("Кадров: 0")
    
    def capture_image(self):
        """Сделать снимок."""
        self.add_log("📸 Снимок сохранен")
        QMessageBox.information(self, "Снимок", "Снимок сохранен в папку captures/")
    
    def update_video(self):
        """Обновление видео (симуляция)."""
        self.frame_count += 1
        self.info_label.setText(f"Кадров: {self.frame_count}")
        
        # Симуляция обновления видео
        # В реальном приложении здесь будет получение кадра с камеры
        self.video_label.setText(f"🎥 Видео\n\nКадр #{self.frame_count}")
        self.video_label.setStyleSheet("""
            background-color: #2a2a2a;
            color: #00ff00;
            border: 2px solid #4CAF50;
            border-radius: 5px;
            font-size: 16px;
        """)
    
    def add_log(self, message):
        """Добавить сообщение в лог."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        # Автоскролл вниз
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )