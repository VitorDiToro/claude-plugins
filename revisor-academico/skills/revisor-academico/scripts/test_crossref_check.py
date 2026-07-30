# test_crossref_check.py -- stdlib unittest for crossref_check.py's CLI
# contract and detection logic. Run from this directory:
#   python3 -m unittest test_crossref_check -v
#
# Code/comments in English (matching the module); no pip, stdlib only.

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def run(script, d):
    return subprocess.run([sys.executable, os.path.join(HERE, script), d],
                          capture_output=True, text=True)


class TestCrossref(unittest.TestCase):
    """Brief's conformance test (verbatim fixture): orphan/broken/duplicate."""

    def setUp(self):
        self.d = tempfile.mkdtemp()
        with open(os.path.join(self.d, "main.tex"), "w", encoding="utf-8") as f:
            f.write("\\documentclass{article}\n\\begin{document}\n"
                    "\\label{sec:orfao}\n"                 # never \ref'd -> orphan
                    "Ver \\ref{fig:fantasma}.\n"           # no matching \label -> broken
                    "\\label{tab:dup}\n\\label{tab:dup}\n" # duplicate
                    "\\end{document}\n")

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_orphan_broken_duplicate(self):
        r = run("crossref_check.py", self.d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("sec:orfao", r.stdout)
        self.assertIn("fig:fantasma", r.stdout)
        self.assertIn("tab:dup", r.stdout)
        self.assertNotIn(self.d, r.stdout)   # root-relative anchors


class TestCrossrefCheckContract(unittest.TestCase):
    """CLI contract, mirroring test_foreign_terms.py's TestForeignTermsContract."""

    def setUp(self):
        self.d = tempfile.mkdtemp()
        with open(os.path.join(self.d, "main.tex"), "w", encoding="utf-8") as f:
            f.write("\\documentclass{article}\n\\begin{document}\n"
                    "Sem referencias cruzadas aqui.\n\\end{document}\n")

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_no_findings_message(self):
        r = run("crossref_check.py", self.d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("(nenhum", r.stdout)

    def test_cli_contract(self):
        self.assertEqual(run("crossref_check.py", self.d + "/nao-existe").returncode, 1)
        no_arg = subprocess.run([sys.executable, os.path.join(HERE, "crossref_check.py")],
                                capture_output=True, text=True)
        self.assertEqual(no_arg.returncode, 2)


class TestCrossrefDetection(unittest.TestCase):
    """Detection-logic coverage beyond the brief's base fixture."""

    def _project(self, lines):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        body = "\n".join(lines)
        with open(os.path.join(d, "main.tex"), "w", encoding="utf-8") as f:
            f.write("\\documentclass{article}\n\\begin{document}\n" + body +
                     "\n\\end{document}\n")
        return d

    def test_fragile_label_with_accent_is_flagged(self):
        d = self._project(["\\label{seção:um}", "Ver \\ref{seção:um}."])
        r = run("crossref_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("seção:um", r.stdout)
        self.assertIn("não-ASCII", r.stdout)

    def test_eqref_autoref_cref_families_are_recognized(self):
        # \label never referenced -> would be orphan UNLESS every \*ref family
        # member is recognized. Each label is referenced by a different member
        # of the \ref/\eqref/\autoref/\Cref/\cref family, so none should be
        # reported as orphan and none as broken.
        d = self._project([
            "\\label{eq:um}", "Ver \\eqref{eq:um}.",
            "\\label{fig:dois}", "Ver \\autoref{fig:dois}.",
            "\\label{tab:tres}", "Ver \\Cref{tab:tres}.",
            "\\label{sec:quatro}", "Ver \\cref{sec:quatro}.",
        ])
        r = run("crossref_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("(nenhum", r.stdout)

    def test_appendix_ref_without_label_is_flagged(self):
        d = self._project(["Ver \\ref{ap:tcle} para detalhes."])
        r = run("crossref_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("ap:tcle", r.stdout)
        self.assertIn("apêndice", r.stdout.lower())

    def test_textual_appendix_mention_without_any_label_is_flagged(self):
        d = self._project(["Conforme detalhado no Apêndice A, o procedimento segue."])
        r = run("crossref_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Apêndice A", r.stdout)

    def test_textual_appendix_mention_silenced_when_appendix_label_exists(self):
        # An appendix-like \label DOES exist somewhere in the corpus -> exact
        # compiled-letter matching is out of scope for static reading, so the
        # textual mention must be silenced (not flagged).
        d = self._project([
            "\\label{ap:tcle}",
            "Conforme detalhado no Apêndice A, o procedimento segue.",
        ])
        r = run("crossref_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("Apêndice A", r.stdout)

    def test_bib_and_cite_are_out_of_scope(self):
        # BOUNDARY: crossref_check must never touch .bib/\cite -- that is
        # bib_check's territory. A \cite with no .bib entry must NOT surface
        # here.
        d = self._project(["Ver \\cite{fantasma} no texto."])
        r = run("crossref_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("fantasma", r.stdout)
        self.assertIn("(nenhum", r.stdout)


if __name__ == "__main__":
    unittest.main()
