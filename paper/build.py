"""Build the manuscript into a self-contained, print-ready HTML file.

Why not LaTeX. Nothing in the LaTeX toolchain is installed on this machine, and neither is
pandoc or quarto. WeasyPrint installs but cannot load its Pango/GObject system libraries, so
a direct PDF write fails. Rather than block the manuscript on a system-level install, this
produces one HTML file with an embedded print stylesheet: open it in a browser and Print to
PDF. Figures are inlined as data URIs, so the output travels as a single file.

If a true PDF pipeline is wanted later, `brew install pango` makes WeasyPrint work and
`write_pdf()` can be re-enabled at the bottom of this file -- that is a deliberate system
change and is left to the author.

    python paper/build.py            # -> paper/build/main.html
    python paper/build.py --open     # and open it
"""

from __future__ import annotations

import argparse
import base64
import mimetypes
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
OUT = PAPER / "build"

CSS = """
@page { size: A4; margin: 22mm 20mm 24mm; @bottom-center { content: counter(page); } }
:root{
  --ink:#14171c; --muted:#5b6572; --rule:#d5dae1; --accent:#2b5f7e; --soft:#f2f5f8;
}
*{box-sizing:border-box}
body{
  font-family:"Charter","Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
  font-size:10.6pt; line-height:1.52; color:var(--ink); background:#fff;
  max-width:44em; margin:0 auto; padding:2.5em 1.5em 4em; hyphens:auto;
}
h1{font-size:20pt;line-height:1.2;margin:0 0 .15em;font-weight:600;text-wrap:balance}
h2{font-size:13pt;margin:2.1em 0 .5em;font-weight:600;border-bottom:1px solid var(--rule);padding-bottom:.25em;page-break-after:avoid}
h3{font-size:11.2pt;margin:1.5em 0 .35em;font-weight:600;page-break-after:avoid}
p{margin:0 0 .75em;text-align:justify}
blockquote{
  margin:1.1em 0; padding:.7em 1.1em; background:var(--soft);
  border-left:3px solid var(--accent); page-break-inside:avoid;
}
blockquote p{margin:0 0 .4em;text-align:left}
blockquote p:last-child{margin:0}
table{border-collapse:collapse;width:100%;margin:1em 0;font-size:9.2pt;page-break-inside:avoid}
th,td{border-bottom:1px solid var(--rule);padding:5px 8px;text-align:left;vertical-align:top}
thead th{border-bottom:1.4px solid var(--ink);font-weight:600;background:var(--soft)}
td:not(:first-child),th:not(:first-child){font-variant-numeric:tabular-nums}
code{font-family:"SF Mono",Menlo,Consolas,monospace;font-size:.86em;background:var(--soft);padding:1px 4px;border-radius:2px}
pre{background:var(--soft);padding:.8em 1em;overflow-x:auto;font-size:8.8pt;border-radius:3px}
pre code{background:none;padding:0}
img{max-width:100%;height:auto;display:block;margin:1.1em auto .4em}
figure{margin:1.4em 0;page-break-inside:avoid}
hr{border:none;border-top:1px solid var(--rule);margin:2em 0}
a{color:var(--accent);text-decoration:none}
em{font-style:italic}
.figcap{font-size:8.8pt;color:var(--muted);text-align:left;margin:.1em 0 1.4em;line-height:1.4}
.figcap strong{color:var(--ink)}
.meta{color:var(--muted);font-size:9.4pt;margin:0 0 1.6em}
@media print{ body{padding:0;max-width:none} a{color:var(--ink)} }
"""


def inline_images(html: str) -> tuple[str, int]:
    """Replace <img src="..."> with data URIs so the file is self-contained."""
    n = 0

    def sub(m: re.Match) -> str:
        nonlocal n
        src = m.group(2)
        path = (PAPER / src).resolve()
        if not path.exists():
            print(f"  WARNING: missing figure {src}", file=sys.stderr)
            return m.group(0)
        mime = mimetypes.guess_type(path.name)[0] or "image/png"
        b64 = base64.b64encode(path.read_bytes()).decode()
        n += 1
        return f'{m.group(1)}src="data:{mime};base64,{b64}"'

    # markdown emits attributes in arbitrary order, so match src wherever it appears
    return re.sub(r'(<img[^>]*?)src="([^"]+)"', sub, html), n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--open", action="store_true", help="open the result when done")
    ap.add_argument("--source", default="main.md")
    args = ap.parse_args()

    try:
        import markdown
    except ImportError:
        print("pip install markdown", file=sys.stderr)
        return 1

    src = PAPER / args.source
    text = src.read_text()

    body = markdown.markdown(
        text, extensions=["tables", "fenced_code", "attr_list", "md_in_html"]
    )
    # figure captions are authored as a bold "**Figure N.**" paragraph after the image
    body = re.sub(
        r"<p>(<strong>Figure \d+\.</strong>.*?)</p>",
        r'<p class="figcap">\1</p>',
        body,
        flags=re.S,
    )
    body, n_img = inline_images(body)

    title = re.search(r"^#\s+(.+)$", text, re.M)
    title = title.group(1) if title else "Manuscript"

    html = (
        "<!doctype html>\n<html lang='en'><head><meta charset='utf-8'>\n"
        f"<title>{title}</title>\n<style>{CSS}</style>\n</head><body>\n{body}\n</body></html>\n"
    )

    OUT.mkdir(exist_ok=True)
    dest = OUT / (pathlib.Path(args.source).stem + ".html")
    dest.write_text(html)

    words = len(re.findall(r"\b\w+\b", re.sub(r"<[^>]+>", " ", body)))
    print(f"  wrote {dest.relative_to(ROOT)}")
    print(f"  {words:,} words · {n_img} figures inlined · {body.count('<table>')} tables")
    print("  open in a browser and Print to PDF (A4, background graphics on)")

    if args.open:
        subprocess.run(["open", str(dest)], check=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
