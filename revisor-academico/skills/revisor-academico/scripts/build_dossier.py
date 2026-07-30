#!/usr/bin/env python3
# build_dossier.py
#
# Fase-0 ORCHESTRATOR: runs every other analysis script (via subprocess) and
# the shared latex_corpus discovery/anchoring helpers, and assembles their
# output into a single dossier -- one file, `<dir>/dossie.md`, the skill
# reads instead of re-running each script and re-parsing 9 different stdouts.
#
# Section order is FIXED (Brief section 6/7 of the design):
#   §1 Manifesto de arquivos       -- find_manifest_files + orphan diff
#   §2 Perfil de padrão            -- pattern_profile.py, verbatim
#   §3 Classificação normativa     -- DEFERRAL header only, no verdict here
#   §4 Análise textual             -- text_analysis.py, verbatim
#   §5 Candidatos objetivos        -- the 7 candidate scripts, in FIXED order:
#                                      foreign_terms, crossref_check, bib_check,
#                                      float_check, acronym_check, lexicon_check,
#                                      spell_check
#   §6 Corpus normalizado          -- iter_sentences, each anchored
#   §7 Enunciado/rubrica           -- ONLY if the user supplied one (optional
#                                      2nd CLI argument); omitted otherwise
#
# Candidates, never verdicts (project-wide rule): this orchestrator only
# POSITIONS output from the other scripts. It never classifies, parses, or
# rewrites what a candidate script emitted -- §3 in particular is a short
# deferral note, not computed logic, so INATEL vs NBR10719/PUC classification
# stays a reviewing-pass decision, made from the raw signals pattern_profile
# already put in §2.
#
# Never-raise / always-completes: once the blocking prerequisite (hunspell +
# pt_BR, checked FIRST, before any writing) is satisfied, a single failing
# candidate script degrades to a short diagnostic note embedded under its own
# section instead of aborting the whole dossier build.
#
# stdout contract (invariant 8.9, CRITICAL): stdout carries ONLY the resolved
# path of the written dossier -- ONE line, never the dossier body itself
# (the skill Reads the file from disk; echoing the body to stdout would
# double its token cost). All progress/diagnostics go to stderr.
#
# Every subprocess.run(...) call pins encoding="utf-8", errors="replace"
# (not bare text=True) -- a sibling script's fix-round caught a real
# UnicodeEncodeError crash from omitting this under a non-UTF-8 locale.
#
# stdlib only (+ subprocess, os, sys, shutil); code/comments English;
# user-facing output Portuguese, matching every sibling script's tone.
# Invoke: python3 build_dossier.py <dir> [enunciado_file]

import os
import shutil
import subprocess
import sys

import latex_corpus

HERE = os.path.dirname(os.path.abspath(__file__))

# The 7 §5 candidate scripts, in the EXACT order the dossier must present
# them. `title` is used only as a fallback heading when the script fails and
# therefore produced no stdout of its own to supply one.
_CANDIDATE_SCRIPTS = (
    ("foreign_terms.py", "Termos estrangeiros sem itálico"),
    ("crossref_check.py", "Referências cruzadas"),
    ("bib_check.py", "Referências bibliográficas"),
    ("float_check.py", "Floats, imagens e tabelas"),
    ("acronym_check.py", "Siglas"),
    ("lexicon_check.py", "Léxico, crase e formato"),
    ("spell_check.py", "Ortografia (hunspell pt_BR)"),
)


# --- blocking prerequisite: hunspell + pt_BR --------------------------------
#
# Duplicated (not imported) from spell_check._hunspell_ptbr_available, on
# purpose: every Fase-0 script depends only on latex_corpus, never on a
# sibling script, so each stays independently runnable/movable (same
# reasoning documented in spell_check.py / lexicon_check.py for their own
# small local duplications). This is the SAME check spell_check.py performs
# before scanning; build_dossier performs its own equivalent check here so it
# can fail fast, with an actionable message, BEFORE writing anything -- not
# partway through assembling §5.

