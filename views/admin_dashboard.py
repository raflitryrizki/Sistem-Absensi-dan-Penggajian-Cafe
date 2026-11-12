# views/admin_dashboard.py
import sys
import os
import shutil
from config import Config
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, QTabWidget,
    QMessageBox, QHeaderView, QDateEdit, QFileDialog,
    QGroupBox, QComboBox, QLineEdit, QTextEdit
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QAction

class AdminDashboard(QMainWindow):
    def __init__(self, user_data):
        super().__init__()
        self.user_id, self.nama, self.jabatan = user_data
        
        from modules.database import Database
        self.db = Database()
        
        self.setWindowTitle(f"Admin Dashboard - Sistem Absensi Cafe")
        self.setGeometry(100, 100, 1200, 700)
        
        self.setup_ui()
        self.load_data_karyawan()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Header
        header_label = QLabel(f"Admin Dashboard - Selamat Datang, {self.nama}!")
        header_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setStyleSheet("background-color: #2c3e50; color: white; padding: 15px; border-radius: 10px;")
        main_layout.addWidget(header_label)
        
        # Tab Widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create all tabs
        self.create_tab_dashboard()
        self.create_tab_karyawan()
        self.create_tab_absensi()
        self.create_tab_penggajian()      # 🔥 TAB BARU - PENGHITUNGAN GAJI
        self.create_tab_laporan()         # 🔥 TAB BARU - EXPORT LAPORAN
        self.create_tab_backup()          # 🔥 TAB BARU - BACKUP DATABASE
        
    def create_tab_dashboard(self):
        """Tab 1: Dashboard Overview"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Welcome message
        welcome_label = QLabel(
            f"📊 Dashboard Overview\n\n"
            f"Halo {self.nama}!\n"
            f"Jabatan: {self.jabatan}\n"
            f"Tanggal: {datetime.now().strftime('%d %B %Y %H:%M')}"
        )
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setFont(QFont("Arial", 12))
        layout.addWidget(welcome_label)
        
        # Statistics cards
        stats_layout = QHBoxLayout()
        
        # Card 1: Total Karyawan
        card1 = QGroupBox("👥 Total Karyawan")
        card1_layout = QVBoxLayout()
        card1_label = QLabel("5")
        card1_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        card1_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card1_layout.addWidget(card1_label)
        card1.setLayout(card1_layout)
        
        # Card 2: Absensi Hari Ini
        card2 = QGroupBox("✅ Absensi Hari Ini")
        card2_layout = QVBoxLayout()
        card2_label = QLabel("3/5")
        card2_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        card2_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card2_layout.addWidget(card2_label)
        card2.setLayout(card2_layout)
        
        # Card 3: Total Gaji Bulan Ini
        card3 = QGroupBox("💰 Gaji Bulan Ini")
        card3_layout = QVBoxLayout()
        card3_label = QLabel("Rp 15Jt")
        card3_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        card3_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card3_layout.addWidget(card3_label)
        card3.setLayout(card3_layout)
        
        stats_layout.addWidget(card1)
        stats_layout.addWidget(card2)
        stats_layout.addWidget(card3)
        layout.addLayout(stats_layout)
        
        # Quick Actions
        actions_group = QGroupBox("⚡ Quick Actions")
        actions_layout = QHBoxLayout()
        
        btn_absensi = QPushButton("📅 Lihat Absensi")
        btn_gaji = QPushButton("💰 Hitung Gaji")
        btn_export = QPushButton("📤 Export Laporan")
        
        btn_absensi.clicked.connect(lambda: self.tab_widget.setCurrentIndex(2))
        btn_gaji.clicked.connect(lambda: self.tab_widget.setCurrentIndex(3))
        btn_export.clicked.connect(lambda: self.tab_widget.setCurrentIndex(4))
        
        actions_layout.addWidget(btn_absensi)
        actions_layout.addWidget(btn_gaji)
        actions_layout.addWidget(btn_export)
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        self.tab_widget.addTab(tab, "🏠 Dashboard")
    
    def create_tab_karyawan(self):
        """Tab 2: Data Karyawan"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_tambah = QPushButton("➕ Tambah Karyawan")
        btn_edit = QPushButton("✏️ Edit Karyawan")
        btn_hapus = QPushButton("🗑️ Hapus Karyawan")
        btn_refresh = QPushButton("🔄 Refresh")
        
        btn_tambah.clicked.connect(self.tambah_karyawan)
        btn_edit.clicked.connect(self.edit_karyawan)
        btn_hapus.clicked.connect(self.hapus_karyawan)
        btn_refresh.clicked.connect(self.load_data_karyawan)
        
        btn_layout.addWidget(btn_tambah)
        btn_layout.addWidget(btn_edit)
        btn_layout.addWidget(btn_hapus)
        btn_layout.addWidget(btn_refresh)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        # Table
        self.table_karyawan = QTableWidget()
        self.table_karyawan.setColumnCount(6)
        self.table_karyawan.setHorizontalHeaderLabels(["ID", "Nama", "Jabatan", "Gaji Pokok", "Username", "Aksi"])
        
        header = self.table_karyawan.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.table_karyawan)
        
        self.tab_widget.addTab(tab, "👥 Data Karyawan")
    
    def create_tab_absensi(self):
        """Tab 3: Data Absensi"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Periode:"))
        
        self.date_start = QDateEdit()
        self.date_start.setDate(QDate.currentDate().addDays(-7))
        self.date_start.setCalendarPopup(True)
        
        self.date_end = QDateEdit()
        self.date_end.setDate(QDate.currentDate())
        self.date_end.setCalendarPopup(True)
        
        btn_filter = QPushButton("🔍 Filter")
        btn_export = QPushButton("📊 Export Excel")
        
        btn_filter.clicked.connect(self.load_data_absensi)
        btn_export.clicked.connect(self.export_absensi_excel)
        
        filter_layout.addWidget(self.date_start)
        filter_layout.addWidget(QLabel("s/d"))
        filter_layout.addWidget(self.date_end)
        filter_layout.addWidget(btn_filter)
        filter_layout.addWidget(btn_export)
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Table
        self.table_absensi = QTableWidget()
        self.table_absensi.setColumnCount(6)
        self.table_absensi.setHorizontalHeaderLabels(["Tanggal", "Nama", "Jam Masuk", "Jam Pulang", "Status", "Lembur"])
        
        header = self.table_absensi.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.table_absensi)
        
        self.tab_widget.addTab(tab, "📅 Data Absensi")
    
    def create_tab_penggajian(self):
        """Tab 4: Sistem Penggajian - 🔥 TAB BARU LENGKAP"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        title_label = QLabel("💰 SISTEM PENGHITUNGAN GAJI OTOMATIS")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; padding: 10px;")
        layout.addWidget(title_label)
        
        # Filter bulan/tahun
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Bulan:"))
        
        self.combo_bulan_gaji = QComboBox()
        self.combo_bulan_gaji.addItems([
            "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ])
        self.combo_bulan_gaji.setCurrentIndex(datetime.now().month - 1)
        
        self.combo_tahun_gaji = QComboBox()
        current_year = datetime.now().year
        for year in range(current_year - 1, current_year + 2):
            self.combo_tahun_gaji.addItem(str(year))
        self.combo_tahun_gaji.setCurrentText(str(current_year))
        
        btn_hitung = QPushButton("🧮 Hitung Gaji")
        btn_hitung.clicked.connect(self.hitung_semua_gaji)
        
        filter_layout.addWidget(self.combo_bulan_gaji)
        filter_layout.addWidget(QLabel("Tahun:"))
        filter_layout.addWidget(self.combo_tahun_gaji)
        filter_layout.addWidget(btn_hitung)
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Tabel gaji
        self.table_gaji = QTableWidget()
        self.table_gaji.setColumnCount(8)
        self.table_gaji.setHorizontalHeaderLabels([
            "Nama", "Jabatan", "Gaji Pokok", "Hari Kerja", "Lembur (jam)", 
            "Gaji Dibayar", "Uang Lembur", "Total Gaji"
        ])
        layout.addWidget(self.table_gaji)
        
        # Total pengeluaran
        self.label_total_gaji = QLabel("Total Pengeluaran Gaji: Rp 0")
        self.label_total_gaji.setStyleSheet("font-weight: bold; font-size: 14px; color: #e74c3c;")
        layout.addWidget(self.label_total_gaji)
        
        # Action buttons
        action_layout = QHBoxLayout()
        btn_cetak_slip = QPushButton("🖨️ Cetak Slip Gaji")
        btn_export_excel = QPushButton("📊 Export Excel")
        btn_export_pdf = QPushButton("📄 Export PDF")
        
        btn_cetak_slip.clicked.connect(self.cetak_slip_gaji)
        btn_export_excel.clicked.connect(self.export_gaji_excel)
        btn_export_pdf.clicked.connect(self.export_gaji_pdf)
        
        action_layout.addWidget(btn_cetak_slip)
        action_layout.addWidget(btn_export_excel)
        action_layout.addWidget(btn_export_pdf)
        action_layout.addStretch()
        
        layout.addLayout(action_layout)
        
        self.tab_widget.addTab(tab, "💰 Penggajian")
    
    def create_tab_laporan(self):
        """Tab 5: Export Laporan - 🔥 TAB BARU"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        title_label = QLabel("📊 EXPORT LAPORAN LENGKAP")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Laporan Absensi
        absensi_group = QGroupBox("📅 Laporan Absensi")
        absensi_layout = QVBoxLayout()
        
        absensi_info = QLabel("Export data absensi ke format Excel atau PDF")
        btn_absensi_excel = QPushButton("Export Excel")
        btn_absensi_pdf = QPushButton("Export PDF")
        
        btn_absensi_excel.clicked.connect(self.export_absensi_excel)
        btn_absensi_pdf.clicked.connect(self.export_absensi_pdf)
        
        absensi_layout.addWidget(absensi_info)
        
        btn_layout1 = QHBoxLayout()
        btn_layout1.addWidget(btn_absensi_excel)
        btn_layout1.addWidget(btn_absensi_pdf)
        absensi_layout.addLayout(btn_layout1)
        
        absensi_group.setLayout(absensi_layout)
        layout.addWidget(absensi_group)
        
        # Laporan Gaji
        gaji_group = QGroupBox("💰 Laporan Penggajian")
        gaji_layout = QVBoxLayout()
        
        gaji_info = QLabel("Export data penggajian ke format Excel atau PDF")
        btn_gaji_excel = QPushButton("Export Excel")
        btn_gaji_pdf = QPushButton("Export PDF")
        
        btn_gaji_excel.clicked.connect(self.export_gaji_excel)
        btn_gaji_pdf.clicked.connect(self.export_gaji_pdf)
        
        gaji_layout.addWidget(gaji_info)
        
        btn_layout2 = QHBoxLayout()
        btn_layout2.addWidget(btn_gaji_excel)
        btn_layout2.addWidget(btn_gaji_pdf)
        gaji_layout.addLayout(btn_layout2)
        
        gaji_group.setLayout(gaji_layout)
        layout.addWidget(gaji_group)
        
        # Laporan Karyawan
        karyawan_group = QGroupBox("👥 Laporan Data Karyawan")
        karyawan_layout = QVBoxLayout()
        
        karyawan_info = QLabel("Export data karyawan ke format Excel")
        btn_karyawan_excel = QPushButton("Export Excel")
        
        btn_karyawan_excel.clicked.connect(self.export_karyawan_excel)
        
        karyawan_layout.addWidget(karyawan_info)
        karyawan_layout.addWidget(btn_karyawan_excel)
        
        karyawan_group.setLayout(karyawan_layout)
        layout.addWidget(karyawan_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "📤 Export Laporan")
    
    def create_tab_backup(self):
        """Tab 6: Backup Database - 🔥 TAB BARU"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        title_label = QLabel("💾 BACKUP & RESTORE DATABASE")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Backup Section
        backup_group = QGroupBox("💾 Backup Database")
        backup_layout = QVBoxLayout()
        
        backup_info = QLabel("Buat backup seluruh data sistem ke file eksternal")
        self.backup_name = QLineEdit()
        self.backup_name.setPlaceholderText("Nama file backup (kosongkan untuk auto-generate)")
        
        btn_backup = QPushButton("💾 Backup Sekarang")
        btn_backup.clicked.connect(self.backup_database)
        
        backup_layout.addWidget(backup_info)
        backup_layout.addWidget(QLabel("Nama Backup:"))
        backup_layout.addWidget(self.backup_name)
        backup_layout.addWidget(btn_backup)
        
        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)
        
        # Restore Section
        restore_group = QGroupBox("🔄 Restore Database")
        restore_layout = QVBoxLayout()
        
        restore_info = QLabel("Restore data dari backup sebelumnya")
        btn_restore = QPushButton("Pilih File Backup")
        btn_restore.clicked.connect(self.restore_database)
        
        restore_layout.addWidget(restore_info)
        restore_layout.addWidget(btn_restore)
        
        restore_group.setLayout(restore_layout)
        layout.addWidget(restore_group)
        
        # Info Section
        info_group = QGroupBox("ℹ️ Informasi System")
        info_layout = QVBoxLayout()
        
        info_text = QTextEdit()
        info_text.setPlainText(
            "Backup akan disimpan di folder 'backups/'\n"
            "Format file: .db\n"
            "Disarankan backup secara berkala!\n\n"
            "Last Backup: -\n"
            "Database Size: -"
        )
        info_text.setReadOnly(True)
        
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        self.tab_widget.addTab(tab, "💾 Backup")
    
    # ==================== METHOD IMPLEMENTASI ====================
    
    def load_data_karyawan(self):
        """Load data karyawan ke tabel"""
        try:
            data = self.db.get_all_karyawan()
            self.table_karyawan.setRowCount(len(data))
            
            for row, karyawan in enumerate(data):
                for col in range(5):  # ID, Nama, Jabatan, Gaji, Username
                    value = str(karyawan[col])
                    if col == 3:  # Gaji column
                        value = f"Rp {int(karyawan[col]):,}" if karyawan[col] > 0 else "Tidak Digaji"
                    
                    item = QTableWidgetItem(value)
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.table_karyawan.setItem(row, col, item)
                
                # Action buttons
                btn_edit = QPushButton("✏️ Edit")
                btn_hapus = QPushButton("🗑️ Hapus")
                
                btn_edit.clicked.connect(lambda checked, id=karyawan[0]: self.edit_karyawan_by_id(id))
                btn_hapus.clicked.connect(lambda checked, id=karyawan[0]: self.hapus_karyawan_by_id(id))
                
                # Create widget for buttons
                widget = QWidget()
                btn_layout = QHBoxLayout()
                btn_layout.addWidget(btn_edit)
                btn_layout.addWidget(btn_hapus)
                btn_layout.setContentsMargins(0, 0, 0, 0)
                widget.setLayout(btn_layout)
                
                self.table_karyawan.setCellWidget(row, 5, widget)
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Gagal memuat data karyawan: {str(e)}")
    
    def load_data_absensi(self):
        """Load data absensi ke tabel"""
        try:
            start_date = self.date_start.date().toString("yyyy-MM-dd")
            end_date = self.date_end.date().toString("yyyy-MM-dd")
            
            data = self.db.get_riwayat_absensi(start_date, end_date)
            self.table_absensi.setRowCount(len(data))
            
            for row, absensi in enumerate(data):
                for col in range(6):
                    value = str(absensi[col]) if absensi[col] is not None else "-"
                    item = QTableWidgetItem(value)
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.table_absensi.setItem(row, col, item)
                    
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Gagal memuat data absensi: {str(e)}")
    
    def hitung_semua_gaji(self):
        """Hitung gaji semua karyawan"""
        try:
            bulan = self.combo_bulan_gaji.currentIndex() + 1
            tahun = int(self.combo_tahun_gaji.currentText())
            
            data_gaji = self.db.get_all_gaji(bulan, tahun)
            self.table_gaji.setRowCount(len(data_gaji))
            
            total_pengeluaran = 0
            
            for row, gaji in enumerate(data_gaji):
                items = [
                    gaji['nama'],
                    gaji['jabatan'],
                    f"Rp {gaji['gaji_pokok']:,.0f}",
                    str(gaji['hari_kerja']),
                    str(gaji['total_lembur']),
                    f"Rp {gaji['gaji_dibayar']:,.0f}",
                    f"Rp {gaji['uang_lembur']:,.0f}",
                    f"Rp {gaji['total_gaji']:,.0f}"
                ]
                
                for col, value in enumerate(items):
                    item = QTableWidgetItem(value)
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.table_gaji.setItem(row, col, item)
                
                total_pengeluaran += gaji['total_gaji']
            
            self.label_total_gaji.setText(f"Total Pengeluaran Gaji: Rp {total_pengeluaran:,.0f}")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Gagal menghitung gaji: {str(e)}")
    
    # ==================== METHOD ACTION ====================
    
    def tambah_karyawan(self):
        """Tambah karyawan baru"""
        try:
            from views.karyawan_form import KaryawanForm
            form = KaryawanForm(self)
            if form.exec():
                data = form.get_data()
                if self.db.tambah_karyawan(data['nama'], data['jabatan'], float(data['gaji_pokok']), data['username'], data['password']):
                    QMessageBox.information(self, "Sukses", "Karyawan berhasil ditambahkan!")
                    self.load_data_karyawan()
                else:
                    QMessageBox.warning(self, "Error", "Username sudah digunakan!")
                    
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Gagal menambah karyawan: {str(e)}")
    
    def edit_karyawan(self):
        """Edit karyawan yang dipilih"""
        QMessageBox.information(self, "Info", "Pilih karyawan dari tabel dan klik tombol Edit")
    
    def edit_karyawan_by_id(self, karyawan_id):
        """Edit karyawan by ID"""
        try:
            karyawan_data = self.db.get_karyawan_by_id(karyawan_id)
            if karyawan_data:
                from views.karyawan_form import KaryawanForm
                form = KaryawanForm(self, karyawan_data)
                if form.exec():
                    data = form.get_data()
                    success = self.db.update_karyawan(
                        karyawan_id, 
                        data['nama'], 
                        data['jabatan'], 
                        float(data['gaji_pokok']), 
                        data['username'],
                        data['password'] if data['password'] else None
                    )
                    if success:
                        QMessageBox.information(self, "Sukses", "Data karyawan berhasil diupdate!")
                        self.load_data_karyawan()
                    else:
                        QMessageBox.warning(self, "Error", "Username sudah digunakan!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Gagal edit karyawan: {str(e)}")
    
    def hapus_karyawan(self):
        """Hapus karyawan yang dipilih"""
        QMessageBox.information(self, "Info", "Pilih karyawan dari tabel dan klik tombol Hapus")
    
    def hapus_karyawan_by_id(self, karyawan_id):
        """Hapus karyawan by ID"""
        reply = QMessageBox.question(
            self, 'Konfirmasi', 
            'Apakah Anda yakin ingin menghapus karyawan ini?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.hapus_karyawan(karyawan_id):
                QMessageBox.information(self, "Sukses", "Karyawan berhasil dihapus!")
                self.load_data_karyawan()
            else:
                QMessageBox.warning(self, "Error", "Gagal menghapus karyawan!")
    
    # ==================== EXPORT METHODS ====================
    
    def export_absensi_excel(self):
        """Export data absensi ke Excel"""
        try:
            from modules.export_manager import ExportManager
            start_date = self.date_start.date().toString("yyyy-MM-dd")
            end_date = self.date_end.date().toString("yyyy-MM-dd")
            
            data = self.db.get_riwayat_absensi(start_date, end_date)
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Excel", 
                f"absensi_{datetime.now().strftime('%Y%m%d')}.xlsx", 
                "Excel Files (*.xlsx)"
            )
            
            if file_path:
                exporter = ExportManager()
                if exporter.export_absensi_excel(data, file_path):
                    QMessageBox.information(self, "Sukses", f"Data absensi berhasil diexport!\n{file_path}")
                else:
                    QMessageBox.warning(self, "Error", "Gagal mengexport data!")
                    
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Gagal export: {str(e)}")
    
    def export_absensi_pdf(self):
        """Export data absensi ke PDF"""
        QMessageBox.information(self, "Info", "Fitur export PDF akan segera tersedia!")
    
    def export_gaji_excel(self):
        """Export data gaji ke Excel"""
        try:
            from modules.export_manager import ExportManager
            bulan = self.combo_bulan_gaji.currentIndex() + 1
            tahun = int(self.combo_tahun_gaji.currentText())
            
            data = self.db.get_all_gaji(bulan, tahun)
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Excel", 
                f"gaji_{tahun}_{bulan:02d}.xlsx", 
                "Excel Files (*.xlsx)"
            )
            
            if file_path:
                exporter = ExportManager()
                if exporter.export_gaji_excel(data, file_path):
                    QMessageBox.information(self, "Sukses", f"Data gaji berhasil diexport!\n{file_path}")
                else:
                    QMessageBox.warning(self, "Error", "Gagal mengexport data!")
                    
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Gagal export: {str(e)}")
    
    def export_gaji_pdf(self):
        """Export data gaji ke PDF"""
        QMessageBox.information(self, "Info", "Fitur export PDF akan segera tersedia!")
    
    def export_karyawan_excel(self):
        """Export data karyawan ke Excel"""
        QMessageBox.information(self, "Info", "Fitur export data karyawan akan segera tersedia!")
    
    def cetak_slip_gaji(self):
        """Cetak slip gaji"""
        try:
            from views.gaji_form import GajiForm
            form = GajiForm(self, self.db)
            form.exec()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Gagal membuka form slip gaji: {str(e)}")
    
    # ==================== BACKUP METHODS ====================
    
    def backup_database(self):
        """Backup database"""
        try:
            backup_name = self.backup_name.text().strip()
            if not backup_name:
                backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            elif not backup_name.endswith('.db'):
                backup_name += '.db'
            
            # Create backup using shutil
            source = Config.DB_NAME
            destination = f'backups/{backup_name}'
            
            # Ensure backups directory exists
            os.makedirs('backups', exist_ok=True)
            
            shutil.copy2(source, destination)
            QMessageBox.information(self, "Backup Berhasil", f"Database berhasil di backup!\nFile: {destination}")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Gagal backup database: {str(e)}")
    
    def restore_database(self):
        """Restore database dari backup"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Pilih File Backup", 
                "backups", 
                "Database Files (*.db)"
            )
            
            if file_path:
                reply = QMessageBox.question(
                    self, 'Konfirmasi Restore',
                    'Apakah Anda yakin ingin restore database?\nAplikasi akan ditutup otomatis.',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    shutil.copy2(file_path, Config.DB_NAME)
                    QMessageBox.information(self, "Restore Berhasil", "Database berhasil di restore!\nAplikasi akan ditutup.")
                    self.close()
                    
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Gagal restore database: {str(e)}")
    
    def closeEvent(self, event):
        """Handle window close event"""
        try:
            self.db.conn.close()
        except:
            pass
        event.accept()

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    # Test data
    test_data = (1, "Admin User", "Manager")
    window = AdminDashboard(test_data)
    window.show()
    
    sys.exit(app.exec())