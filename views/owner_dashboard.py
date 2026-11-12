# views/owner_dashboard.py

import os
import shutil
import sys
from datetime import datetime

from PyQt6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QMessageBox,
    QHeaderView,
    QGroupBox,
    QGridLayout,
    QMenu,
    QDateEdit,
    QComboBox,
    QDoubleSpinBox

)

from config import Config
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QAction

from modules.database import Database
from modules.export_manager import ExportManager

from views.karyawan_form import KaryawanForm


class OwnerDashboard(QMainWindow):

    def __init__(self, user_data):
        super().__init__()

        self.user_id, self.nama, self.jabatan = user_data

        self.db = Database()

        self.setWindowTitle(
            "Owner Dashboard - Sistem Absensi Cafe"
        )

        self.setGeometry(
            100,
            100,
            1200,
            700
        )

        self.setup_ui()
        self.load_dashboard_data()

    # ==========================================================
    # SETUP UI
    # ==========================================================

    def setup_ui(self):

        central_widget = QWidget()

        self.setCentralWidget(
            central_widget
        )

        main_layout = QVBoxLayout()

        central_widget.setLayout(
            main_layout
        )

        # ======================================================
        # HEADER
        # ======================================================

        header_label = QLabel(
            "Owner Dashboard - Selamat Datang"
        )

        header_label.setFont(
            QFont(
                "Arial",
                18,
                QFont.Weight.Bold
            )
        )

        header_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        header_label.setStyleSheet(
            "background-color: #2c3e50;"
            "color: white;"
            "padding: 15px;"
        )

        main_layout.addWidget(
            header_label
        )

        # ======================================================
        # TAB
        # ======================================================

        self.tab_widget = QTabWidget()

        main_layout.addWidget(
            self.tab_widget
        )

        # ======================================================
        # TAB DASHBOARD
        # ======================================================

        tab_dashboard = QWidget()

        self.setup_tab_dashboard(
            tab_dashboard
        )

        self.tab_widget.addTab(
            tab_dashboard,
            "📊 Dashboard"
        )

        # ======================================================
        # TAB KARYAWAN
        # ======================================================

        tab_karyawan = QWidget()

        self.setup_tab_karyawan(
            tab_karyawan
        )

        self.tab_widget.addTab(
            tab_karyawan,
            "👥 Data Karyawan"
        )

        # ======================================================
        # TAB ABSENSI
        # ======================================================

        tab_absensi = QWidget()

        self.setup_tab_absensi(
            tab_absensi
        )

        self.tab_widget.addTab(
            tab_absensi,
            "📅 Data Absensi"
        )

        # ======================================================
        # TAB KEUANGAN
        # ======================================================

        tab_keuangan = QWidget()

        self.setup_tab_keuangan(
            tab_keuangan
        )

        self.tab_widget.addTab(
            tab_keuangan,
            "💰 Laporan Keuangan"
        )

        # ======================================================
        # TAB PENGATURAN
        # ======================================================

        tab_pengaturan = QWidget()

        self.setup_tab_pengaturan(
            tab_pengaturan
        )

        self.tab_widget.addTab(
            tab_pengaturan,
            "⚙️ Pengaturan"
        )

    # ==========================================================
    # DASHBOARD
    # ==========================================================

    def setup_tab_dashboard(self, tab):

        layout = QVBoxLayout(tab)

        stats_group = QGroupBox(
            "📈 Statistik Overview"
        )

        stats_layout = QGridLayout()

        stats_data = [
            (
                "Total Karyawan",
                "15",
                "#3498db"
            ),
            (
                "Hadir Hari Ini",
                "12",
                "#2ecc71"
            ),
            (
                "Tidak Hadir",
                "3",
                "#e74c3c"
            ),
            (
                "Total Gaji Bulan Ini",
                "Rp 45.000.000",
                "#f39c12"
            ),
            (
                "Rata-rata Kehadiran",
                "92%",
                "#9b59b6"
            ),
            (
                "Karyawan Aktif",
                "2",
                "#1abc9c"
            )
        ]

        row = 0
        col = 0

        for title, value, color in stats_data:

            stat_card = self.create_stat_card(
                title,
                value,
                color
            )

            stats_layout.addWidget(
                stat_card,
                row,
                col
            )

            col += 1

            if col > 2:
                col = 0
                row += 1

        stats_group.setLayout(
            stats_layout
        )

        layout.addWidget(
            stats_group
        )

        # ======================================================
        # AKTIVITAS
        # ======================================================

        activity_group = QGroupBox(
            "📋 Aktivitas Terkini"
        )

        activity_layout = QVBoxLayout()

        self.table_activity = QTableWidget()

        self.table_activity.setColumnCount(
            4
        )

        self.table_activity.setHorizontalHeaderLabels([
            "Tanggal",
            "Karyawan",
            "Aktivitas",
            "Waktu"
        ])

        activity_layout.addWidget(
            self.table_activity
        )

        activity_group.setLayout(
            activity_layout
        )

        layout.addWidget(
            activity_group
        )

    # ==========================================================
    # DATA KARYAWAN
    # ==========================================================

    def setup_tab_karyawan(self, tab):

        layout = QVBoxLayout(tab)

        # ======================================================
        # BUTTON
        # ======================================================

        btn_layout = QHBoxLayout()

        self.btn_tambah = QPushButton(
            "➕ Tambah Karyawan"
        )

        self.btn_refresh = QPushButton(
            "🔄 Refresh"
        )

        self.btn_tambah.clicked.connect(
            self.tambah_karyawan
        )

        self.btn_refresh.clicked.connect(
            self.load_data_karyawan
        )

        btn_layout.addWidget(
            self.btn_tambah
        )

        btn_layout.addWidget(
            self.btn_refresh
        )

        btn_layout.addStretch()

        layout.addLayout(
            btn_layout
        )

        # ======================================================
        # TABEL
        # ======================================================

        self.table_karyawan = QTableWidget()

        self.table_karyawan.setColumnCount(
            6
        )

        self.table_karyawan.setHorizontalHeaderLabels([
            "ID",
            "Nama",
            "Jabatan",
            "Gaji Pokok",
            "Username",
            "Aksi"
        ])

        header = (
            self.table_karyawan.horizontalHeader()
        )

        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch
        )

        self.table_karyawan.setColumnWidth(
            5,
            150
        )

        self.table_karyawan.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )

        self.table_karyawan.customContextMenuRequested.connect(
            self.show_context_menu
        )

        layout.addWidget(
            self.table_karyawan
        )

        self.load_data_karyawan()

    # ==========================================================
    # DATA ABSENSI
    # ==========================================================

    def setup_tab_absensi(self, tab):

        layout = QVBoxLayout(tab)

        # ======================================================
        # FILTER PERIODE
        # ======================================================

        filter_layout = QHBoxLayout()

        filter_layout.addWidget(
            QLabel("Dari:")
        )

        self.date_start = QDateEdit()

        self.date_start.setCalendarPopup(
            True
        )

        self.date_start.setDisplayFormat(
            "dd/MM/yyyy"
        )

        today = QDate.currentDate()

        self.date_start.setDate(
            QDate(
                today.year(),
                today.month(),
                1
            )
        )

        filter_layout.addWidget(
            self.date_start
        )

        filter_layout.addWidget(
            QLabel("Sampai:")
        )

        self.date_end = QDateEdit()

        self.date_end.setCalendarPopup(
            True
        )

        self.date_end.setDisplayFormat(
            "dd/MM/yyyy"
        )

        self.date_end.setDate(
            today
        )

        filter_layout.addWidget(
            self.date_end
        )

        # ======================================================
        # TAMPILKAN
        # ======================================================

        self.btn_filter_absensi = QPushButton(
            "🔍 Tampilkan"
        )

        self.btn_filter_absensi.setMinimumHeight(
            35
        )

        self.btn_filter_absensi.clicked.connect(
            self.load_data_absensi
        )

        filter_layout.addWidget(
            self.btn_filter_absensi
        )

        # ======================================================
        # EXPORT
        # ======================================================

        self.btn_export_absensi = QPushButton(
            "📤 Export Excel"
        )

        self.btn_export_absensi.setMinimumHeight(
            35
        )

        self.btn_export_absensi.clicked.connect(
            self.export_data
        )

        filter_layout.addWidget(
            self.btn_export_absensi
        )

        filter_layout.addStretch()

        layout.addLayout(
            filter_layout
        )

        # ======================================================
        # TABEL ABSENSI
        # ======================================================

        self.table_absensi = QTableWidget()

        self.table_absensi.setColumnCount(
            6
        )

        self.table_absensi.setHorizontalHeaderLabels([
            "Tanggal",
            "Nama",
            "Jam Masuk",
            "Jam Pulang",
            "Status",
            "Lembur"
        ])

        self.table_absensi.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.table_absensi.setAlternatingRowColors(
            True
        )

        layout.addWidget(
            self.table_absensi
        )

        self.load_data_absensi()

    # ==========================================================
    # LAPORAN KEUANGAN / PAYROLL
    # ==========================================================

    def setup_tab_keuangan(self, tab):

        layout = QVBoxLayout(tab)

        # ======================================================
        # JUDUL
        # ======================================================

        title_label = QLabel(
            "💰 LAPORAN PENGGAJIAN"
        )

        title_label.setFont(
            QFont(
                "Arial",
                16,
                QFont.Weight.Bold
            )
        )

        title_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(
            title_label
        )

        # ======================================================
        # FILTER BULAN
        # ======================================================

        filter_layout = QHBoxLayout()

        filter_layout.addWidget(
            QLabel("Bulan:")
        )

        self.combo_bulan_gaji = QComboBox()

        nama_bulan = [
            "Januari",
            "Februari",
            "Maret",
            "April",
            "Mei",
            "Juni",
            "Juli",
            "Agustus",
            "September",
            "Oktober",
            "November",
            "Desember"
        ]

        self.combo_bulan_gaji.addItems(
            nama_bulan
        )

        bulan_sekarang = datetime.now().month

        self.combo_bulan_gaji.setCurrentIndex(
            bulan_sekarang - 1
        )

        filter_layout.addWidget(
            self.combo_bulan_gaji
        )

        # ======================================================
        # FILTER TAHUN
        # ======================================================

        filter_layout.addWidget(
            QLabel("Tahun:")
        )

        self.combo_tahun_gaji = QComboBox()

        tahun_sekarang = datetime.now().year

        for tahun in range(
            tahun_sekarang - 5,
            tahun_sekarang + 2
        ):

            self.combo_tahun_gaji.addItem(
                str(tahun)
            )

        self.combo_tahun_gaji.setCurrentText(
            str(tahun_sekarang)
        )

        filter_layout.addWidget(
            self.combo_tahun_gaji
        )

        # ======================================================
        # TAMPILKAN
        # ======================================================

        self.btn_filter_gaji = QPushButton(
            "🔍 Tampilkan"
        )

        self.btn_filter_gaji.setMinimumHeight(
            35
        )

        self.btn_filter_gaji.clicked.connect(
            self.load_data_gaji
        )

        filter_layout.addWidget(
            self.btn_filter_gaji
        )

        # ======================================================
        # EXPORT GAJI
        # ======================================================

        self.btn_export_gaji = QPushButton(
            "📊 Export Gaji"
        )

        self.btn_export_gaji.setMinimumHeight(
            35
        )

        self.btn_export_gaji.clicked.connect(
            self.export_gaji
        )

        filter_layout.addWidget(
            self.btn_export_gaji
        )

        filter_layout.addStretch()

        layout.addLayout(
            filter_layout
        )

        # ======================================================
        # TOTAL GAJI
        # ======================================================

        self.total_gaji_label = QLabel()

        self.total_gaji_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.total_gaji_label.setStyleSheet(
            "font-size: 20px;"
            "font-weight: bold;"
            "padding: 10px;"
        )

        layout.addWidget(
            self.total_gaji_label
        )

        # ======================================================
        # TABEL GAJI
        # ======================================================

        self.table_gaji = QTableWidget()

        self.table_gaji.setColumnCount(
            8
        )

        self.table_gaji.setHorizontalHeaderLabels([
            "Nama",
            "Jabatan",
            "Gaji Pokok",
            "Hari Kerja",
            "Lembur (Jam)",
            "Gaji Dibayar",
            "Uang Lembur",
            "Total Gaji"
        ])

        self.table_gaji.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.table_gaji.setAlternatingRowColors(
            True
        )

        layout.addWidget(
            self.table_gaji
        )

        # ======================================================
        # TOMBOL CETAK SLIP
        # ======================================================

        button_layout = QHBoxLayout()

        btn_cetak_slip = QPushButton(
            "🖨️ Cetak Slip Gaji"
        )

        btn_cetak_slip.setMinimumHeight(
            40
        )

        btn_cetak_slip.clicked.connect(
            self.cetak_slip_gaji_owner
        )

        button_layout.addWidget(
            btn_cetak_slip
        )

        button_layout.addStretch()

        layout.addLayout(
            button_layout
        )

        # ======================================================
        # INFO
        # ======================================================

        info_label = QLabel(
            "Perhitungan berdasarkan data absensi "
            "dan gaji pokok karyawan."
        )

        info_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        info_label.setStyleSheet(
            "color: gray;"
            "padding: 5px;"
        )

        layout.addWidget(
            info_label
        )

        # ======================================================
        # LOAD DATA AWAL
        # ======================================================

        self.load_data_gaji()

    # ==========================================================
    # PENGATURAN
    # ==========================================================

    def setup_tab_pengaturan(self, tab):

        layout = QVBoxLayout(tab)

        btn_backup = QPushButton(
            "💾 Backup Database"
        )

        btn_restore = QPushButton(
            "♻️ Restore Database"
        )

        btn_reset = QPushButton(
            "🧹 Reset Data"
        )

        btn_pengaturan = QPushButton(
            "⚙️ Pengaturan Aplikasi"
        )

        btn_backup.clicked.connect(
            self.backup_database
        )

        btn_restore.clicked.connect(
            self.restore_database
        )

        btn_reset.clicked.connect(
            self.reset_database
        )

        btn_pengaturan.clicked.connect(
            self.show_settings
        )

        for btn in [
            btn_backup,
            btn_restore,
            btn_reset,
            btn_pengaturan
        ]:

            btn.setMinimumHeight(
                40
            )

            layout.addWidget(
                btn
            )

        layout.addStretch()

    # ==========================================================
    # LOAD DATA GAJI
    # ==========================================================

    def load_data_gaji(self):

        bulan = (
            self.combo_bulan_gaji.currentIndex()
            + 1
        )

        tahun = int(
            self.combo_tahun_gaji.currentText()
        )

        self.gaji_data = self.db.get_all_gaji(
            bulan,
            tahun
        )

        # ======================================================
        # TOTAL
        # ======================================================

        total_pengeluaran = sum(
            item["total_gaji"]
            for item in self.gaji_data
        )

        nama_bulan = [
            "Januari",
            "Februari",
            "Maret",
            "April",
            "Mei",
            "Juni",
            "Juli",
            "Agustus",
            "September",
            "Oktober",
            "November",
            "Desember"
        ]

        self.total_gaji_label.setText(
            f"💰 Total Pengeluaran Gaji "
            f"{nama_bulan[bulan - 1]} {tahun}: "
            f"Rp {total_pengeluaran:,.0f}"
        )

        # ======================================================
        # TABEL
        # ======================================================

        self.table_gaji.setRowCount(
            len(self.gaji_data)
        )

        for row, gaji in enumerate(
            self.gaji_data
        ):

            items = [
                gaji["nama"],
                gaji["jabatan"],
                f"Rp {gaji['gaji_pokok']:,.0f}",
                str(gaji["hari_kerja"]),
                f"{gaji['total_lembur']:.2f}",
                f"Rp {gaji['gaji_dibayar']:,.0f}",
                f"Rp {gaji['uang_lembur']:,.0f}",
                f"Rp {gaji['total_gaji']:,.0f}"
            ]

            for col, value in enumerate(
                items
            ):

                item = QTableWidgetItem(
                    str(value)
                )

                item.setFlags(
                    item.flags()
                    & ~Qt.ItemFlag.ItemIsEditable
                )

                self.table_gaji.setItem(
                    row,
                    col,
                    item
                )

    # ==========================================================
    # LOAD DATA KARYAWAN
    # ==========================================================

    def load_data_karyawan(self):

        data = self.db.get_all_karyawan()

        self.table_karyawan.setRowCount(
            len(data)
        )

        for row, karyawan in enumerate(
            data
        ):

            for col in range(5):

                item = QTableWidgetItem(
                    str(karyawan[col])
                )

                item.setFlags(
                    item.flags()
                    & ~Qt.ItemFlag.ItemIsEditable
                )

                self.table_karyawan.setItem(
                    row,
                    col,
                    item
                )

            # ==================================================
            # TOMBOL AKSI
            # ==================================================

            btn_container = QWidget()

            btn_layout = QHBoxLayout(
                btn_container
            )

            btn_layout.setContentsMargins(
                0,
                0,
                0,
                0
            )

            btn_edit = QPushButton(
                "✏️ Edit"
            )

            btn_hapus = QPushButton(
                "🗑️ Hapus"
            )

            btn_edit.clicked.connect(
                lambda _, id=karyawan[0]:
                self.edit_karyawan(id)
            )

            btn_hapus.clicked.connect(
                lambda _, id=karyawan[0]:
                self.hapus_karyawan(id)
            )

            btn_layout.addWidget(
                btn_edit
            )

            btn_layout.addWidget(
                btn_hapus
            )

            self.table_karyawan.setCellWidget(
                row,
                5,
                btn_container
            )

    # ==========================================================
    # LOAD DATA ABSENSI
    # ==========================================================

    def load_data_absensi(self):

        start_date = (
            self.date_start.date()
            .toString("yyyy-MM-dd")
        )

        end_date = (
            self.date_end.date()
            .toString("yyyy-MM-dd")
        )

        if start_date > end_date:

            QMessageBox.warning(
                self,
                "Periode Tidak Valid",
                "Tanggal mulai tidak boleh "
                "lebih besar dari tanggal akhir."
            )

            return

        data = self.db.get_riwayat_absensi(
            start_date,
            end_date
        )

        self.table_absensi.setRowCount(
            len(data)
        )

        for row, absensi in enumerate(
            data
        ):

            for col in range(6):

                value = (
                    absensi[col]
                    if absensi[col] is not None
                    else "-"
                )

                item = QTableWidgetItem(
                    str(value)
                )

                item.setFlags(
                    item.flags()
                    & ~Qt.ItemFlag.ItemIsEditable
                )

                self.table_absensi.setItem(
                    row,
                    col,
                    item
                )

    # ==========================================================
    # CETAK SLIP GAJI
    # ==========================================================

    def cetak_slip_gaji_owner(self):

        selected_row = (
            self.table_gaji.currentRow()
        )

        if selected_row < 0:

            QMessageBox.warning(
                self,
                "Peringatan",
                "Pilih karyawan terlebih dahulu!"
            )

            return

        # ======================================================
        # PERIODE YANG DIPILIH
        # ======================================================

        bulan = (
            self.combo_bulan_gaji.currentIndex()
            + 1
        )

        tahun = int(
            self.combo_tahun_gaji.currentText()
        )

        # ======================================================
        # NAMA KARYAWAN
        # ======================================================

        nama_item = self.table_gaji.item(
            selected_row,
            0
        )

        if not nama_item:

            QMessageBox.warning(
                self,
                "Error",
                "Data karyawan tidak ditemukan!"
            )

            return

        nama = nama_item.text()

        # ======================================================
        # DATA GAJI
        # ======================================================

        semua_gaji = self.db.get_all_gaji(
            bulan,
            tahun
        )

        gaji_data = None

        for data in semua_gaji:

            if data["nama"] == nama:

                gaji_data = data
                break

        if not gaji_data:

            QMessageBox.warning(
                self,
                "Error",
                "Data gaji karyawan tidak ditemukan!"
            )

            return

        # ======================================================
        # SIMPAN PDF
        # ======================================================

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Simpan Slip Gaji",
            f"slip_gaji_{nama}_{tahun}_{bulan:02d}.pdf",
            "PDF Files (*.pdf)"
        )

        if not file_path:
            return

        # ======================================================
        # CETAK
        # ======================================================

        exporter = ExportManager()

        berhasil = exporter.cetak_slip_gaji(
            gaji_data,
            file_path,
            bulan,
            tahun
        )

        if berhasil:

            QMessageBox.information(
                self,
                "Sukses",
                "Slip gaji berhasil dibuat!\n\n"
                f"File:\n{file_path}"
            )

        else:

            QMessageBox.warning(
                self,
                "Error",
                "Gagal membuat slip gaji."
            )

    # ==========================================================
    # EXPORT ABSENSI
    # ==========================================================

    def export_data(self):

        start_date = (
            self.date_start.date()
            .toString("yyyy-MM-dd")
        )

        end_date = (
            self.date_end.date()
            .toString("yyyy-MM-dd")
        )

        if start_date > end_date:

            QMessageBox.warning(
                self,
                "Periode Tidak Valid",
                "Tanggal mulai tidak boleh "
                "lebih besar dari tanggal akhir."
            )

            return

        data = self.db.get_absensi_export(
            start_date,
            end_date
        )

        if not data:

            QMessageBox.information(
                self,
                "Export Excel",
                "Tidak ada data absensi pada "
                "periode yang dipilih."
            )

            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Simpan Data Absensi",
            f"absensi_{start_date}_sampai_{end_date}.xlsx",
            "Excel Files (*.xlsx)"
        )

        if not file_path:
            return

        exporter = ExportManager()

        berhasil = exporter.export_absensi_excel(
            data,
            file_path
        )

        if berhasil:

            QMessageBox.information(
                self,
                "Export Berhasil",
                "Data absensi berhasil diexport "
                "ke Excel!\n\n"
                f"Periode: {start_date} s/d {end_date}\n\n"
                f"File:\n{file_path}"
            )

        else:

            QMessageBox.warning(
                self,
                "Export Gagal",
                "Terjadi kesalahan saat "
                "mengexport data absensi."
            )

    # ==========================================================
    # EXPORT GAJI
    # ==========================================================

    def export_gaji(self):

        bulan = (
            self.combo_bulan_gaji.currentIndex()
            + 1
        )

        tahun = int(
            self.combo_tahun_gaji.currentText()
        )

        data = self.db.get_all_gaji(
            bulan,
            tahun
        )

        if not data:

            QMessageBox.information(
                self,
                "Export Gaji",
                "Tidak ada data gaji pada "
                "periode yang dipilih."
            )

            return

        nama_bulan = [
            "Januari",
            "Februari",
            "Maret",
            "April",
            "Mei",
            "Juni",
            "Juli",
            "Agustus",
            "September",
            "Oktober",
            "November",
            "Desember"
        ]

        nama_periode = (
            f"{nama_bulan[bulan - 1]}_{tahun}"
        )

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Simpan Data Gaji",
            f"gaji_{nama_periode}.xlsx",
            "Excel Files (*.xlsx)"
        )

        if not file_path:
            return

        exporter = ExportManager()

        berhasil = exporter.export_gaji_excel(
            data,
            file_path
        )

        if berhasil:

            QMessageBox.information(
                self,
                "Export Berhasil",
                "Data gaji berhasil diexport "
                "ke Excel!\n\n"
                f"Periode: "
                f"{nama_bulan[bulan - 1]} {tahun}\n\n"
                f"File:\n{file_path}"
            )

        else:

            QMessageBox.warning(
                self,
                "Export Gagal",
                "Terjadi kesalahan saat "
                "mengexport data gaji."
            )

    # ==========================================================
    # CONTEXT MENU
    # ==========================================================

    def show_context_menu(
        self,
        position
    ):

        menu = QMenu()

        edit_action = QAction(
            "Edit Karyawan",
            self
        )

        hapus_action = QAction(
            "Hapus Karyawan",
            self
        )

        edit_action.triggered.connect(
            self.edit_selected_karyawan
        )

        hapus_action.triggered.connect(
            self.hapus_selected_karyawan
        )

        menu.addAction(
            edit_action
        )

        menu.addAction(
            hapus_action
        )

        menu.exec(
            self.table_karyawan.mapToGlobal(
                position
            )
        )

    # ==========================================================
    # TAMBAH KARYAWAN
    # ==========================================================

    def tambah_karyawan(self):

        form = KaryawanForm(
            self
        )

        if form.exec():

            data = form.get_data()

            berhasil = self.db.tambah_karyawan(
                data["nama"],
                data["jabatan"],
                float(data["gaji_pokok"]),
                data["username"],
                data["password"]
            )

            if berhasil:

                QMessageBox.information(
                    self,
                    "Sukses",
                    "Karyawan berhasil ditambahkan!"
                )

                self.load_data_karyawan()

            else:
                QMessageBox.warning(
                    self,
                    "Gagal",
                    "Username sudah digunakan. Silakan gunakan username lain."
                )

    # ==========================================================
    # EDIT KARYAWAN
    # ==========================================================

    def edit_karyawan(
        self,
        karyawan_id
    ):

        karyawan_data = (
            self.db.get_karyawan_by_id(
                karyawan_id
            )
        )

        if not karyawan_data:
            return

        form = KaryawanForm(
            self,
            karyawan_data
        )

        if form.exec():

            data = form.get_data()

            password = (
                data["password"]
                if data["password"]
                else None
            )

            success = self.db.update_karyawan(
                karyawan_id,
                data["nama"],
                data["jabatan"],
                float(data["gaji_pokok"]),
                data["username"],
                password
            )

            if success:

                QMessageBox.information(
                    self,
                    "Sukses",
                    "Data karyawan berhasil diupdate!"
                )

                self.load_data_karyawan()

    # ==========================================================
    # HAPUS KARYAWAN
    # ==========================================================

    def hapus_karyawan(
        self,
        karyawan_id
    ):

        reply = QMessageBox.question(
            self,
            "Konfirmasi",
            "Apakah Anda yakin ingin "
            "menghapus karyawan ini?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        if self.db.hapus_karyawan(
            karyawan_id
        ):

            QMessageBox.information(
                self,
                "Sukses",
                "Karyawan berhasil dihapus!"
            )

            self.load_data_karyawan()

    # ==========================================================
    # EDIT SELECTED
    # ==========================================================

    def edit_selected_karyawan(self):

        selected_row = (
            self.table_karyawan.currentRow()
        )

        if selected_row < 0:
            return

        item = self.table_karyawan.item(
            selected_row,
            0
        )

        if item:

            karyawan_id = int(
                item.text()
            )

            self.edit_karyawan(
                karyawan_id
            )

    # ==========================================================
    # HAPUS SELECTED
    # ==========================================================

    def hapus_selected_karyawan(self):

        selected_row = (
            self.table_karyawan.currentRow()
        )

        if selected_row < 0:
            return

        item = self.table_karyawan.item(
            selected_row,
            0
        )

        if item:

            karyawan_id = int(
                item.text()
            )

            self.hapus_karyawan(
                karyawan_id
            )

    # ==========================================================
    # BACKUP DATABASE
    # ==========================================================

    def backup_database(self):

        src = Config.DB_NAME

        if not os.path.exists(src):

            QMessageBox.warning(
                self,
                "Backup",
                "Database tidak ditemukan."
            )

            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Simpan Backup Database",
            "cafe_payroll_backup.db",
            "Database Files (*.db)"
        )

        if not file_path:
            return

        try:

            shutil.copy(
                src,
                file_path
            )

            QMessageBox.information(
                self,
                "Backup",
                "Backup database berhasil."
            )

        except Exception as e:

            QMessageBox.warning(
                self,
                "Backup Gagal",
                f"Gagal melakukan backup:\n{e}"
            )

    # ==========================================================
    # RESTORE DATABASE
    # ==========================================================

    def restore_database(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Pilih File Database",
            "",
            "Database Files (*.db)"
        )

        if not file_path:
            return

        try:

            shutil.copy(
                file_path,
                Config.DB_NAME
            )

            QMessageBox.information(
                self,
                "Restore",
                "Database berhasil direstore.\n"
                "Silakan restart aplikasi."
            )

        except Exception as e:

            QMessageBox.warning(
                self,
                "Restore Gagal",
                f"Gagal melakukan restore:\n{e}"
            )

    # ==========================================================
    # RESET DATABASE
    # ==========================================================

    def reset_database(self):

        reply = QMessageBox.question(
            self,
            "Konfirmasi Reset",
            "Semua data absensi dan karyawan "
            "akan dihapus.\nLanjutkan?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:

            self.db.cursor.execute(
                "DELETE FROM absensi"
            )

            self.db.cursor.execute(
                "DELETE FROM karyawan "
                "WHERE jabatan != 'Owner'"
            )

            self.db.conn.commit()

            QMessageBox.information(
                self,
                "Reset",
                "Data berhasil direset."
            )

            self.load_data_karyawan()
            self.load_data_absensi()
            self.load_data_gaji()

        except Exception as e:

            QMessageBox.warning(
                self,
                "Reset Gagal",
                f"Gagal mereset data:\n{e}"
            )

    # ==========================================================
    # SETTINGS
    # ==========================================================

    def show_settings(self):
        from PyQt6.QtWidgets import (
            QDialog,
            QVBoxLayout,
            QFormLayout,
            QTimeEdit,
            QSpinBox,
            QDialogButtonBox
        )
        from PyQt6.QtCore import QTime

        dialog = QDialog(self)
        dialog.setWindowTitle("Pengaturan Aplikasi")
        dialog.setMinimumWidth(350)

        layout = QVBoxLayout(dialog)
        form = QFormLayout()

        # Jam masuk kerja
        jam_masuk = QTimeEdit()
        jam_masuk.setDisplayFormat("HH:mm")

        jam = Config.WORK_START_TIME.split(":")
        jam_masuk.setTime(
            QTime(int(jam[0]), int(jam[1]))
        )

        # Jam mulai lembur
        jam_lembur = QTimeEdit()
        jam_lembur.setDisplayFormat("HH:mm")

        jam = Config.OVERTIME_START_TIME.split(":")
        jam_lembur.setTime(
            QTime(int(jam[0]), int(jam[1]))
        )

        # Toleransi keterlambatan
        toleransi = QSpinBox()
        toleransi.setRange(0, 120)
        toleransi.setSuffix(" menit")
        toleransi.setValue(Config.LATE_TOLERANCE)
        
        # Tarif lembur
        tarif_lembur = QDoubleSpinBox()
        tarif_lembur.setRange(1.0, 5.0)
        tarif_lembur.setSingleStep(0.1)
        tarif_lembur.setDecimals(1)
        tarif_lembur.setSuffix(" ×")
        tarif_lembur.setValue(Config.OVERTIME_RATE)

        form.addRow("Jam Masuk:", jam_masuk)
        form.addRow("Mulai Lembur:", jam_lembur)
        form.addRow("Toleransi:", toleransi)
        form.addRow("Tarif Lembur:", tarif_lembur)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )

        def simpan_pengaturan():
            Config.WORK_START_TIME = jam_masuk.time().toString("HH:mm")
            Config.OVERTIME_START_TIME = jam_lembur.time().toString("HH:mm")
            Config.LATE_TOLERANCE = toleransi.value()
            Config.OVERTIME_RATE = tarif_lembur.value()

            Config.save_settings()

            QMessageBox.information(
                self,
                "Berhasil",
                "Pengaturan berhasil disimpan."
            )

            dialog.accept()

        buttons.accepted.connect(simpan_pengaturan)
        buttons.rejected.connect(dialog.reject)

        layout.addWidget(buttons)

        dialog.exec()

    # ==========================================================
    # STAT CARD
    # ==========================================================

    def create_stat_card(
        self,
        title,
        value,
        color
    ):

        card = QWidget()

        card.setStyleSheet(
            f"""
            background-color: {color};
            color: white;
            padding: 15px;
            border-radius: 10px;
            font-weight: bold;
            """
        )

        layout = QVBoxLayout()

        value_label = QLabel(
            value
        )

        value_label.setStyleSheet(
            "font-size: 24px;"
        )

        title_label = QLabel(
            title
        )

        title_label.setStyleSheet(
            "font-size: 12px;"
        )

        layout.addWidget(
            value_label
        )

        layout.addWidget(
            title_label
        )

        card.setLayout(
            layout
        )

        return card

    # ==========================================================
    # DASHBOARD DATA
    # ==========================================================

    def load_dashboard_data(self):
        from datetime import datetime

        today = datetime.now().date()
        bulan = datetime.now().month
        tahun = datetime.now().year

        # Total karyawan
        self.db.cursor.execute(
            """
            SELECT COUNT(*)
            FROM karyawan
            WHERE jabatan != 'Owner'
            """
        )
        total_karyawan = self.db.cursor.fetchone()[0]

        # Karyawan yang hadir hari ini
        self.db.cursor.execute(
            """
            SELECT COUNT(*)
            FROM absensi
            WHERE tanggal = ?
            """,
            (today,)
        )
        hadir_hari_ini = self.db.cursor.fetchone()[0]

        # Tidak hadir
        tidak_hadir = max(
            total_karyawan - hadir_hari_ini,
            0
        )

        # Total gaji bulan ini
        data_gaji = self.db.get_all_gaji(
            bulan,
            tahun
        )

        total_gaji = sum(
            float(data["total_gaji"])
            for data in data_gaji
        )

        # Rata-rata kehadiran
        if total_karyawan > 0:
            rata_kehadiran = (
                hadir_hari_ini / total_karyawan
            ) * 100
        else:
            rata_kehadiran = 0

        # Karyawan baru
        # Untuk sementara mengikuti jumlah karyawan
        # yang ada di database.
        karyawan_baru = total_karyawan

        # Update angka pada kartu dashboard
        data_statistik = {
            "Total Karyawan": str(total_karyawan),
            "Hadir Hari Ini": str(hadir_hari_ini),
            "Tidak Hadir": str(tidak_hadir),
            "Total Gaji Bulan Ini": f"Rp {total_gaji:,.0f}".replace(",", "."),
            "Rata-rata Kehadiran": f"{rata_kehadiran:.0f}%",
            "Karyawan Aktif": str(karyawan_baru)
        }

        # Cari label judul pada setiap kartu,
        # lalu ubah label angka di atasnya.
        for label in self.findChildren(QLabel):

            judul = label.text()

            if judul in data_statistik:

                card = label.parentWidget()

                if card and card.layout():

                    value_label = card.layout().itemAt(0).widget()

                    if value_label:
                        value_label.setText(
                            data_statistik[judul]
                        )

        # ==========================================================
        # AKTIVITAS TERKINI
        # ==========================================================

        self.db.cursor.execute(
            """
            SELECT
                a.tanggal,
                k.nama,
                a.jam_masuk,
                a.jam_keluar
            FROM absensi a
            JOIN karyawan k
                ON a.id_karyawan = k.id
            ORDER BY
                a.tanggal DESC,
                a.jam_masuk DESC
            LIMIT 10
            """
        )

        aktivitas = self.db.cursor.fetchall()

        daftar_aktivitas = []

        for data in aktivitas:

            tanggal = str(data[0])
            nama = str(data[1])
            jam_masuk = data[2]
            jam_keluar = data[3]

            if jam_masuk:
                daftar_aktivitas.append(
                    (
                        tanggal,
                        nama,
                        "Absen Masuk",
                        str(jam_masuk)
                    )
                )

            if jam_keluar:
                daftar_aktivitas.append(
                    (
                        tanggal,
                        nama,
                        "Absen Pulang",
                        str(jam_keluar)
                    )
                )

        daftar_aktivitas.sort(
            key=lambda x: f"{x[0]} {x[3]}",
            reverse=True
        )

        daftar_aktivitas = daftar_aktivitas[:10]

        self.table_activity.setRowCount(
            len(daftar_aktivitas)
        )

        for row, data in enumerate(daftar_aktivitas):

            for col, value in enumerate(data):

                self.table_activity.setItem(
                    row,
                    col,
                    QTableWidgetItem(str(value))
                )

    # ==========================================================
    # CLOSE EVENT
    # ==========================================================

    def closeEvent(
        self,
        event
    ):

        try:
            self.db.conn.close()
        except Exception:
            pass

        event.accept()


# ==============================================================
# TESTING
# ==============================================================

if __name__ == "__main__":

    from PyQt6.QtWidgets import QApplication

    app = QApplication(
        sys.argv
    )

    sample_data = (
        5,
        "Pak Owner",
        "Owner"
    )

    window = OwnerDashboard(
        sample_data
    )

    window.show()

    sys.exit(
        app.exec()
    )