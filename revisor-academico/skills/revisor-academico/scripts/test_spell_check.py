# test_spell_check.py
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import spell_check  # unit-level access to _clean_prose_line (no hunspell involved)


def run(script, d):
    return subprocess.run([sys.executable, os.path.join(HERE, script), d],
                           capture_output=True, text=True)


def _has_ptbr():
    """True when `hunspell` is on PATH AND its -D dictionary listing reports
    pt_BR among the available dictionaries. Mirrors the check spell_check.py
    itself performs before scanning -- see spell_check._hunspell_ptbr_available."""
    if shutil.which("hunspell") is None:
        return False
    p = subprocess.run(["hunspell", "-D"], capture_output=True, text=True)
    return "pt_BR" in (p.stdout + p.stderr)


class TestSpellCheckCLI(unittest.TestCase):
    """Usage-contract tests that run in ANY environment, regardless of
    whether hunspell/pt_BR is installed: both exit codes are produced by the
    arg-count/dir-existence checks, which run BEFORE the hunspell prereq gate
    (order: usage=2 -> dir=1 -> hunspell/pt_BR=3)."""

    def test_cli_contract(self):
        d = tempfile.mkdtemp()
        try:
            self.assertEqual(run("spell_check.py", d + "/nao-existe").returncode, 1)
        finally:
            shutil.rmtree(d, ignore_errors=True)
        no_arg = subprocess.run([sys.executable, os.path.join(HERE, "spell_check.py")],
                                 capture_output=True, text=True)
        self.assertEqual(no_arg.returncode, 2)


class TestSpellPrereq(unittest.TestCase):
    """The blocking hunspell/pt_BR prerequisite check. TESTABLE (and required
    to PASS) in an environment where hunspell is genuinely absent -- exactly
    this sandbox. Skipped when hunspell+pt_BR IS present, since simulating
    absence would require manipulating PATH, which is out of scope here (the
    build_dossier-level version of this same check is Task 8's job, and its
    real-hunspell-present exercise is deferred to the T10 real-project gate)."""

    @unittest.skipIf(_has_ptbr(), "hunspell+pt_BR presente neste ambiente -- "
                                  "nao ha como observar a ausencia sem manipular o PATH")
    def test_exit3_and_actionable_message_when_missing(self):
        d = tempfile.mkdtemp()
        try:
            r = run("spell_check.py", d)
        finally:
            shutil.rmtree(d, ignore_errors=True)
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertEqual(r.stdout, "")
        low = r.stderr.lower()
        self.assertIn("hunspell", low)
        self.assertIn("pt_br", low)
        # "actionable" means at least one concrete, per-platform install
        # command shows up, not just a bare "not found" message.
        self.assertTrue(
            any(hint in r.stderr for hint in ("apt", "dnf", "brew")),
            "stderr deveria trazer um comando de instalação acionável: %r" % r.stderr,
        )


class TestSpellCheckProseExtraction(unittest.TestCase):
    """Unit-level coverage of the prose-extraction step (_clean_prose_line),
    with NO hunspell involved at all -- runs in ANY environment, including
    this hunspell-absent sandbox, since it only exercises spell_check's own
    LaTeX cleanup. Guards against structural/plumbing command arguments
    (environment names, label/ref/cite keys, filenames) leaking into the
    text that gets spell-checked, while prose-bearing commands' argument
    text must still survive."""

    @staticmethod
    def _words(raw):
        cleaned = spell_check._clean_prose_line(raw)
        return re.findall(r"[A-Za-zÀ-ÿ]+", cleaned)

    def test_documentclass_argument_is_excluded(self):
        words = self._words("\\documentclass{article}")
        self.assertNotIn("article", words)

    def test_begin_end_environment_name_is_excluded(self):
        self.assertNotIn("document", self._words("\\begin{document}"))
        self.assertNotIn("document", self._words("\\end{document}"))

    def test_label_and_ref_keys_are_excluded_prose_kept(self):
        words = self._words(
            "Conforme mostrado na Figura \\ref{fig:diagrama}, o sistema funciona bem."
        )
        self.assertNotIn("fig", words)
        self.assertNotIn("diagrama", words)
        self.assertIn("Conforme", words)
        self.assertIn("sistema", words)
        self.assertIn("funciona", words)

    def test_includegraphics_filename_is_excluded(self):
        words = self._words(
            "Veja \\includegraphics[scale=0.5]{img.png} abaixo para detalhes."
        )
        self.assertNotIn("img", words)
        self.assertNotIn("png", words)
        self.assertIn("Veja", words)
        self.assertIn("abaixo", words)
        self.assertIn("detalhes", words)

    def test_cite_key_is_excluded(self):
        words = self._words("Segundo \\cite{silva2020}, os resultados divergem.")
        self.assertNotIn("silva", words)
        self.assertIn("Segundo", words)
        self.assertIn("resultados", words)
        self.assertIn("divergem", words)

    def test_prose_bearing_commands_keep_their_argument_text(self):
        # textbf/emph/etc. are deliberately NOT in _NONPROSE_COMMANDS -- their
        # argument text is real prose and must survive untouched.
        words = self._words("Este é um \\textbf{termo} muito importante.")
        self.assertIn("termo", words)
        self.assertIn("importante", words)

    def test_newacronym_definition_args_excluded_from_prose(self):
        # Calibration change #2: \newacronym{key}{SIGLA}{Long expansion} is a
        # MULTI-ARG acronym declaration -- ALL its brace groups must be
        # blanked, not just the first, or the sigla/expansion text leaks into
        # the spell-checked prose (the real bug: others/acronym.tex being
        # spell-checked as if it were prose).
        words = self._words(
            "\\newacronym{k}{XImagY}{Exprentaçao Fabricadxpta}"
        )
        self.assertNotIn("k", words)
        self.assertNotIn("XImagY", words)
        self.assertNotIn("Exprentaçao", words)
        self.assertNotIn("Fabricadxpta", words)

    def test_declareacronym_definition_args_excluded_from_prose(self):
        words = self._words(
            "\\DeclareAcronym{k}{short=NvLink,long=Exprentaçao Fabricadxpta}"
        )
        self.assertNotIn("NvLink", words)
        self.assertNotIn("Exprentaçao", words)
        self.assertNotIn("Fabricadxpta", words)


