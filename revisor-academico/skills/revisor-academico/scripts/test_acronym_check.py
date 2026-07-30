# test_acronym_check.py -- stdlib unittest for acronym_check.py's CLI
# contract and detection logic. Run from this directory:
#   python3 -m unittest test_acronym_check -v
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


class TestAcronym(unittest.TestCase):
    """Brief's conformance test (verbatim fixture): used-before-expansion +
    manual expansion + re-expansion, all in one small corpus."""

    def setUp(self):
        self.d = tempfile.mkdtemp()
        with open(os.path.join(self.d, "main.tex"), "w", encoding="utf-8") as f:
            f.write("\\documentclass{article}\n\\begin{document}\n"
                    "A RAM é usada. Depois, Random Access Memory (RAM) aparece.\n"  # used before expansion
                    "Interface de Programação de Aplicações (API).\n"              # manual expansion
                    "Mais tarde, Interface de Programação de Aplicações (API) de novo.\n"  # re-expansion
                    "\\end{document}\n")

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_used_before_and_reexpanded(self):
        r = run("acronym_check.py", self.d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("RAM", r.stdout)
        self.assertIn("API", r.stdout)
        self.assertNotIn(self.d, r.stdout)


class TestAcronymCheckContract(unittest.TestCase):
    """CLI contract, mirroring test_foreign_terms.py's TestForeignTermsContract."""

    def setUp(self):
        self.d = tempfile.mkdtemp()
        with open(os.path.join(self.d, "main.tex"), "w", encoding="utf-8") as f:
            f.write("\\documentclass{article}\n\\begin{document}\n"
                    "Nenhuma sigla por aqui.\n\\end{document}\n")

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_no_findings_message(self):
        r = run("acronym_check.py", self.d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("(nenhuma", r.stdout)

    def test_cli_contract(self):
        self.assertEqual(run("acronym_check.py", self.d + "/nao-existe").returncode, 1)
        no_arg = subprocess.run([sys.executable, os.path.join(HERE, "acronym_check.py")],
                                capture_output=True, text=True)
        self.assertEqual(no_arg.returncode, 2)


class TestAcronymDetection(unittest.TestCase):
    """Detection-logic coverage beyond the brief's base fixture."""

    def _project(self, lines):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        body = "\n".join(lines)
        with open(os.path.join(d, "main.tex"), "w", encoding="utf-8") as f:
            f.write("\\documentclass{article}\n\\begin{document}\n" + body +
                     "\n\\end{document}\n")
        return d

    def test_single_correct_manual_expansion_is_still_flagged(self):
        # Checklist: a manual "(SIGLA)" expansion is flagged ALWAYS, even
        # when it is the only occurrence and used correctly (no reuse
        # before it, no re-expansion later). It is fragile by construction.
        d = self._project(["Trabalhamos com Light Emitting Diode (LED) no protótipo."])
        r = run("acronym_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Expansão manual", r.stdout)
        self.assertIn("LED", r.stdout)
        self.assertNotIn("Reexpansão", r.stdout)
        self.assertNotIn("expandida manualmente 2", r.stdout)

    def test_gender_inconsistency_is_flagged(self):
        d = self._project([
            "A API do sistema responde rapido.",
            "Depois, o API retorna um erro.",
        ])
        r = run("acronym_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("gênero", r.stdout.lower())
        self.assertIn("API", r.stdout)

    def test_consistent_gender_is_not_flagged(self):
        d = self._project([
            "A API do sistema responde rapido.",
            "Depois, a API retorna um erro.",
        ])
        r = run("acronym_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        # The disclaimer always mentions "gênero" (it describes the check);
        # only the section heading proves whether a finding actually fired.
        self.assertNotIn("### Gênero", r.stdout)

    def test_command_name_is_not_mistaken_for_a_sigla(self):
        # \LARGE is a LaTeX command NAME (directly preceded by a backslash),
        # never running prose -- must not surface as a sigla candidate.
        d = self._project(["{\\LARGE Titulo}", "Texto normal sem siglas aqui."])
        r = run("acronym_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("LARGE", r.stdout)

    def test_bib_key_inside_cite_is_not_mistaken_for_a_sigla(self):
        # A \cite bib key (e.g. "IEEE2020") is plumbing, not prose -- must
        # not surface as a sigla usage/expansion candidate.
        d = self._project(["Conforme \\cite{IEEE2020}, o resultado se confirma."])
        r = run("acronym_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("IEEE", r.stdout)

    def test_never_manually_expanded_sigla_is_not_flagged_as_used_before(self):
        # Out of scope by design: a sigla that is used but NEVER manually
        # expanded anywhere has no "1st expansion" to compare against, so it
        # must not trigger the "used before expansion" check.
        d = self._project(["O sistema usa TCP para a comunicacao.",
                            "O TCP garante entrega confiavel."])
        r = run("acronym_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("TCP", r.stdout)
        self.assertIn("(nenhuma", r.stdout)

    def test_used_after_expansion_is_not_flagged(self):
        # A sigla used only AFTER its manual expansion must not be flagged
        # under "used before expansion".
        d = self._project([
            "Trabalhamos com Random Access Memory (RAM) no projeto.",
            "A RAM utilizada tem 16GB.",
        ])
        r = run("acronym_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("Sigla usada antes", r.stdout)
        self.assertIn("Expansão manual", r.stdout)


if __name__ == "__main__":
    unittest.main()
