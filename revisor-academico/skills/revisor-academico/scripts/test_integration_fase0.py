# test_integration_fase0.py
#
# Integration test for the Fase-0 pipeline: build_dossier.build_dossier_body()
# run over a small, VERSIONED LaTeX fixture (tests/fixture_fase0/) is compared
# against a FROZEN reference dossier (tests/dossie_referencia.md) that was
# hand-verified once (see task-9-report.md) and then committed.
#
# Portability (the whole point of this test): it must be GREEN in an
# environment WITHOUT hunspell (this sandbox) AND must not spuriously fail on
# a machine WITH hunspell installed. spell_check.py is the only Fase-0 script
# whose output is environment-dependent (fail-soft diagnostic note here vs.
# real spelling candidates on a hunspell box), so its §5 subsection is
# stripped from BOTH bodies before any comparison -- see
# _strip_spell_check_section(). Everything else (§1-§4, §5's other six
# scripts, §6) is fully deterministic given the fixture, so it is compared
# for real.
#
# Per the brief (fase0-integration-brief.md §8) and task-9-brief.md, the
# comparison is on ANCHORS and SECTION-HEADER SEQUENCE, never on wording --
# the prose is free to evolve without breaking this test.
#
# Code/comments English; assertion failure messages may quote Portuguese
# dossier text verbatim (that's fixture/report content, not authored prose).

import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import build_dossier  # noqa: E402  (path insert must precede this import)

FIXTURE_DIR = os.path.join(HERE, "tests", "fixture_fase0")
REFERENCE_PATH = os.path.join(HERE, "tests", "dossie_referencia.md")

# The spell_check subsection's header prefix. It matches BOTH the degraded
# header build_dossier._embed_or_note synthesizes on failure ("## Ortografia
# (hunspell pt_BR)") and the live header spell_check.py itself prints on
# success ("## Ortografia (hunspell pt_BR) — candidatos") -- see
# spell_check.main(). The region to strip runs from that line up to (but NOT
# including) the next "# §6" line, i.e. the whole §5/spell_check subsection.
_SPELLCHECK_HEADER_PREFIX = "## Ortografia (hunspell pt_BR)"
_SECTION_6_PREFIX = "# §6"

# Section-header lines: 1-6 leading '#' followed by a space, to end of line.
_HEADER_RE = re.compile(r"^#{1,6} .*$", re.MULTILINE)

# Anchor tokens, exactly per the brief: "<path-ish>:<line-number>".
_ANCHOR_RE = re.compile(r"\b[\w./-]+:\d+\b")


def _strip_spell_check_section(body):
    """Return `body` with the spell_check §5 subsection removed: every line
    from the first line starting with _SPELLCHECK_HEADER_PREFIX up to (not
    including) the next line starting with _SECTION_6_PREFIX. Makes the
    comparison indifferent to whether spell_check degraded (no hunspell, this
    sandbox) or produced real candidates (a hunspell-equipped machine) -- the
    only environment-dependent part of an otherwise fully deterministic
    dossier body. If the prefix is never found, `body` is returned unchanged
    (defensive; should not happen for this fixture)."""
    lines = body.split("\n")
    start = None
    end = len(lines)
    for i, line in enumerate(lines):
        if start is None and line.startswith(_SPELLCHECK_HEADER_PREFIX):
            start = i
            continue
        if start is not None and line.startswith(_SECTION_6_PREFIX):
            end = i
            break
    if start is None:
        return body
    return "\n".join(lines[:start] + lines[end:])


def _extract_anchors(body):
    """Sorted multiset (as a list) of every `\\b[\\w./-]+:\\d+\\b` anchor in
    `body`. A list, not a set, so an anchor that legitimately repeats (e.g.
    the same label cited from two spots) still has to repeat identically on
    both sides of the comparison."""
    return sorted(_ANCHOR_RE.findall(body))


def _extract_normalized_headers(body):
    """The sequence of `#`/`##`/... header lines in `body`, in order, with
    the ONE environment-dependent header (spell_check's) truncated to its
    common prefix so the degraded and live variants compare equal. Locks the
    §1-§7 order and every script's presence under §5, without caring about
    any other wording."""
    headers = _HEADER_RE.findall(body)
    normalized = []
    for h in headers:
        if h.startswith(_SPELLCHECK_HEADER_PREFIX):
            normalized.append(_SPELLCHECK_HEADER_PREFIX)
        else:
            normalized.append(h)
    return normalized


