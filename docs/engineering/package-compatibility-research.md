# Python 3.11 package compatibility research

**Research date:** 2026-08-19

This note records official package evidence for the development toolchain used by SoulMap AI. It is a maintenance aid, not a promise to support every future package release or every Python patch release.

## Official compatibility findings

| Package | Locked version on v0.9.0 | Official source | Relevant finding for SoulMap |
| --- | --- | --- | --- |
| Ruff | 0.16.3 | [Ruff documentation](https://docs.astral.sh/ruff/) | Current docs advertise Python 3.14 compatibility, `pyproject.toml` support, caching and active development. Python 3.11 is below the documented compatibility ceiling; upgrades still require repository CI evidence. |
| pytest | 9.1.1 | [pytest compatibility policy](https://docs.pytest.org/en/stable/backwards-compatibility.html) | pytest 9.0+ supports Python 3.10+, so Python 3.11 is supported. Its deprecation policy makes warnings an upgrade signal rather than something to ignore silently. |
| Hypothesis | 6.165.9 | [Hypothesis compatibility](https://hypothesis.readthedocs.io/en/latest/compatibility.html) | Hypothesis supports and tests CPython/PyPy 3.10+. It officially supports only the latest patch release of each supported Python version; documented APIs generally do not break except at major versions. |
| PyMarkdownLnt | 0.9.39 | [PyPI project metadata](https://pypi.org/project/pymarkdownlnt/) | Requires Python >=3.10 and classifies Python 3.10 through 3.13. Python 3.11 is a declared supported interpreter, matching the Markdown contract role. |
| pytest-cov | 7.1.0 | [PyPI project metadata](https://pypi.org/project/pytest-cov/) | Requires Python >=3.9 and classifies Python 3.9 through 3.14. It supports coverage contexts and xdist integration; coverage data must remain reproducible under parallel workers. |
| pytest-xdist | 3.8.0 | [pytest-xdist documentation](https://pytest-xdist.readthedocs.io/en/latest/) | `pytest -n auto` starts workers based on available CPUs and distributes tests randomly. Test order/count must remain consistent; a serial diagnostic path is still required for failures. |
| pytest-timeout | 2.4.0 | [PyPI project metadata](https://pypi.org/project/pytest-timeout/) | Requires Python >=3.10 and classifies Python 3.10 through 3.14. It is for catching hangs/deadlocks, not precise timing or performance measurement. |
| pytest-randomly | 4.1.0 | [pytest-randomly project metadata](https://pypi.org/project/pytest-randomly/) | Upstream states Python 3.10 through 3.15 support. It randomizes test order and controls `random.seed`; failures must preserve the seed and support an explicit serial rerun. |
| Pyright | 1.1.411 | [Pyright project metadata](https://pypi.org/project/pyright/) | Pyright is a standards-compliant static type checker with CLI and editor integration. Its configured Python target and CI invocation are the source of truth for type semantics. |
| Commitizen | 4.17.0 | [Commitizen project metadata](https://pypi.org/project/commitizen/) | Requires Python 3.10+. `cz bump` changes version, creates a tag and can update the changelog, so release validation must run before the mutation steps. |
| Deptry | 0.25.1 | [Deptry documentation](https://deptry.com/) | Scans imports against dependency declarations and explicitly supports uv and PEP 621. It must run inside the project's dedicated virtual environment. |
| Vulture | 2.16 | [PyPI project metadata](https://pypi.org/project/vulture/) | Requires Python >=3.9 and classifies Python 3.9 through 3.14 for CPython/PyPy. Its findings remain subject to the repository confidence threshold and human review. |
| Hatchling | transitive build backend | [Hatch documentation](https://hatch.pypa.io/latest/) | Hatch documents reproducible builds, uv-supported environments and PEP 517 build workflows. SoulMap's explicit ZIP/skill builders remain the product artifact source. |
| lefthook | 2.1.10 | [lefthook documentation](https://lefthook.dev/) | lefthook is a Git hooks manager, not a Python runtime package. Python 3.11 compatibility does not apply to the binary; the relevant contract is that hooks invoke `uv run` commands consistently. |
| uv | 0.12.5 (CI installer pin) | [uv installer documentation](https://docs.astral.sh/uv/reference/installer/) | CI installs uv through the official unmanaged standalone installer into the ephemeral runner. It is a toolchain executable, not a SoulMap runtime or locked project dependency. |
| actionlint | 1.7.12 (CI binary pin) | [actionlint installation documentation](https://github.com/rhysd/actionlint/blob/main/docs/install.md) | CI downloads the Linux amd64 release archive from the official release URL and verifies a repository-pinned SHA-256 before checking workflows. It replaces a third-party action archive dependency and is CI-only. |

## Locked baseline and support policy

The v0.9.0 lock baseline uses Python `>=3.11` in `pyproject.toml` and CI installs Python 3.11. The sandbox used during this research runs Python 3.12.3, so local success is not a substitute for the CI Python 3.11 evidence.

As of 2026-08-19, the latest official Python 3.11 source release is **Python 3.11.16**, released on 2026-08-12. Python.org classifies it as a security bugfix release for the legacy 3.11 series. The repository records this patch as the current CI review baseline without expanding the Python support floor or claiming that local Python 3.12 success substitutes for CI evidence. The release notes include security fixes affecting areas such as `ssl`, `webbrowser`, archive extraction, `ftplib`, `io.open_code`, HTTP handling, and XML parsing; future lockfile refresh reviews should check the same official release notes and the project's transitive package advisories. [15]

The repository should retain a support floor of Python 3.11, test the latest available 3.11 patch release in CI, and treat the lockfile as the exact dependency set for release. Package upgrades should be grouped by purpose, reviewed against the official compatibility source, and merged only after the full repository validation passes.

## Reproducibility policy

Because pytest-xdist and pytest-randomly intentionally introduce process and order variation, a failed run should preserve the pytest-randomly seed, worker count, operating system, Python version, and package lock state. The first diagnostic rerun should use the same seed and then a serial command such as `uv run pytest -n 0`; no test should be disabled merely to hide order dependence.

`pytest-timeout` failures indicate a hang or deadlock investigation, not a performance regression. Coverage changes should be compared using the same worker mode and coverage configuration. Vulture findings should remain at the configured confidence threshold and require manual classification before deletion.

## Upgrade and security response

Dependency updates should be handled through the existing Dependabot/Renovate dashboard and `uv.lock` refresh process. The operational sequence, evidence fields and release boundary are defined in [`docs/operations/dependency-refresh.md`](../operations/dependency-refresh.md). A package security advisory or incompatible release should trigger a focused branch, an explicit compatibility note, full local validation, and CI evidence on Python 3.11 before release. Do not replace packages or add a security scanner solely because it is available; add a new tool only when it protects a specific repository
 contract or resolves a documented blocker.

This document does not introduce a new runtime dependency, package migration, Python-version expansion, platform adapter, or semantic safety layer.

## References

[1]: https://docs.astral.sh/ruff/ "Ruff documentation"
[2]: https://docs.pytest.org/en/stable/backwards-compatibility.html "pytest backwards compatibility policy"
[3]: https://hypothesis.readthedocs.io/en/latest/compatibility.html "Hypothesis compatibility"
[4]: https://pypi.org/project/pymarkdownlnt/ "PyMarkdownLnt on PyPI"
[5]: https://pypi.org/project/pytest-cov/ "pytest-cov on PyPI"
[6]: https://pytest-xdist.readthedocs.io/en/latest/ "pytest-xdist documentation"
[7]: https://pypi.org/project/pytest-timeout/ "pytest-timeout on PyPI"
[8]: https://pypi.org/project/pytest-randomly/ "pytest-randomly on PyPI"
[9]: https://pypi.org/project/pyright/ "Pyright on PyPI"
[10]: https://pypi.org/project/commitizen/ "Commitizen on PyPI"
[11]: https://deptry.com/ "Deptry documentation"
[12]: https://pypi.org/project/vulture/ "Vulture on PyPI"
[13]: https://hatch.pypa.io/latest/ "Hatch documentation"
[14]: https://lefthook.dev/ "lefthook documentation"
[15]: https://www.python.org/downloads/release/python-31116/ "Python 3.11.16 release notes"
[16]: https://docs.astral.sh/uv/reference/installer/ "uv installer options"
[17]: https://github.com/rhysd/actionlint/blob/main/docs/install.md "actionlint installation documentation"
