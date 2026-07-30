#!/usr/bin/env python3
# acronym_check.py
#
# Objective-signal script for the "Acrônimos e siglas" rule of the academic-
# report reviewer (references/checklist-revisao.md). It finds, mechanically,
# four shapes of sigla/acronym trouble in the running prose:
#   1. A sigla (uppercase token, e.g. RAM, API) used in prose BEFORE its
#      first manual expansion in the document.
#   2. A manual expansion "Nome Completo (SIGLA)" -- flagged ALWAYS, even
#      when it is the only/correct occurrence, because it is fragile: nothing
#      guarantees the same sigla isn't expanded again in another chapter
#      without the author noticing (no automatic tracking, unlike \ac{...}
#      from the acro/acronym package).
#   3. The SAME sigla manually expanded more than once (re-expansion) --
#      flagged even on a single reoccurrence, per the checklist's own note
#      that this item is objective and does not require a recurring pattern.
#   4. Inconsistent grammatical gender for the same sigla ("a API" in one
#      place, "o API" in another).
#
# OUT OF SCOPE (by design, matches the task brief's boundary, not an
# oversight): "sigla nunca expandida" (a sigla never expanded anywhere) is
# NOT checked here -- reliably telling a genuine undefined acronym apart from
# an incidental all-caps token (an equation constant, a Roman numeral, a
# citation key already excluded below, ...) needs judgement this mechanical
# layer doesn't have. pattern_profile.py's "Mecanismo de siglas" section
# already gives the reviewer raw counts (\ac-family usage, manual "(SIGLA)"
# patterns) as context for that broader judgement call.
#
# Everything here is a LOCATED CANDIDATE, never a verdict (parity with every
# other Fase-0 script): the reviewing pass decides whether a flagged item is
# a real defect or a legitimate exception.
#
# Design decisions that matter:
#   - We scan comment-stripped lines WITH commands intact (mirrors
#     foreign_terms.py), because the exclusions below need to see command
#     names and their arguments, not just the underlying prose.
#   - A sigla-shaped token directly preceded by a backslash (a LaTeX command
#     NAME, e.g. \LARGE, \ABNT) is never a sigla usage -- this is the
#     "obvious LaTeX-command noise" guard.
#   - A sigla-shaped token sitting inside the FIRST {...} argument of a
#     "plumbing" command (\label, \ref-family, \cite-family, \input,
#     \include, \includegraphics, \usepackage, \documentclass,
#     \bibliography(style), \begin/\end, \newcommand/\renewcommand,
#     \DeclareAcronym/\acro/\newacronym) is plumbing (an env name, a label
#     key, a bib key, a macro name, ...), not running prose, and is excluded.
#   - A "(SIGLA)" is ALWAYS excluded from the bare-token stream (whether or
#     not it turns out to look like a real manual expansion), so the sigla
#     being introduced is never ALSO counted as a separate "usage" of itself.
#   - Well-known false-positive siglas (Roman numerals, common two-letter
#     abbreviations, ...) are intentionally NOT filtered out: this is a
#     candidate signal, not a verdict, and the checklist note explicitly
#     accepts over-surfacing here (the reviewer discards non-issues).
#
# stdlib only, cross-platform, UTF-8 pinned. Reuses latex_corpus for
# manifest-scoped discovery, reading, comment stripping, and anchoring (the
# ONLY way a location string is built here). Code/comments English; output
# Portuguese. Invoke: python3 acronym_check.py <dir>

import os
import re
import sys

import latex_corpus


# --- regexes -----------------------------------------------------------------

# A sigla candidate: 2-6 uppercase ASCII letters, optionally followed by up to
# 2 trailing digits (e.g. project jargon like "5G"-style tokens). \b on both
# ends means a plural like "APIs" (lowercase suffix) does NOT match -- plural
# handling is out of scope for this mechanical layer.
_SIGLA_RE = re.compile(r"\b[A-Z]{2,6}[0-9]{0,2}\b")

# A parenthesised sigla: "(SIGLA)" -- the tail shape of a manual expansion.
_PAREN_SIGLA_RE = re.compile(r"\(([A-Z]{2,6}[0-9]{0,2})\)")

