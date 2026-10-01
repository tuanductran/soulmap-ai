from __future__ import annotations

import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import urllib.request


def main() -> int:
    version, expected_sha256, config_file = _arguments()
    root = Path(os.environ.get("GITHUB_WORKSPACE", Path.cwd()))
    cache_dir = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "soulmap-actionlint"
    cache_dir.mkdir(parents=True, exist_ok=True)
    archive = cache_dir / f"actionlint_{version}_linux_amd64.tar.gz"
    binary = cache_dir / "actionlint"

    if not binary.exists():
        url = (
            "https://github.com/rhysd/actionlint/releases/download/"
            f"v{version}/actionlint_{version}_linux_amd64.tar.gz"
        )
        urllib.request.urlretrieve(url, archive)
        _verify_sha256(archive, expected_sha256)
        with tarfile.open(archive, "r:gz") as bundle:
            member = next(
                (item for item in bundle.getmembers() if item.name.endswith("/actionlint")),
                None,
            )
            if member is None:
                raise RuntimeError("actionlint binary was not found in release archive")
            extracted = bundle.extractfile(member)
            if extracted is None:
                raise RuntimeError("failed to read actionlint binary")
            binary.write_bytes(extracted.read())
        binary.chmod(0o755)

    return subprocess.run(
        [str(binary), "-config-file", str(root / config_file)],
        cwd=root,
        check=False,
    ).returncode


def _arguments() -> tuple[str, str, str]:
    values = sys.argv[1:]
    return (
        values[0] if values else "1.7.12",
        values[1]
        if len(values) > 1
        else "8aca8db96f1b94770f1b0d72b6dddcb1ebb8123cb3712530b08cc387b349a3d8",
        values[2] if len(values) > 2 else ".github/actionlint.yaml",
    )


def _verify_sha256(path: Path, expected: str) -> None:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != expected:
        path.unlink(missing_ok=True)
        raise RuntimeError(
            f"actionlint archive SHA-256 mismatch: expected {expected}, got {digest}"
        )


if __name__ == "__main__":
    raise SystemExit(main())
