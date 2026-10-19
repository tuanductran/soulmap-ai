"""Shared constants for the dependency-free GitHub Action."""

API_ROOT = "https://api.github.com"
API_VERSION = "2026-03-10"
VERIFY_API_VERSION = "2022-11-28"
USER_AGENT = "soulmap-github-action"
MAX_RETRIES = 4
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
IDEMPOTENT_METHODS = {"DELETE", "GET", "HEAD", "PATCH", "PUT"}
