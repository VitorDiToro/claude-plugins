#!/usr/bin/env python3
# spell_check.py
#
# Objective-signal script for Portuguese spelling: runs the corpus prose
# (LaTeX commands/comments stripped) through the external `hunspell` binary
# with the pt_BR dictionary, and reports every word hunspell flags. This is
# the ONE Fase-0 script that shells out to an external process -- every
# other script is pure Python over the corpus, but there is no stdlib
# Portuguese spellchecker, so hunspell is a hard, blocking prerequisite (see
# __main__ below).
#
# Like every other Fase-0 script, this emits LOCATED CANDIDATES, never
# verdicts (parity with foreign_terms.py / lexicon_check.py / ...): hunspell
# has no notion of proper nouns, acronyms, brand names, or domain jargon, so
# a real academic report WILL surface plenty of legitimate non-dictionary
# words here (author names, "USRP", "IoT", English technical terms, ...).
# The reviewing pass, not this script, decides which candidate is a real
# typo and which is a legitimate exception.
#
# Design decisions that matter:
#
#   - `-d pt_BR` is ALWAYS passed explicitly to every hunspell invocation.
#     Never rely on hunspell's default dictionary (locale-dependent, may not
#     even be Portuguese on the machine running this script).
#
#   - Every subprocess.run(...) call to hunspell pins `encoding="utf-8",
#     errors="replace"` explicitly, alongside `text=True`. Without an
#     explicit `encoding=`, Python falls back to the LOCALE's preferred
#     encoding for both directions of the pipe -- under a non-UTF-8 locale
#     (e.g. `LC_ALL=C`, common in minimal CI containers) that is ASCII, and
#     accented Portuguese prose piped to hunspell's stdin raises an uncaught
#     UnicodeEncodeError (a ValueError subclass, NOT an OSError, so it is NOT
#     caught by the `except OSError` guards below) -- a real crash, violating
#     this layer's "never raise" contract. On Windows the locale encoding is
#     typically cp1252, which would silently mis-decode accented output
#     instead of crashing. Pinning UTF-8 (matching latex_corpus.read_text and
#     the stdout reconfigure in __main__) fixes both failure modes.
#
#   - Word -> source-line mapping. hunspell's simplest output mode, `-l`
#     ("list misspelled words, one per output line, in the order
#     encountered"), does NOT tag each flagged word with the input line it
#     came from. The richer `-a` ("ispell -a" pipe protocol) protocol *can*
#     recover that via its blank-line-per-input-line convention, but relies
#     on undocumented-here banner/terse-mode details that are hard to get
#     right without a live hunspell to test against (absent in this sandbox
#     -- see __main__ note below).
#
#     Instead, this script uses a robust, low-tech trick that depends on
#     NOTHING but the simple, well-defined `-l` contract: every prose line
#     handed to hunspell is prefixed with `_LINE_SEP_TOKEN`, a fixed,
#     letters-only nonsense string that no real dictionary will ever
#     recognise. That token is therefore GUARANTEED to be reported as
#     "misspelled" itself, in encounter order, immediately before that
#     line's other flagged words. Splitting the flat `-l` output on
#     occurrences of the token recovers per-line grouping. This also lets
#     the WHOLE FILE be checked in a SINGLE hunspell invocation (dictionary
#     loading, not per-word checking, is the dominant per-process cost), so
#     the script pays that cost once per .tex file, not once per line/word.
#
#   - Only lines whose cleaned prose contains at least one letter are sent to
#     hunspell at all (pure LaTeX-syntax lines, once commands/comments are
#     stripped, collapse to nothing and are skipped -- there's no prose to
#     check).
#
#   - hunspell is invoked with the corpus's OWN casing preserved (words are
#     not lowercased before being checked): hunspell/pt_BR handles ordinary
#     sentence-initial capitalisation on its own, matching how a human
#     speller would read the same text.
#
# IMPORTANT ENVIRONMENT NOTE (documented here on purpose): hunspell is ABSENT
# from the sandbox this script was authored in, so the actual detection path
# (scan/_scan_file/main against a real misspelling) could not be exercised
# live during development. It is covered by a test that SKIPS when
# hunspell+pt_BR is unavailable and is meant to be exercised for real at the
# project's real-project validation gate, in an environment that has
# hunspell + the pt_BR dictionary installed. What IS fully exercised here,
# in any environment, is the blocking prerequisite path: no hunspell/pt_BR
# -> actionable stderr message + exit 3, before any scanning is attempted.
#
# stdlib only except for the one `subprocess` call to the external hunspell
# binary. Cross-platform, UTF-8 pinned. Code/comments English; user-facing
# output Portuguese. Invoke: python3 spell_check.py <dir>

