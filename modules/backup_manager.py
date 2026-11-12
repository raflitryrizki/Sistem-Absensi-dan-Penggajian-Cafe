# modules/backup_manager.py
import shutil
import os
from datetime import datetime
from config import Config
from modules.logger import logger

class BackupManager:
    def __init__(self):
        Config.setup_directories()
    
    def backup_database(self, backup_name=None):
        try:
            if not backup_name:
                backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            
            backup_path = os.path.join(Config.BACKUP_FOLDER, backup_name)
            shutil.copy2(Config.DB_NAME, backup_path)
            
            logger.log_system(f"Backup created: {backup_name}")
            return True, backup_path
            
        except Exception as e:
            logger.log_error(f"Backup failed: {e}")
            return False, str(e)
    
    def restore_database(self, backup_file):
        try:
            if os.path.exists(backup_file):
                shutil.copy2(backup_file, Config.DB_NAME)
                logger.log_system(f"Database restored from: {backup_file}")
                return True
            return False
        except Exception as e:
            logger.log_error(f"Restore failed: {e}")
            return False
    
    def get_backup_list(self):
        try:
            backups = []
            if os.path.exists(Config.BACKUP_FOLDER):
                for file in os.listdir(Config.BACKUP_FOLDER):
                    if file.endswith('.db'):
                        file_path = os.path.join(Config.BACKUP_FOLDER, file)
                        stats = os.stat(file_path)
                        backups.append({
                            'name': file,
                            'path': file_path,
                            'size': stats.st_size,
                            'date': datetime.fromtimestamp(stats.st_mtime)
                        })
            return sorted(backups, key=lambda x: x['date'], reverse=True)
        except Exception as e:
            logger.log_error(f"Get backup list failed: {e}")
            return []