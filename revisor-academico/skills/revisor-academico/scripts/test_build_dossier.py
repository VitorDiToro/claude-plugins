# test_build_dossier.py
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import build_dossier  # unit-level access to build_dossier_body/write_dossier


def run(script, *args):
    return subprocess.run([sys.executable, os.path.join(HERE, script), *args],
                           capture_output=True, text=True)


def _has_hunspell_ptbr():
    """True when `hunspell` is on PATH AND its -D dictionary listing reports
    pt_BR among the available dictionaries. Mirrors the check build_dossier.py
    itself performs before writing anything -- see
    build_dossier._hunspell_ptbr_available (and spell_check's own, identical,
    check -- see test_spell_check.py's _has_ptbr, which this mirrors)."""
    if shutil.which("hunspell") is None:
        return False
    p = subprocess.run(["hunspell", "-D"], capture_output=True, text=True)
    return "pt_BR" in (p.stdout + p.stderr)


class TestBuildDossierCLIContract(unittest.TestCase):
    """Usage-contract tests that run in ANY environment, regardless of
    whether hunspell/pt_BR is installed: these exit codes are produced by the
    arg-count/dir-existence/enunciado-readability checks, which all run
    BEFORE the hunspell prereq gate (order: usage=2 -> dir/enunciado=1 ->
    hunspell/pt_BR=3)."""

    def test_no_args_exits_2(self):
        r = run("build_dossier.py")
        self.assertEqual(r.returncode, 2)

    def test_too_many_args_exits_2(self):
        r = run("build_dossier.py", "a", "b", "c")
        self.assertEqual(r.returncode, 2)

    def test_missing_dir_exits_1(self):
        d = tempfile.mkdtemp()
        try:
            r = run("build_dossier.py", os.path.join(d, "nao-existe"))
        finally:
            shutil.rmtree(d, ignore_errors=True)
        self.assertEqual(r.returncode, 1)

    def test_unreadable_enunciado_arg_exits_1_before_any_writing(self):
        # This check runs before the hunspell gate, so it is exercised for
        # real here even though hunspell is absent in this sandbox.
        d = tempfile.mkdtemp()
        try:
            r = run("build_dossier.py", d, os.path.join(d, "nao-existe-enunciado.txt"))
            self.assertEqual(r.returncode, 1, r.stderr)
            self.assertFalse(os.path.isfile(os.path.join(d, "dossie.md")))
        finally:
            shutil.rmtree(d, ignore_errors=True)


class TestBuildDossierPrereq(unittest.TestCase):
    """The blocking hunspell/pt_BR prerequisite check. TESTABLE (and required
    to PASS) in an environment where hunspell is genuinely absent -- exactly
    this sandbox. Skipped when hunspell+pt_BR IS present, since simulating
    absence would require manipulating PATH (out of scope here)."""

    @unittest.skipIf(_has_hunspell_ptbr(), "hunspell+pt_BR presente neste ambiente -- "
                                           "nao ha como observar a ausencia sem manipular o PATH")
    def test_exit3_and_actionable_message_when_missing_no_dossie_written(self):
        d = tempfile.mkdtemp()
        try:
            r = run("build_dossier.py", d)
            self.assertEqual(r.returncode, 3, r.stderr)
            self.assertEqual(r.stdout, "")
            # No dossier written on the blocking-prereq path.
            self.assertFalse(os.path.isfile(os.path.join(d, "dossie.md")))
            low = r.stderr.lower()
            self.assertIn("hunspell", low)
            self.assertIn("pt_br", low)
            # "actionable" means at least one concrete, per-platform install
            # command shows up, not just a bare "not found" message.
            self.assertTrue(
                any(hint in r.stderr for hint in ("apt", "dnf", "brew")),
                "stderr deveria trazer um comando de instalação acionável: %r" % r.stderr,
            )
        finally:
            shutil.rmtree(d, ignore_errors=True)


