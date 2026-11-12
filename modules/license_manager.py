from pathlib import Path
import hashlib
import platform
import uuid

from config import Config


class LicenseManager:
    APP_SECRET = "SAC-2026-LICENSE-SECRET"

    @staticmethod
    def get_machine_id():
        raw_id = f"{platform.node()}-{uuid.getnode()}"
        return hashlib.sha256(raw_id.encode()).hexdigest()[:16].upper()

    @classmethod
    def generate_license_key(cls, machine_id):
        raw = f"{machine_id}-{cls.APP_SECRET}"
        hashed = hashlib.sha256(raw.encode()).hexdigest().upper()

        return (
            f"{hashed[:4]}-"
            f"{hashed[4:8]}-"
            f"{hashed[8:12]}-"
            f"{hashed[12:16]}"
        )

    @classmethod
    def verify_license_key(cls, license_key):
        if not license_key:
            return False

        machine_id = cls.get_machine_id()
        expected_key = cls.generate_license_key(machine_id)

        return license_key.strip().upper() == expected_key

    @staticmethod
    def get_license_file():
        return Path(Config.BASE_DIR) / "license.key"

    @classmethod
    def save_license(cls, license_key):
        license_file = cls.get_license_file()

        license_file.write_text(
            license_key.strip().upper(),
            encoding="utf-8"
        )

    @classmethod
    def load_license(cls):
        license_file = cls.get_license_file()

        if not license_file.exists():
            return None

        return license_file.read_text(
            encoding="utf-8"
        ).strip()

    @classmethod
    def is_activated(cls):
        license_key = cls.load_license()

        if not license_key:
            return False

        return cls.verify_license_key(license_key)