from __future__ import annotations


def short_error(error: Exception | str, max_len: int = 160) -> str:
    text = str(error).replace("\n", " ").replace("\r", " ").strip()
    text = " ".join(text.split())
    if len(text) > max_len:
        return text[:max_len] + "..."
    return text