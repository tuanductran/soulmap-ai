"""The SoulMap orchestration runtime.

This package routes a message to exactly one framework, enforces the safety
contract, and validates generated response text. It never generates response
content: wording, tone, and doctrine live in the Markdown knowledge base under
``skills/`` and in ``AGENTS.md``.
"""
