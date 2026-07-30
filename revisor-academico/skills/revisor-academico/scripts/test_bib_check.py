# test_bib_check.py -- stdlib unittest for bib_check.py's CLI contract and
# detection logic. Run from this directory: python3 -m unittest test_bib_check -v
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


class TestBibCheck(unittest.TestCase):
    """Brief's conformance + \\cite-without-entry tests (verbatim fixture)."""

    def setUp(self):
        self.d = tempfile.mkdtemp()
        with open(os.path.join(self.d, "main.tex"), "w", encoding="utf-8") as f:
            f.write("\\documentclass{article}\n\\begin{document}\n"
                    "Ver \\cite{existe} e \\cite{fantasma}.\n"
                    "\\bibliography{refs}\n\\end{document}\n")
        with open(os.path.join(self.d, "refs.bib"), "w", encoding="utf-8") as f:
            f.write("@article{existe, title={T}, author={A}, journal={J}, year={2020}}\n"
                    "@book{naocitado, title={T2}, author={B}, publisher={P}, year={2019}}\n")

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_cite_without_entry_is_flagged(self):
        r = run("bib_check.py", self.d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("fantasma", r.stdout)          # \cite key with no .bib entry

    def test_never_cited_entry_still_flagged(self):
        self.assertIn("naocitado", run("bib_check.py", self.d).stdout)

    def test_anchors_root_relative(self):
        r = run("bib_check.py", self.d)
        self.assertNotIn(self.d, r.stdout)           # no absolute path
        self.assertIn("main.tex:", r.stdout)         # or refs.bib: -- root-relative


class TestBibCheckContract(unittest.TestCase):
    """CLI contract, mirroring test_foreign_terms.py's TestForeignTermsContract."""

    def setUp(self):
        self.d = tempfile.mkdtemp()
        with open(os.path.join(self.d, "main.tex"), "w", encoding="utf-8") as f:
            f.write("\\documentclass{article}\n\\begin{document}\n"
                    "Sem citacoes nem bib.\n\\end{document}\n")

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_cli_contract(self):
        self.assertEqual(run("bib_check.py", self.d + "/nao-existe").returncode, 1)
        no_arg = subprocess.run([sys.executable, os.path.join(HERE, "bib_check.py")],
                                capture_output=True, text=True)
        self.assertEqual(no_arg.returncode, 2)

    def test_no_bib_file_present(self):
        r = run("bib_check.py", self.d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("nenhum arquivo `.bib` encontrado", r.stdout)

    def test_uppercase_bib_extension_is_found(self):
        # A `.BIB` (or any other-cased extension) must not silently disable
        # the whole bibliography check family on case-preserving filesystems --
        # matches latex_corpus's deliberate case-insensitive `.tex` convention.
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        with open(os.path.join(d, "main.tex"), "w", encoding="utf-8") as f:
            f.write("\\documentclass{article}\n\\begin{document}\n"
                    "Ver \\cite{fantasma}.\n\\bibliography{refs}\n\\end{document}\n")
        with open(os.path.join(d, "refs.BIB"), "w", encoding="utf-8") as f:
            f.write("@book{naocitado, title={T}, author={A}, publisher={P}, year={2020}}\n")
        r = run("bib_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        # the uppercase-extension .bib must have been discovered/parsed:
        # both an orphan-entry signal and the cite-without-entry signal fire.
        self.assertIn("naocitado", r.stdout)
        self.assertIn("fantasma", r.stdout)
        self.assertNotIn("nenhum arquivo `.bib` encontrado", r.stdout)


class TestBibCheckDetection(unittest.TestCase):
    """Detection-logic coverage for bib_check's inherited checks (essential
    field by type, conditional DOI, implausible format, duplicate key).

    Each test builds its own tiny .bib + .tex fixture. These LOCK the CURRENT
    detection behavior -- inherited from before this conformance pass and
    untested in-repo until now. Do not "fix" detection logic here; only the
    discovery/anchoring plumbing changed in this task."""

    def _project(self, bib_content, keys_to_cite=()):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        cites = " ".join("\\cite{%s}" % k for k in keys_to_cite) or "Sem citacoes."
        with open(os.path.join(d, "main.tex"), "w", encoding="utf-8") as f:
            f.write("\\documentclass{article}\n\\begin{document}\n" + cites +
                     "\n\\bibliography{refs}\n\\end{document}\n")
        with open(os.path.join(d, "refs.bib"), "w", encoding="utf-8") as f:
            f.write(bib_content)
        return d

    def test_essential_field_missing_by_type(self):
        # @article without journal -- essential field for the type is absent.
        d = self._project(
            "@article{semrevista, title={T}, author={A}, year={2020}}\n",
            keys_to_cite=["semrevista"],
        )
        r = run("bib_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("semrevista", r.stdout)
        self.assertIn("sem campo essencial", r.stdout)
        self.assertIn("journal", r.stdout)

    def test_doi_conditional_flagged_when_sibling_has_doi(self):
        # Same type (@article): one entry has doi, the sibling does not --
        # only the one WITHOUT doi is flagged (conditional on the type).
        d = self._project(
            "@article{comdoi, title={T1}, author={A}, journal={J}, year={2020}, doi={10.1/x}}\n"
            "@article{semdoi, title={T2}, author={B}, journal={J}, year={2021}}\n",
            keys_to_cite=["comdoi", "semdoi"],
        )
        r = run("bib_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("semdoi", r.stdout)
        self.assertIn("sem `doi`", r.stdout)
        # comdoi has every essential field plus doi -- a fully clean entry,
        # so it must not appear anywhere in the output.
        self.assertNotIn("comdoi", r.stdout)

    def test_doi_not_flagged_when_no_sibling_has_doi(self):
        # Same type, neither entry has doi -- the bibliography deliberately
        # omits DOIs for this type, so neither is flagged.
        d = self._project(
            "@article{a1, title={T1}, author={A}, journal={J}, year={2020}}\n"
            "@article{a2, title={T2}, author={B}, journal={J}, year={2021}}\n",
            keys_to_cite=["a1", "a2"],
        )
        r = run("bib_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("sem `doi`", r.stdout)

    def test_bad_year_flagged(self):
        d = self._project(
            "@article{anoruim, title={T}, author={A}, journal={J}, year={20AB}}\n",
            keys_to_cite=["anoruim"],
        )
        r = run("bib_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("anoruim", r.stdout)
        self.assertIn("não é um ano de 4 dígitos", r.stdout)

    def test_year_out_of_plausible_range_flagged(self):
        d = self._project(
            "@article{anofuturo, title={T}, author={A}, journal={J}, year={3020}}\n",
            keys_to_cite=["anofuturo"],
        )
        r = run("bib_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("anofuturo", r.stdout)
        self.assertIn("fora de faixa plausível", r.stdout)

    def test_inverted_page_range_flagged(self):
        d = self._project(
            "@article{paginas, title={T}, author={A}, journal={J}, year={2020}, pages={50-10}}\n",
            keys_to_cite=["paginas"],
        )
        r = run("bib_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("paginas", r.stdout)
        self.assertIn("intervalo de páginas invertido", r.stdout)

    def test_malformed_url_flagged(self):
        d = self._project(
            "@online{link, title={T}, url={www.example.com sem protocolo}}\n",
            keys_to_cite=["link"],
        )
        r = run("bib_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("link", r.stdout)
        self.assertIn("malformada", r.stdout)

    def test_duplicate_key_flagged(self):
        d = self._project(
            "@article{dup, title={T1}, author={A}, journal={J}, year={2020}}\n"
            "@book{dup, title={T2}, author={B}, publisher={P}, year={2021}}\n",
            keys_to_cite=["dup"],
        )
        r = run("bib_check.py", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("chave duplicada", r.stdout)
        self.assertIn("dup", r.stdout)


if __name__ == "__main__":
    unittest.main()
