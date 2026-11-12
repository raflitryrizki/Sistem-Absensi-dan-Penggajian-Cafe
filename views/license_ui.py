from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)


class LicenseWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Aktivasi Sistem Absensi Cafe")
        self.setFixedSize(450, 250)

        layout = QVBoxLayout()

        title = QLabel("Aktivasi Sistem Absensi Cafe")
        title.setStyleSheet(
            "font-size: 20px; font-weight: bold;"
        )

        info = QLabel(
            "Masukkan License Key untuk mengaktifkan aplikasi."
        )
        info.setWordWrap(True)

        self.machine_id = QLineEdit()
        self.machine_id.setReadOnly(True)

        key_label = QLabel("License Key:")

        self.license_input = QLineEdit()
        self.license_input.setPlaceholderText(
            "XXXX-XXXX-XXXX-XXXX"
        )

        activate_button = QPushButton("Aktivasi")
        activate_button.clicked.connect(self.activate_license)

        layout.addWidget(title)
        layout.addWidget(info)

        layout.addWidget(QLabel("Machine ID:"))
        layout.addWidget(self.machine_id)

        layout.addWidget(key_label)
        layout.addWidget(self.license_input)

        layout.addWidget(activate_button)

        self.setLayout(layout)

        self.load_machine_id()

    def load_machine_id(self):
        from modules.license_manager import LicenseManager

        self.machine_id.setText(
            LicenseManager.get_machine_id()
        )

    def activate_license(self):
        from modules.license_manager import LicenseManager

        license_key = self.license_input.text().strip()

        if not license_key:
            QMessageBox.warning(
                self,
                "Aktivasi",
                "Silakan masukkan License Key."
            )
            return

        if LicenseManager.verify_license_key(license_key):
            LicenseManager.save_license(license_key)

            QMessageBox.information(
                self,
                "Aktivasi Berhasil",
                "Aplikasi berhasil diaktifkan."
            )

            self.accept()

        else:
            QMessageBox.critical(
                self,
                "Aktivasi Gagal",
                "License Key tidak valid untuk komputer ini."
            )