class TestBuildDossierAssembly(unittest.TestCase):
    """Unit-level coverage of the section-assembly logic, calling
    build_dossier.build_dossier_body/write_dossier DIRECTLY -- bypassing the
    CLI's hunspell gate (only __main__ checks it) -- so this exercises the
    real §1/§3/§6/§7 logic AND the real never-raise degradation of a failing
    candidate script (§5's spell_check.py genuinely fails here, since
    hunspell is absent, which is exactly the failure-degrades-to-a-note path
    the design requires) in ANY environment, including this sandbox."""

    def setUp(self):
        self.d = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.d, "others"))
        with open(os.path.join(self.d, "main.tex"), "w", encoding="utf-8") as f:
            f.write("\\documentclass{article}\n\\begin{document}\n"
                    "\\include{others/cap}\n% \\include{others/orfao}\n\\end{document}\n")
        for n in ("cap", "orfao"):
            with open(os.path.join(self.d, "others", n + ".tex"), "w", encoding="utf-8") as f:
                f.write("Texto.\n")

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_section_order_and_orphan_signal(self):
        body = build_dossier.build_dossier_body(self.d)
        for sec in ("§1", "§2", "§3", "§4", "§5", "§6"):
            self.assertIn(sec, body)
        self.assertNotIn("§7", body)  # no enunciado given -> §7 omitted entirely
        self.assertIn("others/orfao.tex", body)  # orphan diff signal in §1
        # fixed order: sections appear in ascending §N order
        positions = [body.index(sec) for sec in ("§1", "§2", "§3", "§4", "§5", "§6")]
        self.assertEqual(positions, sorted(positions))

    def test_candidate_scripts_appear_in_fixed_order_in_section_5(self):
        body = build_dossier.build_dossier_body(self.d)
        sec5_start = body.index("§5")
        sec6_start = body.index("§6")
        sec5_body = body[sec5_start:sec6_start]
        markers = ["foreign_terms.py", "crossref_check.py", "bib_check.py",
                   "float_check.py", "acronym_check.py", "lexicon_check.py",
                   "spell_check.py"]
        # spell_check.py genuinely fails here (no hunspell) -> degrades to a
        # note that names the script; every other candidate script succeeds
        # and does NOT print its own filename, so only assert spell_check's
        # failure note is present and positioned last among these markers.
        self.assertIn("spell_check.py", sec5_body)
        self.assertIn("falhou", sec5_body)

    def test_section_7_omitted_without_enunciado_present_with_one(self):
        without = build_dossier.build_dossier_body(self.d)
        self.assertNotIn("§7", without)

        enunciado_path = os.path.join(self.d, "enunciado.txt")
        with open(enunciado_path, "w", encoding="utf-8") as f:
            f.write("Critério de avaliação: revisar ortografia e ABNT.\n")
        with_enunciado = build_dossier.build_dossier_body(self.d, enunciado_path)
        self.assertIn("§7", with_enunciado)
        self.assertIn("Critério de avaliação: revisar ortografia e ABNT.", with_enunciado)

    def test_write_dossier_writes_file_and_returns_resolved_path(self):
        path = build_dossier.write_dossier(self.d)
        self.assertTrue(os.path.isfile(path))
        self.assertTrue(os.path.isabs(path))
        body = open(path, encoding="utf-8").read()
        self.assertIn("§1", body)


@unittest.skipUnless(_has_hunspell_ptbr(), "hunspell+pt_BR ausente")
class TestBuildDossier(unittest.TestCase):
    """Brief's happy-path test, verbatim (full CLI run through __main__,
    including the real hunspell prereq gate and spell_check.py invocation).
    SKIPPED in this sandbox (no hunspell); exercised for real at the T10
    real-project validation gate, in an environment that has hunspell + the
    pt_BR dictionary installed."""

    def setUp(self):
        self.d = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.d, "others"))
        with open(os.path.join(self.d, "main.tex"), "w", encoding="utf-8") as f:
            f.write("\\documentclass{article}\n\\begin{document}\n"
                    "\\include{others/cap}\n% \\include{others/orfao}\n\\end{document}\n")
        for n in ("cap", "orfao"):
            with open(os.path.join(self.d, "others", n + ".tex"), "w", encoding="utf-8") as f:
                f.write("Texto.\n")

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_writes_dossie_and_stdout_is_only_path(self):
        r = run("build_dossier.py", self.d)
        self.assertEqual(r.returncode, 0, r.stderr)
        dossie = os.path.join(self.d, "dossie.md")
        self.assertTrue(os.path.isfile(dossie))
        # stdout is ONLY the status line (path), not the dossier body:
        self.assertLessEqual(len(r.stdout.strip().splitlines()), 2)
        self.assertIn("dossie.md", r.stdout)
        body = open(dossie, encoding="utf-8").read()
        # dossier has the fixed section order and the orphan signal:
        for sec in ("§1", "§5", "§6"):
            self.assertIn(sec, body)
        self.assertIn("others/orfao.tex", body)      # orphan diff signal in §1


if __name__ == "__main__":
    unittest.main()
