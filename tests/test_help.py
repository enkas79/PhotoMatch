"""Test del renderer della guida in-app (puro, senza Qt)."""

from photomatch.markdown_lite import guide_path, render_markdown


def test_render_markdown_subset():
    html = render_markdown("# Titolo\n\n- punto **grassetto**\n- altro `codice`\n\n1. primo\n2. secondo\n\n[link](https://example.com)\n\n---\n\n```\nblocco\n```\n")
    assert "<h1>Titolo</h1>" in html
    assert "<b>grassetto</b>" in html
    assert "<code>codice</code>" in html
    assert html.count("<li>") == 4
    assert '<a href="https://example.com">link</a>' in html
    assert "<hr>" in html
    assert "<pre>" in html and "blocco" in html


def test_guide_file_exists():
    assert guide_path().is_file()
    text = guide_path().read_text(encoding="utf-8")
    assert text.startswith("# Guida a PhotoMatch")
