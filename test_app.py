
import pytest
from app import app, submissions


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client

    submissions.clear()


def test_valid_submission(client):
    response = client.post("/", data={
        "student_name": "Afifa Batool",
        "registration_number": "SP23-BCS-OO2",
        "assignment_title": "DevOps Lab Mid",
        "submission_url": "https://github.com/"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Afifa Batool" in response.data
    assert b"DevOps Lab Mid" in response.data
    assert len(submissions) == 1


def test_missing_registration_number(client):
    response = client.post("/", data={
        "student_name": "Afifa Batool",
        "registration_number": "",
        "assignment_title": "DevOps Lab Mid",
        "submission_url": "https://github.com/"
    })

    assert response.status_code == 200
    assert b"All fields are required." in response.data
    assert len(submissions) == 0


def test_invalid_submission_url(client):
    response = client.post("/", data={
        "student_name": "Afifa Batool",
        "registration_number": "SP23-BCS-OO2",
        "assignment_title": "DevOps Lab Mid",
        "submission_url": "not-a-valid-url"
    })

    assert response.status_code == 200
    assert b"Please enter a valid submission URL." in response.data
    assert len(submissions) == 0