"""Render Results as Markdown (human, default) or JSON (machine) for MCP output.

Base render() reused from mcp-factory; render_passages() added for RAG search
output (a list of cited passages).
"""
from __future__ import annotations

import json
from enum import Enum

from .result import Result


class ResponseFormat(str, Enum):
    """Output format for tool responses."""

    MARKDOWN = "markdown"
    JSON = "json"


def _fmt_value(v: object) -> str:
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, float):
        return f"{v:,.2f}"
    if isinstance(v, int):
        return f"{v:,}"
    if isinstance(v, list):
        return ", ".join(str(x) for x in v[:12]) + (" …" if len(v) > 12 else "")
    return str(v)


def render(result: Result, title: str, fmt: ResponseFormat) -> str:
    """Format a single Result for return to an MCP client."""
    if fmt == ResponseFormat.JSON:
        return json.dumps(result.to_dict(), indent=2, default=str)

    lines = [f"# {title}"]
    if not result.ok:
        lines += ["", f"⚠️ No data available — {result.error}"]
        return "\n".join(lines)
    if result.summary:
        lines += ["", result.summary]
    if result.data:
        passages = result.data.get("passages")
        if passages:
            lines += ["", "## Passages"]
            for p in passages:
                cite = p.get("citation", "?")
                rel = p.get("relevance")
                head = f"**[{cite}]**" + (f"  · relevance {rel:.0%}" if isinstance(rel, (int, float)) else "")
                lines += ["", head, "", p.get("text", "").strip()]
            answer = result.data.get("answer")
            if answer:
                lines = [f"# {title}", "", answer, "", "---", "## Sources"] + [
                    f"- [{p.get('citation','?')}] {p.get('source','?')}" for p in passages
                ]
            return "\n".join(lines)
        for k, v in result.data.items():
            if v is None:
                continue
            lines.append(f"- **{k.replace('_', ' ')}:** {_fmt_value(v)}")
    return "\n".join(lines)
