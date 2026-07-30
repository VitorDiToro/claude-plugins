#!/usr/bin/env python3
# bib_check.py
#
# Objective-signal script for the bibliography rules of the academic-report
# reviewer. It performs ONLY the mechanical / low-cost checks -- the ones that
# are parsing plus fixed per-type rules -- and deliberately does NOT judge
# bibliographic CONTENT (whether a source is appropriate, current, trustworthy,
# or whether a DOI resolves to the right paper). That semantic judgement belongs
# to a separate future skill; here we stay in the "located candidates, not
# verdicts" contract shared by every objective script.
#
# Checks emitted:
#   1. \cite{key} whose key has no matching entry in any .bib (undefined citation).
#   2. .bib entry never cited anywhere in the corpus (orphan entry).
#   3. Essential field missing for the entry type (@article without journal, ...).
#   4. DOI missing CONDITIONALLY: only flagged when other entries of the SAME
#      type already carry a doi -- respects bibliographies that deliberately
#      omit DOIs, and never nags a document that uses none.
#   5. Implausible format: year out of range / non-numeric, inverted page range,
#      malformed URL.
#
# Everything is a SIGNAL. Deciding whether an orphan entry is dead weight or a
# deliberately-kept reference, or whether a missing field matters for a given
# source, is the reviewing pass's call.
#
# stdlib only, cross-platform, UTF-8 pinned. Reuses latex_corpus for corpus
# reading and .tex discovery; parses .bib with a small tolerant scanner (no
# bibtexparser, which is pip). Code/comments English; output Portuguese.
# Invoke: python3 bib_check.py <dir>

import datetime
import os
import re
import sys

import latex_corpus


# --- .bib discovery ----------------------------------------------------------

def find_bib_files(directory):
    """Every .bib under `directory`, recursively, path-sorted (deterministic)."""
    out = []
    for root, _dirs, files in os.walk(directory):
        for name in files:
            if name.endswith(".bib"):
                out.append(os.path.join(root, name))
    out.sort()
    return out


# --- .bib parsing ------------------------------------------------------------
#
# A tolerant, single-pass scanner. It is NOT a full BibTeX grammar: it handles
# @type{key, field = {value} | "value" | bareword, ...}, brace/quote-balanced
# values, nested braces, and @string/@comment/@preamble (skipped). It tracks the
# source line of each entry so signals are actionable (file:line).

BibEntry = latex_corpus.namedtuple(
    "BibEntry", ["etype", "key", "fields", "file", "line"]
)

_ENTRY_START_RE = re.compile(r"@(\w+)\s*[{(]", re.IGNORECASE)