def _index_of_prefix(headers, prefix):
    """Index of the first header in `headers` starting with `prefix`, or -1.
    Used for the §5/§6 order guardrail without pinning the rest of either
    header's wording."""
    for i, h in enumerate(headers):
        if h.startswith(prefix):
            return i
    return -1


class TestIntegrationFase0(unittest.TestCase):
    """Fresh-vs-frozen comparison, portable across hunspell/no-hunspell
    environments (see module docstring)."""

    @classmethod
    def setUpClass(cls):
        with open(REFERENCE_PATH, encoding="utf-8") as fh:
            cls.frozen = fh.read()
        # build_dossier_body() never raises and needs no hunspell to run --
        # only spell_check.py's own subsection degrades when hunspell/pt_BR
        # is absent (see build_dossier._embed_or_note's never-abort design).
        cls.fresh = build_dossier.build_dossier_body(FIXTURE_DIR)

    def test_fixture_dir_exists(self):
        # Fails loudly (not with a confusing downstream diff) if the fixture
        # was ever moved/renamed without updating this test.
        self.assertTrue(os.path.isdir(FIXTURE_DIR), FIXTURE_DIR)

    def test_anchors_match_excluding_spell_check(self):
        frozen_body = _strip_spell_check_section(self.frozen)
        fresh_body = _strip_spell_check_section(self.fresh)
        self.assertEqual(
            _extract_anchors(fresh_body),
            _extract_anchors(frozen_body),
            "anchors diverged between the fresh run and the frozen reference "
            "(spell_check subsection excluded from both)",
        )

    def test_section_header_sequence_matches(self):
        frozen_headers = _extract_normalized_headers(self.frozen)
        fresh_headers = _extract_normalized_headers(self.fresh)
        self.assertEqual(
            fresh_headers, frozen_headers,
            "section/script header sequence diverged between the fresh run "
            "and the frozen reference",
        )

    def test_orphan_chapter_listed_in_section_1(self):
        # Asserts against self.fresh (the LIVE pipeline run over the fixture),
        # not just the frozen golden -- a golden-only check is always true
        # regardless of what the pipeline does today, so it would silently
        # pass straight through a real orphan-detection regression (e.g. §1
        # falling back to "(nenhum arquivo órfão detectado)"). Neither the
        # anchor nor the header-sequence test would catch that either: the
        # orphan bullet "- `capitulos/orfao.tex`" carries no ":line" suffix
        # (not anchor-shaped) and isn't a header line. The frozen check is
        # kept alongside as a bonus sanity check on the golden file itself,
        # but the fresh assertion is the one that actually guards a
        # regression.
        fresh_sec1_start = self.fresh.index("§1")
        fresh_sec2_start = self.fresh.index("§2")
        fresh_sec1_body = self.fresh[fresh_sec1_start:fresh_sec2_start]
        self.assertIn(
            "capitulos/orfao.tex", fresh_sec1_body,
            "orphan diff regressed: capitulos/orfao.tex missing from the "
            "FRESH pipeline run's §1 (not just the frozen golden)",
        )

        frozen_sec1_start = self.frozen.index("§1")
        frozen_sec2_start = self.frozen.index("§2")
        frozen_sec1_body = self.frozen[frozen_sec1_start:frozen_sec2_start]
        self.assertIn("capitulos/orfao.tex", frozen_sec1_body)

    def test_section_5_precedes_section_6(self):
        headers = _extract_normalized_headers(self.frozen)
        idx5 = _index_of_prefix(headers, "# §5")
        idx6 = _index_of_prefix(headers, "# §6")
        self.assertNotEqual(idx5, -1, "no '# §5' header found in the frozen reference")
        self.assertNotEqual(idx6, -1, "no '# §6' header found in the frozen reference")
        self.assertLess(idx5, idx6, "§5 must precede §6 in the dossier")


if __name__ == "__main__":
    unittest.main()
