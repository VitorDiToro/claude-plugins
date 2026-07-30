# test_foreign_terms.py
import os, shutil, subprocess, sys, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__))

def run(script, d):
    return subprocess.run([sys.executable, os.path.join(HERE, script), d],
                          capture_output=True, text=True)

class TestForeignTermsContract(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.d, "cap"))
        with open(os.path.join(self.d, "main.tex"), "w", encoding="utf-8") as f:
            f.write("\\documentclass{article}\n\\begin{document}\n"
                    "\\include{cap/intro}\n\\end{document}\n")
        with open(os.path.join(self.d, "cap", "intro.tex"), "w", encoding="utf-8") as f:
            f.write("Usamos um framework de deploy no pipeline.\n")
        # orphan draft NOT included by main -> must NOT be scanned
        with open(os.path.join(self.d, "rascunho.tex"), "w", encoding="utf-8") as f:
            f.write("Um outro framework aqui no rascunho.\n")
    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_anchors_are_root_relative_and_manifest_scoped(self):
        r = run("foreign_terms.py", self.d)
        self.assertEqual(r.returncode, 0, r.stderr)
        # root-relative anchor for the included file, forward slashes, no abs path
        self.assertIn("cap/intro.tex:1", r.stdout)
        self.assertNotIn(self.d, r.stdout)          # no absolute path leaked
        # the orphan draft must not be scanned (manifest-scoped discovery)
        self.assertNotIn("rascunho.tex", r.stdout)

    def test_cli_contract(self):
        self.assertEqual(run("foreign_terms.py", self.d + "/nao-existe").returncode, 1)
        no_arg = subprocess.run([sys.executable, os.path.join(HERE, "foreign_terms.py")],
                                capture_output=True, text=True)
        self.assertEqual(no_arg.returncode, 2)


class TestForeignTermsDetection(unittest.TestCase):
    """Detection-logic coverage (glossary / whitelist / italic-span scan).

    Each test builds its own tiny single-file project: `main.tex` needs only
    \\documentclass + \\begin{document} for latex_corpus's manifest resolution
    to pick it up as the main file (and thus as a scanned file in its own
    right -- no separate \\include is required)."""

    def _project(self, lines):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        body = "\n".join(lines)
        with open(os.path.join(d, "main.tex"), "w", encoding="utf-8") as f:
            f.write("\\documentclass{article}\n\\begin{document}\n" + body +
                     "\n\\end{document}\n")
        return d

    def test_whitelist_excludes_proper_nouns(self):
        # "Python" / "Linux" are WHITELIST brand/product names -- prose using
        # them must never be reported as missing italics.
        d = self._project(["Utilizamos Python e Linux para o desenvolvimento."])
        r = run("foreign_terms.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("nenhum termo do glossário aparece sem itálico", r.stdout)
        self.assertNotIn("Python", r.stdout)
        self.assertNotIn("Linux", r.stdout)

    def test_italic_and_foreignlanguage_are_covered(self):
        # A glossary term inside \emph{...} and inside the two-arg
        # \foreignlanguage{english}{...} must both count as already-italicised
        # (covered), so neither is reported as a missing-italics candidate.
        d = self._project([
            "Este \\emph{framework} e usado no projeto.",
            "Tambem usamos \\foreignlanguage{english}{pipeline} no fluxo.",
        ])
        r = run("foreign_terms.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("nenhum termo do glossário aparece sem itálico", r.stdout)

    def test_inconsistente_note_when_same_term_mixed(self):
        # Same term italicised once and bare once in the same corpus must
        # trigger the "inconsistente: N de M" note, not a plain missing-count.
        d = self._project([
            "Primeiro usamos \\emph{framework} no capitulo um.",
            "Depois usamos framework sem italico no capitulo dois.",
        ])
        r = run("foreign_terms.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("**inconsistente**: 1 de 2 ocorrências já usam itálico", r.stdout)
        self.assertIn("main.tex:4", r.stdout)  # the bare (line 4) occurrence

    def test_bare_glossary_term_is_flagged_current_behavior(self):
        # LOCK test: a generic glossary term used bare in plain prose IS
        # flagged today. This documents CURRENT behavior on purpose -- it is
        # NOT a bug and glossary calibration (pruning noisy generic terms like
        # "log"/"bit"/"chip") is a separate decision deferred to the real-
        # project run. Do not "fix" this by editing GLOSSARY or detection.
        d = self._project(["Analisamos o log do sistema."])
        r = run("foreign_terms.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("**log**", r.stdout)
        self.assertIn("main.tex:3", r.stdout)


if __name__ == "__main__":
    unittest.main()
