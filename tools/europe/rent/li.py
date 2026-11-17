"""Liechtenstein: no rent source reachable, so no rows.

The Amt fuer Statistik (statistikportal.li, llv.li) sits behind a Cloudflare bot challenge that answers every plain
fetch with 403, and opendata.li lists no rent dataset. The BFS tables used for Switzerland do not cover Liechtenstein.
See .agent/research/europe/li.md for what was tried and the options.
"""

SOURCES = []


def rows():
    return []
