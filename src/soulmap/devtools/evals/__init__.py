"""Deterministic evaluation runners.

These runners execute the datasets under ``evals/datasets/`` against the
runtime: routing groups, response-generation cases, and cross-file Markdown
contract sync. They are a regression gate, not a response-quality benchmark,
and they never call a language model.
"""