import os
import re
import shutil
import subprocess
import sys

import latex_corpus


_HUNSPELL_BIN = "hunspell"
_DICT = "pt_BR"

# See "Word -> source-line mapping" above. Deliberately letters-only (no
# digits) and deliberately not a real word in any language this project
# might plausibly contain, so it can never collide with a genuine flagged
# token and is never at risk of being silently skipped by any
# looks-like-a-number special-casing a dictionary/tokenizer might apply.
_LINE_SEP_TOKEN = "zzzxqkwqxzzz"

_CONTROL_SYMBOL_RE = re.compile(r"\\.")


def _hunspell_ptbr_available():
    """True when `hunspell` is on PATH AND its `-D` dictionary listing
    reports pt_BR among the available dictionaries. Checking only
    shutil.which('hunspell') is NOT enough: hunspell can be installed with
    only e.g. en_US present, which would otherwise fail silently the first
    time `-d pt_BR` is used. Never raises: any subprocess failure here is
    simply treated as 'unavailable'."""
    if shutil.which(_HUNSPELL_BIN) is None:
        return False
    try:
        proc = subprocess.run(
            [_HUNSPELL_BIN, "-D"], capture_output=True,
            text=True, encoding="utf-8", errors="replace",
        )
    except OSError:
        return False
    return _DICT in (proc.stdout + proc.stderr)


_INSTALL_HINT = (
    "hunspell (ou o dicionário pt_BR) não foi encontrado neste ambiente.\n"
    "\n"
    "Este script exige explicitamente o dicionário 'pt_BR' (nunca o dicionário\n"
    "padrão do sistema). Instale o hunspell e o dicionário pt_BR:\n"
    "\n"
    "  Debian/Ubuntu : sudo apt install hunspell hunspell-pt-br\n"
    "  Fedora/RHEL   : sudo dnf install hunspell hunspell-pt_BR\n"
    "  macOS (brew)  : brew install hunspell\n"
    "                  em seguida instale o dicionário pt_BR (ex.: baixe\n"
    "                  pt_BR.aff/pt_BR.dic do projeto LibreOffice dictionaries\n"
    "                  e copie para /usr/local/share/hunspell ou\n"
    "                  ~/Library/Spelling)\n"
    "  Windows       : instale via WSL/MSYS2 (ex.: dentro do WSL,\n"
    "                  'sudo apt install hunspell hunspell-pt-br') ou obtenha\n"
    "                  um build de hunspell com o dicionário pt_BR e adicione\n"
    "                  o executável ao PATH\n"
    "\n"
    "Depois de instalar, confirme com: hunspell -D  (deve listar 'pt_BR')\n"
)


# --- non-prose command-argument exclusion ------------------------------------
#
# latex_corpus.strip_commands() removes only the command NAME (by design --
# see latex_corpus.py's own parity note), KEEPING {...} argument text, so
# real prose survives (\textbf{antena} -> antena). That is exactly right for
# prose-bearing commands, but WRONG for structural/plumbing commands whose
# argument is not prose at all: \documentclass{article} would otherwise leak
# "article" into the spell-checked text, \label{fig:diagrama} would leak
# "fig"/"diagrama", \includegraphics{img.png} would leak "img"/"png", and so
# on -- flooding a real thesis with false spelling candidates that are
# nothing but environment names, label/ref/cite keys, and filenames.
#
# The fix: before handing a line to strip_commands, blank out (replace with
# spaces) the {...} argument of every _NONPROSE_COMMANDS occurrence, using
# the same brace-aware span-scanning approach as acronym_check.py's
# _nonprose_spans (duplicated here, not imported, for the same
# independently-runnable-script reason as the rest of this module).
# Prose-bearing commands (textbf, textit, emph, section, caption, ...) are
# NOT in this list, so their argument text is left untouched and still
# spell-checked, same as before.
_NONPROSE_COMMANDS = (
    "documentclass", "usepackage", "begin", "end",
    "label", "ref", "cref", "Cref", "eqref", "autoref",
    "cite", "citep", "citet", "citeauthor", "citeyear", "nocite",
    "includegraphics", "input", "include",
    "bibliography", "bibliographystyle",
    "newcommand", "renewcommand",
    "setcounter", "geometry", "pagestyle",
)

