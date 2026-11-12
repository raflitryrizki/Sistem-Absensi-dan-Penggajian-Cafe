import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, 
    QLineEdit, QPushButton, QVBoxLayout, QMessageBox
)
from modules.database import Database

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setWindowTitle("Login - Sistem Absensi Cafe")
        self.setFixedSize(300, 200)
        
        # Widgets
        self.label_username = QLabel("Username:")
        self.input_username = QLineEdit()
        self.label_password = QLabel("Password:")
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.btn_login = QPushButton("Login")
        
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label_username)
        layout.addWidget(self.input_username)
        layout.addWidget(self.label_password)
        layout.addWidget(self.input_password)
        layout.addWidget(self.btn_login)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        # Event
        self.btn_login.clicked.connect(self.handle_login)
        self.input_password.returnPressed.connect(self.handle_login)
        
    def handle_login(self):
        try:
            username = self.input_username.text().strip()
            password = self.input_password.text().strip()
        
            if not username or not password:
                QMessageBox.warning(self, "Peringatan", "Username dan password harus diisi!")
                return
            
            user_data = self.db.login(username, password)
        
            if user_data:
                user_id, nama, jabatan = user_data
                QMessageBox.information(self, "Berhasil", f"Selamat datang {nama} ({jabatan})!")
            
                # Buka dashboard sesuai jabatan
                if str(jabatan).lower() == "owner":
                    from views.owner_dashboard import OwnerDashboard
                    self.dashboard = OwnerDashboard(user_data)
                    self.dashboard.show()
                elif str(jabatan).lower() == "manager":
                    from views.admin_dashboard import AdminDashboard
                    self.dashboard = AdminDashboard(user_data)
                    self.dashboard.show()
                else:
                    from views.karyawan_dashboard import KaryawanDashboard
                    self.dashboard = KaryawanDashboard(user_data)
                    self.dashboard.show()

                self.close()
            else:
                QMessageBox.warning(self, "Gagal", "Username atau password salah!")
                self.input_password.clear()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Terjadi kesalahan: {str(e)}")
    

# Untuk testing tanpa dashboard
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())