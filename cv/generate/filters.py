"""LaTeX text filters for the CV Jinja2 templates.

Escaping order matters: markdown links must be parsed out of the raw string
*before* any escaping happens, and only the surrounding plain text / the
link's display label get escaped - never the URL. Hyperref's `\\href` reads
its first argument in URL-scanning mode, so a raw URL (including `%`, `_`,
`&`, etc.) is passed through untouched; escaping it would literally break
the link (e.g. turning `_` into the two characters `\\_`, which is not a
valid URL byte).
"""
import re

_LATEX_SPECIAL_CHARS = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}

_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def latex_escape(value):
    """Escape LaTeX special characters in plain text. Never apply this to
    a URL that will be passed to \\href/\\url."""
    if value is None:
        return ""
    return "".join(_LATEX_SPECIAL_CHARS.get(ch, ch) for ch in str(value))


def markdown_and_escape(value):
    """Convert `[label](url)` markdown links to `\\href{url}{label}` and
    LaTeX-escape everything else (including the label), leaving URLs raw."""
    if value is None:
        return ""
    text = str(value)
    out = []
    pos = 0
    for m in _MD_LINK_RE.finditer(text):
        out.append(latex_escape(text[pos : m.start()]))
        label, url = m.group(1), m.group(2)
        out.append(r"\href{%s}{%s}" % (url, latex_escape(label)))
        pos = m.end()
    out.append(latex_escape(text[pos:]))
    return "".join(out)
