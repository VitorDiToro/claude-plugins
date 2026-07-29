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


if __name__ == "__main__":
    unittest.main()
