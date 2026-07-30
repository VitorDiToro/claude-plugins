#!/usr/bin/env python3
# lexicon_check.py
#
# Objective-signal script bundling four mechanical, low-cost checklist items
# that are all about lexical/orthographic HABITS rather than grammar in the
# deep sense: the "Tom" superlatives/coloquialismos rule, the "Unidades e
# formatos" decimal-separator rule, and a small curated crase-error pattern
# list, plus a spelling-consistency check (same term written two different
# ways across the document). Everything here is a LOCATED CANDIDATE, never a
# verdict (parity with every other Fase-0 script): a flagged "revolucionária"
# may be inside a legitimate quote; a flagged "à medida" may turn out fine in
# context. The reviewing pass decides.
#
# Checks emitted:
#   1. Superlatives/marketing wording and colloquialisms, matched against a
#      small curated list (grows over time, like foreign_terms.GLOSSARY).
#      EVERY occurrence is signalled (unlike foreign_terms, there is no
#      "already correct" state to filter against here).
#   2. Crase in a SMALL set of known error-prone patterns: "à cada", "à
#      partir", and "à medida" NOT followed by "que" (the fixed, correct
#      expression is "à medida que"; "à medida" alone is flagged). This is
#      deliberately NOT a general crase grammar checker -- just the patterns
#      the checklist calls out.
#   3. Decimal-separator inconsistency: numbers using a comma decimal (3,5)
#      and numbers using a dot decimal (4.2) both appearing in the same
#      corpus. Thousands-grouping (1.234.567 / 1,234,567 / the mixed
#      Brazilian 1.234,56) is deliberately excluded from this signal -- see
#      _NUMBER_RE / _is_probable_thousands_group below for the heuristic and
#      its known limitation.
#   4. Divergent spellings of the same term: normalized (lowercased, hyphens
#      stripped) to the same key but written 2+ distinct surface ways in the
#      corpus (front-end/frontend, GitHub/Github). To avoid flooding on
#      ordinary sentence-initial capitalization ("Este"/"este"), a normalized
#      key is only tracked at all when AT LEAST ONE of its surface forms is
#      "structurally interesting" -- contains a hyphen, or an internal
#      (non-initial) capital letter. See _is_interesting_token.
#
# stdlib only, cross-platform, UTF-8 pinned. Reuses latex_corpus for
# manifest-scoped discovery, reading, comment stripping, and anchoring (the
# ONLY way a location string is built here). Code/comments English; output
# Portuguese. Invoke: python3 lexicon_check.py <dir>

import os
import re
import sys

import latex_corpus


# --- 1. Superlatives / marketing wording / colloquialisms -------------------
#
# Two curated buckets, reported under one combined section (both are "Tom"
# register issues per the checklist). Deliberately NOT included, to keep the
# false-positive rate low: words with a common, legitimate TECHNICAL meaning
# in engineering/science prose even though they can also read as superlatives
# in marketing copy -- "ideal" (gás ideal, condição ideal), "único" (valor
# único, solução única no sentido de "only one"), "perfeito" (número
# perfeito, quadrado perfeito), "estado da arte" (a standard academic phrase
# for "state of the art", not a marketing claim). Only words/phrases that are
# overwhelmingly superlative/marketing IN PRACTICE made the cut.
SUPERLATIVE_TERMS = {
    "revolucionário", "revolucionária", "revolucionários", "revolucionárias",
    "incrível", "incríveis",
    "inovador", "inovadora", "inovadores", "inovadoras",
    "extraordinário", "extraordinária", "extraordinários", "extraordinárias",
    "fantástico", "fantástica", "fantásticos", "fantásticas",
    "sensacional", "sensacionais",
    "espetacular", "espetaculares",
    "surpreendente", "surpreendentes",
    "imbatível", "imbatíveis",
    "insuperável", "insuperáveis",
    "de ponta",
    "melhor do mundo",
    "o melhor do mercado",
}

# Colloquial hedges/affirmations: informal register, out of place in ABNT
# academic prose, but each is a single common word/phrase, low ambiguity.
COLLOQUIAL_TERMS = {
    "simplesmente",
    "obviamente",
    "definitivamente",
    "com certeza",
    "é claro que",
    "óbvio que",
    "na real",
}

_LEXICON_CATEGORY = {}
for _t in SUPERLATIVE_TERMS:
    _LEXICON_CATEGORY[_t] = "marketing/superlativo"
