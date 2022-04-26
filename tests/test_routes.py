import pytest
from fastapi.testclient import TestClient
from gianturl.app import app

client = TestClient(app)


@pytest.fixture(scope="session")
def mock_enlarged():
    # https://www.eliasfgabriel.com over 7 rounds
    yield (
        "/V1ZWb1UwMUhUa2xVVkZwTlpWUnJlbHBFVG1wa1ZuQllaVWhDV2xkRk5YUlhha3BIWVZkT2RHSkhlR"
        "2xSZWxaeFdXcEpkMUJSUFQwPQ==?r=4"
    )


def test_enlarge_pass():
    resp = client.get("/api?url=https://www.eliasfgabriel.com")
    assert resp.status_code == 200

    res = resp.json()
    assert res["original"] == "https://www.eliasfgabriel.com"
    assert res["improvement"] == "3762.07%"
    assert res["enlarged"].startswith("http://testserver/")
    assert res["enlarged"].endswith("?r=12")


def test_enlarge_loop():
    resp = client.get("/api?url=http://testserver/banana")
    assert resp.status_code == 422
    assert resp.json() == {
        "detail": "There's a possibility for infinite loops, where there be dragons"
    }


def test_enlarge_toolong():
    resp = client.get(f"/api?url={'a' * 1001}")
    assert resp.status_code == 422
    assert resp.json() == {
        "detail": "Enlarging the provided URL would exceed the maximum URL length"
        " for browser compatability. Sorry!"
    }


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
        resp = client.get("/invalidurl")
        assert resp.status_code == 400
        assert resp.json() == {"detail": "Bad Request"}

        resp = client.get("/invalidurl?r=1")
        assert resp.status_code == 400
        assert resp.json() == {"detail": "Bad Request"}
