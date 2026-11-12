import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()

from config import Config
from datetime import datetime, timedelta
from pathlib import Path
from modules.logger import logger   # ✅ IMPORT GLOBAL DI SINI

class Database:
    def __init__(self, db_name=None):
        if db_name is None:
            db_name = Path(Config.DB_NAME)
        
        db_name.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.insert_sample_data()
        
        logger.log_system("Database initialized")

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS karyawan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT NOT NULL,
                jabatan TEXT,
                gaji_pokok REAL NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS absensi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_karyawan INTEGER NOT NULL,
                tanggal DATE NOT NULL,
                jam_masuk TIME,
                jam_keluar TIME,
                status TEXT,
                lembur REAL DEFAULT 0,
                FOREIGN KEY (id_karyawan) REFERENCES karyawan (id)
            )
        ''')
        self.conn.commit()

    def insert_sample_data(self):
        self.cursor.execute("SELECT COUNT(*) FROM karyawan")
        if self.cursor.fetchone()[0] == 0:
            print("Menambahkan data karyawan...")
            self.tambah_karyawan("Rizki Noor Ramadhan", "Owner", 0, "rizky", "rizky123")
            print("Data sample berhasil ditambahkan!")

    def tambah_karyawan(self, nama, jabatan, gaji_pokok, username, password):
        password = hash_password(password)

        try:
            self.cursor.execute('''
                INSERT INTO karyawan (nama, jabatan, gaji_pokok, username, password)
                VALUES (?, ?, ?, ?, ?)
            ''', (nama, jabatan, gaji_pokok, username, password))
            self.conn.commit()
            logger.log_system(f"Karyawan ditambah: {nama} ({username})")
            return True
        except sqlite3.IntegrityError:
            logger.log_error(f"Username sudah digunakan: {username}")
            return False

    def get_all_karyawan(self):
        self.cursor.execute("SELECT * FROM karyawan WHERE jabatan != 'Owner'")
        return self.cursor.fetchall()

    def get_karyawan_by_id(self, karyawan_id):
        self.cursor.execute("SELECT * FROM karyawan WHERE id=? AND jabatan != 'Owner'", (karyawan_id,))
        return self.cursor.fetchone()

    def update_karyawan(self, karyawan_id, nama, jabatan, gaji_pokok, username, password=None):
        self.cursor.execute("SELECT username FROM karyawan WHERE id = ?", (karyawan_id,))
        current_user = self.cursor.fetchone()
    
        if username and current_user and username != current_user[0]:
            self.cursor.execute("SELECT id FROM karyawan WHERE username = ? AND id != ?", (username, karyawan_id))
            if self.cursor.fetchone():
                return False
    
        try:
            if password:
                password = hash_password(password)

                self.cursor.execute('''
                    UPDATE karyawan 
                    SET nama=COALESCE(?, nama),
                        jabatan=COALESCE(?, jabatan),
                        gaji_pokok=COALESCE(?, gaji_pokok),
                        username=COALESCE(?, username),
                        password=?
                    WHERE id=?
                ''', (nama, jabatan, gaji_pokok, username, password, karyawan_id))
            else:
                self.cursor.execute('''
                    UPDATE karyawan 
                    SET nama=COALESCE(?, nama),
                        jabatan=COALESCE(?, jabatan),
                        gaji_pokok=COALESCE(?, gaji_pokok),
                        username=COALESCE(?, username)
                    WHERE id=?
                ''', (nama, jabatan, gaji_pokok, username, karyawan_id))
        
            self.conn.commit()
            logger.log_system(f"Karyawan diupdate: ID {karyawan_id}")
            return True
        except sqlite3.IntegrityError:
            logger.log_error(f"Username sudah digunakan: {username}")
            return False

    def hapus_karyawan(self, karyawan_id):
        self.cursor.execute("SELECT * FROM karyawan WHERE id=? AND jabatan != 'Owner'", (karyawan_id,))
        if not self.cursor.fetchone():
            return False
        
        try:
            self.cursor.execute('DELETE FROM absensi WHERE id_karyawan=?', (karyawan_id,))
            self.cursor.execute('DELETE FROM karyawan WHERE id=?', (karyawan_id,))
            self.conn.commit()
            logger.log_system(f"Karyawan dihapus: ID {karyawan_id}")
            return True
        except Exception as e:
            logger.log_error(f"Gagal hapus karyawan ID {karyawan_id}: {e}")
            return False

    def absen_masuk(self, id_karyawan):
        """Mencatat absensi masuk dan menentukan status hadir/terlambat."""

        today = datetime.now().date()
        now = datetime.now()

        # Cek apakah karyawan sudah absen hari ini
        self.cursor.execute(
            '''
            SELECT id
            FROM absensi
            WHERE id_karyawan = ? AND tanggal = ?
            ''',
            (id_karyawan, today)
        )

        if self.cursor.fetchone():
            logger.log_attendance(
                id_karyawan,
                "Gagal Masuk (sudah absen)"
            )
            return False

        # Waktu masuk saat ini
        now_time = now.strftime("%H:%M:%S")

        # Batas waktu hadir
        jam_masuk = datetime.strptime(
            Config.WORK_START_TIME,
            "%H:%M"
        ).time()

        batas_hadir = now.replace(
            hour=jam_masuk.hour,
            minute=jam_masuk.minute,
            second=0,
            microsecond=0
        ) + timedelta(
            minutes=Config.LATE_TOLERANCE
        )

        # Tentukan status
        if now <= batas_hadir:
            status = "Hadir"
        else:
            status = "Terlambat"

        # Simpan absensi
        self.cursor.execute(
            '''
            INSERT INTO absensi
            (
                id_karyawan,
                tanggal,
                jam_masuk,
                status,
                lembur
            )
            VALUES (?, ?, ?, ?, ?)
            ''',
            (
                id_karyawan,
                today,
                now_time,
                status,
                0
            )
        )

        self.conn.commit()

        logger.log_attendance(
            id_karyawan,
            f"Masuk ({status})"
        )

        return True

    def absen_pulang(self, id_karyawan):
        """Mencatat waktu pulang dan menghitung durasi lembur."""

        today = datetime.now().date()
        now = datetime.now()

        # Cari absensi hari ini yang belum memiliki jam pulang
        self.cursor.execute(
            '''
            SELECT id, jam_masuk
            FROM absensi
            WHERE id_karyawan = ?
            AND tanggal = ?
            AND jam_keluar IS NULL
            ''',
            (id_karyawan, today)
        )

        attendance = self.cursor.fetchone()

        # Belum melakukan absen masuk
        if not attendance:
            logger.log_attendance(
                id_karyawan,
                "Gagal Pulang (belum absen masuk)"
            )
            return False

        attendance_id, jam_masuk = attendance

        now_time = now.strftime("%H:%M:%S")

        # Jam mulai lembur
        jam_lembur = datetime.strptime(
            Config.OVERTIME_START_TIME,
            "%H:%M"
        ).time()

        jam_mulai_lembur = now.replace(
            hour=jam_lembur.hour,
            minute=jam_lembur.minute,
            second=0,
            microsecond=0
        )

        # Hitung lembur
        lembur = 0

        if now > jam_mulai_lembur:
            durasi_lembur = now - jam_mulai_lembur
            lembur = round(
                durasi_lembur.total_seconds() / 3600,
                2
            )

        # Update absensi
        self.cursor.execute(
            '''
            UPDATE absensi
            SET
                jam_keluar = ?,
                lembur = ?
            WHERE id = ?
            ''',
            (
                now_time,
                lembur,
                attendance_id
            )
        )

        self.conn.commit()

        logger.log_attendance(
            id_karyawan,
            f"Pulang (Lembur: {lembur} jam)"
        )

        return True

    def get_absensi_hari_ini(self):
        """Mengambil data absensi untuk hari ini."""
        today = datetime.now().date()
        self.cursor.execute('''
            SELECT a.tanggal, k.nama, a.jam_masuk, a.jam_keluar, a.status, a.lembur
            FROM absensi a
            JOIN karyawan k ON a.id_karyawan = k.id
            WHERE a.tanggal = ?
            ORDER BY a.jam_masuk DESC
        ''', (today,))
        return self.cursor.fetchall()
    
    def get_absensi_export(self, start_date=None, end_date=None):
        """Mengambil data absensi berdasarkan periode untuk export Excel."""

        if start_date is None or end_date is None:
            today = datetime.now().date()
            start_date = today
            end_date = today

        self.cursor.execute(
            """
            SELECT
                a.tanggal,
                k.nama,
                k.jabatan,
                a.jam_masuk,
                a.jam_keluar,
                a.status,
                a.lembur
            FROM absensi a
            JOIN karyawan k
                ON a.id_karyawan = k.id
            WHERE a.tanggal BETWEEN ? AND ?
            ORDER BY a.tanggal DESC, a.jam_masuk DESC
            """,
            (start_date, end_date)
        )

        return self.cursor.fetchall()

    def get_riwayat_absensi(self, start_date, end_date):
        """Mengambil riwayat absensi berdasarkan rentang tanggal."""

        self.cursor.execute("""
            SELECT
                a.tanggal,
                k.nama,
                a.jam_masuk,
                a.jam_keluar,
                a.status,
                a.lembur
            FROM absensi a
            JOIN karyawan k
                ON a.id_karyawan = k.id
            WHERE a.tanggal BETWEEN ? AND ?
            ORDER BY a.tanggal DESC, a.jam_masuk DESC
        """, (start_date, end_date))

        return self.cursor.fetchall()

    def get_all_gaji(self, bulan=None, tahun=None):
        """Mengambil dan menghitung data gaji karyawan berdasarkan bulan dan tahun."""

        # Jika bulan/tahun tidak diberikan,
        # gunakan bulan dan tahun sekarang
        if bulan is None or tahun is None:
            sekarang = datetime.now()
            bulan = sekarang.month
            tahun = sekarang.year

        periode = f"{tahun:04d}-{bulan:02d}"

        # Parameter payroll sementara
        HARI_KERJA_STANDAR = 26
        JAM_KERJA_PER_HARI = 8
        TARIF_LEMBUR = Config.OVERTIME_RATE

        query = """
            SELECT
                k.id,
                k.nama,
                k.jabatan,
                k.gaji_pokok,

                COUNT(a.id) AS hari_kerja,

                COALESCE(
                    SUM(a.lembur),
                    0
                ) AS total_lembur

            FROM karyawan k

            LEFT JOIN absensi a
                ON k.id = a.id_karyawan
                AND strftime('%Y-%m', a.tanggal) = ?

            WHERE k.jabatan != 'Owner'

            GROUP BY
                k.id,
                k.nama,
                k.jabatan,
                k.gaji_pokok

            ORDER BY k.nama ASC
        """

        self.cursor.execute(query, (periode,))
        rows = self.cursor.fetchall()

        result = []

        for row in rows:

            id_karyawan = row[0]
            nama = row[1]
            jabatan = row[2]
            gaji_pokok = float(row[3] or 0)
            hari_kerja = int(row[4] or 0)
            total_lembur = float(row[5] or 0)

            # ==========================================
            # GAJI BERDASARKAN HARI KERJA
            # ==========================================

            gaji_per_hari = (
                gaji_pokok / HARI_KERJA_STANDAR
            )

            gaji_dibayar = (
                gaji_per_hari * hari_kerja
            )

            # ==========================================
            # UANG LEMBUR
            # ==========================================

            gaji_per_jam = (
                gaji_per_hari / JAM_KERJA_PER_HARI
            )

            uang_lembur = (
                gaji_per_jam
                * total_lembur
                * TARIF_LEMBUR
            )

            # ==========================================
            # TOTAL GAJI
            # ==========================================

            total_gaji = (
                gaji_dibayar
                + uang_lembur
            )

            result.append({
                "id": id_karyawan,
                "nama": nama,
                "jabatan": jabatan,
                "gaji_pokok": gaji_pokok,
                "hari_kerja": hari_kerja,
                "total_lembur": round(total_lembur, 2),
                "gaji_dibayar": round(gaji_dibayar),
                "uang_lembur": round(uang_lembur),
                "total_gaji": round(total_gaji)
            })

        return result



    def login(self, username, password):
        self.cursor.execute(
            """
            SELECT id, nama, jabatan, password
            FROM karyawan
            WHERE username = ?
            """,
            (username,)
        )

        result = self.cursor.fetchone()

        if not result:
            logger.log_login(username, False)
            return None

        password_hash = hash_password(password)

        # Password sudah menggunakan hash
        if result[3] == password_hash:
            logger.log_login(username, True)
            return result[:3]

        # Kompatibilitas password lama yang masih plaintext
        if result[3] == password:
            self.cursor.execute(
                """
                UPDATE karyawan
                SET password = ?
                WHERE id = ?
                """,
                (password_hash, result[0])
            )

            self.conn.commit()

            logger.log_login(username, True)
            return result[:3]

        logger.log_login(username, False)
        return None
