#!/usr/bin/env python3
# foreign_terms.py
#
# Objective-signal script for the "italics on foreign terms" rule of the
# academic-report reviewer. ABNT (and most institutional templates) require
# English/foreign words used as running prose to be set in italics
# (\textit{...} or \emph{...}). This script finds, with 100% recall over a
# fixed glossary, every occurrence of a known foreign term that is NOT wrapped
# in an italic command -- the check a semantic pass used to do twice, once per
# reviewer, at the cost of two full corpus reads.
#
# It emits LOCATED CANDIDATES, never verdicts (parity with text_analysis.py and
# pattern_profile.py): the reviewing pass decides whether a flagged occurrence
# is a real vice or a legitimate exception. The glossary is meant to grow across
# reviews -- unknown terms surfaced by a semantic pass get fed back into
# GLOSSARY here, and the next run catches them mechanically.
#
# Design decisions that matter:
#   - We must inspect the source WITH commands intact, because the signal we
#     need (is this word inside \textit{...}?) lives in the command that
#     latex_corpus.strip_commands() would delete. So this script does its own
#     brace-aware scan over comment-stripped raw lines, and does NOT reuse the
#     command-stripping helpers.
#   - Matching is case-insensitive and word-boundary anchored, but the reported
#     text preserves the source casing.
#   - A term already inside \textit{}, \emph{}, \textsl{}, or \foreignlanguage{}
#     is considered CORRECT and is not flagged. Proper nouns / brands in the
#     WHITELIST are never flagged (Python, GitHub, Docker, ...), matching the
#     SKILL.md exception.
#
# Cross-platform, stdlib only, UTF-8 pinned on stdout. Code/comments English;
# user-facing output Portuguese. Invoke: python3 foreign_terms.py <dir>

import os
import re
import sys

import latex_corpus


# --- Glossary of foreign (mostly English) terms that require italics ---------
#
# Lowercased, matched case-insensitively. Multi-word entries are matched as a
# phrase (whitespace-flexible). This list is intentionally editable: the whole
# point of the mechanical layer is that adding a term here gives it 100% recall
# on the next run. Keep entries that are genuinely foreign PROSE; do NOT add
# proper nouns, product names, or brands -- those go in WHITELIST below.
GLOSSARY = {
    # software / method vocabulary commonly left un-italicised in pt-BR reports
    "framework", "frameworks", "backend", "back-end", "frontend", "front-end",
    "deploy", "deployment", "pipeline", "pipelines", "build", "builds",
    "release", "releases", "commit", "commits", "branch", "branches",
    "merge", "pull request", "issue", "issues", "bug", "bugs", "patch",
    "patches", "hardware", "software", "firmware", "middleware",
    "dataset", "datasets", "benchmark", "benchmarks", "baseline", "baselines",
    "overhead", "overflow", "buffer", "cache", "caching", "thread", "threads",
    "kernel", "kernels", "driver", "drivers", "socket", "sockets",
    "throughput", "latency", "downlink", "uplink", "handover", "handshake",
    "oversampling", "downsampling", "upsampling", "clock", "timestamp",
    "log", "logs", "logging", "token", "tokens", "endpoint", "endpoints",
    "framework", "workflow", "workflows", "workaround", "template", "templates",
    "wrapper", "wrappers", "callback", "callbacks", "feedback", "loopback",
    "default", "defaults", "trade-off", "tradeoff", "trade-offs",
    "state-of-the-art", "state of the art", "know-how",
    "e-mail", "email", "online", "offline", "real-time", "realtime",
    "chip", "chips", "layout", "setup", "set-up", "backup", "back-up",
    "script", "scripts", "scripting", "loop", "loops", "array", "arrays",
    "bit", "bits", "byte", "bytes", "clusters", "cluster", "clusters",
    "spread spectrum", "bitstream", "datapath", "testbed", "testbench",
    # research-writing vocabulary
    "paper", "papers", "abstract", "background", "insight", "insights",
    "survey", "review", "trade-off", "state-of-the-art",
}

# Terms that are English but are proper nouns / brands / product or language
# names -- explicitly NOT italicised even in prose (SKILL.md exception).
# Matched case-insensitively too, so "python" as a bare word is skipped; this
# means a term must not live in BOTH sets. WHITELIST wins.
WHITELIST = {
    "python", "github", "gitlab", "docker", "kubernetes", "linux", "windows",
    "macos", "ubuntu", "debian", "fedora", "git", "bash", "powershell",
    "latex", "tex", "overleaf", "matlab", "simulink", "gnu", "gnu radio",
    "gnuradio", "usrp", "intel", "arm", "nvidia", "amd", "arduino",
    "raspberry pi", "tensorflow", "pytorch", "numpy", "scipy", "pandas",
    "wireshark", "verilog", "vhdl", "fpga", "asic", "inatel", "anthropic",
    "claude", "openai", "google", "microsoft", "apple", "amazon", "aws",
    "azure", "ieee", "acm", "abnt", "iso", "rfc", "nist", "owasp",
}

# Italic-bearing commands: an occurrence sitting inside any of these {...}
# groups is CORRECT and must not be flagged.
_ITALIC_COMMANDS = ("textit", "emph", "textsl", "foreignlanguage")


