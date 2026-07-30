#!/usr/bin/env python3
# pattern_profile.py
#
# Port of perfil-padrao.sh -- computes a cheap STRUCTURAL profile of a LaTeX
# project (no semantic reading), emitting 9 Markdown sections with the
# same nature of counts, so nothing downstream changes. Reviewers read this.
#
# Regexes are applied line by line over RAW file content (comments NOT stripped),
# exactly like the original grep/sed pipeline. Multi-line "grep -rn" listings are
# emitted in deterministic path-sorted order instead of grep's filesystem-readdir
# order (an intentional cross-platform determinism improvement; counts identical).
#
# Code/comments English; output strings Portuguese. Invoke: python3 pattern_profile.py <dir>

import os
import re
import sys
from collections import Counter

import latex_corpus

# --- line-oriented "-o" match patterns (count every occurrence per line) ---
FLOAT_SPEC_RE = re.compile(r"\[[Hh!tbp]+\]")
ACRONYM_CMD_RE = re.compile(r"\\ac[slfp]?\{")
MANUAL_SIGLA_RE = re.compile(r"\([A-Z]{2,6}\)")
CITE_RE = re.compile(r"\\[Cc]ite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{")
LABEL_PREFIX_RE = re.compile(r"\\label\{([a-zA-Z0-9_]+):")
HLINE_RE = re.compile(r"\\hline")
BOOKTABS_RE = re.compile(r"\\toprule|\\midrule|\\bottomrule")
STRAIGHT_QUOTE_RE = re.compile(r'"')
TYPO_QUOTE_RE = re.compile(r"``|''")
HISTORICO_ATUALIZACOES_RE = re.compile(r"Hist[oó]rico de Atualiza[cç][oõ]es", re.IGNORECASE)
CONCLUSAO_SECTION_RE = re.compile(r"\\(?:section|chapter)\*?\{\s*Conclus[aã]o\s*\}", re.IGNORECASE)
CONSIDERACOES_FINAIS_RE = re.compile(
    r"\\(?:section|chapter)\*?\{\s*Considera[cç][oõ]es\s+[Ff]inais\s*\}", re.IGNORECASE
)
RESUMO_SECTION_RE = re.compile(r"\\(?:section|chapter)\*?\{\s*Resumo\s*\}", re.IGNORECASE)
GLOSSARIO_SECTION_RE = re.compile(r"\\(?:section|chapter)\*?\{\s*Gloss[aá]rio\s*\}", re.IGNORECASE)
FOLHA_ROSTO_RE = re.compile(r"[Ff]olha de [Rr]osto", re.IGNORECASE)
PRINTONLYUSED_RE = re.compile(r"printonlyused")

# --- line-oriented "grep -rn" (whole matching line) patterns ---
FLOAT_PKG_RE = re.compile(r"usepackage.*float")
ACRONYM_PKG_RE = re.compile(r"usepackage.*acronym|usepackage.*acro\b")
BIBSTYLE_RE = re.compile(r"bibliographystyle")
LANG_PKG_RE = re.compile(r"usepackage.*babel|usepackage.*polyglossia")


def _iter_lines(files):
    """Yield (path, lineno, line) over raw file content (comments kept)."""
    for path in files:
        for lineno, line in enumerate(latex_corpus.read_text(path).split("\n"), 1):
            yield path, lineno, line


def _grep_n(files, regex, root):
    """Emulate `grep -rn regex`: matching lines as 'path:lineno:line',
    deterministically path/line sorted. The path component is rendered
    root-relative via latex_corpus.project_relative (Fase-0 hard rule #1);
    only the path is anchored -- the trailing content stays raw, exactly as
    grep -rn would emit it."""
    hits = []
    for path, lineno, line in _iter_lines(files):
        if regex.search(line):
            hits.append((path, lineno, line))
    hits.sort(key=lambda h: (h[0], h[1]))
    return ["%s:%d:%s" % (latex_corpus.project_relative(p, root), ln, txt) for p, ln, txt in hits]


def _count_matches(files, regex):
    """Emulate `grep -rohE regex | wc -l`: total occurrences (many per line)."""
    total = 0
    for _p, _ln, line in _iter_lines(files):
        total += len(regex.findall(line))
    return total


def _collect_matches(files, regex, group=0):
    """All occurrences of `regex` (optionally a capture group) across the corpus."""
    out = []
    for _p, _ln, line in _iter_lines(files):
        for m in regex.finditer(line):
            out.append(m.group(group))
    return out


def _uniq_c_desc(items):
    """Emulate `sort | uniq -c | sort -rn`: '%7d value', count desc, ties by
    reversed full-line order."""
    counts = Counter(items)
    rows = [("%7d %s" % (c, v), c, v) for v, c in counts.items()]
    # sort -rn: numeric desc primary; equal counts -> reversed full-line compare
    rows.sort(key=lambda r: (r[1], r[0]), reverse=True)
    return [r[0] for r in rows]


def _uniq_c_alpha(items):
    """Emulate `sort | uniq -c` (no final numeric sort): '%7d value', ascending
    by matched string (codepoint order == C-locale bytes for ASCII)."""
    counts = Counter(items)
    rows = sorted(counts.items(), key=lambda kv: kv[0])
    return ["%7d %s" % (c, v) for v, c in rows]


