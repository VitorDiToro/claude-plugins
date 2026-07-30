# test_text_analysis.py
import os, shutil, subprocess, sys, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__))

def run(script, d):
    return subprocess.run([sys.executable, os.path.join(HERE, script), d],
                          capture_output=True, text=True)


class TestTextAnalysisManifestScoped(unittest.TestCase):
    """LOCK test: text_analysis.py itself has NO manifest-scoping code -- it
    inherits scoping entirely from latex_corpus.iter_sentences/tokenize_words
    (already manifest-aware). This test only confirms that inheritance holds:
    an orphan .tex file (on disk but not \\include'd by the main file) must
    not leak into ANY of the 4 output sections (word frequency, expressions,
    repeated sentences, longest sentences). Do NOT "fix" text_analysis.py if
    this fails -- that would mean the manifest scoping regressed in
    latex_corpus; escalate instead."""

    def setUp(self):
        self.d = tempfile.mkdtemp()
        with open(os.path.join(self.d, "main.tex"), "w", encoding="utf-8") as f:
            f.write("\\documentclass{article}\n\\begin{document}\n"
                    "\\include{cap}\n% \\include{orfao}\n\\end{document}\n")
        with open(os.path.join(self.d, "cap.tex"), "w", encoding="utf-8") as f:
            f.write("A antena recebe o sinal com clareza.\n")
        with open(os.path.join(self.d, "orfao.tex"), "w", encoding="utf-8") as f:
            f.write("Palavraorfaunicaxyz num rascunho descartado e nunca incluido.\n")

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_orphan_absent_from_all_sections(self):
        r = run("text_analysis.py", self.d)
        self.assertEqual(r.returncode, 0, r.stderr)
        # token que só existe no órfão não pode aparecer em NENHUMA das 4 seções
        self.assertNotIn("palavraorfaunicaxyz", r.stdout.lower())
        self.assertNotIn("orfao.tex", r.stdout)


if __name__ == "__main__":
    unittest.main()
