import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--ip", action="store", default="192.168.0.10", help="ip address of the DMD"
    )

@pytest.fixture
def luxbeam_ip(request):
    return request.config.getoption("--ip")