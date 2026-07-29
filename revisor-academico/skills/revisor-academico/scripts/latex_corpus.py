#!/usr/bin/env python3
# latex_corpus.py
#
# Shared, importable corpus module for the objective-signal layer.
# Recursively collects .tex files from a project directory and exposes helpers
# to read them (UTF-8, CRLF-tolerant), strip LaTeX comments/commands, and
# tokenize the running text into words and (approximate) sentences.
#
# Cross-platform requirements baked in on purpose (the marketplace is installed
# on arbitrary Windows/Linux machines):
#   - explicit UTF-8 decoding with errors="replace" (Windows default may be cp1252);
#   - os.walk / pathlib for traversal (no shell globbing);
#   - text-mode reads with universal newlines (tolerate Windows CRLF);
#   - stdlib only (os, pathlib, re, sys, collections, difflib) -- no pip, no shell.
#
# Parity note with the former frequencia-lexical.sh: command stripping removes
# only the command NAME (and an optional [...] option group), but KEEPS the
# {...} argument text, so real prose survives (\textbf{antena} -> antena).
# Code identifiers and comments are English; user-facing output (produced by the
# entry scripts, not here) is Portuguese.

import os
import re
from collections import namedtuple

# A sentence anchored to its source location, so signals are actionable.
Sentence = namedtuple("Sentence", ["text", "norm", "file", "line"])

# Letters accepted as part of a word: ASCII plus the accented set used by the
# former frequencia-lexical.sh (matched AFTER lowercasing).
_WORD_RE = re.compile(r"[a-záéíóúâêôãõàüç]+")

# Comment stripping, mirroring the sed 's/(^|[^\\])%.*/\1/' of the .sh:
# a '%' starts a comment unless the char immediately before it is a backslash
# (escaped \%). Only the first unescaped '%' on the line matters (greedy to EOL).
_COMMENT_RE = re.compile(r"(^|[^\\])%.*")