for _t in COLLOQUIAL_TERMS:
    _LEXICON_CATEGORY[_t] = "coloquialismo"


def _build_alternation_regex(terms):
    """One case-insensitive, word-boundary-anchored alternation for all
    `terms` (words or whitespace-flexible phrases). Longer terms first so a
    multi-word phrase wins over a shorter word it contains. Mirrors
    foreign_terms._build_term_regex; duplicated here (not imported) because
    each Fase-0 script only depends on latex_corpus, never on a sibling
    script, so scripts stay independently runnable/movable."""
    if not terms:
        return None
    ordered = sorted(terms, key=len, reverse=True)
    alts = []
    for term in ordered:
        escaped = re.escape(term)
        escaped = escaped.replace(r"\ ", r"\s+")
        alts.append(escaped)
    pattern = r"(?<![\w-])(?:%s)(?![\w-])" % "|".join(alts)
    return re.compile(pattern, re.IGNORECASE)


_LEXICON_RE = _build_alternation_regex(SUPERLATIVE_TERMS | COLLOQUIAL_TERMS)


def _scan_lexicon(directory):
    """Yield (path, line_no, matched_text) for every superlative/colloquial
    occurrence. Comment-stripped prose only (mirrors every other objective
    script); commands are NOT stripped -- these are plain words/phrases and a
    surrounding \\textbf{...} does not change whether the word itself is a
    superlative."""
    if _LEXICON_RE is None:
        return
    for path in latex_corpus.find_manifest_files(directory).files:
        for line_no, raw in enumerate(latex_corpus.read_text(path).split("\n"), 1):
            line = latex_corpus.strip_comment(raw)
            if not line.strip():
                continue
            for m in _LEXICON_RE.finditer(line):
                yield path, line_no, m.group(0)


# --- 2. Crase in known error-prone patterns ----------------------------------
#
# A SMALL, curated pattern list -- not a general crase grammar. Each simple
# pattern names the erroneous phrase and the commonly correct alternative.
_CRASE_SIMPLE_PATTERNS = [
    ("à cada", re.compile(r"\bà\s+cada\b", re.IGNORECASE),
     'crase provavelmente incorreta -- a forma comum é "a cada"'),
    ("à partir", re.compile(r"\bà\s+partir\b", re.IGNORECASE),
     'crase provavelmente incorreta -- a forma comum é "a partir"'),
]

# "à medida que" is the correct, fixed expression. "à medida" NOT followed by
# "que" is the candidate (it may be a truncated/incorrect use of that same
# expression, or crase misapplied to a different construction entirely).
_A_MEDIDA_RE = re.compile(r"\bà\s+medida\b(?!\s+que\b)", re.IGNORECASE)


def _scan_crase(directory):
    """Yield (path, line_no, matched_text, note) for every crase-pattern
    candidate. Line-based (like every other Fase-0 scan): a phrase split
    across a line break is not caught -- an accepted limitation of a
    line-oriented signal layer, not a correctness bug."""
    for path in latex_corpus.find_manifest_files(directory).files:
        for line_no, raw in enumerate(latex_corpus.read_text(path).split("\n"), 1):
            line = latex_corpus.strip_comment(raw)
            if not line.strip():
                continue
            for _label, pattern, note in _CRASE_SIMPLE_PATTERNS:
                for m in pattern.finditer(line):
                    yield path, line_no, m.group(0), note
            for m in _A_MEDIDA_RE.finditer(line):
                yield (path, line_no, m.group(0),
                       'sem "que" em seguida -- a locução correta é "à medida que"')


# --- 3. Decimal-separator inconsistency ---------------------------------------
#
# A number token is any digit run possibly interspersed with '.'/',' as
# separators (e.g. "3,5", "4.2", "1.234.567", "1.234,56", "1,234.56").
_NUMBER_RE = re.compile(r"\d+(?:[.,]\d+)*")

# Within a matched number token, split back into (separator, digits-after-it)
# pairs so each individual separator use can be judged on its own -- this is
# what correctly handles a mixed-convention number like "1.234,56" (dot for
# thousands grouping, comma for the real decimal): the dot group has exactly
# 3 digits after it (thousands signature) and is excluded; the comma group
# has 2 (a real decimal) and is counted.
_SEPARATOR_GROUP_RE = re.compile(r"([.,])(\d+)")


def _decimal_events(number_token):
    """Yield (separator, digits_after) for each separator inside a matched
    number token, e.g. "1.234,56" -> [(".", "234"), (",", "56")]."""
    for m in _SEPARATOR_GROUP_RE.finditer(number_token):
        yield m.group(1), m.group(2)