# A "word" for the name-phrase scan: letters (incl. accented) plus internal
# hyphens (e.g. "Spread-Spectrum").
_TOKEN_RE = re.compile(r"[A-Za-zÀ-ÿ]+(?:-[A-Za-zÀ-ÿ]+)*")

# Portuguese connector words that may appear LOWERCASE inside a capitalised
# "Full Name" phrase (e.g. "Interface de Programação de Aplicações"). Bare
# single-letter articles ("a", "o", "as", "os") are deliberately NOT included:
# they mostly show up as the article BEFORE a name ("a RAM"), not inside one,
# and including them would make the backward scan too eager to cross into an
# unrelated preceding clause.
_CONNECTORS = {"de", "da", "do", "das", "dos", "e", "em", "para", "com"}

# Definite/indefinite articles used to read the grammatical gender a sigla is
# used with. Matched case-insensitively against the single word immediately
# preceding a bare sigla occurrence.
_FEMININE_ARTICLES = {"a", "à", "as", "às", "uma", "umas"}
_MASCULINE_ARTICLES = {"o", "ao", "aos", "os", "um", "uns"}

# Commands whose FIRST {...} argument is plumbing (environment name,
# label/ref/cite key, macro name, package/class/file name) rather than
# running prose. A sigla-shaped token inside one of these spans (e.g. a bib
# key like "IEEE2020") must never be treated as a prose usage/expansion.
# `acro`'s own \acro{SIGLA}{Full name} correctly belongs here: the sigla
# itself IS the first argument, so protecting only arg-1 is exactly right --
# unlike the two commands below, whose sigla lives in a LATER argument.
_NONPROSE_COMMANDS = (
    "label", "ref", "eqref", "autoref", "cref", "Cref",
    "cite", "citep", "citet", "citeauthor", "citeyear", "nocite",
    "input", "include", "includegraphics", "usepackage", "documentclass",
    "bibliography", "bibliographystyle",
    "begin", "end", "newcommand", "renewcommand", "acro",
)

# Multi-argument acronym-DECLARATION commands where the sigla lives in a
# LATER brace group, not the first: glossaries' \newacronym{label}{ABBRV}
# {Full name} (sigla in arg 2) and acro's \DeclareAcronym{label}{short =
# SIGLA, long = ...} (sigla inside arg 2's value). Protecting only the first
# group (as _NONPROSE_COMMANDS does) would leave the sigla itself exposed as
# a bare prose token, producing a false "used before expansion" finding that
# cites the declaration line. So for these, ALL consecutive {...} groups
# right after the command (and its optional [...] group) are protected, not
# just the first -- see _nonprose_spans.
_MULTI_ARG_NONPROSE_COMMANDS = ("newacronym", "DeclareAcronym")


# --- brace-aware plumbing-span scan (parity with foreign_terms._italic_spans) -

def _skip_ws(line, i):
    while i < len(line) and line[i] in " \t":
        i += 1
    return i


