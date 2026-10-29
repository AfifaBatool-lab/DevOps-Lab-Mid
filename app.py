
from flask import Flask, request, redirect, url_for, render_template_string
from urllib.parse import urlparse

app = Flask(__name__)

submissions = []

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>University Assignment Submission Portal</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 30px auto;
            padding: 20px;
            background: #f3f4f6;
        }
        h1, h2 { color: #1e3a8a; }
        form, .submission {
            background: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
        }
        input {
            display: block;
            width: 95%;
            padding: 10px;
            margin: 10px 0 15px;
        }
        button {
            background: #1e40af;
            color: white;
            padding: 10px 20px;
            border: none;
            cursor: pointer;
        }
        .message { color: #b91c1c; }
    </style>
</head>
<body>
    <h1>University Assignment Submission Portal</h1>

    {% if message %}
        <p class="message">{{ message }}</p>
    {% endif %}

    <form method="POST" action="/">
        <label>Student Name</label>
        <input name="student_name" required>

        <label>Registration Number</label>
        <input name="registration_number" required>

        <label>Assignment Title</label>
        <input name="assignment_title" required>

        <label>Submission URL</label>
        <input name="submission_url" type="url" required>

        <button type="submit">Submit Assignment</button>
    </form>

    <h2>Submitted Assignments</h2>

    {% for item in submissions %}
        <div class="submission">
            <p><b>Name:</b> {{ item.student_name }}</p>
            <p><b>Registration Number:</b>
                {{ item.registration_number }}</p>
            <p><b>Assignment:</b> {{ item.assignment_title }}</p>
            <p><b>URL:</b>
                <a href="{{ item.submission_url }}">
                    {{ item.submission_url }}
                </a>
            </p>
        </div>
    {% else %}
        <p>No assignments submitted yet.</p>
    {% endfor %}
</body>
</html>
"""


def valid_url(value):
    try:
        parsed = urlparse(value)
        return (
            parsed.scheme in ("http", "https")
            and bool(parsed.netloc)
            and "." in parsed.netloc
            and " " not in parsed.netloc
        )
    except ValueError:
        return False


@app.route("/", methods=["GET", "POST"])
def home():
    message = ""

    if request.method == "POST":
        student_name = request.form.get("student_name", "").strip()
        registration_number = request.form.get(
            "registration_number", ""
        ).strip()
        assignment_title = request.form.get(
            "assignment_title", ""
        ).strip()
        submission_url = request.form.get(
            "submission_url", ""
        ).strip()

        if not all([
            student_name,
            registration_number,
            assignment_title,
            submission_url
        ]):
            message = "All fields are required."

        elif not valid_url(submission_url):
            message = "Please enter a valid submission URL."

        else:
            submissions.append({
                "student_name": student_name,
                "registration_number": registration_number,
                "assignment_title": assignment_title,
                "submission_url": submission_url
            })
            return redirect(url_for("home"))

    return render_template_string(
        HTML,
        submissions=submissions,
        message=message
    )


if __name__ == "__main__":
    app.run(debug=True)
