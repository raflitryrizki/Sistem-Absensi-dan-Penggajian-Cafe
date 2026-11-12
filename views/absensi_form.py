# views/absensi_form.py

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QCalendarWidget,
    QComboBox
)
from PyQt6.QtCore import Qt
from datetime import datetime
from modules.database import Database


class AbsensiForm(QDialog):
    def __init__(self, parent=None, karyawan_data=None):
        super().__init__(parent)

        self.karyawan_data = karyawan_data
        self.db = Database()

        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Data Absensi")
        self.setFixedSize(500, 450)

        layout = QVBoxLayout()

        # ==========================================
        # INFO KARYAWAN
        # ==========================================

        if self.karyawan_data:
            info_label = QLabel(
                f"Riwayat Absensi: {self.karyawan_data[1]}"
            )
            info_label.setStyleSheet(
                "font-weight: bold; font-size: 14px;"
            )
            info_label.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            layout.addWidget(info_label)

        # ==========================================
        # FILTER BULAN / TAHUN
        # ==========================================

        filter_layout = QHBoxLayout()

        filter_layout.addWidget(QLabel("Bulan:"))

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

        filter_layout.addWidget(self.combo_bulan)

        filter_layout.addWidget(QLabel("Tahun:"))

        self.combo_tahun = QComboBox()

        current_year = datetime.now().year

        for year in range(
            current_year - 2,
            current_year + 1
        ):
            self.combo_tahun.addItem(str(year))

        self.combo_tahun.setCurrentText(
            str(current_year)
        )

        filter_layout.addWidget(self.combo_tahun)

        layout.addLayout(filter_layout)

        # ==========================================
        # CALENDAR
        # ==========================================

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)

        layout.addWidget(self.calendar)

        # ==========================================
        # INFORMASI ABSENSI
        # ==========================================

        self.info_label = QLabel()

        self.info_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.info_label.setWordWrap(True)

        self.info_label.setStyleSheet(
            """
            QLabel {
                padding: 10px;
                border: 1px solid #cccccc;
                border-radius: 5px;
            }
            """
        )

        layout.addWidget(self.info_label)

        # ==========================================
        # BUTTON
        # ==========================================

        button_layout = QHBoxLayout()

        self.btn_tutup = QPushButton("Tutup")
        self.btn_tutup.clicked.connect(self.accept)

        button_layout.addWidget(self.btn_tutup)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # ==========================================
        # SIGNAL
        # ==========================================

        self.calendar.selectionChanged.connect(
            self.update_info
        )

        self.combo_bulan.currentIndexChanged.connect(
            self.update_calendar
        )

        self.combo_tahun.currentTextChanged.connect(
            self.update_calendar
        )

        # ==========================================
        # LOAD DATA AWAL
        # ==========================================

        self.update_calendar()

    # ==============================================
    # UPDATE CALENDAR
    # ==============================================

    def update_calendar(self):
        bulan = self.combo_bulan.currentIndex() + 1
        tahun = int(self.combo_tahun.currentText())

        date = self.calendar.selectedDate()

        # Jika bulan/tahun berubah,
        # pilih tanggal 1 pada periode tersebut
        if (
            date.year() != tahun
            or date.month() != bulan
        ):
            from PyQt6.QtCore import QDate

            self.calendar.setSelectedDate(
                QDate(tahun, bulan, 1)
            )
        else:
            self.update_info()

    # ==============================================
    # UPDATE INFORMASI ABSENSI
    # ==============================================

    def update_info(self):
        selected_date = self.calendar.selectedDate()

        date_str = selected_date.toString(
            "yyyy-MM-dd"
        )

        # ==========================================
        # JIKA TIDAK ADA DATA KARYAWAN
        # ==========================================

        if not self.karyawan_data:
            self.info_label.setText(
                f"Tanggal: "
                f"{selected_date.toString('dd MMMM yyyy')}\n\n"
                "Data karyawan tidak tersedia."
            )
            return

        id_karyawan = self.karyawan_data[0]

        # ==========================================
        # AMBIL DATA ABSENSI
        # ==========================================

        self.db.cursor.execute(
            """
            SELECT
                tanggal,
                jam_masuk,
                jam_keluar,
                status,
                lembur
            FROM absensi
            WHERE id_karyawan = ?
              AND tanggal = ?
            """,
            (
                id_karyawan,
                date_str
            )
        )

        absensi = self.db.cursor.fetchone()

        # ==========================================
        # TIDAK ADA ABSENSI
        # ==========================================

        if not absensi:
            self.info_label.setText(
                f"Tanggal: "
                f"{selected_date.toString('dd MMMM yyyy')}\n\n"
                "❌ Tidak ada data absensi."
            )
            return

        # ==========================================
        # DATA ABSENSI DITEMUKAN
        # ==========================================

        tanggal = absensi[0]
        jam_masuk = absensi[1] or "-"
        jam_keluar = absensi[2] or "-"
        status = absensi[3] or "-"
        lembur = absensi[4] or 0

        self.info_label.setText(
            f"Tanggal: "
            f"{selected_date.toString('dd MMMM yyyy')}\n\n"
            f"Jam Masuk  : {jam_masuk}\n"
            f"Jam Keluar : {jam_keluar}\n"
            f"Status     : {status}\n"
            f"Lembur     : {lembur} jam"
        )