# Calibration change #2 (real-artifact finding: others/acronym.tex itself was
# being spell-checked as if it were prose). Acronym-DEFINITION commands are
# MULTI-ARG (\newacronym{key}{SIGLA}{Long expansion},
# \DeclareAcronym{key}{short=SIGLA,long=Long expansion}, ...): the sigla
# and/or expansion text live in a LATER brace group, not the first, so
# _NONPROSE_COMMANDS' first-arg-only blanking above is not enough. Mirrors
# acronym_check.py's own _MULTI_ARG_NONPROSE_COMMANDS handling (ALL
# consecutive {...} groups right after the command are blanked, not just the
# first) -- see _nonprose_spans below.
_MULTI_ARG_NONPROSE_COMMANDS = (
    "newacronym", "acro", "acs", "acl", "acrodef", "DeclareAcronym", "newacro",
)


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
    """If line[i] == '[', skip past the matching ']' (e.g.
    \\includegraphics[scale=0.5]{...}, \\cite[p.3]{key}). Returns the new
    index, or None if the option group is unbalanced on this line (caller
    should give up on this occurrence rather than guess)."""
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
    """Return [(start, end), ...] character spans covering non-prose argument
    text on `line`, so that text is excluded from the spell-checked prose:
      - the FIRST {...} argument of every _NONPROSE_COMMANDS occurrence
        (environment names, label/ref/cite keys, package/class/file names);
      - EVERY consecutive {...} argument of every _MULTI_ARG_NONPROSE_COMMANDS
        occurrence (acronym-definition commands whose sigla/expansion live in
        a later group, not the first -- see that tuple's comment)."""
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


def _blank_spans(line, spans):
    """Return `line` with every character inside `spans` replaced by a
    space, preserving length/positions. Applied BEFORE the generic
    comment/command/brace cleanup below, so excluded argument text never
    survives into the extracted prose."""
    if not spans:
        return line
    chars = list(line)
    n = len(chars)
    for start, end in spans:
        for i in range(start, min(end, n)):
            chars[i] = " "
    return "".join(chars)


def _clean_prose_line(raw):
    """Comment- and command-stripped prose, with non-prose command arguments
    and residual braces/control symbols turned into spaces. Duplicated from
    (not imported off of) latex_corpus's private text-cleaning logic:
    latex_corpus deliberately keeps that helper private to iter_sentences, so
    -- mirroring lexicon_check.py's own documented duplication of
    _build_alternation_regex -- this script re-implements the small amount of
    logic it needs locally. Every Fase-0 script depends only on latex_corpus,
    never on a sibling script, so each one stays independently
    runnable/movable."""
    line = latex_corpus.strip_comment(raw)
    line = _blank_spans(line, _nonprose_spans(line))
    line = latex_corpus.strip_commands(line)
    line = line.replace("{", " ").replace("}", " ")
    line = _CONTROL_SYMBOL_RE.sub(" ", line)  # \%, \&, \\, ... -> space
    line = line.replace("\\", " ")
    line = line.replace("~", " ")  # LaTeX non-breaking space
    return line


