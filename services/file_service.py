import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image, ImageDraw, ImageFont

from config import UPLOAD_FOLDER, STATIC_RESULTS_FOLDER, ALLOWED_EXTENSIONS


class FileValidationError(Exception):
    pass


def ensure_directories():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(STATIC_RESULTS_FOLDER, exist_ok=True)


def get_file_extension(filename):
    filename = filename.lower()

    if filename.endswith(".nii.gz"):
        return "nii.gz"

    if "." not in filename:
        return ""

    return filename.rsplit(".", 1)[1]


def is_allowed_file(filename):
    extension = get_file_extension(filename)
    return extension in ALLOWED_EXTENSIONS


def generate_case_id():
    time_part = datetime.now().strftime("%Y%m%d-%H%M%S")
    random_part = uuid.uuid4().hex[:6].upper()
    return f"CASE-{time_part}-{random_part}"


def create_case_folders(case_id):
    upload_case_dir = os.path.join(UPLOAD_FOLDER, case_id)
    result_case_dir = os.path.join(STATIC_RESULTS_FOLDER, case_id)

    os.makedirs(upload_case_dir, exist_ok=True)
    os.makedirs(result_case_dir, exist_ok=True)

    return upload_case_dir, result_case_dir


def save_uploaded_file(file, case_id):
    if file is None:
        raise FileValidationError("No file part was found in the request.")

    if file.filename == "":
        raise FileValidationError("No file was selected.")

    if not is_allowed_file(file.filename):
        raise FileValidationError(
            "Unsupported file type. Please upload png, jpg, jpeg, nii, nii.gz, dcm, or zip."
        )

    upload_case_dir, result_case_dir = create_case_folders(case_id)

    original_filename = secure_filename(file.filename)
    extension = get_file_extension(original_filename)

    stored_filename = f"input.{extension}"
    upload_path = os.path.join(upload_case_dir, stored_filename)

    file.save(upload_path)

    return {
        "original_filename": original_filename,
        "stored_filename": stored_filename,
        "upload_path": upload_path,
        "upload_case_dir": upload_case_dir,
        "result_case_dir": result_case_dir,
    }


def is_regular_image(filename):
    extension = get_file_extension(filename)
    return extension in {"png", "jpg", "jpeg"}


def get_default_font(size=28):
    try:
        return ImageFont.truetype("Arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


def create_placeholder_preview(original_filename, preview_path):
    width = 1024
    height = 1024

    image = Image.new("RGB", (width, height), "#FFFFFF")
    draw = ImageDraw.Draw(image)

    draw.ellipse(
        (262, 202, 762, 702),
        outline="#4198AC",
        width=18
    )

    draw.ellipse(
        (362, 302, 662, 602),
        outline="#7BC0CD",
        width=12
    )

    title_font = get_default_font(34)
    small_font = get_default_font(22)

    draw.text(
        (width / 2, 760),
        "MRI File Uploaded",
        fill="#4198AC",
        font=title_font,
        anchor="mm"
    )

    draw.text(
        (width / 2, 815),
        original_filename,
        fill="#51999F",
        font=small_font,
        anchor="mm"
    )

    draw.text(
        (width / 2, 870),
        "Preview will be generated after medical image preprocessing.",
        fill="#51999F",
        font=small_font,
        anchor="mm"
    )

    image.save(preview_path)


def create_preview_image(upload_path, original_filename, preview_path):
    if is_regular_image(original_filename):
        try:
            image = Image.open(upload_path)
            image = image.convert("RGB")

            image.thumbnail((1200, 1200))

            canvas = Image.new("RGB", (1200, 1200), "#FFFFFF")
            x = (1200 - image.width) // 2
            y = (1200 - image.height) // 2
            canvas.paste(image, (x, y))

            canvas.save(preview_path)
            return preview_path

        except Exception:
            create_placeholder_preview(original_filename, preview_path)
            return preview_path

    create_placeholder_preview(original_filename, preview_path)
    return preview_path