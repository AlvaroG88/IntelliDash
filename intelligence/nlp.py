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
    """
    Heuristic sentiment analysis with an expanded lexicon and basic negation handling.
    Returns a score between -1.0 (negative) and 1.0 (positive).
    """
    # Expanded lexicon
    pos_words = {
        "good", "great", "excellent", "positive", "benefit", "win", "success", "safe", "fast", "easy", "love", "like", 
        "improvement", "growth", "bullish", "sunny", "clear", "best", "amazing", "awesome", "nice", "cool", "happy", 
        "joy", "gain", "profit", "up", "boom", "strong", "rich", "fresh", "clean", "bright", "smooth", "smart", "wise", 
        "pure", "free", "top", "hot", "hit", "pro", "plus", "award", "star", "hero", "secure", "stable", "trust", 
        "faith", "hope", "luck", "peace", "calm", "simple", "quick", "swift", "agile", "fit", "bold", "brave", "kind", 
        "sweet", "fun", "funny", "humor", "laugh", "smile", "grin", "joke", "wit", "art", "beauty", "soul", "mind", 
        "heart", "spirit", "life", "live", "born", "grow", "heal", "cure", "fix", "solve", "save", "help", "aid", 
        "support", "gift", "prize", "bonus", "deal", "cheap", "gold", "gem", "jewel", "pearl", "silk", "soft", "warm", 
        "shine", "light", "sun", "sky", "moon", "sea", "beach", "ocean", "river", "hill", "mountain", "peak", "high", 
        "rise", "fly", "soar", "wing", "bird", "friend", "pal", "mate", "buddy", "family", "home", "house", "health", 
        "gym", "run", "walk", "play", "game", "sport", "glad", "merry", "jolly", "fortune", "chance", "destiny", 
        "truth", "fact", "real", "true", "right", "just", "fair", "goal", "aim", "target", "value", "worth", "innovative",
        "breakthrough", "revolutionary", "upgrade", "new", "launch", "release", "announce", "reveal", "unveil"
    }
    
    neg_words = {
        "bad", "poor", "terrible", "negative", "loss", "fail", "risk", "slow", "hard", "hate", "dislike", "issue", 
        "decline", "bearish", "storm", "rainy", "cloudy", "worst", "awful", "horrible", "nasty", "ugly", "sad", 
        "unhappy", "grief", "pain", "hurt", "harm", "kill", "die", "dead", "death", "sick", "ill", "disease", "virus", 
        "flu", "cold", "fever", "cough", "ache", "wound", "cut", "break", "broke", "broken", "smash", "crash", "burn", 
        "fire", "hell", "demon", "devil", "evil", "sin", "crime", "jail", "prison", "war", "fight", "battle", "murder", 
        "rob", "steal", "lie", "cheat", "fake", "false", "wrong", "error", "fault", "bug", "defect", "flaw", "weak", 
        "dull", "dark", "dim", "gloom", "shade", "shadow", "cloud", "rain", "snow", "ice", "waste", "junk", "scrap", 
        "rot", "decay", "poison", "toxic", "acid", "sour", "bitter", "tear", "cry", "scream", "yell", "shout", "anger", 
        "rage", "fear", "dread", "panic", "scare", "terror", "horror", "ghost", "monster", "beast", "enemy", "foe", 
        "rival", "opponent", "disgust", "shame", "guilt", "vice", "mistake", "debt", "cost", "price", "pay", "bill", 
        "tax", "fine", "fee", "penalty", "lock", "ban", "stop", "end", "quit", "leave", "go", "away", "off", "down", 
        "fall", "drop", "sink", "low", "bottom", "under", "below", "less", "minus", "lose", "lost", "miss", "crisis",
        "crash", "collapse", "recession", "depression", "inflation", "shortage", "outage", "leak", "hack", "breach",
        "scam", "fraud", "lawsuit", "sue", "court", "trial", "judge", "jury", "verdict", "guilty", "charge", "arrest"
    }

    negations = {"not", "no", "never", "neither", "nor", "none", "nobody", "nowhere", "nothing", "hardly", "scarcely", "barely", "doesn't", "isn't", "wasn't", "shouldn't", "wouldn't", "couldn't", "won't", "can't", "don't"}

    toks = tokenize(text)
    if not toks: return 0.0
    
    score = 0.0
    # Look at words in context of previous word for negation
    for i, t in enumerate(toks):
        val = 0
        if t in pos_words:
            val = 1
        elif t in neg_words:
            val = -1
            
        # Check negation
        if i > 0 and toks[i-1] in negations:
            val *= -1
            
        score += val

    # Normalize: divide by a factor related to length, but dampen it so short sentences can have high impact
    # Using sqrt(len) helps balance short vs long texts better than linear division
    norm_factor = math.sqrt(len(toks))
    if norm_factor < 1: norm_factor = 1
    
    final_score = score / norm_factor
    
    # Clamp between -1 and 1
    return max(-1.0, min(1.0, final_score))
