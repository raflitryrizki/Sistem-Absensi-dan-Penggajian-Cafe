# views/karyawan_form.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt

class KaryawanForm(QDialog):
    def __init__(self, parent=None, karyawan_data=None):
        super().__init__(parent)
        self.karyawan_data = karyawan_data
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Tambah Karyawan" if not self.karyawan_data else "Edit Karyawan")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        # Form fields
        fields = [
            ("Nama:", QLineEdit()),
            ("Jabatan:", QComboBox()),
            ("Gaji Pokok:", QLineEdit()),
            ("Username:", QLineEdit()),
            ("Password:", QLineEdit())
        ]
        
        # Setup jabatan options
        fields[1][1].addItems(["Manager", "Barista", "Kasir", "Waitress", "Kitchen"])
        
        # Setup password field
        fields[4][1].setEchoMode(QLineEdit.EchoMode.Password)
        
        # Add fields to layout
        for label_text, input_widget in fields:
            field_layout = QHBoxLayout()
            field_layout.addWidget(QLabel(label_text))
            field_layout.addWidget(input_widget)
            layout.addLayout(field_layout)
            
            # Simpan reference ke widget
            setattr(self, label_text.lower().replace(':', '').replace(' ', '_'), input_widget)
        
        # Pre-fill data jika edit mode
        if self.karyawan_data:
            self.nama.setText(self.karyawan_data[1])
            self.jabatan.setCurrentText(self.karyawan_data[2])
            self.gaji_pokok.setText(str(self.karyawan_data[3]))
            self.username.setText(self.karyawan_data[4])
            self.password.setText(self.karyawan_data[5])
            self.password.setPlaceholderText("Kosongkan jika tidak ingin mengubah password")
        
        # Button layout
        button_layout = QHBoxLayout()
        self.btn_simpan = QPushButton("Simpan")
        self.btn_batal = QPushButton("Batal")
        
        self.btn_simpan.clicked.connect(self.accept)
        self.btn_batal.clicked.connect(self.reject)
        
        button_layout.addWidget(self.btn_simpan)
        button_layout.addWidget(self.btn_batal)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def get_data(self):
        return {
            'nama': self.nama.text().strip(),
            'jabatan': self.jabatan.currentText(),
            'gaji_pokok': self.gaji_pokok.text().strip(),
            'username': self.username.text().strip(),
            'password': self.password.text().strip()
        }
    
    def accept(self):
        data = self.get_data()
        
        # Validasi
        if not all([data['nama'], data['jabatan'], data['gaji_pokok'], data['username']]):
            QMessageBox.warning(self, "Error", "Semua field harus diisi!")
            return
            
        if not data['password'] and not self.karyawan_data:
            QMessageBox.warning(self, "Error", "Password harus diisi untuk karyawan baru!")
            return
            
        try:
            float(data['gaji_pokok'])
        except ValueError:
            QMessageBox.warning(self, "Error", "Gaji pokok harus angka!")
            return
            
        super().accept()