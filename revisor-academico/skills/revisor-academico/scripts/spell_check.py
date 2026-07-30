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
        proc = subprocess.run([_HUNSPELL_BIN, "-D"], capture_output=True, text=True)
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


def _clean_prose_line(raw):
    """Comment- and command-stripped prose, with residual braces/control
    symbols turned into spaces. Duplicated from (not imported off of)
    latex_corpus's private text-cleaning logic: latex_corpus deliberately
    keeps that helper private to iter_sentences, so -- mirroring
    lexicon_check.py's own documented duplication of _build_alternation_regex
    -- this script re-implements the small amount of logic it needs locally.
    Every Fase-0 script depends only on latex_corpus, never on a sibling
    script, so each one stays independently runnable/movable."""
    line = latex_corpus.strip_commands(latex_corpus.strip_comment(raw))
    line = line.replace("{", " ").replace("}", " ")
    line = _CONTROL_SYMBOL_RE.sub(" ", line)  # \%, \&, \\, ... -> space
    line = line.replace("\\", " ")
    line = line.replace("~", " ")  # LaTeX non-breaking space
    return line


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
            input=blob, capture_output=True, text=True,
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
    the manifest-scoped corpus."""
    for path in latex_corpus.find_manifest_files(directory).files:
        for line_no, word in _scan_file(path):
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

    for word in sorted(by_word.keys(), key=lambda w: (-len(by_word[w]), w.lower())):
        locs = by_word[word]
        out.append("")
        out.append("- **%s** (%d ocorrência%s)"
                   % (word, len(locs), "s" if len(locs) != 1 else ""))
        for path, line_no in locs:
            out.append("  - `%s`" % latex_corpus.anchor(path, line_no, directory))

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
