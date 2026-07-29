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

if __name__ == "__main__":
    unittest.main()
