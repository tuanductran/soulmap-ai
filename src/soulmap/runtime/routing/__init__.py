"""Library layer: framework selection and safety-gate routing.

This is the single place that decides which framework's detector runs for a
given request, and the single place responsible for reaching
`_apply_safety_gate` on every return branch. See
docs/engineering/library-vs-framework.md and
docs/engineering/adr/0001-layered-crisis-detection.md.
"""
