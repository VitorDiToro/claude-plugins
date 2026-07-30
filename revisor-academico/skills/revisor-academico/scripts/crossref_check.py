#!/usr/bin/env python3
# crossref_check.py
#
# Objective-signal script for the "Referências cruzadas e rótulos" rule of the
# academic-report reviewer. It finds mechanical mismatches between LaTeX
# `\label{...}` definitions and `\ref`-family uses (`\ref`, `\eqref`,
# `\autoref`, `\Cref`, `\cref`), plus a coarse signal for appendix/anexo
# mentions that have no corresponding label anywhere in the document.
#
# Checks emitted (all LOCATED CANDIDATES, never verdicts -- parity with every
# other Fase-0 script: the reviewing pass decides whether a flagged item is a
# real defect or a legitimate exception, e.g. a label intentionally kept
# unreferenced):
#   1. Orphan label: `\label{k}` defined but never used by any \ref-family
#      command.
#   2. Broken reference: a \ref-family use of `k` with no matching `\label{k}`
#      anywhere in the manifest.
#   3. Duplicate label: the same `k` defined by `\label` more than once.
#   4. Fragile label: a label key containing accented/non-ASCII characters
#      (risky across LaTeX engines/packages).
#   5. Appendix/anexo without a matching label -- two sub-cases:
#        a) a broken \ref-family use whose key looks like an appendix/anexo
#           label (prefix `ap:`, `apend:`, `anexo:`, ...);
#        b) a hardcoded textual mention ("Apêndice A" / "Anexo B", NOT via
#           \ref) when the corpus defines NO appendix-like \label at all.
#      Exact compiled-letter matching ("does 'Apêndice A' really correspond to
#      THIS appendix?") is out of scope for static reading (checklist note);
#      case (b) only fires on the coarser situation where no appendix label
#      exists anywhere for the mention to plausibly correspond to.
#
# BOUNDARY: this script never inspects `.bib` files or `\cite`-family commands
# -- that is bib_check.py's territory. crossref_check is `\ref`/`\label`/
# appendix ONLY.
#
# stdlib only, cross-platform, UTF-8 pinned. Reuses latex_corpus for
# manifest-scoped discovery, reading, comment stripping, and anchoring (the
# ONLY way a location string is built here). Code/comments English; output
# Portuguese. Invoke: python3 crossref_check.py <dir>

import os
import re
import sys

import latex_corpus


# --- regexes -----------------------------------------------------------------

# \label{key}. A single key per command (LaTeX doesn't support multi-key
# \label), so the whole argument is the key.
_LABEL_RE = re.compile(r"\\label\{([^}]*)\}")

# The \ref-family this check covers, per the checklist item: \ref, \eqref,
# \autoref, \Cref, \cref. Deliberately NOT \pageref/\nameref/\subref (out of
# the stated family) and NOT \cite-family (bib_check's territory). Matching is
# anchored right after the backslash, so "\eqref{...}" is never mistaken for a
# "\ref{...}" match starting mid-command.
_REF_RE = re.compile(r"\\(?:ref|eqref|autoref|Cref|cref)\{([^}]*)\}")

# Hardcoded textual "Apêndice A" / "Anexo B" mentions -- i.e. the letter is
# typed literally in prose rather than produced by a \ref-family command. Only
# a single uppercase ASCII letter is matched (the ABNT/Inatel convention for
# appendix/anexo designators), so this does not fire on "Apêndice Único" or on
# a bare "Apêndice" with no designator.
_APPENDIX_TEXT_RE = re.compile(r"\b(?:Ap[eê]ndice|Anexo)\s+([A-Z])\b")

# Label/ref key prefixes (before the first ':') that conventionally denote an
# appendix or anexo, e.g. `ap:tcle`, `anexo:parecer`. Matched case-insensitively
# against the prefix only.
_APPENDIX_KEY_PREFIXES = {"ap", "app", "apend", "apendice", "anexo", "anex", "anx"}


def _is_appendix_key(key):
    """True if `key` looks like an appendix/anexo label by its prefix
    convention (the part before the first ':', case-insensitive)."""
    prefix = key.split(":", 1)[0].strip().lower()
    return prefix in _APPENDIX_KEY_PREFIXES


# --- collection ---------------------------------------------------------------

def collect(directory):
    """Single pass over the manifest-scoped corpus. Returns:
      - labels: dict {key: [(path, line_no), ...]} for every \\label{key}
        occurrence, in file/line order (first entry = first definition);
      - refs: list of (path, line_no, key) for every \\ref-family occurrence,
        in file/line order;
      - appendix_mentions: list of (path, line_no, matched_text) for every
        hardcoded "Apêndice X"/"Anexo X" textual mention.
    Comments are stripped first (latex_corpus.strip_comment), so anything
    inside a % comment does not count, matching every other objective script.
    Never raises on malformed input: unmatched braces on a line simply don't
    match the regexes above (no crash), and blank lines are skipped."""
    labels = {}
    refs = []
    appendix_mentions = []

    for path in latex_corpus.find_manifest_files(directory).files:
        for line_no, raw in enumerate(latex_corpus.read_text(path).split("\n"), 1):
            line = latex_corpus.strip_comment(raw)
            if not line.strip():
                continue

            for m in _LABEL_RE.finditer(line):
                key = m.group(1).strip()
                if key:
                    labels.setdefault(key, []).append((path, line_no))

            for m in _REF_RE.finditer(line):
                # \cref/\Cref (cleveref) support multi-key groups like
                # "fig:a,fig:b"; split defensively so each key is checked on
                # its own. A plain single-key \ref{fig:a} is unaffected.
                for k in m.group(1).split(","):
                    k = k.strip()
                    if k:
                        refs.append((path, line_no, k))

            for m in _APPENDIX_TEXT_RE.finditer(line):
                appendix_mentions.append((path, line_no, m.group(0)))

    return labels, refs, appendix_mentions


