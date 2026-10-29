
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

REPORT_FILE = Path("pytest-report.json")
RECEIVER_URL = "http://127.0.0.1:5001/report"


def main():
    if not REPORT_FILE.exists():
        print(f"ERROR: {REPORT_FILE} was not created.")
        return 1

    with REPORT_FILE.open("r", encoding="utf-8") as file:
        pytest_report = json.load(file)

    summary = pytest_report.get("summary", {})
    test_details = []

    for test in pytest_report.get("tests", []):
        call = test.get("call", {})
        outcome = call.get("outcome", test.get("outcome", "unknown"))
        failure_message = ""

        if outcome == "failed":
            failure_message = (
                call.get("longrepr")
                or test.get("longrepr")
                or "Test failed; no failure message was provided."
            )
            if not isinstance(failure_message, str):
                failure_message = str(failure_message)

        test_details.append({
            "name": test.get("nodeid", "Unknown test"),
            "result": outcome,
            "failure_message": failure_message or None,
        })

    passed = summary.get("passed", 0)
    failed = summary.get("failed", 0)
    total = summary.get("total", len(test_details))

    report = {
        "repository": os.environ.get(
            "GITHUB_REPOSITORY", "local/unknown"
        ),
        "branch": os.environ.get("GITHUB_REF_NAME", "unknown"),
        "commit_sha": os.environ.get("GITHUB_SHA", "unknown"),
        "run_id": os.environ.get("GITHUB_RUN_ID", "local-run"),
        "execution_timestamp": datetime.now(timezone.utc).isoformat(),
        "tests": test_details,
        "total": total,
        "passed": passed,
        "failed": failed,
        "status": "passed" if failed == 0 and passed == total else "failed",
    }

    payload = json.dumps(report).encode("utf-8")
    request = urllib.request.Request(
        RECEIVER_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            print(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError) as error:
        print(f"ERROR: Could not send report to local receiver: {error}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