_HUNSPELL_BIN = "hunspell"
_DICT = "pt_BR"


def _hunspell_ptbr_available():
    """True when `hunspell` is on PATH AND its `-D` dictionary listing
    reports pt_BR among the available dictionaries. Checking only
    shutil.which('hunspell') is NOT enough: hunspell can be installed with
    only e.g. en_US present. Never raises: any subprocess failure here is
    simply treated as 'unavailable'."""
    if shutil.which(_HUNSPELL_BIN) is None:
        return False
    try:
        proc = subprocess.run(
            [_HUNSPELL_BIN, "-D"], capture_output=True,
            text=True, encoding="utf-8", errors="replace",
        )
    except OSError:
        return False
    return _DICT in (proc.stdout + proc.stderr)


_INSTALL_HINT = (
    "hunspell (ou o dicionário pt_BR) não foi encontrado neste ambiente.\n"
    "\n"
    "O dossiê depende do dicionário 'pt_BR' explícito (§5 inclui o "
    "spell_check.py) -- nunca do dicionário padrão do sistema. Instale o "
    "hunspell e o dicionário pt_BR antes de gerar o dossiê:\n"
    "\n"
    "  Debian/Ubuntu : sudo apt-get install hunspell hunspell-pt-br\n"
    "  Fedora/RHEL   : sudo dnf install hunspell hunspell-pt_BR\n"
    "  macOS (brew)  : brew install hunspell\n"
    "                  em seguida instale o dicionário pt_BR (ex.: baixe\n"
    "                  pt_BR.aff/pt_BR.dic do projeto LibreOffice dictionaries\n"
    "                  e copie para /usr/local/share/hunspell ou\n"
    "                  ~/Library/Spelling)\n"
    "  Windows       : instale via WSL/MSYS2 (ex.: dentro do WSL,\n"
    "                  'sudo apt-get install hunspell hunspell-pt-br') ou\n"
    "                  obtenha um build de hunspell com o dicionário pt_BR e\n"
    "                  adicione o executável ao PATH\n"
    "\n"
    "Depois de instalar, confirme com: hunspell -D  (deve listar 'pt_BR')\n"
    "\n"
    "Nenhum dossiê foi escrito.\n"
)


# --- running a sibling analysis script, never raising -----------------------

