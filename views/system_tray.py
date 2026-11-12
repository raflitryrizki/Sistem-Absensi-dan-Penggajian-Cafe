# views/system_tray.py
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QTimer
import os

class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(QIcon("assets/icon.png"))
        self.setToolTip("Sistem Absensi Cafe - Berjalan di background")
        
        # Create menu
        self.menu = QMenu()
        
        self.show_action = QAction("Buka Aplikasi", self)
        self.show_action.triggered.connect(self.show_application)
        
        self.exit_action = QAction("Keluar", self)
        self.exit_action.triggered.connect(self.exit_application)
        
        self.menu.addAction(self.show_action)
        self.menu.addSeparator()
        self.menu.addAction(self.exit_action)
        
        self.setContextMenu(self.menu)
        
        # Timer untuk auto-save
        self.timer = QTimer()
        self.timer.timeout.connect(self.auto_backup)
        self.timer.start(3600000)  # Setiap 1 jam
        
        self.activated.connect(self.on_tray_activated)
    
    def show_application(self):
        """Show main application window"""
        if self.parent():
            self.parent().show()
            self.parent().raise_()
            self.parent().activateWindow()
    
    def exit_application(self):
        """Exit application"""
        self.timer.stop()
        QApplication.quit()
    
    def on_tray_activated(self, reason):
        """Handle tray icon click"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_application()
    
    def auto_backup(self):
        """Auto backup database"""
        try:
            from modules.database import Database
            from config import Config
            
            # Create backup folder if not exists
            os.makedirs(Config.BACKUP_FOLDER, exist_ok=True)
            
            # Backup database
            backup_file = os.path.join(Config.BACKUP_FOLDER, f"auto_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.db")
            db = Database()
            if db.backup_database(backup_file):
                self.showMessage("Auto Backup", "Database berhasil di-backup otomatis", QSystemTrayIcon.MessageIcon.Information, 3000)
        except Exception as e:
            print(f"Auto backup error: {e}")

# Untuk testing
if __name__ == "__main__":
    app = QApplication([])
    tray = SystemTrayIcon()
    tray.show()
    app.exec()