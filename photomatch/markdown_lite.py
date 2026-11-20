"""Renderer Markdown minimale (sottoinsieme usato da docs/GUIDA.md): puro, senza Qt."""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path


def guide_path() -> Path:
    """Percorso della guida: bundlata nell'eseguibile PyInstaller o nella repo."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return base / "docs" / "GUIDA.md"


def _inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def render_markdown(markdown: str) -> str:
    """Converte un sottoinsieme di Markdown in HTML (usato solo dalla guida in-app)."""
    out: list[str] = []
    in_list = False
    in_pre = False
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            out.append("</pre>" if in_pre else "<pre>")
            in_pre = not in_pre
            continue
        if in_pre:
            out.append(html.escape(line))
            continue
        if in_list and not stripped.startswith(("- ", "* ")) and not re.match(r"^\d+\. ", stripped):
            out.append("</ul>")
            in_list = False
        if stripped.startswith("#### "):
            out.append(f"<h4>{_inline(stripped[5:])}</h4>")
        elif stripped.startswith("### "):
            out.append(f"<h3>{_inline(stripped[4:])}</h3>")
        elif stripped.startswith("## "):
            out.append(f"<h2>{_inline(stripped[3:])}</h2>")
        elif stripped.startswith("# "):
            out.append(f"<h1>{_inline(stripped[2:])}</h1>")
        elif stripped.startswith(("- ", "* ")):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{_inline(stripped[2:])}</li>")
        elif re.match(r"^\d+\. ", stripped):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{_inline(re.sub(r'^\\d+\\. ', '', stripped))}</li>")
        elif stripped == "---":
            out.append("<hr>")
        elif stripped:
            out.append(f"<p>{_inline(stripped)}</p>")
    if in_list:
        out.append("</ul>")
    if in_pre:
        out.append("</pre>")
    return "<html><body>" + "".join(out) + "</body></html>"
