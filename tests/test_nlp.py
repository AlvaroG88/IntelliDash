
import pytest
from intelligence.nlp import rake_keywords, textrank_summarize, tiny_sentiment, sentences, tokenize

def test_tokenize():
    text = "Hello world, this is a test!"
    expected = ["hello", "world", "this", "is", "a", "test"]
    assert tokenize(text) == expected

def test_sentences():
    text = "This is the first sentence. And this is the second one! Is this the third?"
    expected = ["This is the first sentence.", "And this is the second one!", "Is this the third?"]
    assert sentences(text) == expected

def test_rake_keywords():
    text = "The quick brown fox jumps over the lazy dog. The dog was not amused."
    keywords = rake_keywords(text, top_k=3)
    assert len(keywords) == 3
    phrases = [k[0] for k in keywords]
    assert "quick brown fox jumps" in phrases
    assert "lazy dog" in phrases
    assert "dog" in phrases or "amused" in phrases

def test_textrank_summarize():
    text = "This is the first sentence. This sentence is very important. This is the third sentence. The second sentence is key."
    summary = textrank_summarize(text, max_sentences=1)
    assert summary

def test_tiny_sentiment():
    positive_text = "This is a great, excellent, and wonderful product. I love it."
    assert tiny_sentiment(positive_text) > 0.5

    negative_text = "This is a bad, poor, and terrible product. I hate it."
    assert tiny_sentiment(negative_text) < -0.5

    neutral_text = "This is a product."
    assert tiny_sentiment(neutral_text) == 0.0

    mixed_text = "It has some good features, but also some bad ones."
    assert -0.3 < tiny_sentiment(mixed_text) < 0.3
