# test_float_check.py
import os, shutil, subprocess, sys, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__))


def run(script, d):
    return subprocess.run([sys.executable, os.path.join(HERE, script), d],
                          capture_output=True, text=True)


class TestFloat(unittest.TestCase):
    """The brief's Step-1 test, verbatim."""

    def setUp(self):
        self.d = tempfile.mkdtemp()
        with open(os.path.join(self.d, "main.tex"), "w", encoding="utf-8") as f:
            f.write("\\documentclass{article}\n\\begin{document}\n"
                    "\\begin{figure}\\includegraphics{faltando}\\end{figure}\n"  # missing file, no caption/label
                    "\\begin{table}\\begin{tabular}{c}\\hline a\\\\\\end{tabular}\\end{table}\n"
                    "\\toprule\n"                          # booktabs mixed with \hline
                    "\\end{document}\n")

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_missing_image_and_mixed_rules(self):
        r = run("float_check.py", self.d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("faltando", r.stdout)          # missing includegraphics target
        self.assertNotIn(self.d, r.stdout)


class TestFloatCheckContract(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.d, "cap"))
        with open(os.path.join(self.d, "main.tex"), "w", encoding="utf-8") as f:
            f.write("\\documentclass{article}\n\\begin{document}\n"
                    "\\include{cap/ch1}\n\\end{document}\n")
        with open(os.path.join(self.d, "cap", "ch1.tex"), "w", encoding="utf-8") as f:
            f.write("\\begin{figure}\n\\includegraphics{sumido}\n"
                    "\\caption{x}\\label{fig:x}\n\\end{figure}\n")
        # orphan draft NOT included by main -> must NOT be scanned
        with open(os.path.join(self.d, "rascunho.tex"), "w", encoding="utf-8") as f:
            f.write("\\begin{figure}\\includegraphics{outro-sumido}\\end{figure}\n")

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_anchors_are_root_relative_and_manifest_scoped(self):
        r = run("float_check.py", self.d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("cap/ch1.tex:2", r.stdout)
        self.assertNotIn(self.d, r.stdout)
        self.assertNotIn("rascunho.tex", r.stdout)
        self.assertNotIn("outro-sumido", r.stdout)

    def test_cli_contract(self):
        self.assertEqual(run("float_check.py", self.d + "/nao-existe").returncode, 1)
        no_arg = subprocess.run([sys.executable, os.path.join(HERE, "float_check.py")],
                                capture_output=True, text=True)
        self.assertEqual(no_arg.returncode, 2)


class TestFloatCheckDetection(unittest.TestCase):
    """Detection-logic coverage for each of the 5 checks, one tiny project
    per scenario so each test is independent and easy to read."""

    def _project(self, body):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        with open(os.path.join(d, "main.tex"), "w", encoding="utf-8") as f:
            f.write("\\documentclass{article}\n\\begin{document}\n" + body +
                     "\n\\end{document}\n")
        return d

    # --- \includegraphics existence -----------------------------------------

    def test_existing_image_same_dir_not_flagged(self):
        d = self._project(
            "\\begin{figure}\\includegraphics{foo.png}"
            "\\caption{c}\\label{fig:foo}\\end{figure}"
        )
        with open(os.path.join(d, "foo.png"), "w") as f:
            f.write("x")
        r = run("float_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("nenhum problema de floats, imagens ou tabelas detectado", r.stdout)

    def test_image_resolved_via_root_figures_subfolder_and_extension(self):
        # \includegraphics{img} with NO extension; the real file lives
        # under <ROOT>/figures/img.png (not the chapter's own directory) --
        # both the extension-appending and the root-level figures/ subfolder
        # widening must kick in together, even for a reference sitting in a
        # chapter sub-file.
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        os.makedirs(os.path.join(d, "cap"))
        os.makedirs(os.path.join(d, "figures"))
        with open(os.path.join(d, "main.tex"), "w", encoding="utf-8") as f:
            f.write("\\documentclass{article}\n\\begin{document}\n"
                    "\\include{cap/ch1}\n\\end{document}\n")
        with open(os.path.join(d, "cap", "ch1.tex"), "w", encoding="utf-8") as f:
            f.write("\\begin{figure}\\includegraphics{img}"
                    "\\caption{c}\\label{fig:img}\\end{figure}\n")
        with open(os.path.join(d, "figures", "img.png"), "w") as f:
            f.write("x")
        r = run("float_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("nenhum problema de floats, imagens ou tabelas detectado", r.stdout)

    def test_chapter_local_image_without_graphicspath_is_flagged_missing(self):
        # Fix-round-1 regression guard: resolving against each including
        # .tex file's OWN directory was removed (false-negative vector).
        # An image that lives ONLY under the chapter's own figures/
        # subfolder -- with no \graphicspath declared -- would fail to
        # compile under a standard root build, so it MUST be flagged.
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        os.makedirs(os.path.join(d, "cap", "figures"))
        with open(os.path.join(d, "main.tex"), "w", encoding="utf-8") as f:
            f.write("\\documentclass{article}\n\\begin{document}\n"
                    "\\include{cap/ch1}\n\\end{document}\n")
        with open(os.path.join(d, "cap", "ch1.tex"), "w", encoding="utf-8") as f:
            f.write("\\begin{figure}\\includegraphics{img}"
                    "\\caption{c}\\label{fig:img}\\end{figure}\n")
        with open(os.path.join(d, "cap", "figures", "img.png"), "w") as f:
            f.write("x")  # exists ONLY chapter-locally, not under the root
        r = run("float_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Imagem referenciada não encontrada", r.stdout)
        self.assertIn("`img`", r.stdout)

    def test_missing_image_message_names_the_argument(self):
        d = self._project(
            "\\begin{figure}\\includegraphics[width=\\linewidth]{no-tal}"
            "\\caption{c}\\label{fig:x}\\end{figure}"
        )
        r = run("float_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("no-tal", r.stdout)
        self.assertIn("Imagem referenciada não encontrada", r.stdout)

    # --- duplicate \includegraphics argument --------------------------------

    def test_same_image_used_twice_is_flagged(self):
        d = self._project(
            "\\begin{figure}\\includegraphics{rep.png}"
            "\\caption{a}\\label{fig:a}\\end{figure}\n"
            "\\begin{figure}\\includegraphics{rep.png}"
            "\\caption{b}\\label{fig:b}\\end{figure}"
        )
        with open(os.path.join(d, "rep.png"), "w") as f:
            f.write("x")
        r = run("float_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Mesma imagem usada em múltiplos locais", r.stdout)
        self.assertIn("rep.png", r.stdout)
        self.assertIn("usada 2 vezes", r.stdout)

    # --- figure/table missing \caption or \label ----------------------------

    def test_missing_label_only_is_named(self):
        d = self._project("\\begin{figure}\\caption{c}\\end{figure}")
        r = run("float_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("ambiente `figure` sem `\\label`", r.stdout)
        self.assertNotIn("e sem", r.stdout)  # only ONE item missing, no join

    def test_missing_caption_only_is_named(self):
        d = self._project("\\begin{table}\\label{tab:x}\\end{table}")
        r = run("float_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("ambiente `table` sem `\\caption`", r.stdout)
        self.assertNotIn("e sem", r.stdout)  # only ONE item missing, no join

    def test_short_caption_form_is_recognized(self):
        # Fix-round-2 regression guard: \caption[short]{long} (the standard
        # short-caption form, used when the List-of-Figures entry should
        # differ from the full caption) must be recognized as a REAL
        # caption -- must NOT be flagged as missing \caption.
        d = self._project(
            "\\begin{figure}\\includegraphics{ok.png}"
            "\\caption[Short entry]{Long caption text}"
            "\\label{fig:ok}\\end{figure}"
        )
        with open(os.path.join(d, "ok.png"), "w") as f:
            f.write("x")
        r = run("float_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("nenhum problema de floats, imagens ou tabelas detectado", r.stdout)

    def test_captionsetup_is_not_mistaken_for_caption(self):
        # Fix-round-1 regression guard: \captionsetup{...} (caption package
        # styling command, common in ABNT templates) must NOT satisfy the
        # \caption requirement -- a table with only \captionsetup and no
        # real \caption is still missing its caption.
        d = self._project(
            "\\begin{table}\\captionsetup{font=small}\\label{tab:x}\\end{table}"
        )
        r = run("float_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("ambiente `table` sem `\\caption`", r.stdout)

    def test_complete_figure_not_flagged(self):
        d = self._project(
            "\\begin{figure}\\includegraphics{ok.png}"
            "\\caption{c}\\label{fig:ok}\\end{figure}"
        )
        with open(os.path.join(d, "ok.png"), "w") as f:
            f.write("x")
        r = run("float_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("nenhum problema de floats, imagens ou tabelas detectado", r.stdout)

    # --- long tabular (longtable candidate) ---------------------------------

    def _tabular_with_rows(self, n):
        rows = "".join("a & b \\\\\n" for _ in range(n))
        return "\\begin{table}\\begin{tabular}{cc}\n" + rows + "\\end{tabular}\\end{table}"

    def test_tabular_above_threshold_is_flagged(self):
        d = self._project(self._tabular_with_rows(31))
        r = run("float_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Tabela extensa (candidata a `longtable`)", r.stdout)
        self.assertIn("31", r.stdout)

    def test_tabular_at_threshold_is_not_flagged(self):
        d = self._project(self._tabular_with_rows(30))
        r = run("float_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("Tabela extensa", r.stdout)

    def test_longtable_itself_is_never_flagged(self):
        # A longtable with many row breaks must NOT be suggested for
        # conversion to longtable -- that would be circular.
        rows = "".join("a & b \\\\\n" for _ in range(40))
        d = self._project("\\begin{longtable}{cc}\n" + rows + "\\end{longtable}")
        r = run("float_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("Tabela extensa", r.stdout)

    # --- \hline vs booktabs mixing -------------------------------------------

    def test_hline_only_not_flagged_as_mixed(self):
        d = self._project(
            "\\begin{table}\\begin{tabular}{c}\\hline a\\\\\\end{tabular}\\end{table}"
        )
        r = run("float_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("misturados", r.stdout)

    def test_booktabs_only_not_flagged_as_mixed(self):
        d = self._project(
            "\\begin{table}\\begin{tabular}{c}\\toprule a\\\\\\bottomrule\\end{tabular}\\end{table}"
        )
        r = run("float_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("misturados", r.stdout)

    def test_hline_and_booktabs_both_present_is_flagged(self):
        d = self._project(
            "\\begin{table}\\begin{tabular}{c}\\hline a\\\\\\end{tabular}\\end{table}\n"
            "\\toprule\n\\bottomrule"
        )
        r = run("float_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("`\\hline` e booktabs misturados no mesmo projeto", r.stdout)

    # --- never raise on malformed input --------------------------------------

    def test_unclosed_figure_does_not_crash(self):
        d = self._project("\\begin{figure}\\includegraphics{x}")
        r = run("float_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_empty_includegraphics_argument_is_flagged_as_missing(self):
        # An empty \includegraphics{} target is itself a broken reference;
        # it must be surfaced (not silently skipped) and must never crash.
        d = self._project("\\begin{figure}\\includegraphics{}\\end{figure}")
        r = run("float_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Imagem referenciada não encontrada", r.stdout)
        self.assertIn("argumento vazio", r.stdout)
        self.assertNotIn("aponta para ``", r.stdout)  # not the generic "missing named arg" phrasing


if __name__ == "__main__":
    unittest.main()
