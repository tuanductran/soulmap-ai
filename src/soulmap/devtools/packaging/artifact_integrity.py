"""Shared archive-member content verification for shipped distribution artifacts.

Both ``scripts/verify_extracted_artifacts.py`` and
``src/soulmap/devtools/packaging/release_verify.py`` must agree on what
"correctly shipped" means. Filename presence alone does not prove that an
archive member's bytes match the repository source file it was built from, so
this module provides the one content-equality check both call, to keep their
behavior from diverging.
"""

from __future__ import annotations

import zipfile
from pathlib import Path


class ArtifactContentError(ValueError):
    """Raised when a shipped archive member's bytes do not match its source file."""


def verify_member_content(
    archive: zipfile.ZipFile, repo_root: Path, member_names: set[str]
) -> None:
    """Verify that every named archive member's bytes match its source file.

    Args:
        archive: Open archive to read shipped member bytes from.
        repo_root: Repository root the members were built from.
        member_names: Archive member names to check, each expected to exist
            as a file at ``repo_root / name``.

    Raises:
        ArtifactContentError: If a member's bytes differ from the source
            file's bytes, or the source file is missing.
    """
    for name in sorted(member_names):
        source_path = repo_root / name
        if not source_path.is_file():
            raise ArtifactContentError(
                f"source file for shipped member is missing: {name}"
            )
        source_bytes = source_path.read_bytes()
        archive_bytes = archive.read(name)
        if archive_bytes != source_bytes:
            raise ArtifactContentError(
                f"content mismatch for shipped member {name}: "
                "archive bytes do not match repository source"
            )
