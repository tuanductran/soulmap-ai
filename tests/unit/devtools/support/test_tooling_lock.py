from __future__ import annotations

import time
from multiprocessing import get_context
from multiprocessing.queues import Queue
from pathlib import Path

import pytest

from soulmap.devtools.support.run import repo_tooling_lock


def _lock_worker(
    lock_dir: str, sleep_s: float, queue: Queue[tuple[str, float]]
) -> None:
    with repo_tooling_lock(Path(lock_dir)):
        acquired_at = time.monotonic()
        queue.put(("acquired", acquired_at))
        time.sleep(sleep_s)
        queue.put(("released", time.monotonic()))


def test_repo_tooling_lock_serializes_parallel_processes(tmp_path: Path) -> None:
    ctx = get_context("spawn")
    queue = ctx.Queue()

    first = ctx.Process(target=_lock_worker, args=(str(tmp_path), 0.5, queue))
    second = ctx.Process(target=_lock_worker, args=(str(tmp_path), 0.1, queue))

    first.start()
    time.sleep(0.1)
    second.start()

    events: list[tuple[str, float]] = [queue.get(timeout=5) for _ in range(4)]

    first.join(timeout=5)
    second.join(timeout=5)

    assert first.exitcode == 0
    assert second.exitcode == 0

    acquired = sorted(timestamp for event, timestamp in events if event == "acquired")
    released = sorted(timestamp for event, timestamp in events if event == "released")

    assert len(acquired) == 2
    assert len(released) == 2
    assert acquired[0] <= released[0] <= acquired[1] <= released[1]
    assert (tmp_path / ".format-lint.lock").is_file()


def test_repo_tooling_lock_reuses_persistent_lock_file(tmp_path: Path) -> None:
    lock_path = tmp_path / ".format-lint.lock"

    with repo_tooling_lock(tmp_path):
        assert lock_path.is_file()

    first_inode = lock_path.stat().st_ino

    with repo_tooling_lock(tmp_path):
        assert lock_path.is_file()
        assert lock_path.stat().st_ino == first_inode

    assert lock_path.is_file()
