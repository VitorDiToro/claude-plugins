#!/usr/bin/env python3
# float_check.py
#
# Objective-signal script for the "Floats: consistência e legendas" checklist
# rule of the academic-report reviewer. It performs mechanical / low-cost
# checks over \includegraphics targets, figure/table environments, and
# tabular row counts -- never judging whether a figure or table is content-
# appropriate, well-chosen, or correctly captioned in SUBSTANCE. That is the
# reviewing pass's job; this script only surfaces LOCATED CANDIDATES, never
# verdicts (parity with every other Fase-0 script).
#
# Checks emitted:
#   1. \includegraphics{p} whose target image file cannot be found on disk.
#      `p` is resolved ONLY relative to the project ROOT (never relative to
#      the including .tex sub-file's own directory -- see _base_dirs for
#      why), trying the common image subfolders figures/, fig/, images/,
#      img/ under the root, and -- when `p` has no recognised image
#      extension -- appending each of .png/.pdf/.jpg/.jpeg/.eps. An empty
#      argument (\includegraphics{}) is itself a broken reference and is
#      flagged directly, never silently skipped.
#   2. The SAME \includegraphics argument used in 2+ places (candidate for
#      unintentional figure reuse / copy-paste).
#   3. A figure/figure*/table/table* environment missing \caption OR \label.
#   4. A tabular/tabular*/tabularx environment with more than ROW_THRESHOLD
#      \\ row-breaks -- a candidate for converting to longtable. longtable
#      itself is never flagged (suggesting longtable FOR a longtable would
#      be circular).
#   5. \hline and booktabs (\toprule/\midrule/\bottomrule) both used
#      somewhere in the project -- a candidate for standardising on one
#      table-rule style.
#
# Everything here is a SIGNAL, never a verdict: image existence is a
# filesystem check that must never raise on a weird/malformed path -- an
# unresolvable path is simply reported as "missing", nothing more.
#
# stdlib only, cross-platform, UTF-8 pinned. Reuses latex_corpus for
# manifest-scoped discovery, reading, comment stripping, and anchoring (the
# ONLY way a location string is built here). Code/comments English; output
# Portuguese. Invoke: python3 float_check.py <dir>

import os
import re
import sys

import latex_corpus


# --- tunables ----------------------------------------------------------------

# Row-break threshold above which a tabular is flagged as a longtable
# candidate. 30 rows is roughly a full printed page for a typical
# single-column ABNT/Inatel body table -- comfortably past that and the
# table is very likely to overflow or force an awkward page break, which
# longtable handles by splitting across pages. A constant, not a magic
# number, so a future calibration pass has one place to tune it.
ROW_THRESHOLD = 30

# Recognised image extensions; used both to decide whether `p` in
# \includegraphics{p} already carries an extension, and as the set appended
# when it doesn't (mirrors the extensions pdflatex itself tries).
_IMAGE_EXTS = (".png", ".pdf", ".jpg", ".jpeg", ".eps")

# Common image subfolders tried under the project root, per the checklist
# (figures/, fig/) plus two more common conventions (images/, img/).
_IMAGE_SUBDIRS = ("figures", "fig", "images", "img")

_FLOAT_ENV_NAMES = ("figure", "figure*", "table", "table*")
_TABULAR_ENV_NAMES = ("tabular", "tabular*", "tabularx")


# --- regexes -----------------------------------------------------------------

_INCLUDEGRAPHICS_RE = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}")
_HLINE_RE = re.compile(r"\\hline\b")
_BOOKTABS_RE = re.compile(r"\\(?:top|mid|bottom)rule\b")

