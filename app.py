import os
from datetime import datetime

from flask import Flask, render_template, request, jsonify, url_for, send_file
from werkzeug.exceptions import RequestEntityTooLarge

from config import (
    MAX_CONTENT_LENGTH,
    STATIC_RESULTS_FOLDER,
    DATA_FOLDER,
)

from services.db_service import init_db, insert_case, get_case_by_case_id
from services.file_service import (
    ensure_directories,
    generate_case_id,
    save_uploaded_file,
    create_preview_image,
    FileValidationError,
)
from services.model_service import run_placeholder_model
from services.report_service import generate_report


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH


def initialize_app_storage():
    os.makedirs(DATA_FOLDER, exist_ok=True)
    os.makedirs(STATIC_RESULTS_FOLDER, exist_ok=True)
    ensure_directories()
    init_db()


initialize_app_storage()


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/detect")
def detect():
    return render_template("detect.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/api/detect", methods=["POST"])
def api_detect():
    try:
        uploaded_file = request.files.get("mriFile")

        client_case_id = request.form.get("caseId", "").strip()
        modality = request.form.get("modality", "").strip()
        notes = request.form.get("notes", "").strip()

        case_id = generate_case_id()

        saved_file = save_uploaded_file(uploaded_file, case_id)

        result_case_dir = saved_file["result_case_dir"]

        preview_filename = "original_preview.png"
        result_filename = "anomaly_result.png"
        report_filename = "analysis_report.txt"

        preview_path = os.path.join(result_case_dir, preview_filename)
        result_image_path = os.path.join(result_case_dir, result_filename)
        report_path = os.path.join(result_case_dir, report_filename)

        create_preview_image(
            upload_path=saved_file["upload_path"],
            original_filename=saved_file["original_filename"],
            preview_path=preview_path,
        )

        model_result = run_placeholder_model(
            preview_path=preview_path,
            result_path=result_image_path,
        )

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        case_data = {
            "case_id": case_id,
            "client_case_id": client_case_id,
            "original_filename": saved_file["original_filename"],
            "stored_filename": saved_file["stored_filename"],
            "upload_path": saved_file["upload_path"],
            "preview_path": preview_path,
            "result_image_path": result_image_path,
            "report_path": report_path,
            "modality": modality,
            "notes": notes,
            "score": model_result["score"],
            "status": model_result["status"],
            "created_at": created_at,
        }

        generate_report(report_path, case_data)
        insert_case(case_data)

        response = {
            "success": True,
            "case_id": case_id,
            "client_case_id": client_case_id,
            "status": "completed",
            "score": model_result["score"],
            "score_label": "High anomaly confidence",
            "original_filename": saved_file["original_filename"],
            "modality": modality,
            "created_at": created_at,
            "original_image_url": url_for(
                "static",
                filename=f"results/{case_id}/{preview_filename}"
            ),
            "result_image_url": url_for(
                "static",
                filename=f"results/{case_id}/{result_filename}"
            ),
            "download_original_url": url_for(
                "download_file",
                case_id=case_id,
                file_type="original"
            ),
            "download_result_image_url": url_for(
                "download_file",
                case_id=case_id,
                file_type="image"
            ),
            "download_report_url": url_for(
                "download_file",
                case_id=case_id,
                file_type="report"
            ),
            "analysis": [
                "模型流程已完成，当前结果图展示了异常检测可视化输出。",
                "当前 Abnormality Score 由预留模型接口返回，后续可替换为真实模型推理结果。",
                "本平台仅用于科研与演示，不作为临床诊断依据。"
            ]
        }

        return jsonify(response), 200

    except FileValidationError as error:
        return jsonify(
            {
                "success": False,
                "error": str(error)
            }
        ), 400

    except Exception as error:
        return jsonify(
            {
                "success": False,
                "error": f"Server error: {str(error)}"
            }
        ), 500


@app.route("/download/<case_id>/<file_type>", methods=["GET"])
def download_file(case_id, file_type):
    case_data = get_case_by_case_id(case_id)

    if case_data is None:
        return jsonify(
            {
                "success": False,
                "error": "Case not found."
            }
        ), 404

    if file_type == "original":
        file_path = case_data["upload_path"]
        download_name = case_data["original_filename"]

    elif file_type == "image":
        file_path = case_data["result_image_path"]
        download_name = f"{case_id}_anomaly_result.png"

    elif file_type == "report":
        file_path = case_data["report_path"]
        download_name = f"{case_id}_analysis_report.txt"

    else:
        return jsonify(
            {
                "success": False,
                "error": "Invalid download file type."
            }
        ), 400

    if not file_path or not os.path.exists(file_path):
        return jsonify(
            {
                "success": False,
                "error": "Requested file does not exist."
            }
        ), 404

    return send_file(
        file_path,
        as_attachment=True,
        download_name=download_name
    )


@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(error):
    return jsonify(
        {
            "success": False,
            "error": "Uploaded file is too large."
        }
    ), 413


if __name__ == "__main__":
    app.run(debug=True)