# --- acronym-noise suppression (calibration changes #1 and #3) -------------
#
# Real-artifact finding: on a real Portuguese HPC/6G thesis, hunspell/pt_BR
# flagged 765 distinct candidates, ~70% of the whole dossier, almost entirely
# acronym/technical noise (GPU, HPC, NVAIE, MIG, ...) drowning the real
# Portuguese typos this script exists to find. An all-caps token is never a
# Portuguese spelling error -- it's an acronym, adjudicated by
# acronym_check.py, not here. Single-letter and mixed-case tokens are
# deliberately NOT covered by this rule (a genuine mixed-case typo must still
# surface); a document-defined MIXED-CASE sigla is instead caught by
# _defined_siglas below.

_ALL_CAPS_ACRONYM_RE = re.compile(r"^[A-Z0-9]{2,}$")

# Calibration change #3: siglas the document DEFINES via an acronym-
# declaration command are suppressed even when not all-caps (e.g. a doc-
# defined "NvLink"-style token), which change #1 above cannot catch. Only the
# three shapes with a well-documented, unambiguous sigla position are parsed
# (the others in _MULTI_ARG_NONPROSE_COMMANDS are still excluded from prose
# by change #2 above, just not mined for a sigla here -- their argument
# shapes are not uniformly used in this project's real .tex sources, so
# guessing a brace position would be speculative):
#   - \newacronym{key}{SIGLA}{Long expansion}        -> 2nd brace group
#   - \acro{SIGLA}{Long expansion}                    -> 1st brace group
#   - \DeclareAcronym{key}{short=SIGLA,long=...}       -> `short=` value
#     inside the 2nd brace group
# Small local duplication of acronym_check.py's brace-span-scanning pattern
# (not imported off of it), per this module's own independently-runnable-
# script design note above.

_SHORT_KV_RE = re.compile(r"short\s*=\s*([^,}]+)")


def _brace_group_texts(line, i):
    """Consecutive {...} argument TEXTS starting at index i (after any
    optional [...] group has already been skipped by the caller) -- same
    brace-group scan as the _MULTI_ARG_NONPROSE_COMMANDS loop in
    _nonprose_spans, but returning the group CONTENTS, not just spans."""
    texts = []
    while True:
        span, i = _brace_group_after(line, i)
        if span is None:
            break
        start, end = span
        texts.append(line[start:end])
        i = _skip_ws(line, i)
    return texts


def _defined_siglas(directory):
    """Set of siglas the document itself DEFINES via \\newacronym, \\acro or
    \\DeclareAcronym, scanned once per corpus (see comment above for which
    brace group holds the sigla for each). Comment-stripped lines only; never
    raises -- malformed/unbalanced braces on a line simply yield fewer/no
    groups, never a crash."""
    siglas = set()
    for path in latex_corpus.find_manifest_files(directory).files:
        for raw in latex_corpus.read_text(path).split("\n"):
            line = latex_corpus.strip_comment(raw)
            if not line.strip():
                continue
            for cmd in ("newacronym", "acro", "DeclareAcronym"):
                for m in re.finditer(r"\\%s\*?\b" % re.escape(cmd), line):
                    i = _skip_optional_option(line, _skip_ws(line, m.end()))
                    if i is None:
                        continue
                    texts = _brace_group_texts(line, i)
                    if cmd == "newacronym" and len(texts) >= 2:
                        siglas.add(texts[1].strip())
                    elif cmd == "acro" and len(texts) >= 1:
                        siglas.add(texts[0].strip())
                    elif cmd == "DeclareAcronym" and len(texts) >= 2:
                        kv = _SHORT_KV_RE.search(texts[1])
                        if kv:
                            siglas.add(kv.group(1).strip())
    return siglas


def _is_acronym_noise(word, defined_siglas):
    """True when `word` must never be reported as a spelling candidate
    because it's acronym-shaped (change #1) or is a sigla this very document
    defines (change #3)."""
    if _ALL_CAPS_ACRONYM_RE.match(word):
        return True
    return word in defined_siglas


