# Small hardcoded per-language stopword lists rather than a full NLP
# dependency: this is a curated caption archive with short, controlled
# vocabulary notules, not free text, so a fixed list is enough to strip
# function words that otherwise dominate exact-match/semantic search
# results. Selected by request.LANGUAGE_CODE rather than combined, so e.g.
# French "on" (we) doesn't get stripped out of an English query and vice
# versa for words that mean something in one language and nothing in the
# other.

STOPWORDS_EN = frozenset({
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "has", "have", "had", "he", "in", "is", "it", "its", "of", "on",
    "or", "that", "the", "to", "was", "were", "will", "with", "this",
    "these", "those", "but", "not", "so", "if", "then", "than", "too",
    "very", "can", "do", "does", "did", "i", "you", "we", "they",
})

STOPWORDS_FR = frozenset({
    "le", "la", "les", "un", "une", "des", "de", "du", "et", "ou",
    "est", "sont", "à", "au", "aux", "dans", "sur", "pour", "par",
    "avec", "sans", "ce", "cette", "ces", "qui", "que", "quoi",
    "il", "elle", "ils", "elles", "nous", "vous", "je", "tu",
    "ne", "pas", "plus", "moins", "trop", "très", "mais", "donc",
    "se", "sa", "son", "ses", "leur", "leurs", "on", "en", "y",
})


def stopwords_for_language(language_code):
    return STOPWORDS_EN if language_code == 'en' else STOPWORDS_FR


def filter_stopwords(terms, stopwords):
    return [term for term in terms if term.lower() not in stopwords]