def _is_probable_decimal(digits_after):
    """A separator is treated as a DECIMAL point (not thousands grouping)
    when the digit run after it is NOT exactly 3 digits. Thousands grouping
    (Brazilian '.' or English/international ',') always groups in runs of
    exactly 3; a genuine decimal fraction in running prose is overwhelmingly
    1-2 digits (occasionally 4+, e.g. a measured constant). KNOWN LIMITATION:
    a true 3-decimal-digit value (e.g. "3.142" for pi) is silently excluded
    by this heuristic rather than risk misreading a thousands-grouped count
    (a much more common pattern in academic prose: sample sizes, populations,
    byte counts) as a spurious decimal-style disagreement."""
    return len(digits_after) != 3


def _scan_decimals(directory):
    """Yield (path, line_no, number_text, separator) for every number token
    whose separator is judged a real decimal point (see _is_probable_decimal).
    `separator` is "," or "."."""
    for path in latex_corpus.find_manifest_files(directory).files:
        for line_no, raw in enumerate(latex_corpus.read_text(path).split("\n"), 1):
            line = latex_corpus.strip_comment(raw)
            if not line.strip():
                continue
            for m in _NUMBER_RE.finditer(line):
                token = m.group(0)
                if "." not in token and "," not in token:
                    continue
                for sep, digits_after in _decimal_events(token):
                    if _is_probable_decimal(digits_after):
                        yield path, line_no, token, sep


# --- 4. Divergent spellings of the same term ---------------------------------
#
# A "token" here is a run of letters, possibly hyphen-joined (front-end,
# state-of-the-art). Minimum length (letters only, hyphens excluded) filters
# out trivial short tokens that are unlikely to carry a real spelling
# question and are more likely math/notation noise (single letters, "x-y").
_SPELLING_TOKEN_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ]+(?:-[A-Za-zÀ-ÖØ-öø-ÿ]+)*")
_MIN_SPELLING_LEN = 4


def _is_interesting_token(token):
    """True if `token` is structurally distinctive enough to justify tracking
    its normalized key at all: it has an internal hyphen (front-end) or an
    internal (non-initial) capital letter (GitHub). Plain words that only
    differ by ordinary sentence-initial capitalization ("Este"/"este") never
    satisfy this on their own, so a key built purely from that kind of pair is
    never even opened -- the false-positive guard that keeps this check from
    flagging half the nouns in the document."""
    if "-" in token:
        return True
    return any(c.isupper() for c in token[1:])


def _scan_spelling_groups(directory):
    """Return {normalized_key: {surface_form: [(path, line_no), ...]}} for
    every normalized key that has at least one "interesting" occurrence
    (see _is_interesting_token). Words/commands are extracted from
    comment-AND-command-stripped text (unlike the other three scans in this
    module): a bare macro like "\\LaTeX" or a command name like "textbf" would
    otherwise itself become a tracked token and pollute this specific check
    with LaTeX-syntax artifacts that have nothing to do with prose spelling.
    latex_corpus.strip_commands() already exists for exactly this purpose
    (parity with tokenize_words); reusing it here is not a change to
    latex_corpus.py, just a second caller of a function it already exports."""
    groups = {}
    for path in latex_corpus.find_manifest_files(directory).files:
        for line_no, raw in enumerate(latex_corpus.read_text(path).split("\n"), 1):
            line = latex_corpus.strip_commands(latex_corpus.strip_comment(raw))
            if not line.strip():
                continue
            for m in _SPELLING_TOKEN_RE.finditer(line):
                token = m.group(0)
                letters_only = token.replace("-", "")
                if len(letters_only) < _MIN_SPELLING_LEN:
                    continue
                key = token.lower().replace("-", "")
                rec = groups.setdefault(key, {"surface": {}, "gated": False})
                rec["surface"].setdefault(token, []).append((path, line_no))
                if _is_interesting_token(token):
                    rec["gated"] = True
    # Only keys that are gated AND have 2+ distinct surface spellings are
    # real candidates.
    return {
        key: rec for key, rec in groups.items()
        if rec["gated"] and len(rec["surface"]) >= 2
    }


# --- output ------------------------------------------------------------------