def _scan_file(path):
    """Yield (line_no, word) for every hunspell-flagged token in `path`,
    using a SINGLE hunspell invocation for the whole file (see module
    docstring for the line-separator-token design). Never raises: any
    subprocess failure here simply yields no findings for this file."""
    prose_lines = []  # [(line_no, cleaned_prose), ...] -- only lines with letters
    for line_no, raw in enumerate(latex_corpus.read_text(path).split("\n"), 1):
        cleaned = _clean_prose_line(raw)
        if any(c.isalpha() for c in cleaned):
            prose_lines.append((line_no, cleaned))
    if not prose_lines:
        return

    blob = "\n".join(
        "%s %s" % (_LINE_SEP_TOKEN, cleaned) for _, cleaned in prose_lines
    )
    try:
        proc = subprocess.run(
            [_HUNSPELL_BIN, "-d", _DICT, "-l"],
            input=blob, capture_output=True,
            text=True, encoding="utf-8", errors="replace",
        )
    except OSError:
        return

    idx = -1
    for token in proc.stdout.split("\n"):
        token = token.strip()
        if not token:
            continue
        if token == _LINE_SEP_TOKEN:
            idx += 1
            continue
        # A flagged token before the first separator should never happen
        # (the separator is always the first word fed per line); dropped
        # defensively rather than raising or mis-attributing it.
        if 0 <= idx < len(prose_lines):
            yield prose_lines[idx][0], token


def scan(directory):
    """Yield (file, line_no, word) for every hunspell-flagged token across
    the manifest-scoped corpus, EXCLUDING acronym-shaped tokens and siglas
    the document itself defines (calibration changes #1 and #3 -- see
    _is_acronym_noise)."""
    defined_siglas = _defined_siglas(directory)
    for path in latex_corpus.find_manifest_files(directory).files:
        for line_no, word in _scan_file(path):
            if _is_acronym_noise(word, defined_siglas):
                continue
            yield path, line_no, word


def main(directory):
    out = ["## Ortografia (hunspell pt_BR) — candidatos", ""]
    out.append(
        "_Sinal objetivo de ortografia via hunspell (`-d pt_BR`) sobre a prosa "
        "(comandos/comentários LaTeX removidos) — candidatos, não vereditos. "
        "Nomes próprios, siglas, estrangeirismos legítimos e jargão técnico vão "
        "aparecer aqui normalmente; o revisor decide, caso a caso, o que é erro "
        "real e o que é exceção legítima._"
    )
    out.append("")

    # Group by word (surface form) so repeated occurrences read as one entry
    # with all its locations, mirroring foreign_terms' by-term grouping.
    by_word = {}
    for path, line_no, word in scan(directory):
        by_word.setdefault(word, []).append((path, line_no))

    if not by_word:
        out.append("(nenhum candidato de ortografia encontrado)")
        print("\n".join(out))
        return

    # Calibration change #4: one bullet per candidate -- word, total
    # occurrence count, and the FIRST anchor only (not a per-occurrence
    # anchor list, which is what turned a single "GPU" candidate into 107
    # lines on the real-artifact run). `locs` is already in document order
    # (manifest file order, then increasing line number), so locs[0] IS the
    # first occurrence.
    for word in sorted(by_word.keys(), key=lambda w: (-len(by_word[w]), w.lower())):
        locs = by_word[word]
        first_path, first_line = locs[0]
        out.append("")
        out.append(
            "- **%s** (%d ocorrência%s) — `%s`"
            % (word, len(locs), "s" if len(locs) != 1 else "",
               latex_corpus.anchor(first_path, first_line, directory))
        )

    print("\n".join(out))


if __name__ == "__main__":
    # Pin stdout to UTF-8, symmetric with latex_corpus's UTF-8 read side. A
    # piped stdout on Windows defaults to cp1252 and would crash on echoed
    # source characters outside it. Python 3.7+, stdlib only.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) != 2:
        sys.stderr.write("Uso: python3 spell_check.py <diretório-do-projeto-latex>\n")
        sys.exit(2)
    target = sys.argv[1]
    if not os.path.isdir(target):
        sys.stderr.write("Diretório não encontrado: %s\n" % target)
        sys.exit(1)
    # Blocking prerequisite: hunspell + pt_BR MUST be available (checked
    # here, in __main__, so this script also fails fast when run standalone;
    # build_dossier does the equivalent check for the orchestrated run --
    # Task 8).
    if not _hunspell_ptbr_available():
        sys.stderr.write(_INSTALL_HINT)
        sys.exit(3)
    main(target)
