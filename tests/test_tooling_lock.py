from __future__ import annotations

from multiprocessing import get_context
from pathlib import Path
import time

from tools._run import repo_tooling_lock


def _lock_worker(lock_dir: str, sleep_s: float, queue) -> None:
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

    first_acquired = events[0][1]
    first_released = events[1][1]
    second_acquired = events[2][1]
    second_released = events[3][1]

    assert first_acquired <= first_released <= second_acquired <= second_released
    assert not (tmp_path / ".format-lint.lock").exists()