def main(directory):
    out = ["## Léxico, crase e formatos — candidatos", ""]
    out.append("_Sinais objetivos de léxico: superlativos/marketing e coloquialismos "
               "(lista curada), padrões conhecidos de erro de crase, inconsistência de "
               "separador decimal e grafias divergentes do mesmo termo. Candidatos, não "
               "vereditos -- o revisor decide se cada ocorrência é vício real ou um uso "
               "legítimo (ex.: citação direta, termo técnico)._")
    out.append("")

    any_finding = False

    # --- Section 1: superlatives / colloquialisms ---
    by_term = {}
    for path, line_no, text in _scan_lexicon(directory):
        key = text.lower()
        rec = by_term.setdefault(key, {"category": _LEXICON_CATEGORY.get(key, ""),
                                        "occ": []})
        rec["occ"].append((path, line_no, text))

    if by_term:
        any_finding = True
        out.append("### Superlativos, marketing e coloquialismos")
        for key in sorted(by_term.keys()):
            rec = by_term[key]
            occs = rec["occ"]
            out.append("")
            out.append("- **%s** (%s, %d ocorrência%s)"
                       % (key, rec["category"], len(occs), "s" if len(occs) != 1 else ""))
            for path, line_no, text in occs:
                out.append("  - `%s` — `%s`" % (latex_corpus.anchor(path, line_no, directory), text))
        out.append("")

    # --- Section 2: crase ---
    crase_items = sorted(_scan_crase(directory), key=lambda t: (t[0], t[1], t[2]))
    if crase_items:
        any_finding = True
        out.append("### Possíveis erros de crase")
        for path, line_no, text, note in crase_items:
            out.append("- `%s` — `%s` (%s)"
                       % (latex_corpus.anchor(path, line_no, directory), text, note))
        out.append("")

    # --- Section 3: decimal-separator inconsistency ---
    comma_hits = []
    dot_hits = []
    for path, line_no, token, sep in _scan_decimals(directory):
        (comma_hits if sep == "," else dot_hits).append((path, line_no, token))

    if comma_hits and dot_hits:
        any_finding = True
        comma_note = " (minoritário)" if len(comma_hits) < len(dot_hits) else ""
        dot_note = " (minoritário)" if len(dot_hits) < len(comma_hits) else ""
        out.append("### Separador decimal inconsistente")
        out.append("")
        out.append("- **Vírgula decimal** (%d ocorrência%s)%s"
                   % (len(comma_hits), "s" if len(comma_hits) != 1 else "", comma_note))
        for path, line_no, token in sorted(comma_hits, key=lambda t: (t[0], t[1])):
            out.append("  - `%s` — `%s`" % (latex_corpus.anchor(path, line_no, directory), token))
        out.append("- **Ponto decimal** (%d ocorrência%s)%s"
                   % (len(dot_hits), "s" if len(dot_hits) != 1 else "", dot_note))
        for path, line_no, token in sorted(dot_hits, key=lambda t: (t[0], t[1])):
            out.append("  - `%s` — `%s`" % (latex_corpus.anchor(path, line_no, directory), token))
        out.append("")

    # --- Section 4: divergent spellings ---
    spelling_groups = _scan_spelling_groups(directory)
    if spelling_groups:
        any_finding = True
        out.append("### Grafias divergentes do mesmo termo")
        for key in sorted(spelling_groups.keys()):
            rec = spelling_groups[key]
            variants = " / ".join(sorted(rec["surface"].keys()))
            out.append("")
            out.append("- **%s** — grafias divergentes: %s" % (key, variants))
            for surface in sorted(rec["surface"].keys()):
                locs = rec["surface"][surface]
                anchors = ", ".join(
                    "`%s`" % latex_corpus.anchor(p, l, directory) for p, l in locs
                )
                out.append("  - `%s` (%dx): %s" % (surface, len(locs), anchors))
        out.append("")

    if not any_finding:
        out.append("(nenhum problema de léxico, crase ou formato detectado)")

    print("\n".join(out))


if __name__ == "__main__":
    # Pin stdout to UTF-8, symmetric with latex_corpus's UTF-8 read side. A
    # piped stdout on Windows defaults to cp1252 and would crash on echoed
    # source characters outside it. Python 3.7+, stdlib only.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) != 2:
        sys.stderr.write("Uso: python3 lexicon_check.py <diretório-do-projeto-latex>\n")
        sys.exit(2)
    target = sys.argv[1]
    if not os.path.isdir(target):
        sys.stderr.write("Diretório não encontrado: %s\n" % target)
        sys.exit(1)
    main(target)