def _build_term_regex(terms):
    """One case-insensitive, word-boundary-anchored alternation for all terms.

    Longer terms first so 'front-end' wins over 'front'. Internal whitespace in
    multi-word entries is made flexible (\\s+) so a line break between the words
    still matches. Hyphens and other regex metachars are escaped, then the
    escaped space is relaxed back to \\s+."""
    if not terms:
        return None
    ordered = sorted(terms, key=len, reverse=True)
    alts = []
    for term in ordered:
        escaped = re.escape(term)
        # re.escape turns a space into '\ '; relax it to match any run of space.
        escaped = escaped.replace(r"\ ", r"\s+")
        alts.append(escaped)
    # \b word boundaries; the accented pt-BR set isn't a concern here because
    # the terms themselves are ASCII, and \b sits between \w and non-\w.
    pattern = r"(?<![\w-])(?:%s)(?![\w-])" % "|".join(alts)
    return re.compile(pattern, re.IGNORECASE)


# Match a whole italic command and capture its {...} argument span so we can
# tell whether a term occurrence falls inside it. Brace-aware to ONE level of
# nesting (enough for real prose like \textit{spread spectrum}); deeper nesting
# is rare in a foreign-term wrap and degrades safely to "not covered".
def _italic_spans(line):
    """Return a list of (start, end) character spans covered by an italic
    command's argument on this line. Approximate: single-level brace matching."""
    spans = []
    for cmd in _ITALIC_COMMANDS:
        # \foreignlanguage takes TWO args: \foreignlanguage{english}{term}.
        # We approximate by covering the LAST {...} after the command name.
        for m in re.finditer(r"\\%s\b" % cmd, line):
            i = m.end()
            n = len(line)
            # skip an optional first brace group for foreignlanguage's language arg
            if cmd == "foreignlanguage":
                i = _skip_ws(line, i)
                if i < n and line[i] == "{":
                    i = _match_brace(line, i)
                    if i is None:
                        continue
            i = _skip_ws(line, i)
            if i < n and line[i] == "{":
                start = i + 1
                end = _match_brace(line, i)
                if end is not None:
                    # end points PAST the closing brace; content is [start, end-1)
                    spans.append((start, end - 1))
    return spans


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


def _inside_any(pos, spans):
    """True if character index `pos` falls within any (start, end) span."""
    for start, end in spans:
        if start <= pos < end:
            return True
    return False


def scan(directory):
    """Yield (file, line_no, term_text, covered) for every glossary-term
    occurrence, where `covered` is True when it already sits inside an italic
    command. Whitelisted terms are skipped entirely."""
    term_re = _build_term_regex(GLOSSARY)
    if term_re is None:
        return
    white_re = _build_term_regex(WHITELIST)

    for path in latex_corpus.find_manifest_files(directory).files:
        for line_no, raw in enumerate(latex_corpus.read_text(path).split("\n"), 1):
            # Strip the comment tail so a term mentioned in a % comment is not
            # flagged, mirroring every other objective script.
            line = latex_corpus.strip_comment(raw)
            if not line.strip():
                continue
            italic = _italic_spans(line)
            for m in term_re.finditer(line):
                # Skip if this same span is a whitelisted proper noun/brand.
                if white_re is not None and white_re.fullmatch(m.group(0)):
                    continue
                covered = _inside_any(m.start(), italic)
                yield path, line_no, m.group(0), covered


def main(directory):
    out = ["## Termos estrangeiros sem itálico (candidatos)", ""]
    out.append("_Sinal objetivo sobre glossário fixo — o revisor decide se cada ocorrência é "
               "vício real ou exceção legítima (nome próprio, marca, citação). Nomes próprios e "
               "marcas conhecidas já são ignorados automaticamente._")
    out.append("")

    # Group by term (lowercased) so the reviewer sees consistency per term:
    # if a term appears 8x and 2 of them lack italics, that pattern is the
    # actionable signal, not each hit in isolation.
    by_term = {}
    for path, line_no, text, covered in scan(directory):
        key = text.lower()
        rec = by_term.setdefault(key, {"total": 0, "missing": []})
        rec["total"] += 1
        if not covered:
            rec["missing"].append((path, line_no, text))

    # Only terms that have at least one un-italicised occurrence are worth
    # reporting. Order by number of missing occurrences (desc), then term.
    reportable = [(k, v) for k, v in by_term.items() if v["missing"]]
    if not reportable:
        out.append("(nenhum termo do glossário aparece sem itálico)")
        print("\n".join(out))
        return

    reportable.sort(key=lambda kv: (-len(kv[1]["missing"]), kv[0]))

    for term, rec in reportable:
        total = rec["total"]
        missing = rec["missing"]
        italic_count = total - len(missing)
        # A term that is italicised somewhere but not here is the strongest
        # signal (inconsistency within the same document); flag that explicitly.
        if italic_count > 0:
            note = (" — **inconsistente**: %d de %d ocorrências já usam itálico"
                    % (italic_count, total))
        else:
            note = " — nenhuma ocorrência usa itálico (%d no total)" % total
        out.append("")
        out.append("- **%s** (%d sem itálico)%s" % (term, len(missing), note))
        for path, line_no, text in missing:
            out.append("  - `%s` — `%s`" % (latex_corpus.anchor(path, line_no, directory), text))

    print("\n".join(out))


if __name__ == "__main__":
    # Pin stdout to UTF-8, symmetric with latex_corpus's UTF-8 read side. A
    # piped stdout on Windows defaults to cp1252 and would crash on echoed
    # source characters outside it. Python 3.7+, stdlib only.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) != 2:
        sys.stderr.write("Uso: python3 foreign_terms.py <diretório-do-projeto-latex>\n")
        sys.exit(2)
    target = sys.argv[1]
    if not os.path.isdir(target):
        sys.stderr.write("Diretório não encontrado: %s\n" % target)
        sys.exit(1)
    main(target)