# Stack-driving tokenizer: ONLY recognises \begin/\end for float and
# tabular-like environments -- anything else (itemize, equation, document,
# longtable, ...) is deliberately invisible to this regex, so it never
# perturbs the stack. This also means a \caption or \label sitting inside
# some OTHER environment nested in a figure still correctly marks the
# enclosing figure/table frame (it's simply not pushed/popped itself).
#
# The \caption alternative REQUIRES the opening brace ("\{") right after the
# optional "*" and an optional "[short]" argument, so it matches
# \caption{...}, \caption*{...}, and \caption[short]{...} (the standard
# short-caption form used when the List-of-Figures entry should differ from
# the full caption) -- but NOT \captionsetup{...} (the caption package's
# styling command, very common in ABNT templates) or \captionof{...}{...}
# (the caption package's out-of-float variant), since neither has a brace
# (optionally preceded by a "[...]" group) directly after "\caption"/
# "\caption*". Without this anchor, \captionsetup{...} would be mistaken for
# a real caption and silently suppress the "missing \caption" finding.
_ENV_EVENT_RE = re.compile(
    r"\\begin\{(?P<begin>figure\*?|table\*?|tabular\*?|tabularx)\}"
    r"|\\end\{(?P<end>figure\*?|table\*?|tabular\*?|tabularx)\}"
    r"|\\caption\*?(?:\[[^\]]*\])?\{"
    r"|\\label\{[^}]*\}"
    r"|\\\\"
)


# --- image resolution ---------------------------------------------------------

def _candidate_names(arg):
    """Filenames to test for `arg`: itself, plus -- when it has no
    recognised image extension -- itself with each common extension
    appended (mirrors pdflatex's own extension search when none is given)."""
    ext = os.path.splitext(arg)[1].lower()
    if ext in _IMAGE_EXTS:
        return [arg]
    return [arg] + [arg + e for e in _IMAGE_EXTS]


def _base_dirs(root):
    """Base directories to resolve an image path against: the project ROOT
    and its common image subfolders ONLY -- deliberately NOT each including
    .tex sub-file's own directory. Standard pdflatex/xelatex resolves
    \\includegraphics targets relative to the compile directory (the main
    .tex file's directory -- the project root passed on the CLI) or an
    explicit \\graphicspath, NEVER relative to a \\input/\\include'd
    sub-file's own directory. Resolving against each source file's own
    directory would be a FALSE-NEGATIVE vector: a chapter-local image (e.g.
    `cap/figures/x.png` referenced as `\\includegraphics{x}` from
    `cap/ch.tex` with no \\graphicspath) would appear to "resolve" here but
    would fail to compile under a standard root build.

    KNOWN LIMITATION: \\graphicspath itself is not parsed, so a project that
    declares a non-root \\graphicspath may see false-positive "missing"
    candidates for images that actually compile fine. That is the safe
    direction for a candidate signal -- a false negative (silently missing
    a genuinely broken reference) is worse than an occasional false
    positive the reviewer can dismiss."""
    bases = [root]
    for sub in _IMAGE_SUBDIRS:
        combined = os.path.join(root, sub)
        if combined not in bases:
            bases.append(combined)
    return bases


def _image_exists(arg, root):
    """True if `arg` (an \\includegraphics argument, possibly extension-
    less) resolves to an existing file under any tried base-dir/extension
    combination (project root + common image subfolders only -- see
    _base_dirs). NEVER raises: any filesystem oddity (weird path, OS error)
    degrades to 'not found', matching the 'candidates never crash'
    contract -- an unresolvable path is a missing-image CANDIDATE, not a
    crash."""
    arg = (arg or "").strip()
    if not arg:
        return False
    arg = arg.replace("\\", "/")
    names = _candidate_names(arg)
    for base in _base_dirs(root):
        for name in names:
            try:
                candidate = os.path.join(base, name)
                if os.path.isfile(candidate):
                    return True
            except (OSError, ValueError, TypeError):
                continue
    return False


# --- collection ----------------------------------------------------------------

def _scan_includegraphics(directory):
    """Yield (path, line_no, arg) for every \\includegraphics occurrence,
    manifest-scoped, comment-stripped."""
    for path in latex_corpus.find_manifest_files(directory).files:
        for line_no, raw in enumerate(latex_corpus.read_text(path).split("\n"), 1):
            line = latex_corpus.strip_comment(raw)
            if not line.strip():
                continue
            for m in _INCLUDEGRAPHICS_RE.finditer(line):
                yield path, line_no, m.group(1)


