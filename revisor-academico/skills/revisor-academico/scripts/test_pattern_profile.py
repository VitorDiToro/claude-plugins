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


class TestGrepNAnchoring(unittest.TestCase):
    """_grep_n's 'path:lineno:content' hits (float/acronym/bibstyle/lang package
    lines, institutional-signal lines) must carry a ROOT-RELATIVE path, never a
    raw absolute filesystem path -- same Fase-0 hard rule #1 as project_relative
    everywhere else. A relative-substring assertIn alone would NOT catch a leak
    here (the relative path is a substring of the absolute one), so the
    discriminating check is assertNotIn(abs_dir, stdout)."""

    def setUp(self):
        self.d = tempfile.mkdtemp()
        with open(os.path.join(self.d, "main.tex"), "w", encoding="utf-8") as f:
            f.write(
                "\\documentclass{article}\n"
                "\\usepackage{float}\n"
                "\\usepackage[brazil]{babel}\n"
                "\\begin{document}\n"
                "Texto.\n"
                "\\end{document}\n"
            )

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_grep_n_hits_are_root_relative_not_absolute(self):
        r = run("pattern_profile.py", self.d)
        self.assertEqual(r.returncode, 0, r.stderr)
        # the absolute tempdir prefix must never leak into stdout
        self.assertNotIn(self.d, r.stdout)
        # FLOAT_PKG_RE hit (line 2) and LANG_PKG_RE hit (line 3) must appear
        # with the root-relative 'main.tex' path.
        self.assertIn("main.tex:2:\\usepackage{float}", r.stdout)
        self.assertIn("main.tex:3:\\usepackage[brazil]{babel}", r.stdout)


if __name__ == "__main__":
    unittest.main()