def parse_bib(path):
    """Yield BibEntry for each entry in `path`. Malformed entries are skipped
    as gracefully as possible rather than raising."""
    text = latex_corpus.read_text(path)
    # Precompute a char-index -> line-number map for anchoring.
    line_starts = [0]
    for i, ch in enumerate(text):
        if ch == "\n":
            line_starts.append(i + 1)

    def line_of(pos):
        # binary search would be nicer; linear is fine for .bib sizes
        lo, hi = 0, len(line_starts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if line_starts[mid] <= pos:
                lo = mid
            else:
                hi = mid - 1
        return lo + 1

    for m in _ENTRY_START_RE.finditer(text):
        etype = m.group(1).lower()
        if etype in ("string", "comment", "preamble"):
            continue
        open_char = text[m.end() - 1]
        close_char = "}" if open_char == "{" else ")"
        body, _end = _read_balanced(text, m.end(), open_char, close_char)
        if body is None:
            continue
        key, fields = _parse_entry_body(body)
        if key is None:
            continue
        yield BibEntry(
            etype=etype,
            key=key,
            fields=fields,
            file=path,
            line=line_of(m.start()),
        )


def _read_balanced(text, start, open_char, close_char):
    """From just past the opening delimiter, return (inner_text, index_past_close)
    respecting nested {...}. Quotes are not treated as delimiters here; field-level
    quote handling happens in _parse_entry_body."""
    depth = 1
    i = start
    n = len(text)
    while i < n:
        c = text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[start:i], i + 1
        i += 1
    return None, n  # unbalanced to EOF


def _parse_entry_body(body):
    """Split '<key>, field=value, ...' into (key, {field: value}). Returns
    (None, {}) if no key is found."""
    # key is everything up to the first comma
    comma = body.find(",")
    if comma == -1:
        # entry with a key but no fields, or garbage
        key = body.strip()
        return (key or None), {}
    key = body[:comma].strip()
    if not key:
        return None, {}
    fields = {}
    i = comma + 1
    n = len(body)
    while i < n:
        # field name
        eq = body.find("=", i)
        if eq == -1:
            break
        name = body[i:eq].strip().lower()
        # skip stray commas/whitespace captured into name
        name = name.strip(", \t\r\n")
        value, i = _read_field_value(body, eq + 1)
        if name:
            fields[name] = value
    return key, fields


def _read_field_value(body, i):
    """Read one field value starting at index i; return (value, next_index).
    Handles {braced} (nested), "quoted", and bareword/number values, stopping at
    the top-level comma that separates fields."""
    n = len(body)
    while i < n and body[i] in " \t\r\n":
        i += 1
    if i >= n:
        return "", i
    c = body[i]
    if c == "{":
        depth = 0
        start = i
        while i < n:
            if body[i] == "{":
                depth += 1
            elif body[i] == "}":
                depth -= 1
                if depth == 0:
                    inner = body[start + 1:i]
                    i += 1
                    break
            i += 1
        else:
            inner = body[start + 1:]
        return _clean_value(inner), _advance_past_comma(body, i)
    if c == '"':
        start = i + 1
        i += 1
        depth = 0
        while i < n:
            if body[i] == "{":
                depth += 1
            elif body[i] == "}":
                depth -= 1
            elif body[i] == '"' and depth == 0:
                inner = body[start:i]
                i += 1
                break
            i += 1
        else:
            inner = body[start:]
        return _clean_value(inner), _advance_past_comma(body, i)
    # bareword / number until the next top-level comma
    start = i
    while i < n and body[i] != ",":
        i += 1
    return _clean_value(body[start:i]), _advance_past_comma(body, i)


def _advance_past_comma(body, i):
    n = len(body)
    while i < n and body[i] in " \t\r\n":
        i += 1
    if i < n and body[i] == ",":
        i += 1
    return i


_WS_RE = re.compile(r"\s+")


def _clean_value(raw):
    """Collapse whitespace and trim; keep the text otherwise intact."""
    return _WS_RE.sub(" ", raw).strip()


# --- citation-key extraction from the corpus ---------------------------------
#
# Parity note with pattern_profile.CITE_RE, which matches the command but not
# the keys. Here we capture the argument and split multi-key \cite{a,b,c}.
# Handles \cite, \citep, \citet, \cite[p.~3]{key}, \parencite, \textcite, etc.

_CITE_RE = re.compile(
    r"\\[a-zA-Z]*cite[a-zA-Z]*\*?"   # any \...cite... command
    r"(?:\[[^\]]*\])*"               # optional [..] option groups
    r"\{([^}]*)\}"                   # the {key,key,...} argument
)


def cite_occurrences(directory):
    """Yield (path, line_no, key) for every citation key referenced anywhere in
    the manifest-scoped .tex corpus (latex_corpus.find_manifest_files), in
    file/line order. Comments are stripped first, so a citation inside a %
    comment does not count. A multi-key \\cite{a,b,c} yields one tuple per key,
    so each undefined-citation site can be anchored individually."""
    for path in latex_corpus.find_manifest_files(directory).files:
        for line_no, raw in enumerate(latex_corpus.read_text(path).split("\n"), 1):
            line = latex_corpus.strip_comment(raw)
            for m in _CITE_RE.finditer(line):
                for k in m.group(1).split(","):
                    k = k.strip()
                    if k:
                        yield path, line_no, k


def cited_keys(directory):
    """Set of every citation key referenced anywhere in the corpus (dedup of
    cite_occurrences). Used by the orphan-entry check, which only cares
    whether a key is cited ANYWHERE, not where."""
    return {key for _path, _line, key in cite_occurrences(directory)}


# --- per-type essential fields ----------------------------------------------
#
# Minimal, widely-agreed required fields per common BibTeX type. Kept
# conservative on purpose: only fields whose absence is almost always a real
# defect. "author OR editor" and "journal OR journaltitle" style alternatives
# are encoded as tuples (any-one-present satisfies the requirement).

_REQUIRED_FIELDS = {
    "article":       [("author",), ("title",), ("journal", "journaltitle"), ("year", "date")],
    "book":          [("author", "editor"), ("title",), ("publisher",), ("year", "date")],
    "inbook":        [("author", "editor"), ("title",), ("publisher",), ("year", "date")],
    "incollection":  [("author",), ("title",), ("booktitle",), ("publisher",), ("year", "date")],
    "inproceedings": [("author",), ("title",), ("booktitle",), ("year", "date")],
    "conference":    [("author",), ("title",), ("booktitle",), ("year", "date")],
    "phdthesis":     [("author",), ("title",), ("school", "institution"), ("year", "date")],
    "mastersthesis": [("author",), ("title",), ("school", "institution"), ("year", "date")],
    "techreport":    [("author",), ("title",), ("institution",), ("year", "date")],
    "manual":        [("title",)],
    "misc":          [("title",)],
    "online":        [("title",), ("url",)],
    "electronic":    [("title",), ("url",)],
    "www":           [("title",), ("url",)],
    "unpublished":   [("author",), ("title",), ("note",)],
}

# Types for which a missing URL is itself worth flagging (web sources).
_URL_EXPECTED_TYPES = {"online", "electronic", "www", "misc"}

_URL_RE = re.compile(r"^(https?|ftp)://\S+$", re.IGNORECASE)
_DOI_FIELD = "doi"


def _year_of(entry):
    """Best-effort year extraction from 'year' or from a 'date' like 2021-05."""
    if "year" in entry.fields:
        return entry.fields["year"]
    if "date" in entry.fields:
        m = re.match(r"\s*(\d{4})", entry.fields["date"])
        if m:
            return m.group(1)
    return None


# --- checks ------------------------------------------------------------------

def check(directory):
    """Run all checks; return a dict of category -> list of finding strings
    (each pre-formatted with its file:line anchor)."""
    bib_files = find_bib_files(directory)
    findings = {
        "undefined": [],   # \cite with no entry
        "orphan": [],      # entry never cited
        "fields": [],      # essential field missing
        "doi": [],         # conditional DOI
        "format": [],      # implausible format
    }
    if not bib_files:
        return findings, False  # False => no .bib present at all

    # Parse every entry; detect duplicate keys along the way.
    entries = []
    seen_keys = {}
    for path in bib_files:
        for entry in parse_bib(path):
            if entry.key in seen_keys:
                first = seen_keys[entry.key]
                findings["format"].append(
                    "`%s` — chave duplicada `%s` (primeira em `%s`)"
                    % (latex_corpus.anchor(entry.file, entry.line, directory),
                       entry.key,
                       latex_corpus.anchor(first.file, first.line, directory))
                )
            else:
                seen_keys[entry.key] = entry
            entries.append(entry)

    defined = set(seen_keys.keys())
    occurrences = list(cite_occurrences(directory))
    cited = {key for _path, _line, key in occurrences}

    # 1. Undefined citations: \cite sites whose key has no .bib entry --
    # anchored at each \cite occurrence (not deduplicated per key), so the
    # reviewer sees every offending site rather than just the bare key.
    for path, line_no, key in occurrences:
        if key not in defined:
            findings["undefined"].append(
                "`%s` — `\\cite{%s}` não tem entrada em nenhum `.bib`"
                % (latex_corpus.anchor(path, line_no, directory), key)
            )

    # 2. Orphan entries: defined but never cited.
    for entry in entries:
        if entry.key not in cited:
            findings["orphan"].append(
                "`%s` — entrada `%s` (`@%s`) nunca é citada"
                % (latex_corpus.anchor(entry.file, entry.line, directory), entry.key, entry.etype)
            )

    # DOI conditional baseline: which types already use DOI somewhere?
    types_with_doi = set()
    for entry in entries:
        if entry.fields.get(_DOI_FIELD):
            types_with_doi.add(entry.etype)

    # 3/4/5. Per-entry field, DOI, and format checks.
    for entry in entries:
        _check_required_fields(entry, findings, directory)
        _check_doi_conditional(entry, types_with_doi, findings, directory)
        _check_formats(entry, findings, directory)

    return findings, True


def _check_required_fields(entry, findings, directory):
    spec = _REQUIRED_FIELDS.get(entry.etype)
    if spec is None:
        return  # unknown type -> no fixed rule, stay silent
    missing = []
    for alternatives in spec:
        if not any(entry.fields.get(name) for name in alternatives):
            missing.append(" ou ".join(alternatives))
    # A web-source type without url is folded into the same signal.
    if entry.etype in _URL_EXPECTED_TYPES and not entry.fields.get("url"):
        if "url" not in " ".join(missing):
            missing.append("url")
    if missing:
        findings["fields"].append(
            "`%s` — `%s` (`@%s`) sem campo essencial: %s"
            % (latex_corpus.anchor(entry.file, entry.line, directory),
               entry.key, entry.etype, ", ".join(missing))
        )


def _check_doi_conditional(entry, types_with_doi, findings, directory):
    # Only flag when THIS type already uses DOI elsewhere and this entry lacks it.
    if entry.etype in types_with_doi and not entry.fields.get(_DOI_FIELD):
        findings["doi"].append(
            "`%s` — `%s` (`@%s`) sem `doi`, embora outras entradas do mesmo tipo tenham"
            % (latex_corpus.anchor(entry.file, entry.line, directory), entry.key, entry.etype)
        )


def _check_formats(entry, findings, directory):
    # Year plausibility.
    year = _year_of(entry)
    if year is not None:
        y = year.strip()
        if not re.fullmatch(r"\d{4}", y):
            findings["format"].append(
                "`%s` — `%s`: ano `%s` não é um ano de 4 dígitos"
                % (latex_corpus.anchor(entry.file, entry.line, directory), entry.key, year)
            )
        else:
            yi = int(y)
            next_year = datetime.date.today().year + 1
            if yi < 1500 or yi > next_year:
                findings["format"].append(
                    "`%s` — `%s`: ano `%s` fora de faixa plausível (1500–%d)"
                    % (latex_corpus.anchor(entry.file, entry.line, directory), entry.key, y, next_year)
                )

    # Page range: "start--end" or "start-end"; flag start > end.
    pages = entry.fields.get("pages")
    if pages:
        m = re.match(r"\s*(\d+)\s*-{1,2}\s*(\d+)\s*$", pages)
        if m:
            start, end = int(m.group(1)), int(m.group(2))
            if start > end:
                findings["format"].append(
                    "`%s` — `%s`: intervalo de páginas invertido (`%s`)"
                    % (latex_corpus.anchor(entry.file, entry.line, directory), entry.key, pages)
                )

    # URL well-formedness, when present.
    url = entry.fields.get("url")
    if url and not _URL_RE.match(url):
        findings["format"].append(
            "`%s` — `%s`: `url` malformada (`%s`)"
            % (latex_corpus.anchor(entry.file, entry.line, directory), entry.key, url)
        )


# --- output ------------------------------------------------------------------

_SECTIONS = [
    ("undefined", "Citações sem entrada no `.bib`"),
    ("fields",    "Campo essencial ausente por tipo"),
    ("format",    "Formato implausível (ano, páginas, URL, chave duplicada)"),
    ("doi",       "DOI ausente (condicional — só onde o tipo já usa DOI)"),
    ("orphan",    "Entradas nunca citadas (órfãs)"),
]


def main(directory):
    findings, has_bib = check(directory)

    out = ["## Verificação de bibliografia (candidatos)", ""]
    out.append("_Sinais objetivos e mecânicos sobre os arquivos `.bib` — presença de campos, "
               "formato, casamento com `\\cite`. **Não** avaliam se a fonte é apropriada, atual "
               "ou confiável (isso é julgamento de conteúdo, fora do escopo). O revisor decide o "
               "que acatar._")
    out.append("")

    if not has_bib:
        out.append("(nenhum arquivo `.bib` encontrado no projeto)")
        print("\n".join(out))
        return

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
        out.append("(nenhum problema mecânico detectado nas referências)")

    print("\n".join(out))


if __name__ == "__main__":
    # Pin stdout to UTF-8, symmetric with latex_corpus's UTF-8 read side.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) != 2:
        sys.stderr.write("Uso: python3 bib_check.py <diretório-do-projeto-latex>\n")
        sys.exit(2)
    target = sys.argv[1]
    if not os.path.isdir(target):
        sys.stderr.write("Diretório não encontrado: %s\n" % target)
        sys.exit(1)
    main(target)
