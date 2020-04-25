from ipaddress import IPv4Address
from datetime import timedelta
from falcon import testing
import pytest
from time import sleep

from app import create_app


@pytest.fixture(scope="function")
def client():
    return testing.TestClient(
        create_app(limiting_req_n=10, limiting_period=timedelta(seconds=1), ip_mask=IPv4Address("255.255.255.0"),)
    )


def test_requests_are_allowed(client):
    for _ in range(10):
        result = client.simulate_get("/")
        assert result.status_code != 429


def test_blocking_many_requests(client):
    for _ in range(10):
        client.simulate_get("/")
    result = client.simulate_get("/")
    assert result.status_code == 429


def test_unblocking_requests_after_ban(client):
    for _ in range(11):
        client.simulate_get("/")
    sleep(10)
    result = client.simulate_get("/")
    assert result.status_code != 429
