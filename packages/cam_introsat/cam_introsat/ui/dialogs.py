# -*- coding: utf-8 -*-
"""Диалог для создания новой конфигурации камеры."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QGroupBox,
    QGridLayout, QLabel, QDialogButtonBox, QMessageBox, QCheckBox
)

from ..core.config import CameraCommandConfig


class CreateConfigDialog(QDialog):
    """
    Диалог, в котором пользователь вводит все параметры конфигурации.
    При нажатии OK создаётся объект CameraCommandConfig.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Создать конфигурацию")
        self.setMinimumWidth(500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        # Основные поля
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Название конфигурации")
        form.addRow("Название:", self.name_edit)

        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("Описание")
        form.addRow("Описание:", self.desc_edit)

        self.version_edit = QLineEdit()
        self.version_edit.setPlaceholderText("Версия прошивки")
        form.addRow("Версия:", self.version_edit)

        # Группа команд
        cmd_group = QGroupBox("Команды")
        cmd_layout = QGridLayout(cmd_group)

        self.capture_edit = QLineEdit("t")
        self.properties_edit = QLineEdit("p")
        self.next_chunk_edit = QLineEdit("n")
        self.set_size_edit = QLineEdit("s")
        self.set_exposure_edit = QLineEdit("e")
        self.start_transfer_edit = QLineEdit("")
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

        # Группа параметров протокола
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

        self.send_chunk_index_check = QCheckBox("Отправлять номер чанка в next_chunk")
        self.send_chunk_index_check.setChecked(False)

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

        proto_layout.addWidget(self.send_chunk_index_check, 4, 0, 1, 2)

        form.addRow(proto_group)

        layout.addLayout(form)

        # Кнопки OK/Cancel
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_config(self) -> CameraCommandConfig:
        """Собирает данные из полей и возвращает объект конфигурации."""
        return CameraCommandConfig(
            name=self.name_edit.text().strip(),
            description=self.desc_edit.text().strip(),
            version=self.version_edit.text().strip(),
            capture=self.capture_edit.text().strip(),
            properties=self.properties_edit.text().strip(),
            next_chunk=self.next_chunk_edit.text().strip(),
            set_size=self.set_size_edit.text().strip(),
            set_exposure=self.set_exposure_edit.text().strip(),
            start_transfer=self.start_transfer_edit.text().strip(),
            get_version=self.get_version_edit.text().strip(),
            baudrate=int(self.baudrate_edit.text().strip()),
            preamble=self.preamble_edit.text().strip(),
            postamble=self.postamble_edit.text().strip(),
            chunk_size=int(self.chunk_size_edit.text().strip()),
            property_size=int(self.property_size_edit.text().strip()),
            timeout_capture=float(self.timeout_capture_edit.text().strip()),
            timeout_chunk=float(self.timeout_chunk_edit.text().strip()),
            timeout_version=float(self.timeout_version_edit.text().strip()),
            send_chunk_index=self.send_chunk_index_check.isChecked(),
        )

    def accept(self):
        """Проверяет корректность введённых данных перед закрытием."""
        try:
            config = self.get_config()
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", f"Проверьте числовые поля конфигурации:\n{str(e)}")
            return

        if not config.name:
            QMessageBox.warning(self, "Ошибка", "Укажите название конфигурации.")
            return

        try:
            bytes.fromhex(config.preamble)
            bytes.fromhex(config.postamble)
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Преамбула и постамбула должны быть hex-строками.")
            return

        super().accept()