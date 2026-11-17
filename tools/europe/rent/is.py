"""Iceland: no rows yet.

The only good source is HMS's rent register (leiguskrá, hms.is), which sits behind a Vercel JavaScript challenge that plain
fetches cannot pass (HTTP 429), and the Wayback Machine was offline when tried. Statistics Iceland publishes rent indices
only. See .agent/research/europe/is.md. Import with importlib: `is` is a Python keyword.
"""

SOURCES: list[dict] = []


def rows() -> list[dict]:
    return []
