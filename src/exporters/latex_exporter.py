"""LaTeX exporter."""
from pathlib import Path

_LATEX_SPECIAL_CHARS = {
    "\\": r"\textbackslash{}",
    "{": r"\{",
    "}": r"\}",
    "_": r"\_",
    "^": r"\textasciicircum{}",
    "#": r"\#",
    "$": r"\$",
    "%": r"\%",
    "&": r"\&",
    "~": r"\textasciitilde{}",
}


def _escape_latex(text) -> str:
    # Single pass over the original characters -- chaining .replace() calls
    # would re-escape the backslash that \textbackslash{} etc. just inserted.
    return "".join(_LATEX_SPECIAL_CHARS.get(ch, ch) for ch in str(text))


def export_latex(summary, output_path: Path = None) -> Path:
    if output_path is None:
        output_path = summary.experiment_directory / "report.tex"

    rows = ""
    for t in summary.tests:
        status = _escape_latex(t.status.upper())
        name = _escape_latex(t.name.replace("_", " ").title())
        rows += f"{name} & {status} & {t.passed}/{t.total} \\\\\n"

    header = r"""\documentclass{article}
\usepackage{booktabs}
\begin{document}
\section*{NIST STS Results: """ + _escape_latex(summary.generator) + r"""}
\begin{tabular}{lcc}
\toprule
Test & Status & Passed \\
\midrule
"""

    footer = r"""\bottomrule
\end{tabular}
\end{document}
"""

    with open(output_path, "w") as f:
        f.write(header + rows + footer)
    return output_path