from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    SECRET_KEY = "change-this-secret-key-for-local-development"
    DEBUG = True

    # Render deployment settings
    HOST = "0.0.0.0"
    PORT = int(os.environ.get("PORT", 5000))

    DATA_DIR = BASE_DIR / "data"
    UPLOAD_FOLDER = DATA_DIR / "uploads"
    PROCESSED_FOLDER = DATA_DIR / "processed"
    EXPORT_FOLDER = DATA_DIR / "exports"
    MODEL_FOLDER = BASE_DIR / "models" / "saved_models"

    ALLOWED_EXTENSIONS = {"xlsx", "json"}
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024
    RANDOM_STATE = 42

    JSON_SORT_KEYS = False


PROJECT_DIRECTORIES = [
    Config.UPLOAD_FOLDER,
    Config.PROCESSED_FOLDER,
    Config.EXPORT_FOLDER,
    Config.MODEL_FOLDER,
]


def ensure_project_directories():
    for directory in PROJECT_DIRECTORIES:
        directory.mkdir(parents=True, exist_ok=True)