class TestSpellCheckCalibration(unittest.TestCase):
    """Calibration coverage (real-artifact finding: 765 distinct candidates /
    ~3800 occurrence-lines / 70% of a real thesis dossier, ~all
    acronym/technical noise drowning the real Portuguese typos). Runs for
    REAL against hunspell/pt_BR -- deliberately NOT skip-guarded, since
    hunspell+pt_BR is installed in this environment and these behaviors can
    only be observed end-to-end through the real binary."""

    def _dir_with(self, content, filename="main.tex"):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        with open(os.path.join(d, filename), "w", encoding="utf-8") as f:
            f.write(content)
        return d

    def test_all_caps_acronym_shaped_token_is_suppressed(self):
        # Change #1: an all-caps token (2+ letters/digits) is never a
        # Portuguese spelling error -- it's an acronym, adjudicated by
        # acronym_check, not spell_check.
        d = self._dir_with(
            "\\documentclass{article}\n\\begin{document}\n"
            "O sistema usa NVAIE para acelerar o treinamento.\n"
            "\\end{document}\n"
        )
        r = run("spell_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("NVAIE", r.stdout)

    def test_acronym_definition_sigla_and_expansion_not_candidates(self):
        # Change #2: acronym-DEFINITION commands (\newacronym here) must not
        # be scanned as prose at all, so neither the sigla nor the expansion
        # text -- both hunspell-flaggable nonsense tokens -- ever become
        # candidates.
        d = self._dir_with(
            "\\documentclass{article}\n\\begin{document}\n"
            "\\newacronym{k}{XImagY}{Exprentaçao Fabricadxpta}\n"
            "\\end{document}\n"
        )
        r = run("spell_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("XImagY", r.stdout)
        self.assertNotIn("Exprentaçao", r.stdout)
        self.assertNotIn("Fabricadxpta", r.stdout)

    def test_defined_mixed_case_sigla_used_in_prose_is_suppressed(self):
        # Change #3: a document-defined MIXED-CASE sigla (not all-caps, so
        # change #1 alone would miss it) used later in running prose must
        # still be suppressed, because the document itself declares it as a
        # sigla via \newacronym.
        d = self._dir_with(
            "\\documentclass{article}\n\\begin{document}\n"
            "\\newacronym{gpu}{NvLink}{Tecnologia de interconexao}\n"
            "O sistema usa NvLink para comunicacao.\n"
            "\\end{document}\n"
        )
        r = run("spell_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("NvLink", r.stdout)

    def test_output_collapses_occurrences_to_one_bullet_with_count_and_first_anchor(self):
        # Change #4: each surviving candidate is ONE bullet -- word + total
        # occurrence count + the FIRST anchor only, not a per-occurrence
        # anchor list.
        d = self._dir_with(
            "\\documentclass{article}\n\\begin{document}\n"
            "Este texto tem conhecimeto errado.\n"
            "Aqui aparece conhecimeto de novo.\n"
            "E mais uma vez conhecimeto aparece.\n"
            "\\end{document}\n"
        )
        r = run("spell_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("- **conhecimeto** (3 ocorrências) — `main.tex:3`", r.stdout)
        # Exactly ONE anchor for the whole (single-candidate) report -- no
        # per-occurrence anchor list survives.
        self.assertEqual(r.stdout.count("main.tex:"), 1)

    def test_recall_preserved_for_real_typo(self):
        # Calibration must not mask a genuine Portuguese typo: lowercase,
        # not acronym-shaped, not a defined sigla -- must still be flagged.
        d = self._dir_with(
            "\\documentclass{article}\n\\begin{document}\n"
            "Este texto apresenta um conhecimeto errado.\n"
            "\\end{document}\n"
        )
        r = run("spell_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("conhecimeto", r.stdout)


@unittest.skipUnless(_has_ptbr(), "hunspell+pt_BR ausente")
class TestSpell(unittest.TestCase):
    """Real spelling-detection coverage. SKIPPED in this sandbox (no
    hunspell); exercised for real at the T10 real-project gate, in an
    environment that has hunspell + the pt_BR dictionary installed."""

    def setUp(self):
        self.d = tempfile.mkdtemp()
        with open(os.path.join(self.d, "main.tex"), "w", encoding="utf-8") as f:
            f.write("\\documentclass{article}\n\\begin{document}\n"
                    "Este texto tem uma palavra errrada de propósito.\n"
                    "\\end{document}\n")

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_flags_misspelling(self):
        r = run("spell_check.py", self.d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("errrada", r.stdout)
        self.assertNotIn(self.d, r.stdout)


if __name__ == "__main__":
    unittest.main()
