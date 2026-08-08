"""Library layer: response, Markdown, and resource validation shared by every framework.

Every framework's detector output passes through this package before it is
trusted. New frameworks must not add a framework-specific validator here or
bypass this layer - see docs/engineering/library-vs-framework.md.
"""
