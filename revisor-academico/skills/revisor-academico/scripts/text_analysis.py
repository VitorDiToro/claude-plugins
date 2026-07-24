#!/usr/bin/env python3
# text_analysis.py
#
# Port + extension of frequencia-lexical.sh. Four sections:
#   1. Most frequent words (top 30, stopwords removed).
#   2. Most frequent expressions (2-4 words, top 20) with the token-based
#      exact-count subsumption filter -- run only among the top-N candidates,
#      so no O(n^2) blow-up over all n-grams (the bug that hung the .sh at 90s).
#   3. Repeated / near-repeated sentences (boilerplate): shingle-blocked
#      candidate pairs + difflib similarity >= 0.80, grouped, each with all
#      file:line locations.
#   4. Longest sentences (prolixity): > 45 words, else the top 15.
#
# Deciding whether a high count is a language vice (vs. legitimate domain
# terminology) or whether a long sentence is real prolixity is the REVIEWER's
# judgement -- these are SIGNALS, not verdicts. Sentence splitting is APPROXIMATE
# (see latex_corpus). Code/comments English; output Portuguese.
# Invoke: python3 text_analysis.py <dir>

import difflib
import os
import sys
from collections import Counter, defaultdict

import latex_corpus

# EXACT stopword list copied from frequencia-lexical.sh.
STOPWORDS = set(
    "a à ao aos as aquele aquela aqueles aquelas até com como da das de dela dele "
    "deles delas depois do dos e é ela elas ele eles em entre essa essas esse esses "
    "esta está estas estar este estes eu foi isso isto já lhe lhes mais mas me mesmo "
    "meu meus minha minhas muito na nas nem no nos nosso nossa nossos nossas num numa "
    "nós o os ou outra outras outro outros para pela pelas pelo pelos por qual quando "
    "quem que se será sem ser seu seus sido só sua suas são também te teu teus teve "
    "tem tinha tu tua tuas um uma você vocês vos".split()
)

TOP_WORDS = 30
TOP_EXPRESSIONS = 20
# Subsumption runs only within this many top n-gram candidates (keeps it cheap;
# faithful to the design's "top-N candidates only" relaxation of the .sh rule).
CANDIDATE_WINDOW = 50

MIN_SENTENCE_WORDS = 8      # boilerplate: only sentences this long or longer
SHINGLE_SIZE = 5            # boilerplate: shared 5-word shingle => candidate pair
SIMILARITY_THRESHOLD = 0.80  # boilerplate: difflib ratio to group as near-dup
LONG_SENTENCE_WORDS = 45    # prolixity threshold
LONG_FALLBACK = 15          # if none exceed the threshold, show this many longest
PREVIEW_CHARS = 160

APPROX_NOTE = ("_Divisão de frase aproximada — sinal de apoio, não medida exata; "
               "o julgamento do revisor decide._")


# --- Section 1: word frequency --------------------------------------------

def section_words(tokens):
    lines = ["### Palavras mais frequentes (top 30, sem stopwords)"]
    counts = Counter(t for t in tokens if t not in STOPWORDS)
    if not counts:
        lines.append("(sem tokens)")
        return lines
    for word, count in _top(counts, TOP_WORDS):
        lines.append("%d\t%s" % (count, word))
    return lines


# --- Section 2: expression frequency with subsumption filter ---------------

def _all_stopwords(ngram):
    return all(tok in STOPWORDS for tok in ngram)


def section_expressions(tokens):
    lines = ["### Expressões mais frequentes (2 a 4 palavras, top 20)"]
    counts = Counter()
    n = len(tokens)
    for size in (2, 3, 4):
        for i in range(n - size + 1):
            ngram = tuple(tokens[i:i + size])
            if not _all_stopwords(ngram):
                counts[ngram] += 1
    if not counts:
        lines.append("(sem expressões)")
        return lines

    # Take the top-N candidates first; subsumption is applied ONLY among them.
    candidates = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:CANDIDATE_WINDOW]

    # Subsumption: drop a shorter n-gram when a longer candidate has the EXACT
    # same count and contains it as a token-level prefix or suffix.
    removed = set()
    for i, (short, sc) in enumerate(candidates):
        for longer, lc in candidates:
            if len(longer) == len(short) + 1 and lc == sc:
                if longer[:len(short)] == short or longer[-len(short):] == short:
                    removed.add(i)
                    break

    survivors = [candidates[i] for i in range(len(candidates)) if i not in removed]
    for ngram, count in survivors[:TOP_EXPRESSIONS]:
        lines.append("%d\t%s" % (count, " ".join(ngram)))
    return lines


# --- Section 3: repeated / near-repeated sentences (boilerplate) -----------