def main(directory):
    files = latex_corpus.find_tex_files(directory)
    out = []

    out.append("## Perfil de padrão do documento")
    out.append("")

    # 1. Float specifiers + float package.
    out.append("### Especificadores de float")
    out.extend(_uniq_c_desc(_collect_matches(files, FLOAT_SPEC_RE)))
    out.append("Pacote `float` carregado:")
    hits = _grep_n(files, FLOAT_PKG_RE, directory)
    out.extend(hits if hits else ["(não encontrado)"])
    out.append("")

    # 2. Acronym mechanism.
    out.append("### Mecanismo de siglas")
    out.append("Ocorrências de comandos de acrônimo (\\ac, \\acs, \\acl, \\acf, \\acp): %d"
               % _count_matches(files, ACRONYM_CMD_RE))
    out.append("Pacote `acronym`/`acro`:")
    hits = _grep_n(files, ACRONYM_PKG_RE, directory)
    out.extend(hits if hits else ["(não encontrado)"])
    out.append("Padrões de expansão manual '(SIGLA)': %d"
               % _count_matches(files, MANUAL_SIGLA_RE))
    out.append("")

    # 3. Citation / bibliography style.
    out.append("### Estilo de citação/bibliografia")
    hits = _grep_n(files, BIBSTYLE_RE, directory)
    out.extend(hits if hits else ["(não encontrado)"])
    out.extend(_uniq_c_alpha(_collect_matches(files, CITE_RE)))
    out.append("")

    # 4. Label-prefix convention.
    out.append("### Convenção de prefixo de rótulo")
    out.extend(_uniq_c_desc(_collect_matches(files, LABEL_PREFIX_RE, group=1)))
    out.append("")

    # 5. Table style.
    out.append("### Estilo de tabela")
    out.append("\\hline (manual): %d" % _count_matches(files, HLINE_RE))
    out.append("booktabs (\\toprule/\\midrule/\\bottomrule): %d"
               % _count_matches(files, BOOKTABS_RE))
    out.append("")

    # 6. Language configuration.
    out.append("### Configuração de idioma")
    hits = _grep_n(files, LANG_PKG_RE, directory)
    out.extend(hits if hits else ["(não encontrado)"])
    out.append("")

    # 7. Quote style.
    out.append("### Estilo de aspas")
    out.append('Retas ("): %d' % _count_matches(files, STRAIGHT_QUOTE_RE))
    out.append("Tipográficas (`` ou ''): %d" % _count_matches(files, TYPO_QUOTE_RE))
    out.append("")

    # 8. Per-file raw word count (largest first, no spurious total line).
    out.append("### Tamanho por arquivo (contagem bruta de palavras)")
    sizes = []
    for path in files:
        words = len(latex_corpus.read_text(path).split())
        rel = latex_corpus.project_relative(path, directory)
        sizes.append(("%d %s" % (words, rel), words))
    # sort -rn: count desc, ties by reversed full-line order.
    sizes.sort(key=lambda s: (s[1], s[0]), reverse=True)
    out.extend(line for line, _w in sizes)
    out.append("")

    # 9. Institutional pattern calibration signals (INATEL vs NBR10719/PUC).
    # Raw facts only, same spirit as every section above -- no classification here.
    out.append("### Sinais de padrão institucional")
    out.append("Sinais de INATEL:")
    out.append("Histórico de Atualizações:")
    hits = _grep_n(files, HISTORICO_ATUALIZACOES_RE, directory)
    out.extend(hits if hits else ["(não encontrado)"])
    out.append('Seção "Conclusão":')
    hits = _grep_n(files, CONCLUSAO_SECTION_RE, directory)
    out.extend(hits if hits else ["(não encontrado)"])
    out.append("Acrônimos com `printonlyused`:")
    hits = _grep_n(files, PRINTONLYUSED_RE, directory)
    out.extend(hits if hits else ["(não encontrado)"])
    out.append("Sinais de NBR10719/PUC:")
    out.append('Seção "Resumo":')
    hits = _grep_n(files, RESUMO_SECTION_RE, directory)
    out.extend(hits if hits else ["(não encontrado)"])
    out.append('Seção "Considerações finais":')
    hits = _grep_n(files, CONSIDERACOES_FINAIS_RE, directory)
    out.extend(hits if hits else ["(não encontrado)"])
    out.append('Seção "Glossário":')
    hits = _grep_n(files, GLOSSARIO_SECTION_RE, directory)
    out.extend(hits if hits else ["(não encontrado)"])
    out.append('"Folha de rosto":')
    hits = _grep_n(files, FOLHA_ROSTO_RE, directory)
    out.extend(hits if hits else ["(não encontrado)"])

    print("\n".join(out))


if __name__ == "__main__":
    # Pin stdout to UTF-8, symmetric with the UTF-8 read side. A piped stdout on
    # Windows defaults to the ANSI codepage (cp1252) and would crash with
    # UnicodeEncodeError on document characters outside it (echoed source lines
    # may contain any character). Python 3.7+, stdlib only.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) != 2:
        sys.stderr.write("Uso: python3 pattern_profile.py <diretório-do-projeto-latex>\n")
        sys.exit(2)
    target = sys.argv[1]
    if not os.path.isdir(target):
        sys.stderr.write("Diretório não encontrado: %s\n" % target)
        sys.exit(1)
    main(target)
