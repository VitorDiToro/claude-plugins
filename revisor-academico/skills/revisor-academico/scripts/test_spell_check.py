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
