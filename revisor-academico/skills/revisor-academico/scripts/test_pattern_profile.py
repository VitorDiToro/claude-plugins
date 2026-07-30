# test_pattern_profile.py
import os, shutil, subprocess, sys, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import pattern_profile  # unit-level access to classify_standard

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


def _write_main(directory, body):
    with open(os.path.join(directory, "main.tex"), "w", encoding="utf-8") as f:
        f.write(body)


class TestClassifyStandard(unittest.TestCase):
    """classify_standard() is the pure, importable, single source of truth
    for the §3 normative-standard label -- deterministic if/else over the
    same structural signals already shown as raw facts in §2's "Sinais de
    padrão institucional" subsection. No hunspell dependency."""

    def setUp(self):
        self.d = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_inatel_only_markers_classify_as_inatel(self):
        # HISTORICO_ATUALIZACOES_RE match, no NBR/PUC markers anywhere.
        _write_main(
            self.d,
            "\\documentclass{article}\n\\begin{document}\n"
            "Histórico de Atualizações\n"
            "\\end{document}\n",
        )
        self.assertEqual(pattern_profile.classify_standard(self.d), "INATEL")

    def test_nbr_puc_only_markers_classify_as_nbr10719_puc(self):
        # RESUMO_SECTION_RE match, no INATEL markers anywhere.
        _write_main(
            self.d,
            "\\documentclass{article}\n\\begin{document}\n"
            "\\section{Resumo}\n"
            "\\end{document}\n",
        )
        self.assertEqual(pattern_profile.classify_standard(self.d), "NBR10719/PUC")

    def test_both_families_present_classify_as_hibrido(self):
        # CONCLUSAO_SECTION_RE (INATEL) + GLOSSARIO_SECTION_RE (NBR/PUC).
        _write_main(
            self.d,
            "\\documentclass{article}\n\\begin{document}\n"
            "\\section{Conclusão}\n"
            "\\section{Glossário}\n"
            "\\end{document}\n",
        )
        self.assertEqual(pattern_profile.classify_standard(self.d), "híbrido")

    def test_no_markers_classify_as_nenhum_reconhecido(self):
        _write_main(
            self.d,
            "\\documentclass{article}\n\\begin{document}\n"
            "Texto comum sem nenhum marcador institucional.\n"
            "\\end{document}\n",
        )
        self.assertEqual(pattern_profile.classify_standard(self.d), "nenhum reconhecido")


if __name__ == "__main__":
    unittest.main()
