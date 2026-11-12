# views/monitor_dashboard.py
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QTableWidget, QTableWidgetItem,
    QTabWidget, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QTextCursor
from modules.database import Database
from modules.logger import logger
import os
from datetime import datetime, timedelta

class MonitorDashboard(QMainWindow):
    def __init__(self, user_data):
        super().__init__()
        self.user_id, self.nama, self.jabatan = user_data
        self.db = Database()
        
        self.setWindowTitle(f"Monitoring System - {self.nama}")
        self.setGeometry(100, 100, 1000, 600)
        
        self.setup_ui()
        self.start_monitoring()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Header
        header_label = QLabel(f"Monitoring System - Selamat Datang, {self.nama}")
        header_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header_label)
        
        # Tab Widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Tab 1: Real-time Logs
        tab_logs = QWidget()
        self.setup_tab_logs(tab_logs)
        self.tab_widget.addTab(tab_logs, "📊 Logs Real-time")
        
        # Tab 2: System Status
        tab_status = QWidget()
        self.setup_tab_status(tab_status)
        self.tab_widget.addTab(tab_status, "🖥️ Status System")
        
        # Tab 3: Statistics
        tab_stats = QWidget()
        self.setup_tab_stats(tab_stats)
        self.tab_widget.addTab(tab_stats, "📈 Statistics")
    
    def setup_tab_logs(self, tab):
        layout = QVBoxLayout(tab)
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setMaximumHeight(300)
        
        # Controls
        control_layout = QHBoxLayout()
        btn_clear = QPushButton("🧹 Clear Logs")
        btn_export = QPushButton("💾 Export Logs")
        
        btn_clear.clicked.connect(self.clear_logs)
        btn_export.clicked.connect(self.export_logs)
        
        control_layout.addWidget(btn_clear)
        control_layout.addWidget(btn_export)
        control_layout.addStretch()
        
        layout.addWidget(QLabel("Aktivitas Real-time:"))
        layout.addWidget(self.log_display)
        layout.addLayout(control_layout)
    
    def setup_tab_status(self, tab):
        layout = QVBoxLayout(tab)
        
        # System info
        info_layout = QVBoxLayout()
        
        self.lbl_db_status = QLabel("🔴 Database: Not Connected")
        self.lbl_app_status = QLabel("🟢 Aplikasi: Running")
        self.lbl_memory = QLabel("💾 Memory: Calculating...")
        self.lbl_uptime = QLabel("⏰ Uptime: 00:00:00")
        
        for widget in [self.lbl_db_status, self.lbl_app_status, self.lbl_memory, self.lbl_uptime]:
            widget.setFont(QFont("Arial", 10))
            info_layout.addWidget(widget)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_check = QPushButton("🔄 Check Status")
        btn_optimize = QPushButton("⚡ Optimize Now")
        
        btn_check.clicked.connect(self.check_system_status)
        btn_optimize.clicked.connect(self.optimize_system)
        
        btn_layout.addWidget(btn_check)
        btn_layout.addWidget(btn_optimize)
        
        layout.addLayout(info_layout)
        layout.addLayout(btn_layout)
        layout.addStretch()
    
    def setup_tab_stats(self, tab):
        layout = QVBoxLayout(tab)
        
        # Statistics table
        self.table_stats = QTableWidget()
        self.table_stats.setColumnCount(3)
        self.table_stats.setHorizontalHeaderLabels(["Metric", "Hari Ini", "Bulan Ini"])
        
        layout.addWidget(QLabel("📊 Statistics:"))
        layout.addWidget(self.table_stats)
        self.load_statistics()
    
    def start_monitoring(self):
        """Start monitoring timers"""
        # Timer untuk update logs
        self.log_timer = QTimer()
        self.log_timer.timeout.connect(self.update_logs)
        self.log_timer.start(2000)  # Update setiap 2 detik
        
        # Timer untuk system status
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_system_status)
        self.status_timer.start(5000)  # Update setiap 5 detik
        
        # Timer untuk uptime
        self.start_time = datetime.now()
        self.uptime_timer = QTimer()
        self.uptime_timer.timeout.connect(self.update_uptime)
        self.uptime_timer.start(1000)  # Update setiap 1 detik
    
    def update_logs(self):
        """Update log display with latest entries"""
        try:
            # Read latest log file
            log_file = os.path.join(Config.LOG_DIR, f"activity_{datetime.now().strftime('%Y%m')}.log")
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[-20:]  # Last 20 lines
                    self.log_display.setPlainText(''.join(lines))
                    # Auto-scroll to bottom
                    self.log_display.moveCursor(QTextCursor.MoveOperation.End)
        except Exception as e:
            logger.log_error(f"Error reading logs: {e}")
    
    def update_system_status(self):
        """Update system status information"""
        try:
            # Check database connection
            self.db.cursor.execute("SELECT 1")
            self.lbl_db_status.setText("🟢 Database: Connected")
            
            # Update memory usage (simplified)
            import psutil
            memory = psutil.virtual_memory()
            self.lbl_memory.setText(f"💾 Memory: {memory.percent}% used")
            
        except Exception as e:
            self.lbl_db_status.setText("🔴 Database: Error")
            logger.log_error(f"System status error: {e}")
    
    def update_uptime(self):
        """Update uptime counter"""
        uptime = datetime.now() - self.start_time
        self.lbl_uptime.setText(f"⏰ Uptime: {str(uptime).split('.')[0]}")
    
    def load_statistics(self):
        """Load statistics data"""
        try:
            # Get today's date
            today = datetime.now().date()
            month_start = today.replace(day=1)
            
            # Query statistics
            stats_data = [
                ("Total Absensi", "0", "0"),
                ("Karyawan Aktif", "2", "2"),
                ("Rata-rata Kehadiran", "100%", "100%")
            ]
            
            self.table_stats.setRowCount(len(stats_data))
            for row, (metric, today_val, month_val) in enumerate(stats_data):
                self.table_stats.setItem(row, 0, QTableWidgetItem(metric))
                self.table_stats.setItem(row, 1, QTableWidgetItem(today_val))
                self.table_stats.setItem(row, 2, QTableWidgetItem(month_val))
                
        except Exception as e:
            logger.log_error(f"Error loading statistics: {e}")
    
    def clear_logs(self):
        """Clear log display"""
        self.log_display.clear()
    
    def export_logs(self):
        """Export logs to file"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Logs", 
                f"logs_export_{datetime.now().strftime('%Y%m%d_%H%M')}.txt", 
                "Text Files (*.txt)"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_display.toPlainText())
                QMessageBox.information(self, "Success", "Logs exported successfully!")
                
        except Exception as e:
            logger.log_error(f"Error exporting logs: {e}")
            QMessageBox.warning(self, "Error", "Failed to export logs!")
    
    def check_system_status(self):
        """Manual system status check"""
        self.update_system_status()
        QMessageBox.information(self, "Status Check", "System status updated!")
    
    def optimize_system(self):
        """Optimize system performance"""
        try:
            self.db.cursor.execute("VACUUM")
            self.db.conn.commit()
            logger.log_system("System optimization completed")
            QMessageBox.information(self, "Success", "System optimized successfully!")
        except Exception as e:
            logger.log_error(f"Optimization error: {e}")
            QMessageBox.warning(self, "Error", "Failed to optimize system!")

# Untuk testing
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication([])
    window = MonitorDashboard((1, "Test User", "Admin"))
    window.show()
    app.exec()