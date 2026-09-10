"""Deterministic evaluation runners.

These runners execute the datasets under ``evals/datasets/`` against the
runtime: routing groups, response-generation cases, response-quality fixtures,
and cross-file Markdown contract sync. Safety evaluation remains deterministic
and release-blocking; response-quality evaluation is advisory and never calls
a language model.
"""
