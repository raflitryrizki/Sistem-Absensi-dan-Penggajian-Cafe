# modules/export_manager.py

import os
import openpyxl

from openpyxl.styles import Font, Alignment, Border, Side
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime


class ExportManager:

    def __init__(self):
        pass

    # ==========================================================
    # EXPORT DATA ABSENSI KE EXCEL
    # ==========================================================

    def export_absensi_excel(self, data, file_path):
        """Export data absensi ke Excel."""

        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Data Absensi"

            # Header
            headers = [
                "Tanggal",
                "Nama",
                "Jabatan",
                "Jam Masuk",
                "Jam Pulang",
                "Status",
                "Lembur (jam)"
            ]

            for col, header in enumerate(headers, 1):
                cell = ws.cell(
                    row=1,
                    column=col,
                    value=header
                )

                cell.font = Font(bold=True)
                cell.alignment = Alignment(
                    horizontal="center"
                )

            # Data
            for row, absensi in enumerate(data, 2):

                ws.cell(
                    row=row,
                    column=1,
                    value=absensi[0]
                )

                ws.cell(
                    row=row,
                    column=2,
                    value=absensi[1]
                )

                ws.cell(
                    row=row,
                    column=3,
                    value=absensi[2]
                )

                ws.cell(
                    row=row,
                    column=4,
                    value=absensi[3] if absensi[3] else "-"
                )

                ws.cell(
                    row=row,
                    column=5,
                    value=absensi[4] if absensi[4] else "-"
                )

                ws.cell(
                    row=row,
                    column=6,
                    value=absensi[5] if absensi[5] else "-"
                )

                ws.cell(
                    row=row,
                    column=7,
                    value=absensi[6] if absensi[6] is not None else 0
                )

            # Auto adjust column widths
            for column in ws.columns:

                max_length = 0
                column_letter = column[0].column_letter

                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except Exception:
                        pass

                adjusted_width = min(
                    max_length + 2,
                    30
                )

                ws.column_dimensions[
                    column_letter
                ].width = adjusted_width

            wb.save(file_path)

            return True

        except Exception as e:

            print(
                f"Error export Excel: {e}"
            )

            return False

    # ==========================================================
    # EXPORT DATA GAJI KE EXCEL
    # ==========================================================

    def export_gaji_excel(self, data, file_path):
        """Export data gaji ke Excel."""

        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Rekap Gaji"

            # Header
            headers = [
                "Nama",
                "Jabatan",
                "Gaji Pokok",
                "Hari Kerja",
                "Lembur (jam)",
                "Gaji Dibayar",
                "Uang Lembur",
                "Total Gaji"
            ]

            for col, header in enumerate(headers, 1):

                cell = ws.cell(
                    row=1,
                    column=col,
                    value=header
                )

                cell.font = Font(bold=True)

                cell.alignment = Alignment(
                    horizontal="center"
                )

            # Data
            total_pengeluaran = 0

            for row, gaji in enumerate(data, 2):

                ws.cell(
                    row=row,
                    column=1,
                    value=gaji["nama"]
                )

                ws.cell(
                    row=row,
                    column=2,
                    value=gaji["jabatan"]
                )

                ws.cell(
                    row=row,
                    column=3,
                    value=gaji["gaji_pokok"]
                )

                ws.cell(
                    row=row,
                    column=4,
                    value=gaji["hari_kerja"]
                )

                ws.cell(
                    row=row,
                    column=5,
                    value=gaji["total_lembur"]
                )

                ws.cell(
                    row=row,
                    column=6,
                    value=gaji["gaji_dibayar"]
                )

                ws.cell(
                    row=row,
                    column=7,
                    value=gaji["uang_lembur"]
                )

                ws.cell(
                    row=row,
                    column=8,
                    value=gaji["total_gaji"]
                )

                total_pengeluaran += gaji["total_gaji"]

            # Total row
            total_row = len(data) + 2

            ws.cell(
                row=total_row,
                column=7,
                value="TOTAL:"
            ).font = Font(bold=True)

            ws.cell(
                row=total_row,
                column=8,
                value=total_pengeluaran
            ).font = Font(bold=True)

            # Format currency
            for row in range(2, total_row + 1):

                for col in [3, 6, 7, 8]:

                    cell = ws.cell(
                        row=row,
                        column=col
                    )

                    cell.number_format = '"Rp"#,##0'

            # Format lembur
            for row in range(2, total_row):

                ws.cell(
                    row=row,
                    column=5
                ).number_format = '0.00'

            # Auto adjust column widths
            for column in ws.columns:

                max_length = 0
                column_letter = column[0].column_letter

                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except Exception:
                        pass

                adjusted_width = min(
                    max_length + 2,
                    25
                )

                ws.column_dimensions[
                    column_letter
                ].width = adjusted_width

            wb.save(file_path)

            return True

        except Exception as e:

            print(
                f"Error export gaji Excel: {e}"
            )

            return False

    # ==========================================================
    # CETAK SLIP GAJI KE PDF
    # ==========================================================

    def cetak_slip_gaji(
        self,
        gaji_data,
        file_path,
        bulan=None,
        tahun=None
    ):
        """Cetak slip gaji ke PDF."""

        try:

            # ==================================================
            # NAMA BULAN
            # ==================================================

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

            # Jika periode diberikan
            if bulan and tahun:

                if 1 <= bulan <= 12:

                    periode = (
                        f"{nama_bulan[bulan - 1]} "
                        f"{tahun}"
                    )

                else:

                    periode = (
                        f"{bulan}/{tahun}"
                    )

            else:

                periode = datetime.now().strftime(
                    "%B %Y"
                )

            # ==================================================
            # BUAT PDF
            # ==================================================

            c = canvas.Canvas(
                file_path,
                pagesize=letter
            )

            width, height = letter

            # ==================================================
            # HEADER
            # ==================================================

            c.setFont(
                "Helvetica-Bold",
                18
            )

            c.drawCentredString(
                width / 2,
                height - 80,
                "SLIP GAJI KARYAWAN"
            )

            c.setFont(
                "Helvetica",
                11
            )

            c.drawCentredString(
                width / 2,
                height - 100,
                f"Periode: {periode}"
            )

            # Garis
            c.line(
                70,
                height - 120,
                width - 70,
                height - 120
            )

            # ==================================================
            # DATA KARYAWAN
            # ==================================================

            y_position = height - 155

            c.setFont(
                "Helvetica-Bold",
                12
            )

            c.drawString(
                80,
                y_position,
                "DATA KARYAWAN"
            )

            c.setFont(
                "Helvetica",
                10
            )

            c.drawString(
                100,
                y_position - 25,
                f"Nama              : {gaji_data['nama']}"
            )

            c.drawString(
                100,
                y_position - 40,
                f"Jabatan           : {gaji_data['jabatan']}"
            )

            c.drawString(
                100,
                y_position - 55,
                f"Periode Gaji      : {periode}"
            )

            # ==================================================
            # RINCIAN GAJI
            # ==================================================

            y_position -= 90

            c.setFont(
                "Helvetica-Bold",
                12
            )

            c.drawString(
                80,
                y_position,
                "RINCIAN GAJI"
            )

            # Garis kecil
            c.line(
                80,
                y_position - 8,
                width - 80,
                y_position - 8
            )

            details = [
                (
                    "Gaji Pokok",
                    f"Rp {gaji_data['gaji_pokok']:,.0f}"
                ),
                (
                    "Hari Kerja",
                    f"{gaji_data['hari_kerja']} hari"
                ),
                (
                    "Gaji Dibayar",
                    f"Rp {gaji_data['gaji_dibayar']:,.0f}"
                ),
                (
                    "Lembur",
                    f"{gaji_data['total_lembur']:.2f} jam"
                ),
                (
                    "Uang Lembur",
                    f"Rp {gaji_data['uang_lembur']:,.0f}"
                )
            ]

            c.setFont(
                "Helvetica",
                10
            )

            start_y = y_position - 35

            for i, (label, value) in enumerate(details):

                current_y = (
                    start_y - (i * 20)
                )

                c.drawString(
                    100,
                    current_y,
                    f"{label}:"
                )

                c.drawRightString(
                    width - 100,
                    current_y,
                    value
                )

            # ==================================================
            # TOTAL GAJI
            # ==================================================

            total_y = start_y - (
                len(details) * 20
            ) - 15

            c.line(
                80,
                total_y + 10,
                width - 80,
                total_y + 10
            )

            c.setFont(
                "Helvetica-Bold",
                13
            )

            c.drawString(
                100,
                total_y - 10,
                "TOTAL GAJI"
            )

            c.drawRightString(
                width - 100,
                total_y - 10,
                f"Rp {gaji_data['total_gaji']:,.0f}"
            )

            # ==================================================
            # FOOTER
            # ==================================================

            c.line(
                80,
                150,
                width - 80,
                150
            )

            c.setFont(
                "Helvetica-Oblique",
                9
            )

            c.drawString(
                80,
                130,
                "Dicetak otomatis oleh Sistem Absensi Cafe"
            )

            c.drawString(
                80,
                115,
                "Tanggal cetak: "
                + datetime.now().strftime(
                    "%d/%m/%Y %H:%M"
                )
            )

            c.save()

            return True

        except Exception as e:

            print(
                f"Error cetak slip: {e}"
            )

            return False


# ==========================================================
# TESTING
# ==========================================================

if __name__ == "__main__":

    exporter = ExportManager()

    print(
        "Export Manager siap digunakan!"
    )