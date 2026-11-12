# views/karyawan_dashboard.py
import sys
from datetime import datetime  # TAMBAHKAN INI!
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QMessageBox, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from modules.database import Database
from views.absensi_form import AbsensiForm

class KaryawanDashboard(QMainWindow):
    def __init__(self, user_data):
        super().__init__()
        self.user_id, self.nama, self.jabatan = user_data
        self.db = Database()
        
        self.setWindowTitle(f"Dashboard Karyawan - {self.nama}")
        self.setGeometry(100, 100, 600, 400)
        
        self.setup_ui()
        self.update_status_absen()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Header
        header_label = QLabel(f"Selamat Bekerja, {self.nama}!")
        header_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Status absen
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; padding: 10px;")
        layout.addWidget(self.status_label)
        
        # Tombol absen
        btn_layout = QHBoxLayout()
        self.btn_masuk = QPushButton("🟢 Absen Masuk")
        self.btn_pulang = QPushButton("🔴 Absen Pulang")
        self.btn_riwayat = QPushButton("📊 Lihat Riwayat")
        
        self.btn_masuk.clicked.connect(self.absen_masuk)
        self.btn_pulang.clicked.connect(self.absen_pulang)
        self.btn_riwayat.clicked.connect(self.lihat_riwayat)
        
        btn_layout.addWidget(self.btn_masuk)
        btn_layout.addWidget(self.btn_pulang)
        btn_layout.addWidget(self.btn_riwayat)
        
        layout.addLayout(btn_layout)
        
        # Info hari ini
        today_label = QLabel(f"Hari ini: {self.get_current_datetime()}")
        today_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(today_label)
        
        # Table absensi hari ini
        self.table_absensi = QTableWidget()
        self.table_absensi.setColumnCount(4)
        self.table_absensi.setHorizontalHeaderLabels(["Tanggal", "Jam Masuk", "Jam Pulang", "Status"])
        layout.addWidget(self.table_absensi)
        
        self.load_absensi_hari_ini()
    
    def get_current_datetime(self):
        return datetime.now().strftime("%A, %d %B %Y %H:%M:%S")  # HAPUS 'from datetime import datetime' DARI SINI
    
    def update_status_absen(self):
        # Cek apakah sudah absen hari ini
        today = datetime.now().date()
        self.db.cursor.execute('''
            SELECT jam_masuk, jam_keluar FROM absensi 
            WHERE id_karyawan = ? AND tanggal = ?
        ''', (self.user_id, today))
        
        absensi = self.db.cursor.fetchone()
        
        if absensi:
            jam_masuk, jam_keluar = absensi
            if jam_keluar:
                status = "✅ Sudah absen masuk dan pulang"
                self.btn_masuk.setEnabled(False)
                self.btn_pulang.setEnabled(False)
            else:
                status = "🟡 Sudah absen masuk, belum pulang"
                self.btn_masuk.setEnabled(False)
                self.btn_pulang.setEnabled(True)
        else:
            status = "🔴 Belum absen masuk"
            self.btn_masuk.setEnabled(True)
            self.btn_pulang.setEnabled(False)
        
        self.status_label.setText(status)
    
    def absen_masuk(self):
        if self.db.absen_masuk(self.user_id):

            # Ambil status absensi yang baru dibuat
            today = datetime.now().date()

            self.db.cursor.execute(
                """
                SELECT jam_masuk, status
                FROM absensi
                WHERE id_karyawan = ?
                AND tanggal = ?
                """,
                (self.user_id, today)
            )

            absensi = self.db.cursor.fetchone()

            if absensi:
                jam_masuk, status = absensi

                QMessageBox.information(
                    self,
                    "Absen Masuk",
                    f"Absen masuk berhasil!\n\n"
                    f"Jam masuk : {jam_masuk}\n"
                    f"Status    : {status}"
                )
            else:
                QMessageBox.information(
                    self,
                    "Sukses",
                    "Absen masuk berhasil!"
                )

            self.update_status_absen()
            self.load_absensi_hari_ini()
            
        else:
            QMessageBox.warning(
                self,
                "Gagal",
                "Anda sudah melakukan absen masuk hari ini!"
            )
    
    def absen_pulang(self):
        if self.db.absen_pulang(self.user_id):
            QMessageBox.information(self, "Sukses", "Absen pulang berhasil!")
            self.update_status_absen()
            self.load_absensi_hari_ini()
        else:
            QMessageBox.warning(self, "Error", "Gagal absen pulang!")
    
    def lihat_riwayat(self):
        form = AbsensiForm(self, (self.user_id, self.nama, self.jabatan))
        form.exec()
    
    def load_absensi_hari_ini(self):
        """Menampilkan absensi hari ini untuk karyawan yang sedang login."""

        today = datetime.now().date()

        self.db.cursor.execute(
            """
            SELECT
                tanggal,
                jam_masuk,
                jam_keluar,
                status
            FROM absensi
            WHERE id_karyawan = ?
            AND tanggal = ?
            ORDER BY tanggal DESC
            """,
            (self.user_id, today)
        )

        data = self.db.cursor.fetchall()

        self.table_absensi.setRowCount(len(data))

        for row, absensi in enumerate(data):
            for col in range(4):
                value = absensi[col] if absensi[col] else "-"

                item = QTableWidgetItem(str(value))

                item.setFlags(
                    item.flags()
                    & ~Qt.ItemFlag.ItemIsEditable
                )

                self.table_absensi.setItem(
                    row,
                    col,
                    item
                )
    
    def closeEvent(self, event):
        self.db.conn.close()
        event.accept()

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    sample_data = (2, "Siti Rahayu", "Barista")
    window = KaryawanDashboard(sample_data)
    window.show()
    sys.exit(app.exec())