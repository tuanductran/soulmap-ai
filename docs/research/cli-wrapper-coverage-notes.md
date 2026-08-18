# CLI wrapper coverage notes

Research date: 2026-08-18.

Pytest's official monkeypatch guidance recommends `monkeypatch.setattr`, `setenv`, `delenv`, `chdir`, and scoped contexts for safely isolating global settings, subprocess-adjacent behavior, environment variables, and filesystem context. Changes are undone after the test function completes.[1]

Coverage.py branch coverage tracks source-to-destination transitions, so a line can be executed while one of its possible branches remains missing. Missing branches should be covered when they represent meaningful behavior; structurally partial branches should not be forced into artificial tests.[2]

SoulMap baseline on 2026-08-18:

| Surface | Statement/branch result | Interpretation |
| --- | --- | --- |
| `bootstrap_venv.py` | 100% with all 8 branches covered | Existing tests already cover the meaningful paths. |
| `quality/lint.py` | 100% with all 8 branches covered | No new tests needed for the current wrapper task. |
| `quality/format.py` | 71%; lines 35-52 and one branch missing | The Markdown file discovery and subprocess return-code behavior need direct tests. |
| Thin `devtools/cli/*.py` entrypoints | 0% for 8 two-line forwarding modules | Direct execution smoke tests can cover `__main__` forwarding, but adding tests only to improve percentage has low value unless the project wants explicit entrypoint contracts. |

Initial implementation priority is therefore `quality.format` behavior and a small parameterized entrypoint-forwarding contract, not duplicating existing bootstrap/lint coverage.

## References

[1]: https://docs.pytest.org/en/stable/how-to/monkeypatch.html "pytest monkeypatch documentation"
[2]: https://coverage.readthedocs.io/en/7.15.4/branch.html "Coverage.py branch coverage documentation"
