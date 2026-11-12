import logging
from datetime import datetime
from pathlib import Path

class ActivityLogger:
    def __init__(self):
        self.setup_logger()
    
    def setup_logger(self):
        """Setup logging configuration"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"activity_{datetime.now().strftime('%Y%m')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('CafeApp')
    
    def log_login(self, username, success=True):
        status = "BERHASIL" if success else "GAGAL"
        self.logger.info(f"LOGIN - User: {username} - {status}")
    
    def log_attendance(self, user_id, action):
        self.logger.info(f"ABSENSI - UserID: {user_id} - Aksi: {action}")
    
    def log_payroll(self, action, details):
        self.logger.info(f"PENGGAJIAN - {action} - {details}")
    
    def log_system(self, action):
        self.logger.info(f"SYSTEM - {action}")
    
    def log_error(self, error_message):
        self.logger.error(f"ERROR - {error_message}")

# ✅ Buat logger global yang bisa digunakan dari modul lain
logger = ActivityLogger()

if __name__ == "__main__":
    logger.log_login("rizki", True)
    logger.log_attendance(1, "Masuk")
    logger.log_system("Aplikasi dimulai")
