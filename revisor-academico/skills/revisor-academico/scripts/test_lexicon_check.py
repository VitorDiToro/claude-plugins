# test_lexicon_check.py -- stdlib unittest for lexicon_check.py's CLI
# contract and detection logic. Run from this directory:
#   python3 -m unittest test_lexicon_check -v
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


class TestLexicon(unittest.TestCase):
    """Brief's conformance test (verbatim fixture): superlative + crase +
    divergent spelling, all in one small document."""

    def setUp(self):
        self.d = tempfile.mkdtemp()
        with open(os.path.join(self.d, "main.tex"), "w", encoding="utf-8") as f:
            f.write("\\documentclass{article}\n\\begin{document}\n"
                    "Uma solução revolucionária. À cada iteração melhora.\n"       # superlative + crase
                    "Usamos frontend e front-end no mesmo texto.\n"                 # divergent spelling
                    "\\end{document}\n")

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_superlative_crase_and_divergent_spelling(self):
        r = run("lexicon_check.py", self.d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("revolucionária", r.stdout)
        self.assertIn("cada", r.stdout)              # "à cada"
        self.assertNotIn(self.d, r.stdout)


class TestLexiconCheckContract(unittest.TestCase):
    """CLI contract, mirroring test_foreign_terms.py's TestForeignTermsContract."""

    def setUp(self):
        self.d = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.d, "cap"))
        with open(os.path.join(self.d, "main.tex"), "w", encoding="utf-8") as f:
            f.write("\\documentclass{article}\n\\begin{document}\n"
                    "\\include{cap/intro}\n\\end{document}\n")
        with open(os.path.join(self.d, "cap", "intro.tex"), "w", encoding="utf-8") as f:
            f.write("Um texto absolutamente comum, sem vicios de linguagem.\n")
        # orphan draft NOT included by main -> must NOT be scanned
        with open(os.path.join(self.d, "rascunho.tex"), "w", encoding="utf-8") as f:
            f.write("Uma solucao revolucionaria no rascunho.\n")

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_no_findings_message(self):
        r = run("lexicon_check.py", self.d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("(nenhum", r.stdout)
        # the orphan draft must not be scanned (manifest-scoped discovery)
        self.assertNotIn("revolucionaria", r.stdout.lower())

    def test_cli_contract(self):
        self.assertEqual(run("lexicon_check.py", self.d + "/nao-existe").returncode, 1)
        no_arg = subprocess.run([sys.executable, os.path.join(HERE, "lexicon_check.py")],
                                capture_output=True, text=True)
        self.assertEqual(no_arg.returncode, 2)


class TestLexiconDetection(unittest.TestCase):
    """Detection-logic coverage beyond the brief's base fixture."""

    def _project(self, lines):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        body = "\n".join(lines)
        with open(os.path.join(d, "main.tex"), "w", encoding="utf-8") as f:
            f.write("\\documentclass{article}\n\\begin{document}\n" + body +
                     "\n\\end{document}\n")
        return d

    # --- superlatives / colloquialisms -------------------------------------

    def test_colloquial_term_is_flagged(self):
        d = self._project(["Isso é simplesmente incrível e obviamente correto."])
        r = run("lexicon_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("simplesmente", r.stdout)
        self.assertIn("obviamente", r.stdout)
        self.assertIn("incrível", r.stdout)

    def test_marketing_phrase_de_ponta_is_flagged(self):
        d = self._project(["Utilizamos uma tecnologia de ponta neste trabalho."])
        r = run("lexicon_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("de ponta", r.stdout)

    def test_legitimate_technical_terms_are_not_flagged(self):
        # "ideal" (gás ideal) and "único" (valor único) are common, legitimate
        # technical words in engineering prose -- must NOT be on the curated
        # list (false-positive-limiting choice), unlike marketing superlatives.
        d = self._project(["O gás ideal apresenta um único ponto de equilíbrio."])
        r = run("lexicon_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("(nenhum", r.stdout)

    # --- crase ---------------------------------------------------------------

    def test_a_partir_crase_is_flagged(self):
        d = self._project(["À partir deste ponto, o sistema estabiliza."])
        r = run("lexicon_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("partir", r.stdout)

    def test_a_medida_que_is_not_flagged(self):
        # "à medida que" is the CORRECT fixed expression -- must be silenced.
        d = self._project(["O erro diminui à medida que o número de amostras cresce."])
        r = run("lexicon_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("(nenhum", r.stdout)

    def test_a_medida_without_que_is_flagged(self):
        d = self._project(["Ajustamos o parâmetro à medida do necessário."])
        r = run("lexicon_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("medida", r.stdout)

    # --- decimal separator inconsistency --------------------------------------

    def test_decimal_inconsistency_flagged_when_both_forms_present(self):
        d = self._project([
            "A temperatura media foi de 3,5 graus.",
            "O segundo ensaio registrou 4.2 graus.",
        ])
        r = run("lexicon_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("3,5", r.stdout)
        self.assertIn("4.2", r.stdout)

    def test_single_decimal_style_is_not_flagged(self):
        d = self._project(["Os valores foram 3,5 e 4,2 e 5,1 em todos os ensaios."])
        r = run("lexicon_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("(nenhum", r.stdout)

    def test_thousands_grouping_is_not_mistaken_for_decimal(self):
        # "1.234.567" (dot-grouped thousands) and "1,234,567" (comma-grouped
        # thousands) must NOT be misread as decimal numbers -- both use a
        # 3-digit group after the separator, the thousands-grouping signature.
        d = self._project([
            "A base de dados contem 1.234.567 amostras coletadas.",
            "Comparamos com outra base de 1,234,567 amostras.",
        ])
        r = run("lexicon_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("(nenhum", r.stdout)

    # --- divergent spellings ---------------------------------------------------

    def test_github_case_divergence_is_flagged(self):
        d = self._project([
            "O codigo foi publicado no GitHub oficial do projeto.",
            "Depois disso, o Github recebeu novas contribuicoes.",
        ])
        r = run("lexicon_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("GitHub", r.stdout)
        self.assertIn("Github", r.stdout)

    def test_plain_capitalization_at_sentence_start_is_not_flagged(self):
        # Ordinary sentence-initial capitalization ("Este"/"este") must NOT be
        # mistaken for a divergent-spelling pair -- neither surface form has a
        # hyphen or an internal capital, so the pair is never gated for
        # tracking in the first place.
        d = self._project([
            "Este resultado confirma a hipotese inicial.",
            "Assim, este resultado e validado por completo.",
        ])
        r = run("lexicon_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("(nenhum", r.stdout)


if __name__ == "__main__":
    unittest.main()