class _UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def section_boilerplate(sentences):
    lines = ["### Frases repetidas ou quase-repetidas (boilerplate)", APPROX_NOTE]

    # Keep only long-enough sentences; remember their normalized token lists.
    records = []
    for s in sentences:
        toks = s.norm.split()
        if len(toks) >= MIN_SENTENCE_WORDS:
            records.append((s, toks))
    if not records:
        lines.append("(nenhuma frase longa o suficiente para avaliar)")
        return lines

    uf = _UnionFind(len(records))

    # Collapse EXACT duplicates first: identical normalized text is ratio 1.0,
    # so union those for free and run the fuzzy step over DISTINCT text only.
    # This keeps the expensive difflib comparisons off the (many) verbatim repeats.
    distinct = {}  # norm string -> representative record index
    for idx, (s, _toks) in enumerate(records):
        rep = distinct.get(s.norm)
        if rep is None:
            distinct[s.norm] = idx
        else:
            uf.union(rep, idx)

    reps = list(distinct.values())  # one node per distinct normalized sentence

    # Inverted index over distinct sentences: 5-word shingle -> representative idxs.
    shingle_index = defaultdict(list)
    for rep in reps:
        toks = records[rep][1]
        seen = set()
        for i in range(len(toks) - SHINGLE_SIZE + 1):
            shingle = tuple(toks[i:i + SHINGLE_SIZE])
            if shingle not in seen:
                seen.add(shingle)
                shingle_index[shingle].append(rep)

    # Candidate pairs = distinct sentences sharing >= 1 shingle (near-linear blocking).
    candidate_pairs = set()
    for idxs in shingle_index.values():
        if len(idxs) < 2:
            continue
        for a in range(len(idxs)):
            for b in range(a + 1, len(idxs)):
                candidate_pairs.add((idxs[a], idxs[b]))

    # Confirm each candidate pair with difflib and union the survivors.
    # quick_ratio() is a cheap upper bound on ratio(); skip the exact call when
    # even the upper bound is below threshold.
    for a, b in candidate_pairs:
        na, nb = records[a][0].norm, records[b][0].norm
        sm = difflib.SequenceMatcher(None, na, nb)
        if sm.real_quick_ratio() < SIMILARITY_THRESHOLD:
            continue
        if sm.quick_ratio() < SIMILARITY_THRESHOLD:
            continue
        if sm.ratio() >= SIMILARITY_THRESHOLD:
            uf.union(a, b)

    # Build groups; keep only those with >= 2 occurrences.
    groups = defaultdict(list)
    for idx in range(len(records)):
        groups[uf.find(idx)].append(idx)

    reported = []
    for members in groups.values():
        if len(members) < 2:
            continue
        occ = [records[m][0] for m in members]
        # Representative = the longest sentence text in the group.
        rep = max(occ, key=lambda s: len(s.text))
        locations = sorted("%s:%d" % (s.file, s.line) for s in occ)
        reported.append((len(occ), len(rep.text), rep.text, locations))

    if not reported:
        lines.append("(nenhuma frase repetida ou quase-repetida detectada)")
        return lines

    # Order by (occurrences * length) desc -- the most reuse-heavy first.
    reported.sort(key=lambda r: (r[0] * r[1], r[0]), reverse=True)
    for count, _len, text, locations in reported:
        lines.append("")
        lines.append("- **%d ocorrências** — %s" % (count, "; ".join(locations)))
        lines.append("  > %s" % _preview(text))
    return lines


# --- Section 4: longest sentences (prolixity) ------------------------------

def section_long_sentences(sentences):
    lines = ["### Frases mais longas (prolixidade)", APPROX_NOTE]
    scored = []
    for s in sentences:
        wc = len(s.text.split())
        scored.append((wc, s))
    if not scored:
        lines.append("(sem frases)")
        return lines

    scored.sort(key=lambda ws: ws[0], reverse=True)
    long_ones = [ws for ws in scored if ws[0] > LONG_SENTENCE_WORDS]
    if long_ones:
        selected = long_ones
        lines.append("_Frases com mais de %d palavras:_" % LONG_SENTENCE_WORDS)
    else:
        selected = scored[:LONG_FALLBACK]
        lines.append("_Nenhuma frase acima de %d palavras; listando as %d maiores:_"
                     % (LONG_SENTENCE_WORDS, min(LONG_FALLBACK, len(scored))))

    for wc, s in selected:
        lines.append("- **%d palavras** — %s:%d" % (wc, s.file, s.line))
        lines.append("  > %s" % _preview(s.text))
    return lines


# --- helpers ---------------------------------------------------------------

def _top(counter, n):
    """Top-n by count desc, ties broken alphabetically (deterministic)."""
    return sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))[:n]


def _preview(text):
    text = text.strip()
    if len(text) <= PREVIEW_CHARS:
        return text
    return text[:PREVIEW_CHARS].rstrip() + "…"


def main(directory):
    tokens = list(latex_corpus.tokenize_words(directory))
    sentences = list(latex_corpus.iter_sentences(directory))

    out = ["## Análise textual do documento", ""]
    out += section_words(tokens) + [""]
    out += section_expressions(tokens) + [""]
    out += section_boilerplate(sentences) + [""]
    out += section_long_sentences(sentences)
    print("\n".join(out))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("Uso: python3 text_analysis.py <diretório-do-projeto-latex>\n")
        sys.exit(2)
    target = sys.argv[1]
    if not os.path.isdir(target):
        sys.stderr.write("Diretório não encontrado: %s\n" % target)
        sys.exit(1)
    main(target)