def _scan_rule_style(directory):
    """Return (hline_occurrences, booktabs_occurrences), each a list of
    (path, line_no), manifest-scoped, comment-stripped. Scanned as plain
    text (not gated to inside a tabular) -- a stray rule command outside any
    recognised environment is still evidence that style is used somewhere
    in the project, which is the whole point of this check."""
    hline_occ, booktabs_occ = [], []
    for path in latex_corpus.find_manifest_files(directory).files:
        for line_no, raw in enumerate(latex_corpus.read_text(path).split("\n"), 1):
            line = latex_corpus.strip_comment(raw)
            if not line.strip():
                continue
            if _HLINE_RE.search(line):
                hline_occ.append((path, line_no))
            if _BOOKTABS_RE.search(line):
                booktabs_occ.append((path, line_no))
    return hline_occ, booktabs_occ


def _scan_environments(path):
    """Single stack-based pass over one file's lines. Returns:
      - float_frames: list of dicts for each CLOSED figure/figure*/table/
        table* environment: {"name", "start_line", "has_caption", "has_label"}
      - tabular_frames: list of dicts for each CLOSED tabular/tabular*/
        tabularx environment: {"name", "start_line", "row_count"}

    An environment left open at end-of-file (malformed/unbalanced source,
    or a mismatched \\end{other-name}) is silently DROPPED -- never reported
    and never raised. A stray/mismatched \\end is likewise ignored rather
    than corrupting the stack."""
    stack = []
    float_frames = []
    tabular_frames = []

    for line_no, raw in enumerate(latex_corpus.read_text(path).split("\n"), 1):
        line = latex_corpus.strip_comment(raw)
        if not line.strip():
            continue
        for m in _ENV_EVENT_RE.finditer(line):
            begin = m.group("begin")
            end = m.group("end")
            if begin:
                stack.append({
                    "name": begin,
                    "start_line": line_no,
                    "has_caption": False,
                    "has_label": False,
                    "row_count": 0,
                })
            elif end:
                idx = None
                for i in range(len(stack) - 1, -1, -1):
                    if stack[i]["name"] == end:
                        idx = i
                        break
                if idx is None:
                    continue  # stray/mismatched \end -- ignore, never crash
                frame = stack[idx]
                del stack[idx:]  # drop this frame + any unclosed ones above it
                if frame["name"] in _FLOAT_ENV_NAMES:
                    float_frames.append(frame)
                else:
                    tabular_frames.append(frame)
            elif m.group(0).startswith("\\caption"):
                for frame in stack:
                    frame["has_caption"] = True
            elif m.group(0).startswith("\\label"):
                for frame in stack:
                    frame["has_label"] = True
            else:  # "\\\\" row break
                for frame in stack:
                    if frame["name"] in _TABULAR_ENV_NAMES:
                        frame["row_count"] += 1

    return float_frames, tabular_frames


# --- checks ------------------------------------------------------------------

