"""Benchmark the Skills modal on throttled mobile browser profiles."""

from __future__ import annotations

import argparse
import json
import statistics
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from playwright.sync_api import (  # deptry: ignore[DEP004]
    Browser,
    FloatRect,
    Page,
    sync_playwright,
)


@dataclass(frozen=True)
class MobileProfile:
    name: str
    width: int
    height: int
    device_scale_factor: float
    cpu_rate: int
    latency_ms: int
    download_bytes_per_second: int
    upload_bytes_per_second: int


PROFILES = (
    MobileProfile("android-budget", 360, 800, 2, 6, 150, 200_000, 75_000),
    MobileProfile("android-mid-low", 412, 915, 2, 4, 100, 500_000, 125_000),
    MobileProfile("iphone-se-low-power", 375, 667, 2, 4, 120, 300_000, 100_000),
)

OBSERVER_SCRIPT = """
() => {
  const state = { active: true, frames: [], longTasks: [], layoutShifts: [] };
  window.__soulmapModalBenchmark = state;
  let lastFrame = null;
  const frame = (timestamp) => {
    if (lastFrame !== null) state.frames.push(timestamp - lastFrame);
    lastFrame = timestamp;
    if (state.active) window.requestAnimationFrame(frame);
  };
  window.requestAnimationFrame(frame);
  if (window.PerformanceObserver) {
    try {
      new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          state.longTasks.push({ duration: entry.duration, startTime: entry.startTime });
        }
      }).observe({ type: 'longtask', buffered: true });
    } catch (_) {}
    try {
      new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (!entry.hadRecentInput) {
            state.layoutShifts.push({
              value: entry.value,
              sources: entry.sources.map((source) => ({
                node: source.node?.id || source.node?.className || source.node?.tagName || null,
                previousRect: source.previousRect,
                currentRect: source.currentRect,
              })),
            });
          }
        }
      }).observe({ type: 'layout-shift', buffered: true });
    } catch (_) {}
  }
}
"""

FINISH_OBSERVER_SCRIPT = """
() => {
  const state = window.__soulmapModalBenchmark || { frames: [], longTasks: [], layoutShifts: [] };
  state.active = false;
  const frameIntervals = state.frames.filter((value) => value > 0);
  const droppedFrames = frameIntervals.reduce(
    (total, interval) => total + Math.max(0, Math.floor(interval / 16.67) - 1),
    0,
  );
  return {
    frameCount: frameIntervals.length,
    frameIntervals,
    droppedFrames,
    longTasks: state.longTasks,
    "layoutShift": state.layoutShifts.reduce((total, entry) => total + entry.value, 0),
    "layoutShiftEntries": state.layoutShifts,
  };
}
"""


@dataclass
class CycleResult:
    shell_open_ms: float
    content_loaded_ms: float
    close_unlock_ms: float
    dialog_before_content: FloatRect
    dialog_after_content: FloatRect
    scroll_before: float
    scroll_after: float
    body_padding_right: str
    horizontal_overflow: bool


def _wait_for_search(page: Page) -> None:
    page.wait_for_function(
        "() => document.querySelector('#skill-grid')?.getAttribute('aria-busy') === 'false'"
    )


