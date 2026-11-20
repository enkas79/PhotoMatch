"""Stub autoupdate: verifica le release GitHub di enkas79/PhotoMatch."""

from __future__ import annotations

import json
import urllib.request


def check_github_release(repo: str = "enkas79/PhotoMatch",
                         current: str = "0.2.0") -> dict[str, object]:
    """Interroga le GitHub Releases; restituisce {'update': bool, 'latest': str}.

    Solleva RuntimeError su errori di rete o risposta non valida.
    """
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    request = urllib.request.Request(url, headers={"User-Agent": "PhotoMatch"})
    with urllib.request.urlopen(request, timeout=10) as response:  # noqa: S310
        payload = json.loads(response.read().decode("utf-8"))
    latest = str(payload.get("tag_name", "")).lstrip("v")
    if not latest:
        raise RuntimeError("Risposta GitHub senza tag_name")
    return {
        "update": _version_tuple(latest) > _version_tuple(current),
        "latest": latest,
        "url": payload.get("html_url", ""),
    }


def _version_tuple(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split(".") if part.isdigit())
