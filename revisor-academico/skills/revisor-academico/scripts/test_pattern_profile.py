# test_pattern_profile.py
import os, shutil, subprocess, sys, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__))

def run(script, d):
    return subprocess.run([sys.executable, os.path.join(HERE, script), d],
                          capture_output=True, text=True)


class TestPatternProfileAnchoring(unittest.TestCase):
    """The 'Tamanho por arquivo' section must list files by ROOT-RELATIVE path
    (via latex_corpus.project_relative), never by raw absolute filesystem path --
    anchor()/project_relative() are the only sanctioned way to produce a
    path/location string (Fase-0 hard rule #1)."""

    def setUp(self):
        self.d = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.d, "others"))
        with open(os.path.join(self.d, "main.tex"), "w", encoding="utf-8") as f:
            f.write("\\documentclass{article}\n\\begin{document}\n"
                    "Palavra um dois tres quatro.\n\\end{document}\n")
        with open(os.path.join(self.d, "others", "cap.tex"), "w", encoding="utf-8") as f:
            f.write("Capitulo com sete oito palavras aqui presente.\n")

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_file_sizes_are_root_relative_not_absolute(self):
        r = run("pattern_profile.py", self.d)
        self.assertEqual(r.returncode, 0, r.stderr)
        # the absolute tempdir prefix must never leak into stdout
        self.assertNotIn(self.d, r.stdout)
        section = r.stdout.split("### Tamanho por arquivo")[1].split("###")[0]
        self.assertIn("others/cap.tex", section)
        self.assertIn("main.tex", section)


if __name__ == "__main__":
    unittest.main()
