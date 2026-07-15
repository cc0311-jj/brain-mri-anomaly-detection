import os


BASE_DIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
STATIC_RESULTS_FOLDER = os.path.join(BASE_DIR, "static", "results")
DATA_FOLDER = os.path.join(BASE_DIR, "data")
DATABASE_PATH = os.path.join(DATA_FOLDER, "cases.db")

MAX_CONTENT_LENGTH = 256 * 1024 * 1024

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "nii",
    "nii.gz",
    "dcm",
    "zip"
}