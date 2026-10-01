# SoulMap actionlint action monorepo

This directory contains independently usable implementations of the same actionlint capability.

- `python/`: Python implementation packaged as a Docker container action.
- `docker/`: minimal Docker implementation without a Python runtime.

GitHub custom actions support JavaScript, Docker container, and composite runtimes; there is no native `runs.using: python` runtime. Therefore the Python implementation is intentionally packaged as a Docker action. citeturn1search7turn1search1

Both variants pin actionlint 1.7.12 and verify the official Linux amd64 release SHA-256 before execution. The upstream actionlint project documents released binaries and Docker usage. citeturn0search0turn0search1
