"""
Lightweight NLP utilities: RAKE-style keyword extraction, simple TextRank summarization,
and heuristic sentiment scoring that doesn't require heavy models.
"""

from __future__ import annotations
from collections import defaultdict, Counter
import itertools
import math
import re
from typing import List, Tuple

import networkx as nx

_WORD_RE = re.compile(r"[A-Za-zÀ-ÿ0-9]+(?:'[A-Za-zÀ-ÿ0-9]+)?")
_STOPWORDS = set("""a about above after again against all am an and any are aren't as at be because been before being below
between both but by can't cannot could couldn't did didn't do does doesn't doing don't down during each few for from further
had hadn't has hasn't have haven't having he he'd he'll he's her here here's hers herself him himself his how how's i i'd i'll
i'm i've if in into is isn't it it's its itself let's me more most mustn't my myself no nor not of off on once only or other
ought our ours  ourselves out over own same shan't she she'd she'll she's should shouldn't so some such than that that's the
their theirs them themselves then there there's these they they'd they'll they're they've this those through to too under until
up very was wasn't we we'd we'll we're we've were weren't what what's when when's where where's which while who who's whom why
why's with won't would wouldn't you you'd you'll you're you've your yours yourself yourselves""".split())

def tokenize(text: str) -> List[str]:
    return [m.group(0).lower() for m in _WORD_RE.finditer(text)]

def sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]

def rake_keywords(text: str, top_k: int = 10):
    words = tokenize(text)
    phrases, phrase = [], []
    for w in words:
        if w in _STOPWORDS:
            if phrase:
                phrases.append(phrase); phrase=[]
        else:
            phrase.append(w)
    if phrase: phrases.append(phrase)
    freq = Counter(itertools.chain.from_iterable(phrases))
    degree = Counter()
    for ph in phrases:
        deg = len(ph) - 1
        for w in ph:
            degree[w] += deg
    word_score = {w: (degree[w] + freq[w]) / (freq[w]*1.0) for w in freq}
    scored = [(" ".join(ph), sum(word_score[w] for w in ph)) for ph in phrases]
    scored.sort(key=lambda x: x[1], reverse=True)
    seen, out = set(), []
    for ph, sc in scored:
        if ph not in seen:
            out.append((ph, sc)); seen.add(ph)
        if len(out) >= top_k: break
    return out

def textrank_summarize(text: str, max_sentences: int = 3):
    sents = sentences(text)
    if not sents: return []
    import networkx as nx
    G = nx.Graph()
    for i in range(len(sents)):
        G.add_node(i)
    token_sets = [set(tokenize(s)) for s in sents]
    for i in range(len(sents)):
        for j in range(i+1, len(sents)):
            a, b = token_sets[i], token_sets[j]
            if not a or not b: continue
            inter, union = len(a & b), len(a | b)
            if union == 0: continue
            sim = inter/union
            if sim > 0: G.add_edge(i, j, weight=sim)
    if G.number_of_edges()==0: return sents[:max_sentences]
    ranks = nx.pagerank(G, weight='weight')
    ordered = sorted(range(len(sents)), key=lambda i: ranks.get(i,0), reverse=True)
    selected = sorted(ordered[:max_sentences])
    return [sents[i] for i in selected]

def tiny_sentiment(text: str) -> float:
    pos = set("good great excellent positive benefit win success safe fast easy love like improvement growth bullish sunny clear".split())
    neg = set("bad poor terrible negative loss fail risk slow hard hate dislike issue decline bearish storm rainy cloudy".split())
    toks = tokenize(text)
    if not toks: return 0.0
    score = 0
    for t in toks:
        if t in pos: score += 1
        if t in neg: score -= 1
    return max(-1.0, min(1.0, score / max(1, len(toks)//8)))