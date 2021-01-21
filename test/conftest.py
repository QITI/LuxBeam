import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--ip", action="store", default="192.168.0.10", help="ip address of the DMD",
    )
    parser.addoption(
        "--interactive", action="store_true", default=False, help="run interactive test"
    )

@pytest.fixture
def luxbeam_ip(request):
    return request.config.getoption("--ip")


def pytest_configure(config):
    config.addinivalue_line("markers", "interactive: mark test that is interactive.")

def pytest_collection_modifyitems(config, items):
    if config.getoption("--interactive"):
        return
    skip_interactive = pytest.mark.skip(reason="need --interactive option to run")
    for item in items:
        if "interactive" in item.keywords:
            item.add_marker(skip_interactive)