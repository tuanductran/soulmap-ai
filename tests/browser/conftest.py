from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from collections.abc import Iterator
from urllib.error import URLError
from urllib.request import urlopen

import pytest

_BROWSER_HOST = "127.0.0.1"
_BROWSER_PORT = 8816
_BROWSER_START_TIMEOUT = 20.0


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("soulmap-browser")
    group.addoption(
        "--run-browser",
        action="store_true",
        default=False,
        help="Run opt-in Playwright browser tests.",
    )
    group.addoption(
        "--browser-base-url",
        action="store",
        default=None,
        help="Use an already running website instead of starting the WSGI server.",
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    if config.getoption("--run-browser"):
        return
    skip = pytest.mark.skip(reason="browser tests require --run-browser")
    for item in items:
        if "browser" in item.keywords:
            item.add_marker(skip)


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((_BROWSER_HOST, 0))
        return int(sock.getsockname()[1])


def _server_is_ready(base_url: str) -> bool:
    try:
        with urlopen(f"{base_url}/", timeout=1) as response:
            return response.status == 200
    except (OSError, URLError):
        return False


@pytest.fixture(scope="session")
def browser_origin(
    pytestconfig: pytest.Config,
) -> Iterator[str]:
    configured = pytestconfig.getoption("--browser-base-url") or os.getenv(
        "SOULMAP_BROWSER_BASE_URL"
    )
    if configured:
        yield configured.rstrip("/")
        return

    port = _free_port()
    origin = f"http://{_BROWSER_HOST}:{port}"
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "soulmap.cli",
            "web",
            "--host",
            _BROWSER_HOST,
            "--port",
            str(port),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    deadline = time.monotonic() + _BROWSER_START_TIMEOUT
    try:
        while time.monotonic() < deadline:
            if process.poll() is not None:
                output = process.stdout.read() if process.stdout else ""
                raise RuntimeError(
                    f"SoulMap web server exited with {process.returncode}: {output}"
                )
            if _server_is_ready(origin):
                break
            time.sleep(0.1)
        else:
            output = process.stdout.read() if process.stdout else ""
            raise RuntimeError(f"SoulMap web server did not start: {output}")
        yield origin
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


@pytest.fixture(autouse=True)
def browser_diagnostics(page):
    console_errors: list[str] = []
    page_errors: list[str] = []
    failed_requests: list[str] = []

    page.on(
        "console",
        lambda message: (
            console_errors.append(message.text) if message.type == "error" else None
        ),
    )
    page.on("pageerror", lambda error: page_errors.append(str(error)))

    def record_failed_request(request) -> None:
        failed_requests.append(f"{request.method} {request.url}: {request.failure}")

    page.on("requestfailed", record_failed_request)

    yield {
        "console_errors": console_errors,
        "page_errors": page_errors,
        "failed_requests": failed_requests,
    }

    assert not console_errors, f"browser console errors: {console_errors}"
    assert not page_errors, f"browser page errors: {page_errors}"
    assert not failed_requests, f"browser request failures: {failed_requests}"
