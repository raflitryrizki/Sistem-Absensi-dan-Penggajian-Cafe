# views/gaji_form.py

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QFileDialog
)

from PyQt6.QtCore import Qt

from datetime import datetime


class GajiForm(QDialog):

    def __init__(self, parent=None, db=None):
        super().__init__(parent)

        self.db = db

        self.setup_ui()
        self.load_data()

    # ==========================================================
    # SETUP UI
    # ==========================================================

    def setup_ui(self):

        self.setWindowTitle(
            "Perhitungan Gaji Karyawan"
        )

        self.setFixedSize(800, 500)

        layout = QVBoxLayout()

        # ======================================================
        # FILTER BULAN / TAHUN
        # ======================================================

        filter_layout = QHBoxLayout()

        filter_layout.addWidget(
            QLabel("Bulan:")
        )

        self.combo_bulan = QComboBox()

        self.combo_bulan.addItems([
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
        ])

        self.combo_bulan.setCurrentIndex(
            datetime.now().month - 1
        )

        self.combo_tahun = QComboBox()

        current_year = datetime.now().year

        for year in range(
            current_year - 1,
            current_year + 2
        ):
            self.combo_tahun.addItem(
                str(year)
            )

        self.combo_tahun.setCurrentText(
            str(current_year)
        )

        filter_layout.addWidget(
            self.combo_bulan
        )

        filter_layout.addWidget(
            QLabel("Tahun:")
        )

        filter_layout.addWidget(
            self.combo_tahun
        )

        # ======================================================
        # BUTTON HITUNG
        # ======================================================

        btn_hitung = QPushButton(
            "💰 Hitung Gaji"
        )

        btn_hitung.clicked.connect(
            self.hitung_gaji
        )

        filter_layout.addWidget(
            btn_hitung
        )

        layout.addLayout(
            filter_layout
        )

        # ======================================================
        # TABEL GAJI
        # ======================================================

        self.table_gaji = QTableWidget()

        self.table_gaji.setColumnCount(8)

        self.table_gaji.setHorizontalHeaderLabels([
            "Nama",
            "Jabatan",
            "Gaji Pokok",
            "Hari Kerja",
            "Lembur (jam)",
            "Gaji Dibayar",
            "Uang Lembur",
            "Total Gaji"
        ])

        layout.addWidget(
            self.table_gaji
        )

        # ======================================================
        # TOTAL
        # ======================================================

        self.label_total = QLabel(
            "Total Pengeluaran Gaji: Rp 0"
        )

        self.label_total.setStyleSheet(
            "font-weight: bold; "
            "font-size: 14px;"
        )

        layout.addWidget(
            self.label_total
        )

        # ======================================================
        # BUTTON
        # ======================================================

        btn_layout = QHBoxLayout()

        btn_cetak = QPushButton(
            "🖨️ Cetak Slip"
        )

        btn_tutup = QPushButton(
            "Tutup"
        )

        btn_cetak.clicked.connect(
            self.cetak_slip
        )

        btn_tutup.clicked.connect(
            self.accept
        )

        btn_layout.addWidget(
            btn_cetak
        )

        btn_layout.addStretch()

        btn_layout.addWidget(
            btn_tutup
        )

        layout.addLayout(
            btn_layout
        )

        self.setLayout(
            layout
        )

    # ==========================================================
    # LOAD DATA
    # ==========================================================

    def load_data(self):

        self.hitung_gaji()

    # ==========================================================
    # HITUNG GAJI
    # ==========================================================

    def hitung_gaji(self):

        bulan = (
            self.combo_bulan.currentIndex()
            + 1
        )

        tahun = int(
            self.combo_tahun.currentText()
        )

        data_gaji = self.db.get_all_gaji(
            bulan,
            tahun
        )

        self.table_gaji.setRowCount(
            len(data_gaji)
        )

        total_pengeluaran = 0

        for row, gaji in enumerate(
            data_gaji
        ):

            gaji_pokok = (
                f"Rp {gaji['gaji_pokok']:,.0f}"
            )

            gaji_dibayar = (
                f"Rp {gaji['gaji_dibayar']:,.0f}"
            )

            uang_lembur = (
                f"Rp {gaji['uang_lembur']:,.0f}"
            )

            total_gaji = (
                f"Rp {gaji['total_gaji']:,.0f}"
            )

            items = [
                gaji["nama"],
                gaji["jabatan"],
                gaji_pokok,
                str(gaji["hari_kerja"]),
                f"{gaji['total_lembur']:.2f}",
                gaji_dibayar,
                uang_lembur,
                total_gaji
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

            total_pengeluaran += (
                gaji["total_gaji"]
            )

        self.label_total.setText(
            f"Total Pengeluaran Gaji: "
            f"Rp {total_pengeluaran:,.0f}"
        )

    # ==========================================================
    # CETAK SLIP GAJI
    # ==========================================================

    def cetak_slip(self):

        from modules.export_manager import (
            ExportManager
        )

        selected_row = (
            self.table_gaji.currentRow()
        )

        # Belum memilih karyawan
        if selected_row < 0:

            QMessageBox.warning(
                self,
                "Peringatan",
                "Pilih karyawan terlebih dahulu!"
            )

            return

        # ======================================================
        # PERIODE
        # ======================================================

        bulan = (
            self.combo_bulan.currentIndex()
            + 1
        )

        tahun = int(
            self.combo_tahun.currentText()
        )

        # ======================================================
        # NAMA KARYAWAN
        # ======================================================

        nama_item = (
            self.table_gaji.item(
                selected_row,
                0
            )
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
        # CARI DATA GAJI LENGKAP
        # ======================================================

        gaji_data = None

        all_gaji = self.db.get_all_gaji(
            bulan,
            tahun
        )

        for data in all_gaji:

            if data["nama"] == nama:

                gaji_data = data

                break

        if not gaji_data:

            QMessageBox.warning(
                self,
                "Error",
                "Data gaji tidak ditemukan!"
            )

            return

        # ======================================================
        # PILIH LOKASI FILE
        # ======================================================

        file_path, _ = (
            QFileDialog.getSaveFileName(
                self,
                "Simpan Slip Gaji",
                f"slip_gaji_{nama}_{tahun}_{bulan}.pdf",
                "PDF Files (*.pdf)"
            )
        )

        if not file_path:

            return

        # ======================================================
        # CETAK PDF
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
                "Slip gaji berhasil disimpan!\n\n"
                f"{file_path}"
            )

        else:

            QMessageBox.warning(
                self,
                "Error",
                "Gagal mencetak slip gaji!"
            )


# ==========================================================
# TESTING
# ==========================================================

if __name__ == "__main__":

    from PyQt6.QtWidgets import QApplication

    from modules.database import Database

    app = QApplication([])

    db = Database()

    form = GajiForm(
        db=db
    )

    form.exec()