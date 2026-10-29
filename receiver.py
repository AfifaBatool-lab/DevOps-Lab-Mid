
from flask import Flask, request, jsonify
import json
from pathlib import Path
from datetime import datetime, timezone

app = Flask(__name__)

REPORT_PATH = Path(__file__).resolve().parent / "testreport.json"


@app.route("/report", methods=["POST"])
def receive_report():
    report = request.get_json(silent=True)

    if not isinstance(report, dict):
        return jsonify({"error": "A valid JSON report is required"}), 400

    required_fields = [
        "repository",
        "branch",
        "commit_sha",
        "run_id",
        "execution_timestamp",
        "tests",
        "total",
        "passed",
        "failed",
        "status",
    ]

    missing = [field for field in required_fields if field not in report]

    if missing:
        return jsonify({
            "error": "Missing required fields",
            "fields": missing
        }), 400

    report["received_at"] = datetime.now(timezone.utc).isoformat()

    REPORT_PATH.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8"
    )

    return jsonify({
        "message": "Test report saved successfully",
        "file": str(REPORT_PATH)
    }), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "receiver is running"}), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)