def _run_script(script_name, directory):
    """Run a sibling analysis script exactly as `python3 <script_name> <dir>`
    and capture its stdout. Returns (stdout, None) on success (exit 0), or
    (None, diagnostic_note) when the script exits nonzero or the subprocess
    itself could not be started/completed. NEVER raises -- the caller embeds
    the diagnostic note under that section and the dossier build continues;
    a single failing candidate script must not abort the whole dossier."""
    script_path = os.path.join(HERE, script_name)
    try:
        proc = subprocess.run(
            [sys.executable, script_path, directory],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
    except Exception as exc:  # pragma: no cover - defensive, matches "never raise"
        msg = str(exc).splitlines()[0] if str(exc) else "erro desconhecido"
        return None, "(script %s falhou: %s)" % (script_name, msg)
    if proc.returncode != 0:
        stderr_lines = proc.stderr.strip().splitlines()
        first_line = stderr_lines[0] if stderr_lines else (
            "saída de erro vazia (exit %d)" % proc.returncode
        )
        return None, "(script %s falhou: %s)" % (script_name, first_line)
    return proc.stdout, None


def _embed_or_note(fallback_title, script_name, directory):
    """The script's own stdout (which already carries its own `##` heading),
    or -- on failure -- a synthetic `## <fallback_title>` heading followed by
    a short diagnostic note, so the section is never silently missing."""
    stdout, note = _run_script(script_name, directory)
    if note:
        return ["## %s" % fallback_title, "", note]
    return [stdout.rstrip("\n")]


# --- §1 Manifesto de arquivos ------------------------------------------------

def _section_1(directory):
    lines = ["# §1 Manifesto de arquivos", ""]

    manifest = latex_corpus.find_manifest_files(directory)
    all_files = latex_corpus.find_tex_files(directory)
    # Determinism: sort the set-diff before emitting (no reliance on set
    # iteration order, which is not guaranteed stable across runs/platforms).
    orphans = sorted(set(all_files) - set(manifest.files))

    lines.append("### Arquivos no manifesto (%d)" % len(manifest.files))
    if manifest.files:
        for f in manifest.files:
            lines.append("- `%s`" % latex_corpus.project_relative(f, directory))
    else:
        lines.append("(nenhum arquivo no manifesto)")
    lines.append("")

    lines.append(
        "### Arquivos órfãos (.tex existentes no projeto, mas não alcançados "
        "a partir do arquivo principal)"
    )
    if orphans:
        for f in orphans:
            lines.append("- `%s`" % latex_corpus.project_relative(f, directory))
    else:
        lines.append("(nenhum arquivo órfão detectado)")
    lines.append("")

    lines.append("### Alvos de \\input/\\include não resolvidos")
    if manifest.unresolved:
        for target in sorted(manifest.unresolved):
            lines.append("- `%s`" % target)
    else:
        lines.append("(nenhum alvo não resolvido)")
    lines.append("")

    lines.append("### Arquivo principal")
    if manifest.resolved_ok:
        lines.append(
            "Um arquivo principal (`\\documentclass` + `\\begin{document}`) foi "
            "identificado com clareza; o manifesto e o diff de órfãos acima são "
            "confiáveis."
        )
    else:
        lines.append(
            "**Nenhum arquivo principal claro foi identificado** (nenhum .tex com "
            "`\\documentclass` + `\\begin{document}`). O manifesto acima caiu para "
            "a lista completa de arquivos .tex do projeto, então o diff de "
            "órfãos **não é confiável**."
        )
    return lines


# --- §2 Perfil de padrão -----------------------------------------------------

def _section_2(directory):
    lines = ["# §2 Perfil de padrão do documento", ""]
    lines += _embed_or_note("Perfil de padrão do documento", "pattern_profile.py", directory)
    return lines


# --- §3 Classificação normativa: DEFERRAL, not a computed verdict -----------

def _section_3():
    lines = ["# §3 Classificação normativa", ""]
    lines.append(
        "_Este orquestrador posiciona sinais, nunca calcula veredito (regra do "
        "projeto: candidatos, não veredictos)._"
    )
    lines.append("")
    lines.append(
        "A classificação normativa deste projeto -- INATEL | NBR10719/PUC | "
        "híbrido | nenhum -- ainda não foi decidida aqui. Cabe à passada de "
        "revisão decidi-la a partir dos sinais de padrão institucional já "
        "levantados em §2 (subseção \"Sinais de padrão institucional\")."
    )
    return lines


# --- §4 Análise textual -------------------------------------------------

def _section_4(directory):
    lines = ["# §4 Análise textual do documento", ""]
    lines += _embed_or_note("Análise textual do documento", "text_analysis.py", directory)
    return lines


# --- §5 Candidatos objetivos por categoria (7 scripts, fixed order) --------

def _section_5(directory):
    lines = ["# §5 Candidatos objetivos por categoria", ""]
    for script_name, fallback_title in _CANDIDATE_SCRIPTS:
        lines += _embed_or_note(fallback_title, script_name, directory)
        lines.append("")
    return lines


# --- §6 Corpus normalizado (anchored sentences) -----------------------------

def _section_6(directory):
    lines = ["# §6 Corpus normalizado", ""]
    lines.append(
        "_Frases da prosa (comandos/comentários LaTeX removidos), extraídas do "
        "corpus do manifesto e ancoradas à sua localização de origem -- insumo "
        "bruto para a passada de revisão, não uma lista de achados._"
    )
    lines.append("")
    any_sentence = False
    for sentence in latex_corpus.iter_sentences(directory):
        any_sentence = True
        anchor = latex_corpus.anchor(sentence.file, sentence.line, directory)
        lines.append("- `%s` — %s" % (anchor, sentence.text))
    if not any_sentence:
        lines.append("(nenhuma frase encontrada no corpus)")
    return lines


# --- §7 Enunciado/rubrica (ONLY when supplied) ------------------------------

def _section_7(enunciado_path, directory):
    lines = ["# §7 Enunciado/rubrica fornecidos", ""]
    lines.append(
        "_Texto bruto do arquivo fornecido pelo usuário (`%s`), embutido sem "
        "reescrita -- a passada de revisão o usa como critério de avaliação._"
        % latex_corpus.project_relative(enunciado_path, directory)
    )
    lines.append("")
    lines.append("```")
    lines.append(latex_corpus.read_text(enunciado_path).rstrip("\n"))
    lines.append("```")
    return lines


# --- assembly ----------------------------------------------------------------

def build_dossier_body(directory, enunciado_path=None):
    """Assemble the full dossier Markdown body, in the fixed §1-§7 order.
    §7 is included ONLY when `enunciado_path` is given (contract: "só existe
    se o usuário forneceu"). Never raises."""
    parts = []
    parts += _section_1(directory)
    parts.append("")
    parts += _section_2(directory)
    parts.append("")
    parts += _section_3()
    parts.append("")
    parts += _section_4(directory)
    parts.append("")
    parts += _section_5(directory)
    parts.append("")
    parts += _section_6(directory)
    if enunciado_path is not None:
        parts.append("")
        parts += _section_7(enunciado_path, directory)
    return "\n".join(parts) + "\n"


def write_dossier(directory, enunciado_path=None):
    """Build the dossier and write it to `<directory>/dossie.md`. Returns the
    resolved (absolute) path of the written file."""
    body = build_dossier_body(directory, enunciado_path)
    dossie_path = os.path.join(directory, "dossie.md")
    with open(dossie_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)
    return os.path.abspath(dossie_path)


if __name__ == "__main__":
    # Pin stdout to UTF-8, symmetric with latex_corpus's UTF-8 read side. A
    # piped stdout on Windows defaults to cp1252 and would crash on echoed
    # source characters outside it. Python 3.7+, stdlib only.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    # Order of checks (fixed): exit 2 (arg count) -> exit 1 (dir/enunciado
    # not found) -> exit 3 (blocking prereq) -> write dossier.
    if len(sys.argv) not in (2, 3):
        sys.stderr.write(
            "Uso: python3 build_dossier.py <diretório-do-projeto-latex> "
            "[arquivo-de-enunciado]\n"
        )
        sys.exit(2)

    target = sys.argv[1]
    if not os.path.isdir(target):
        sys.stderr.write("Diretório não encontrado: %s\n" % target)
        sys.exit(1)

    enunciado_arg = sys.argv[2] if len(sys.argv) == 3 else None
    if enunciado_arg is not None and not os.path.isfile(enunciado_arg):
        sys.stderr.write(
            "Arquivo de enunciado não encontrado ou não legível: %s\n" % enunciado_arg
        )
        sys.exit(1)

    # Blocking prerequisite: hunspell + pt_BR MUST be available (§5 embeds
    # spell_check.py). Checked BEFORE any writing, so a missing dependency
    # never leaves a partial/misleading dossie.md on disk.
    if not _hunspell_ptbr_available():
        sys.stderr.write(_INSTALL_HINT)
        sys.exit(3)

    resolved_path = write_dossier(target, enunciado_arg)
    # stdout contract (invariant 8.9): ONLY the resolved path, one line --
    # never the dossier body. All progress/diagnostics went to stderr above.
    print(resolved_path)
