"""Dialog windows for camera application."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QGroupBox,
    QGridLayout, QLabel, QDialogButtonBox
)

from ..core.config import CameraCommandConfig


class CreateConfigDialog(QDialog):
    """Диалог создания конфигурации"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Создать конфигурацию")
        self.setMinimumWidth(500)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Название конфигурации")
        form.addRow("Название:", self.name_edit)
        
        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("Описание")
        form.addRow("Описание:", self.desc_edit)
        
        self.version_edit = QLineEdit()
        self.version_edit.setPlaceholderText("Версия прошивки")
        form.addRow("Версия:", self.version_edit)
        
        cmd_group = QGroupBox("Команды")
        cmd_layout = QGridLayout(cmd_group)
        
        self.capture_edit = QLineEdit("t")
        self.properties_edit = QLineEdit("p")
        self.next_chunk_edit = QLineEdit("n")
        self.set_size_edit = QLineEdit("s")
        self.set_exposure_edit = QLineEdit("e")
        self.start_transfer_edit = QLineEdit("r")
        self.get_version_edit = QLineEdit("v")
        
        cmd_fields = [
            ("Снимок:", self.capture_edit, 0, 0),
            ("Свойства:", self.properties_edit, 0, 2),
            ("Чанк:", self.next_chunk_edit, 1, 0),
            ("Размер:", self.set_size_edit, 1, 2),
            ("Экспозиция:", self.set_exposure_edit, 2, 0),
            ("Передача:", self.start_transfer_edit, 2, 2),
            ("Версия:", self.get_version_edit, 3, 0),
        ]
        
        for label, edit, row, col in cmd_fields:
            cmd_layout.addWidget(QLabel(label), row, col)
            cmd_layout.addWidget(edit, row, col + 1)
        
        form.addRow(cmd_group)
        
        proto_group = QGroupBox("Параметры протокола")
        proto_layout = QGridLayout(proto_group)
        
        self.baudrate_edit = QLineEdit("230400")
        self.preamble_edit = QLineEdit("ffff00")
        self.postamble_edit = QLineEdit("00ff00")
        self.chunk_size_edit = QLineEdit("240")
        self.property_size_edit = QLineEdit("18")
        self.timeout_capture_edit = QLineEdit("15.0")
        self.timeout_chunk_edit = QLineEdit("2.0")
        self.timeout_version_edit = QLineEdit("1.0")
        
        proto_fields = [
            ("Baudrate:", self.baudrate_edit, 0, 0),
            ("Преамбула:", self.preamble_edit, 0, 2),
            ("Постамбула:", self.postamble_edit, 1, 0),
            ("Размер чанка:", self.chunk_size_edit, 1, 2),
            ("Размер свойств:", self.property_size_edit, 2, 0),
            ("Таймаут захвата:", self.timeout_capture_edit, 2, 2),
            ("Таймаут чанка:", self.timeout_chunk_edit, 3, 0),
            ("Таймаут версии:", self.timeout_version_edit, 3, 2),
        ]
        
        for label, edit, row, col in proto_fields:
            proto_layout.addWidget(QLabel(label), row, col)
            proto_layout.addWidget(edit, row, col + 1)
        
        form.addRow(proto_group)
        
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_config(self) -> CameraCommandConfig:
        return CameraCommandConfig(
            name=self.name_edit.text(),
            description=self.desc_edit.text(),
            version=self.version_edit.text(),
            capture=self.capture_edit.text(),
            properties=self.properties_edit.text(),
            next_chunk=self.next_chunk_edit.text(),
            set_size=self.set_size_edit.text(),
            set_exposure=self.set_exposure_edit.text(),
            start_transfer=self.start_transfer_edit.text(),
            get_version=self.get_version_edit.text(),
            baudrate=int(self.baudrate_edit.text()),
            preamble=self.preamble_edit.text(),
            postamble=self.postamble_edit.text(),
            chunk_size=int(self.chunk_size_edit.text()),
            property_size=int(self.property_size_edit.text()),
            timeout_capture=float(self.timeout_capture_edit.text()),
            timeout_chunk=float(self.timeout_chunk_edit.text()),
            timeout_version=float(self.timeout_version_edit.text()),
        )