# Command stripping: remove "\name", an optional trailing '*', and an optional
# following "[...]" option group; KEEP any following "{...}" argument text.
_COMMAND_RE = re.compile(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?")

# Residual LaTeX control symbols (\%, \&, \_, \#, \\, ...) left after command
# stripping. Only used when cleaning text for sentences (not for word parity).
_CONTROL_SYMBOL_RE = re.compile(r"\\.")

_MULTISPACE_RE = re.compile(r"[ \t]+")

# Non-alphanumeric (keep letters/digits/space) for sentence NORMALIZATION used
# by the boilerplate similarity check.
_NON_WORD_RE = re.compile(r"[^0-9a-záéíóúâêôãõàüçñ ]+", re.IGNORECASE)


# --- Location anchoring: the shared, executable contract -------------------
#
# Every Fase-0 script MUST anchor its findings through anchor()/project_relative
# below, never by hand-formatting "path:line". This is the single source of
# truth for what a location string looks like, so that a foreign-terms finding
# and a bib finding for the same spot produce the SAME anchor -- the invariant
# the whole dossier and every reviewing pass rely on. Hand-rolled anchoring is
# how two scripts silently disagree (1-based vs 0-based, absolute vs relative
# path) and the dossier ends up internally incoherent.
#
# Contract, fixed here so no prose spec has to describe it:
#   - line numbers are 1-based (matching iter_sentences and every enumerate(...,1));
#   - the path is made relative to the project root when a root is given, because
#     the author opens "01_intro.tex:10" in an editor, not the tmp/absolute path;
#   - the separator is a single ':'; the format is exactly "<path>:<line>".

def project_relative(path, root):
    """Return `path` relative to `root` with forward slashes, or the original
    path (normalised to forward slashes) if it isn't under `root` or `root` is
    None. Forward slashes keep anchors identical across Windows and POSIX so a
    reference dossier compares byte-for-byte on any platform."""
    normalized = path.replace("\\", "/")
    if not root:
        return normalized
    try:
        rel = os.path.relpath(path, root)
    except ValueError:
        # e.g. different drives on Windows -> not relativisable
        return normalized
    rel = rel.replace("\\", "/")
    # os.path.relpath can produce '../..' escapes; if it did, the file isn't
    # really under root, so fall back to the normalised absolute-ish path.
    if rel.startswith("../"):
        return normalized
    return rel


def anchor(path, line, root=None):
    """The one true location string: '<project-relative path>:<1-based line>'.
    All Fase-0 scripts build every anchor through this function."""
    return "%s:%d" % (project_relative(path, root), int(line))


def find_tex_files(directory):
    """Return every .tex file under `directory`, recursively, path-sorted.

    Sorting makes the traversal deterministic across platforms (unlike the
    filesystem-readdir order of the old `grep -r`)."""
    out = []
    for root, _dirs, files in os.walk(directory):
        for name in files:
            if name.endswith(".tex"):
                out.append(os.path.join(root, name))
    out.sort()
    return out


def read_text(path):
    """Read a file as UTF-8 with universal newlines; never raise on bad bytes."""
    # Text mode => \r\n and \r are normalized to \n (Windows CRLF tolerated).
    with open(path, encoding="utf-8", errors="replace", newline=None) as fh:
        return fh.read()


def strip_comment(line):
    """Remove a LaTeX line comment (first unescaped '%' to end of line)."""
    return _COMMENT_RE.sub(r"\1", line, count=1)


def strip_commands(text):
    """Remove command names + optional [...] options; keep {...} argument text."""
    return _COMMAND_RE.sub("", text)


def _clean_line_for_words(line):
    """Comment- and command-stripped line, ready for word extraction."""
    return strip_commands(strip_comment(line))


def _clean_line_for_text(line):
    """Comment/command-stripped line with braces and residual control symbols
    turned into spaces, for sentence segmentation and display."""
    line = strip_commands(strip_comment(line))
    line = line.replace("{", " ").replace("}", " ")
    line = _CONTROL_SYMBOL_RE.sub(" ", line)  # \%, \&, \\, ... -> space
    line = line.replace("\\", " ")
    line = line.replace("~", " ")             # LaTeX non-breaking space
    return _MULTISPACE_RE.sub(" ", line)


def tokenize_words(directory):
    """Yield every word token (lowercase, letters incl. accented) across the
    corpus, in reading order. Parity with frequencia-lexical.sh word extraction,
    except [...] command options are also stripped (per the design decision)."""
    for path in find_tex_files(directory):
        for line in read_text(path).split("\n"):
            cleaned = _clean_line_for_words(line).lower()
            for match in _WORD_RE.findall(cleaned):
                yield match


def normalize_sentence(text):
    """Lowercase, drop punctuation/residual markup, collapse spaces -- the form
    compared by the boilerplate similarity check."""
    text = _NON_WORD_RE.sub(" ", text.lower())
    return _MULTISPACE_RE.sub(" ", text).strip()


# --- Approximate sentence segmentation -------------------------------------
#
# DISCLAIMER (also surfaced in the report headers): sentence splitting is
# APPROXIMATE and meant as a SIGNAL, not an exact measure. It splits on . ? !
# with guards, but the reviewer's judgement decides whether a long sentence is
# real prolixity or a group is real boilerplate.
#
# Guards:
#   - do not split when '.' is immediately followed by a letter/digit
#     (handles decimals like 0.1 and internal dots of i.e./e.g./U.S.);
#   - do not split after a known abbreviation token (Fig. Tab. Eq. Cap. Sec.
#     et al. etc. ex. vs. i.e. e.g. no. Dr. Sr. Prof.);
#   - a blank source line (paragraph break) is a hard sentence boundary.

_ABBREVIATIONS = {
    "fig", "tab", "eq", "cap", "sec", "etc", "ex", "vs", "no",
    "dr", "sr", "prof", "al", "i.e", "e.g",
}

_PARAGRAPH_SENTINEL = "\x00"  # marks a blank-line (paragraph) boundary
_SPLIT_CHARS = ".?!"
# token (letters/dots) ending right before a candidate '.' -- used to test abbrevs
_TRAILING_TOKEN_RE = re.compile(r"([a-zàáâãéêíóôõúüç.]+)$", re.IGNORECASE)


def _is_abbreviation_before(text_upto):
    """True if the alnum/dot token ending at `text_upto` is a known abbrev."""
    m = _TRAILING_TOKEN_RE.search(text_upto)
    if not m:
        return False
    token = m.group(1).strip(".").lower()
    return token in _ABBREVIATIONS


def _split_stream(text, char_lines):
    """Split `text` into (sentence, start_line) pairs. `char_lines[i]` is the
    source line number of text[i]. Splits on . ? ! (guarded) and on the
    paragraph sentinel."""
    sentences = []
    start = 0
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        is_boundary = False
        if ch == _PARAGRAPH_SENTINEL:
            is_boundary = True
        elif ch in _SPLIT_CHARS:
            nxt = text[i + 1] if i + 1 < n else ""
            if ch == ".":
                if nxt.isalnum():
                    is_boundary = False  # decimal / internal dot -> keep
                elif _is_abbreviation_before(text[start:i]):
                    is_boundary = False  # known abbreviation -> keep
                else:
                    is_boundary = True
            else:  # '?' or '!'
                is_boundary = True
        if is_boundary:
            if ch == _PARAGRAPH_SENTINEL:
                # exclude the sentinel from the sentence, then step past it
                _emit(sentences, text[start:i], char_lines, start, i)
                i += 1
            else:
                # include the terminal punctuation in the sentence
                _emit(sentences, text[start:i + 1], char_lines, start, i + 1)
                i += 1
            start = i
        else:
            i += 1
    if start < n:
        _emit(sentences, text[start:n], char_lines, start, n)
    return sentences


def _emit(sentences, piece, char_lines, start, end):
    stripped = piece.strip()
    if not stripped:
        return
    # start line = source line of the first non-space char in [start, end)
    line = char_lines[start]
    for j in range(start, end):
        if not piece[j - start].isspace() and piece[j - start] != _PARAGRAPH_SENTINEL:
            line = char_lines[j]
            break
    collapsed = _MULTISPACE_RE.sub(" ", stripped)
    sentences.append((collapsed, line))


def iter_sentences(directory):
    """Yield Sentence(text, norm, file, line) for the whole corpus.

    Each file is cleaned line by line (comments/commands removed, braces and
    control symbols turned to spaces); characters keep a back-reference to their
    source line so each sentence is anchored to file:line."""
    for path in find_tex_files(directory):
        chars = []        # cleaned character stream for this file
        char_lines = []   # parallel: source line number of each char
        for lineno, raw_line in enumerate(read_text(path).split("\n"), start=1):
            if raw_line.strip() == "":
                # paragraph / blank line -> hard boundary sentinel
                chars.append(_PARAGRAPH_SENTINEL)
                char_lines.append(lineno)
                continue
            cleaned = _clean_line_for_text(raw_line)
            for ch in cleaned:
                chars.append(ch)
                char_lines.append(lineno)
            chars.append(" ")  # a source line break reads as a space
            char_lines.append(lineno)
        text = "".join(chars)
        for sentence_text, line in _split_stream(text, char_lines):
            yield Sentence(
                text=sentence_text,
                norm=normalize_sentence(sentence_text),
                file=path,
                line=line,
            )
