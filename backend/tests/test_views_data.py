from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_score_file_rejects_oversized_upload(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("scoring must not run for an oversized upload")

    monkeypatch.setattr("api.views.data.MAX_UPLOAD_BYTES", 64)
    monkeypatch.setattr("api.views.data.concat_scores", fail)

    response = client.post(
        "/data/score",
        files={"file": ("data.csv", b"a" * 66, "text/csv")},
    )

    assert response.status_code == 413
    assert "too large" in response.json()["detail"]


def test_score_file_rejects_too_many_rows(monkeypatch):
    monkeypatch.setattr("api.views.data.MAX_ROWS", 2)
    content = "time,field,value,score\n" + "\n".join(
        "2024-01-10T10:00:00,co2,500,100" for _ in range(3)
    )

    response = client.post(
        "/data/score",
        files={"file": ("data.csv", content.encode(), "text/csv")},
    )

    assert response.status_code == 413
    assert "too many rows" in response.json()["detail"]