def _match_brace(line, i):
    """Given line[i] == '{', return the index just past the matching '}', or
    None if unbalanced on this line. Single-line; nested braces supported."""
    depth = 0
    n = len(line)
    while i < n:
        c = line[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return None


def _skip_optional_option(line, i):
    """If line[i] == '[', skip past the matching ']' (e.g. \\cite[p.3]{key},
    \\newacronym[key=val]{...}...). Returns the new index, or None if the
    option group is unbalanced on this line (caller should give up on this
    occurrence rather than guess)."""
    n = len(line)
    if i < n and line[i] == "[":
        end_opt = line.find("]", i)
        if end_opt == -1:
            return None
        return _skip_ws(line, end_opt + 1)
    return i


def _brace_group_after(line, i):
    """If line[i] == '{', return ((content_start, content_end), i_past_close)
    for the matched group. Otherwise return (None, i) unchanged."""
    if i < len(line) and line[i] == "{":
        start = i + 1
        end = _match_brace(line, i)
        if end is not None:
            return (start, end - 1), end
    return None, i


def _nonprose_spans(line):
    """Return [(start, end), ...] character spans covering plumbing argument
    text -- not running prose -- so a sigla-shaped token there is never
    reported as a usage/expansion/gender candidate:
      - the FIRST {...} argument of each _NONPROSE_COMMANDS occurrence
        (environment name, label/ref/cite key, macro name, package/class/
        file name, or \\acro's own SIGLA argument);
      - EVERY consecutive {...} argument of each _MULTI_ARG_NONPROSE_COMMANDS
        occurrence (\\newacronym/\\DeclareAcronym), because their sigla lives
        in a later group, not the first."""
    spans = []

    for cmd in _NONPROSE_COMMANDS:
        for m in re.finditer(r"\\%s\*?\b" % re.escape(cmd), line):
            i = _skip_optional_option(line, _skip_ws(line, m.end()))
            if i is None:
                continue
            span, _i = _brace_group_after(line, i)
            if span is not None:
                spans.append(span)

    for cmd in _MULTI_ARG_NONPROSE_COMMANDS:
        for m in re.finditer(r"\\%s\*?\b" % re.escape(cmd), line):
            i = _skip_optional_option(line, _skip_ws(line, m.end()))
            if i is None:
                continue
            while True:
                span, i = _brace_group_after(line, i)
                if span is None:
                    break
                spans.append(span)
                i = _skip_ws(line, i)

    return spans


def _inside_any(pos, spans):
    """True if character index `pos` falls within any (start, end) span."""
    return any(start <= pos < end for start, end in spans)


# --- manual-expansion name-phrase scan ----------------------------------------

def _preceded_by_sentence_break(prefix, tok_start):
    """True if the token starting at `tok_start` is separated from whatever
    precedes it (skipping spaces) by a '.', '!' or '?' -- i.e. it opens a new
    sentence, and the backward name-phrase scan must not cross into it."""
    j = tok_start
    while j > 0 and prefix[j - 1] == " ":
        j -= 1
    return j > 0 and prefix[j - 1] in ".!?"


def _looks_like_expansion_name(line, paren_start):
    """Return the 'Full Name' phrase immediately preceding line[paren_start]
    (the '(' of a candidate manual expansion), or None if the text before it
    doesn't look like one. Qualifies when: the text touches the '(' with no
    gap, contains at least 2 capitalised words, and the backward scan never
    crosses a '.', '!' or '?' sentence boundary. Portuguese connector words
    (de/da/do/das/dos/e/em/para/com) may appear lowercase INSIDE the phrase.

    KNOWN LIMITATION: a capitalised word that begins a NEW sentence can still
    be pulled in when it directly abuts an already-accepted connector (e.g.
    "Veja a Random Access Memory (RAM)" at a sentence start would include
    "Veja"). This only makes the DISPLAYED phrase text slightly noisy -- it
    never flips the yes/no classification, since the real name's words alone
    already clear the 2-capitalised-word bar. Acceptable cost for a candidate
    signal (the checklist explicitly tolerates over-surfacing here)."""
    prefix = line[:paren_start].rstrip()
    if not prefix:
        return None
    tokens = list(_TOKEN_RE.finditer(prefix))
    if not tokens or tokens[-1].end() != len(prefix):
        return None

    kept = []
    cap_count = 0
    for tok in reversed(tokens):
        word = tok.group(0)
        if kept and _preceded_by_sentence_break(prefix, tok.start()):
            break
        is_cap = word[0].isupper()
        is_connector = word.lower() in _CONNECTORS
        if not (is_cap or is_connector):
            break
        kept.append(word)
        if is_cap:
            cap_count += 1
        if len(kept) >= 10:  # safety cap against pathological input
            break

    kept.reverse()
    while kept and kept[0].lower() in _CONNECTORS:
        kept.pop(0)  # a phrase shouldn't start on a bare connector
    if cap_count < 2 or len(kept) < 2:
        return None
    return " ".join(kept)


_TRAILING_WORD_RE = re.compile(r"([A-Za-zÀ-ÿ]+)\s*$")


def _preceding_word(line, pos):
    """Return the word immediately before line[pos] (skipping spaces), or
    None if there is no word there (start of line, punctuation, ...)."""
    m = _TRAILING_WORD_RE.search(line[:pos])
    return m.group(1) if m else None


# --- collection ----------------------------------------------------------------

def collect(directory):
    """Single ordered pass over the manifest-scoped corpus. Returns a flat
    list of events in TRUE document order (manifest file order, top-to-bottom
    lines, left-to-right within a line):
      {"kind": "expansion", "sigla", "phrase", "path", "line_no"}
      {"kind": "bare", "sigla", "preceding_word", "path", "line_no"}
    Comments are stripped first. A parenthesised sigla ("(SIGLA)") is ALWAYS
    excluded from the bare-token stream -- whether or not it qualifies as a
    real expansion -- so the sigla being introduced/mentioned parenthetically
    is never ALSO counted as a separate bare 'usage' of itself. Never raises
    on malformed input: unmatched braces/parens on a line simply don't match
    the regexes above (no crash), and blank lines are skipped."""
    events = []
    for path in latex_corpus.find_manifest_files(directory).files:
        for line_no, raw in enumerate(latex_corpus.read_text(path).split("\n"), 1):
            line = latex_corpus.strip_comment(raw)
            if not line.strip():
                continue

            nonprose = _nonprose_spans(line)
            line_events = []

            # 1. Parenthesised siglas: "(SIGLA)" -- candidate expansions.
            paren_spans = []
            for m in _PAREN_SIGLA_RE.finditer(line):
                if _inside_any(m.start(), nonprose):
                    continue  # e.g. a bib/label key, not prose
                paren_spans.append((m.start(), m.end()))
                phrase = _looks_like_expansion_name(line, m.start())
                if phrase:
                    line_events.append((m.start(), {
                        "kind": "expansion", "sigla": m.group(1),
                        "phrase": phrase, "path": path, "line_no": line_no,
                    }))

            # 2. Bare sigla tokens: everything else, excluding plumbing spans,
            # the paren spans just collected, and LaTeX command names.
            exclude = nonprose + paren_spans
            for m in _SIGLA_RE.finditer(line):
                if m.start() > 0 and line[m.start() - 1] == "\\":
                    continue  # command name, e.g. \LARGE, \ABNT -- not prose
                if _inside_any(m.start(), exclude):
                    continue
                line_events.append((m.start(), {
                    "kind": "bare", "sigla": m.group(0),
                    "preceding_word": _preceding_word(line, m.start()),
                    "path": path, "line_no": line_no,
                }))

            line_events.sort(key=lambda e: e[0])
            events.extend(ev for _pos, ev in line_events)

    return events


# --- checks --------------------------------------------------------------------

def check(directory):
    """Run all checks; return a dict of category -> list of pre-formatted,
    anchored finding strings."""
    events = collect(directory)

    # First manual-expansion event index per sigla, in document order.
    first_expansion_idx = {}
    for idx, ev in enumerate(events):
        if ev["kind"] == "expansion" and ev["sigla"] not in first_expansion_idx:
            first_expansion_idx[ev["sigla"]] = idx

    findings = {"used_before": [], "manual_expansion": [], "reexpansion": [], "gender": []}
    expansions_by_sigla = {}
    genders_by_sigla = {}

    for idx, ev in enumerate(events):
        if ev["kind"] == "expansion":
            sigla = ev["sigla"]
            expansions_by_sigla.setdefault(sigla, []).append(ev)
            # Checklist: flag EVERY manual expansion, always -- even the
            # first/only/correct one -- because nothing tracks it automatically.
            findings["manual_expansion"].append(
                "`%s` — expansão manual `%s (%s)` — sinalizar sempre como "
                "ponto de atenção, mesmo quando está correta (frágil frente "
                "a `\\ac`/pacote `acro`/`acronym`)"
                % (latex_corpus.anchor(ev["path"], ev["line_no"], directory),
                   ev["phrase"], sigla)
            )
        else:  # "bare"
            sigla = ev["sigla"]
            word = ev["preceding_word"]
            if word:
                low = word.lower()
                if low in _FEMININE_ARTICLES:
                    genders_by_sigla.setdefault(sigla, []).append((ev, word, "feminino"))
                elif low in _MASCULINE_ARTICLES:
                    genders_by_sigla.setdefault(sigla, []).append((ev, word, "masculino"))
            if sigla in first_expansion_idx and idx < first_expansion_idx[sigla]:
                first_ev = events[first_expansion_idx[sigla]]
                findings["used_before"].append(
                    "`%s` — sigla `%s` usada antes de sua 1ª expansão manual "
                    "(em `%s`)"
                    % (latex_corpus.anchor(ev["path"], ev["line_no"], directory),
                       sigla,
                       latex_corpus.anchor(first_ev["path"], first_ev["line_no"], directory))
                )

    # Re-expansion: same sigla manually expanded more than once anywhere in
    # the corpus -- flagged even on a single reoccurrence (checklist note).
    for sigla in sorted(expansions_by_sigla.keys()):
        occs = expansions_by_sigla[sigla]
        if len(occs) > 1:
            anchors = ", ".join(
                "`%s`" % latex_corpus.anchor(o["path"], o["line_no"], directory)
                for o in occs
            )
            findings["reexpansion"].append(
                "sigla `%s` expandida manualmente %d vezes: %s"
                % (sigla, len(occs), anchors)
            )

    # Gender inconsistency: both a feminine and a masculine article observed
    # preceding the same sigla somewhere in the corpus.
    for sigla in sorted(genders_by_sigla.keys()):
        occs = genders_by_sigla[sigla]
        fem = [o for o in occs if o[2] == "feminino"]
        masc = [o for o in occs if o[2] == "masculino"]
        if fem and masc:
            fem_ev, fem_word, _ = fem[0]
            masc_ev, masc_word, _ = masc[0]
            findings["gender"].append(
                "sigla `%s` — gênero gramatical inconsistente: feminino "
                "(\"%s %s\") em `%s`, masculino (\"%s %s\") em `%s`"
                % (sigla, fem_word, sigla,
                   latex_corpus.anchor(fem_ev["path"], fem_ev["line_no"], directory),
                   masc_word, sigla,
                   latex_corpus.anchor(masc_ev["path"], masc_ev["line_no"], directory))
            )

    return findings


# --- output --------------------------------------------------------------------

_SECTIONS = [
    ("used_before",      "Sigla usada antes da 1ª expansão"),
    ("manual_expansion", "Expansão manual (frágil frente a `\\ac`/pacote de acrônimos)"),
    ("reexpansion",      "Reexpansão manual da mesma sigla"),
    ("gender",           "Gênero gramatical inconsistente"),
]


def main(directory):
    findings = check(directory)

    out = ["## Siglas e acrônimos — candidatos", ""]
    out.append(
        "_Sinais objetivos sobre siglas: uso em prosa antes da 1ª expansão "
        "manual, expansão manual `Nome Completo (SIGLA)` (sinalizada sempre "
        "como ponto de atenção, mesmo quando correta — frágil frente a "
        "`\\ac`/pacote `acro`/`acronym`), reexpansão manual da mesma sigla e "
        "gênero gramatical inconsistente (\"a API\" vs \"o API\"). São "
        "candidatos, não vereditos: o revisor decide se cada um é vício "
        "real ou uma exceção legítima._"
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
        out.append("(nenhuma sigla usada antes da expansão, expansão manual, "
                    "reexpansão ou inconsistência de gênero detectada)")

    print("\n".join(out))


if __name__ == "__main__":
    # Pin stdout to UTF-8, symmetric with latex_corpus's UTF-8 read side. A
    # piped stdout on Windows defaults to cp1252 and would crash on echoed
    # source characters outside it. Python 3.7+, stdlib only.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) != 2:
        sys.stderr.write("Uso: python3 acronym_check.py <diretório-do-projeto-latex>\n")
        sys.exit(2)
    target = sys.argv[1]
    if not os.path.isdir(target):
        sys.stderr.write("Diretório não encontrado: %s\n" % target)
        sys.exit(1)
    main(target)
