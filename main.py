import sys
import traceback
from pathlib import Path


def main():
    try:
        # Add current directory to Python path
        current_dir = Path(__file__).parent
        sys.path.append(str(current_dir))

        # Setup environment first
        from config import Config
        Config.setup_directories()

        from PyQt6.QtWidgets import QApplication
        from views.login_ui import LoginWindow
        from views.license_ui import LicenseWindow
        from modules.license_manager import LicenseManager

        app = QApplication(sys.argv)
        app.setApplicationName("Sistem Absensi Cafe")

        # Check application license
        if not LicenseManager.is_activated():
            license_window = LicenseWindow()

            if license_window.exec() != LicenseWindow.DialogCode.Accepted:
                return 0

        # Open login window after activation
        window = LoginWindow()
        window.show()

        sys.exit(app.exec())

    except Exception as e:
        print("❌ CRITICAL ERROR:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\n📋 Full traceback:")
        traceback.print_exc()
        input("\nPress Enter to exit...")
        return 1


if __name__ == "__main__":
    sys.exit(main())