def check(directory):
    """Run all checks; return a dict of category -> list of pre-formatted,
    anchored finding strings."""
    findings = {
        "missing_image": [],
        "duplicate_image": [],
        "caption_label": [],
        "long_tabular": [],
        "mixed_rules": [],
    }

    # 1/2. \includegraphics existence + duplicate usage.
    by_arg = {}
    for path, line_no, arg in _scan_includegraphics(directory):
        key = arg.strip()
        if not key:
            # \includegraphics{} -- an empty argument IS itself a broken
            # reference; flag it directly rather than silently skipping.
            # Not added to by_arg: deduplicating "" against other "" hits
            # would be a meaningless signal on its own.
            findings["missing_image"].append(
                "`%s` — `\\includegraphics` com argumento vazio (referência quebrada)"
                % latex_corpus.anchor(path, line_no, directory)
            )
            continue
        if not _image_exists(key, directory):
            findings["missing_image"].append(
                "`%s` — `\\includegraphics` aponta para `%s`, não encontrado "
                "no projeto (testado na raiz e em %s, com extensões %s)"
                % (latex_corpus.anchor(path, line_no, directory), key,
                   "/".join("`%s/`" % s for s in _IMAGE_SUBDIRS),
                   "/".join(e.lstrip(".") for e in _IMAGE_EXTS))
            )
        by_arg.setdefault(key, []).append((path, line_no))

    for arg in sorted(by_arg.keys()):
        occs = by_arg[arg]
        if len(occs) >= 2:
            anchors = ", ".join(
                "`%s`" % latex_corpus.anchor(p, l, directory) for p, l in occs
            )
            findings["duplicate_image"].append(
                "`%s` usada %d vezes: %s" % (arg, len(occs), anchors)
            )

    # 3/4. Per-file environment stack: caption/label + long tabular.
    for path in latex_corpus.find_manifest_files(directory).files:
        float_frames, tabular_frames = _scan_environments(path)
        for frame in float_frames:
            missing = []
            if not frame["has_caption"]:
                missing.append("\\caption")
            if not frame["has_label"]:
                missing.append("\\label")
            if missing:
                desc = " e sem ".join("`%s`" % m for m in missing)
                findings["caption_label"].append(
                    "`%s` — ambiente `%s` sem %s"
                    % (latex_corpus.anchor(path, frame["start_line"], directory),
                       frame["name"], desc)
                )
        for frame in tabular_frames:
            if frame["row_count"] > ROW_THRESHOLD:
                findings["long_tabular"].append(
                    "`%s` — ambiente `%s` com %d quebras de linha (`\\\\`), "
                    "acima do limiar de %d — considerar `longtable`"
                    % (latex_corpus.anchor(path, frame["start_line"], directory),
                       frame["name"], frame["row_count"], ROW_THRESHOLD)
                )

    # 5. \hline vs booktabs mixed anywhere in the project.
    hline_occ, booktabs_occ = _scan_rule_style(directory)
    if hline_occ and booktabs_occ:
        hline_anchors = ", ".join(
            "`%s`" % latex_corpus.anchor(p, l, directory) for p, l in hline_occ
        )
        booktabs_anchors = ", ".join(
            "`%s`" % latex_corpus.anchor(p, l, directory) for p, l in booktabs_occ
        )
        findings["mixed_rules"].append(
            "`\\hline` (%d ocorrência(s): %s) e booktabs "
            "`\\toprule`/`\\midrule`/`\\bottomrule` (%d ocorrência(s): %s) "
            "misturados no mesmo projeto"
            % (len(hline_occ), hline_anchors, len(booktabs_occ), booktabs_anchors)
        )

    return findings


# --- output --------------------------------------------------------------------

_SECTIONS = [
    ("missing_image",   "Imagem referenciada não encontrada"),
    ("duplicate_image", "Mesma imagem usada em múltiplos locais"),
    ("caption_label",   "Figura/tabela sem `\\caption` ou sem `\\label`"),
    ("long_tabular",    "Tabela extensa (candidata a `longtable`)"),
    ("mixed_rules",     "`\\hline` e booktabs misturados no mesmo projeto"),
]


def main(directory):
    findings = check(directory)

    out = ["## Floats, imagens e tabelas — candidatos", ""]
    out.append(
        "_Sinais objetivos sobre `\\includegraphics` (existência de arquivo "
        "e reuso), ambientes `figure`/`table` (`\\caption`/`\\label` "
        "ausentes), `tabular` extensa (candidata a `longtable`, limiar de "
        "%d quebras de linha) e mistura de `\\hline` com booktabs no mesmo "
        "projeto. O revisor decide se cada candidato é vício real ou uma "
        "exceção legítima._" % ROW_THRESHOLD
    )
    out.append("")

    any_finding = False
    for key, title in _SECTIONS:
        items = findings[key]
        if not items:
            continue
        any_finding = True
        out.append("### %s" % title)
        for item in items:
            out.append("- %s" % item)
        out.append("")

    if not any_finding:
        out.append("(nenhum problema de floats, imagens ou tabelas detectado)")

    print("\n".join(out))


if __name__ == "__main__":
    # Pin stdout to UTF-8, symmetric with latex_corpus's UTF-8 read side. A
    # piped stdout on Windows defaults to cp1252 and would crash on echoed
    # source characters outside it. Python 3.7+, stdlib only.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) != 2:
        sys.stderr.write("Uso: python3 float_check.py <diretório-do-projeto-latex>\n")
        sys.exit(2)
    target = sys.argv[1]
    if not os.path.isdir(target):
        sys.stderr.write("Diretório não encontrado: %s\n" % target)
        sys.exit(1)
    main(target)
