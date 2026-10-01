"""Verify the extracted shape and content boundary of SoulMap distribution artifacts."""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt

from soulmap.devtools.packaging.members import (
    CORE_FILES,
    PLUGIN_PREFIX,
    RUNTIME_PREFIX,
    source_members,
)
from soulmap.devtools.packaging.artifact_integrity import (
    ArtifactContentError,
    verify_member_content,
)


class ExtractedArtifactError(ValueError):
    """Raised when an archive violates the shipped package contract."""



