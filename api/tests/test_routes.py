import pytest
from fastapi.testclient import TestClient
from gianturl.app import app
from gianturl.encoding import encode
from gianturl.errors import INFINITE_LOOP, URL_TOO_LARGE

client = TestClient(app)


@pytest.fixture(scope="session")
def mock_enlarged():
    yield f"/r/{encode('https://www.eliasfgabriel.com')}"


def test_enlarge_pass():
    resp = client.post("/api?url=https://www.eliasfgabriel.com")
    assert resp.status_code == 200

    res = resp.json()
    assert res["original"] == "https://www.eliasfgabriel.com"
    assert res["improvement"] == 2468
    assert res["enlarged"].startswith("http://testserver/")


def test_enlarge_loop():
    resp = client.post("/api?url=http://testserver/banana")
    assert resp.status_code == 422
    assert resp.json() == {"detail": (INFINITE_LOOP.detail)}


def test_enlarge_toolong():
    resp = client.post(f"/api?url={'a' * 1001}")
    assert resp.status_code == 422
    assert resp.json() == {"detail": URL_TOO_LARGE.detail}


def test_redirect_pass(mock_enlarged):
    with client:
        # NOTE: the testclient cannot handle external redirects, so check
        # the header instead
        # https://github.com/tiangolo/fastapi/issues/790
        resp = client.get(mock_enlarged, allow_redirects=False)
        assert resp.status_code == 301
        assert resp.headers["Location"] == "https://www.eliasfgabriel.com"


def test_redirect_invalid():
    with client:
        resp = client.get("/r/invalidurl")
        assert resp.status_code == 400
        assert resp.json()["detail"].startswith("'invalidurl' is not a valid URL token")