def _run_profile(
    browser: Browser, origin: str, profile: MobileProfile, cycles: int
) -> dict[str, Any]:
    context = browser.new_context(
        viewport={"width": profile.width, "height": profile.height},
        device_scale_factor=profile.device_scale_factor,
        is_mobile=True,
        has_touch=True,
    )
    page = context.new_page()
    client = context.new_cdp_session(page)
    client.send("Emulation.setCPUThrottlingRate", {"rate": profile.cpu_rate})
    client.send(
        "Network.emulateNetworkConditions",
        {
            "offline": False,
            "latency": profile.latency_ms,
            "downloadThroughput": profile.download_bytes_per_second,
            "uploadThroughput": profile.upload_bytes_per_second,
        },
    )
    page.goto(f"{origin}/skills", wait_until="networkidle")
    page.evaluate("document.documentElement.style.scrollBehavior = 'auto'")
    _wait_for_search(page)
    page.evaluate(
        "window.scrollTo(0, Math.max(1, document.documentElement.scrollHeight / 3))"
    )
    page.wait_for_function("() => window.scrollY > 0")
    page.evaluate(OBSERVER_SCRIPT)
    trigger = page.locator('#skill-grid .skill-card a[aria-haspopup="dialog"]').first
    cycles_result: list[CycleResult] = []

    for _ in range(cycles):
        page.wait_for_timeout(80)
        scroll_before = float(page.evaluate("window.scrollY"))
        started = time.perf_counter()
        trigger.dispatch_event("click")
        page.locator('#skill-modal [role="dialog"]').wait_for(state="visible")
        shell_open_ms = (time.perf_counter() - started) * 1000
        dialog_before_content = page.locator(
            '#skill-modal [role="dialog"]'
        ).bounding_box()
        if dialog_before_content is None:
            raise RuntimeError("modal dialog has no bounding box after open")
        content_started = time.perf_counter()
        page.locator("#skill-modal-content [id^='skill-title-']").wait_for(
            state="visible"
        )
        content_loaded_ms = (time.perf_counter() - content_started) * 1000
        dialog_after_content = page.locator(
            '#skill-modal [role="dialog"]'
        ).bounding_box()
        if dialog_after_content is None:
            raise RuntimeError("modal dialog has no bounding box after content load")
        body_padding_right = str(
            page.evaluate("getComputedStyle(document.body).paddingRight")
        )
        page.wait_for_timeout(260)
        close_started = time.perf_counter()
        page.locator("#skill-modal .modal-close").click()
        page.locator("body").wait_for_function(
            "element => !element.classList.contains('modal-open')"
        )
        close_unlock_ms = (time.perf_counter() - close_started) * 1000
        scroll_after = float(page.evaluate("window.scrollY"))
        horizontal_overflow = bool(
            page.evaluate(
                "document.documentElement.scrollWidth > document.documentElement.clientWidth"
            )
        )
        cycles_result.append(
            CycleResult(
                shell_open_ms=shell_open_ms,
                content_loaded_ms=content_loaded_ms,
                close_unlock_ms=close_unlock_ms,
                dialog_before_content=dialog_before_content,
                dialog_after_content=dialog_after_content,
                scroll_before=scroll_before,
                scroll_after=scroll_after,
                body_padding_right=body_padding_right,
                horizontal_overflow=horizontal_overflow,
            )
        )

    observer = page.evaluate(FINISH_OBSERVER_SCRIPT)
    context.close()
    return {
        "profile": asdict(profile),
        "cycles": [asdict(result) for result in cycles_result],
        "summary": {
            "shell_open_p50_ms": statistics.median(
                r.shell_open_ms for r in cycles_result
            ),
            "shell_open_p95_ms": _percentile(
                [r.shell_open_ms for r in cycles_result], 0.95
            ),
            "content_loaded_p50_ms": statistics.median(
                r.content_loaded_ms for r in cycles_result
            ),
            "close_unlock_p50_ms": statistics.median(
                r.close_unlock_ms for r in cycles_result
            ),
            "max_scroll_error_px": max(
                abs(r.scroll_after - r.scroll_before) for r in cycles_result
            ),
            "horizontal_overflow_cycles": sum(
                r.horizontal_overflow for r in cycles_result
            ),
            "body_padding_values": sorted(
                {r.body_padding_right for r in cycles_result}
            ),
            "frame_count": observer["frameCount"],
            "dropped_frames": observer["droppedFrames"],
            "long_task_count": len(observer["longTasks"]),
            "long_task_max_ms": max(
                (entry["duration"] for entry in observer["longTasks"]), default=0
            ),
            "layout_shift": observer["layoutShift"],
            "layout_shift_entries": observer["layoutShiftEntries"],
        },
    }


def _percentile(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    index = (len(ordered) - 1) * percentile
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = index - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--origin", default="http://127.0.0.1:8765")
    parser.add_argument("--cycles", type=int, default=8)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.cycles < 3:
        raise SystemExit("--cycles must be at least 3")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        results = {
            "origin": args.origin,
            "cycles_per_profile": args.cycles,
            "profiles": [
                _run_profile(browser, args.origin, profile, args.cycles)
                for profile in PROFILES
            ],
        }
        browser.close()
    args.output.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
