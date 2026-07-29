#!/usr/bin/env python3
# test_latex_corpus.py -- stdlib unittest for the latex_corpus module.
# Run from this directory: python3 -m unittest test_latex_corpus -v
#
# Code/comments in English (matching the module); no pip, stdlib only.

import os
import shutil
import tempfile
import unittest

import latex_corpus


class TestAnchor(unittest.TestCase):
    def test_anchor_is_root_relative_1based_forward_slash(self):
        root = os.path.join("proj")
        path = os.path.join("proj", "cap", "01_intro.tex")
        self.assertEqual(latex_corpus.anchor(path, 10, root), "cap/01_intro.tex:10")

    def test_anchor_without_root_normalises_slashes(self):
        self.assertEqual(latex_corpus.anchor("a\\b\\c.tex", 3), "a/b/c.tex:3")

    def test_project_relative_outside_root_falls_back(self):
        # path not under root -> normalised path, never a ../.. escape
        rel = latex_corpus.project_relative(os.path.join("other", "x.tex"),
                                            os.path.join("proj"))
        self.assertNotIn("..", rel)
        self.assertTrue(rel.endswith("x.tex"))


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


class TestManifest(unittest.TestCase):
    """Fixture derived from the real Brasil-6G main.tex (spec-manifesto §3)."""

    INCLUDED = {
        "main.tex", "others/configuration.tex", "others/packages.tex",
        "others/capa.tex", "others/historico_de_revisoes.tex",
        "others/acronym.tex", "others/indice.tex", "01_introducao.tex",
    }
    ORPHANS = {"00_avisos.tex", "others/folha_de_rosto.tex", "others/apendice.tex"}

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        _write(os.path.join(self.dir, "main.tex"),
               "\\documentclass[a4paper,12pt]{article}\n"
               "\\input{others/configuration}\n"
               "\\begin{document}\n"
               "\\include{others/capa}\n"
               "% \\include{others/folha_de_rosto}\n"       # commented -> orphan
               "\\include{others/historico_de_revisoes}\n"
               "\\input{others/acronym}\n"
               "\\include{others/indice}\n"
               "%\\include{00_avisos}\n"                     # commented -> orphan
               "\\include{01_introducao}\n"
               "% \\include{others/apendice}\n"              # commented -> orphan
               "\\bibliographystyle{IEEEtran}\n"
               "\\bibliography{references.bib}\n"
               "\\end{document}\n")
        # configuration is \input in the preamble and itself \inputs a nested file:
        _write(os.path.join(self.dir, "others", "configuration.tex"),
               "\\input{others/packages}\n")
        _write(os.path.join(self.dir, "others", "packages.tex"), "% pkgs\n")
        for name in ("capa", "historico_de_revisoes", "acronym", "indice"):
            _write(os.path.join(self.dir, "others", name + ".tex"), name + "\n")
        _write(os.path.join(self.dir, "01_introducao.tex"), "Introducao.\n")
        # orphans (commented out in main):
        _write(os.path.join(self.dir, "others", "folha_de_rosto.tex"), "orfao\n")
        _write(os.path.join(self.dir, "00_avisos.tex"), "orfao\n")
        _write(os.path.join(self.dir, "others", "apendice.tex"), "orfao\n")
        _write(os.path.join(self.dir, "references.bib"), "@book{x, title={t}}\n")

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def _rel(self, paths):
        return set(os.path.relpath(p, self.dir).replace("\\", "/") for p in paths)

    def test_case1_manifest_is_the_included_set(self):
        self.assertEqual(self._rel(latex_corpus.find_manifest_files(self.dir).files),
                         self.INCLUDED)

    def test_case2_orphans_are_the_diff(self):
        allf = self._rel(latex_corpus.find_tex_files(self.dir))
        man = self._rel(latex_corpus.find_manifest_files(self.dir).files)
        self.assertEqual(allf - man, self.ORPHANS)

    def test_case3_comment_rule_depends_on_percent(self):
        main = os.path.join(self.dir, "main.tex")
        _write(main, latex_corpus.read_text(main).replace(
            "%\\include{00_avisos}", "\\include{00_avisos}"))
        self.assertIn("00_avisos.tex",
                      self._rel(latex_corpus.find_manifest_files(self.dir).files))

    def test_case4_subfolder_resolves_no_unresolved(self):
        self.assertEqual(latex_corpus.find_manifest_files(self.dir).unresolved, [])

    def test_case5_recursion_into_nested_input(self):
        self.assertIn("others/packages.tex",
                      self._rel(latex_corpus.find_manifest_files(self.dir).files))

    def test_case6_unresolved_is_signal_not_crash(self):
        main = os.path.join(self.dir, "main.tex")
        _write(main, latex_corpus.read_text(main).replace(
            "\\include{01_introducao}",
            "\\include{01_introducao}\n\\include{others/inexistente}"))
        man = latex_corpus.find_manifest_files(self.dir)
        self.assertTrue(any("inexistente" in u for u in man.unresolved))
        self.assertFalse(any("inexistente" in p for p in self._rel(man.files)))

    def test_case7_fallback_when_no_main(self):
        d = tempfile.mkdtemp()
        try:
            _write(os.path.join(d, "a.tex"), "sem classe\n")
            man = latex_corpus.find_manifest_files(d)
            self.assertFalse(man.resolved_ok)
            self.assertEqual(sorted(man.files), sorted(latex_corpus.find_tex_files(d)))
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_case8_find_tex_files_unchanged_glob_all(self):
        got = self._rel(latex_corpus.find_tex_files(self.dir))
        self.assertEqual(got, self.INCLUDED | self.ORPHANS)   # all 11 .tex

    def test_iter_sentences_excludes_orphans(self):
        names = self._rel(s.file for s in latex_corpus.iter_sentences(self.dir))
        self.assertTrue(names.isdisjoint(self.ORPHANS))


if __name__ == "__main__":
    unittest.main()
