"""Shared exceptions for GitHub Action operations."""


class GitHubActionError(RuntimeError):
    """Raised when an action operation cannot be completed safely."""


class GitHubAPIError(GitHubActionError):
    """Raised when GitHub returns a non-successful HTTP response."""

    def __init__(
        self,
        method: str,
        url: str,
        status: int,
        detail: str,
        *,
        headers: object | None = None,
    ) -> None:
        """Initialize a structured GitHub API error."""
        self.method = method
        self.url = url
        self.status = status
        self.detail = detail
        self.headers = headers
        super().__init__(
            f"GitHub API {method} {url} failed with HTTP {status}: {detail}"
        )
