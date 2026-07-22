#!/usr/bin/env bash
# Uso: perfil-padrao.sh <diretório-do-projeto-latex>
#
# Calcula, por varredura estrutural barata (grep/sed), um perfil de padrão
# do documento LaTeX no diretório dado, cobrindo recursivamente subpastas.
# Não faz nenhuma leitura semântica de conteúdo — só fatos objetivos.
#
# Sem "set -e": várias das sondagens abaixo legitimamente não encontram nada
# (ex.: documento sem booktabs, sem babel) — isso não é um erro do script.

D="${1:?Uso: perfil-padrao.sh <diretório-do-projeto-latex>}"

echo "## Perfil de padrão do documento"
echo

echo "### Especificadores de float"
grep -rohE '\[[Hh!tb]+\]' "$D" --include="*.tex" 2>/dev/null | sort | uniq -c | sort -rn
echo "Pacote \`float\` carregado:"
grep -rn "usepackage.*float" "$D" --include="*.tex" 2>/dev/null || echo "(não encontrado)"
echo

echo "### Mecanismo de siglas"
echo -n "Ocorrências de \\ac{}: "
grep -roh '\\ac{' "$D" --include="*.tex" 2>/dev/null | wc -l
echo "Pacote \`acronym\`/\`acro\`:"
grep -rn "usepackage.*acronym\|usepackage.*acro\b" "$D" --include="*.tex" 2>/dev/null || echo "(não encontrado)"
echo -n "Padrões de expansão manual '(SIGLA)': "
grep -rohE '\([A-Z]{2,6}\)' "$D" --include="*.tex" 2>/dev/null | wc -l
echo

echo "### Estilo de citação/bibliografia"
grep -rn "bibliographystyle" "$D" --include="*.tex" 2>/dev/null || echo "(não encontrado)"
grep -rohE '\\cite[pt]?\{' "$D" --include="*.tex" 2>/dev/null | sort | uniq -c
echo

echo "### Convenção de prefixo de rótulo"
grep -rohE '\\label\{[a-zA-Z]+:' "$D" --include="*.tex" 2>/dev/null | sed -E 's/\\label\{([a-zA-Z]+):/\1/' | sort | uniq -c | sort -rn
echo

echo "### Estilo de tabela"
echo -n "\\hline (manual): "
grep -roh '\\hline' "$D" --include="*.tex" 2>/dev/null | wc -l
echo -n "booktabs (\\toprule/\\midrule/\\bottomrule): "
grep -rohE '\\toprule|\\midrule|\\bottomrule' "$D" --include="*.tex" 2>/dev/null | wc -l
echo

echo "### Configuração de idioma"
grep -rn "usepackage.*babel\|usepackage.*polyglossia" "$D" --include="*.tex" 2>/dev/null || echo "(não encontrado)"
echo

echo "### Estilo de aspas"
echo -n "Retas (\"): "
grep -roh '"' "$D" --include="*.tex" 2>/dev/null | wc -l
echo -n "Tipográficas (\`\` ou ''): "
grep -rohE "\`\`|''" "$D" --include="*.tex" 2>/dev/null | wc -l