# --- checks --------------------------------------------------------------------

def check(directory):
    """Run all checks; return a dict of category -> list of pre-formatted,
    anchored finding strings."""
    labels, refs, appendix_mentions = collect(directory)

    findings = {
        "orphan": [],
        "broken": [],
        "duplicate": [],
        "fragile": [],
        "appendix": [],
    }

    ref_keys = {key for _path, _line, key in refs}

    # 1. Orphan labels: defined but never referenced by any \ref-family use.
    for key in sorted(labels.keys()):
        if key not in ref_keys:
            path, line_no = labels[key][0]
            findings["orphan"].append(
                "`%s` — rótulo `%s` (`\\label`) nunca é referenciado por "
                "`\\ref`/`\\eqref`/`\\autoref`/`\\Cref`/`\\cref`"
                % (latex_corpus.anchor(path, line_no, directory), key)
            )

    # 2. Broken references / 5a. appendix-prefixed broken references.
    # Appendix-prefixed keys are routed to "appendix" instead of "broken" so
    # each finding surfaces in exactly one section.
    for path, line_no, key in refs:
        if key in labels:
            continue
        if _is_appendix_key(key):
            findings["appendix"].append(
                "`%s` — referência a apêndice/anexo `%s` sem `\\label` correspondente"
                % (latex_corpus.anchor(path, line_no, directory), key)
            )
        else:
            findings["broken"].append(
                "`%s` — `%s` não tem `\\label` correspondente"
                % (latex_corpus.anchor(path, line_no, directory), key)
            )

    # 3. Duplicate labels: same key defined by \label more than once.
    for key in sorted(labels.keys()):
        occs = labels[key]
        if len(occs) > 1:
            anchors = ", ".join(
                "`%s`" % latex_corpus.anchor(p, l, directory) for p, l in occs
            )
            findings["duplicate"].append(
                "rótulo `%s` definido %d vezes: %s" % (key, len(occs), anchors)
            )

    # 4. Fragile labels: key contains accented/non-ASCII characters.
    for key in sorted(labels.keys()):
        if not key.isascii():
            path, line_no = labels[key][0]
            findings["fragile"].append(
                "`%s` — rótulo `%s` contém acento/caractere não-ASCII"
                % (latex_corpus.anchor(path, line_no, directory), key)
            )

    # 5b. Textual appendix/anexo mentions, only when the corpus defines NO
    # appendix-like \label at all (see module docstring for the scope note).
    has_appendix_label = any(_is_appendix_key(k) for k in labels)
    if not has_appendix_label:
        for path, line_no, text in appendix_mentions:
            findings["appendix"].append(
                "`%s` — menção textual a `%s` sem nenhum `\\label` de "
                "apêndice/anexo no documento"
                % (latex_corpus.anchor(path, line_no, directory), text)
            )

    return findings


# --- output ------------------------------------------------------------------

_SECTIONS = [
    ("orphan",    "Rótulos órfãos (`\\label` nunca referenciado)"),
    ("broken",    "Referências quebradas (sem `\\label` correspondente)"),
    ("duplicate", "Rótulos duplicados"),
    ("fragile",   "Rótulos frágeis (acento/caractere não-ASCII)"),
    ("appendix",  "Apêndice/anexo sem rótulo correspondente"),
]


def main(directory):
    findings = check(directory)

    out = ["## Referências cruzadas (\\ref/\\label) — candidatos", ""]
    out.append("_Sinais objetivos sobre `\\label`/`\\ref` (e menções textuais a apêndice/anexo) — "
               "casamento de chaves, duplicatas, rótulos frágeis. **Não** cobre `.bib`/`\\cite` "
               "(isso é do `bib_check`). O revisor decide se cada candidato é vício real ou uma "
               "exceção legítima (ex.: rótulo intencionalmente não referenciado)._")
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
        out.append("(nenhum problema de referências cruzadas, rótulos ou apêndice/anexo detectado)")

    print("\n".join(out))


if __name__ == "__main__":
    # Pin stdout to UTF-8, symmetric with latex_corpus's UTF-8 read side. A
    # piped stdout on Windows defaults to cp1252 and would crash on echoed
    # source characters outside it. Python 3.7+, stdlib only.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) != 2:
        sys.stderr.write("Uso: python3 crossref_check.py <diretório-do-projeto-latex>\n")
        sys.exit(2)
    target = sys.argv[1]
    if not os.path.isdir(target):
        sys.stderr.write("Diretório não encontrado: %s\n" % target)
        sys.exit(1)
    main(target)
