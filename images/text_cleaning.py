"""Text-cleaning helpers for Image captions.

strip_ethnic_type_descriptors() removes the "de type <ethnicity>" / "<ethnicity>
type" classification phrasing Philippe Mairesse flagged as discriminating
(2026-09-18 email): "de type africain / african type", "de type nord
africain / north african type", "de type maghrébin / maghrebian type" and
"de type asiatique / asian type". Per his "suppress the existing
discriminating terms" instruction (his preferred option over rephrasing),
the whole classification clause is deleted rather than reworded - this
leaves plain, ungendered captions like "Visage d'homme." / "Face of a man."
"""

import re

_ETHNICITY = r"(?:North African|African|Asian|Maghreb\w*)"

_FR_PATTERNS = [
    r"de type\s+nord[- ]africaines?",
    r"de type\s+nord[- ]africains?",
    r"de type\s+africaines?",
    r"de type\s+africains?",
    r"de type\s+maghr[ée]bines?",
    r"de type\s+maghr[ée]bins?",
    r"de type\s+asiatiques?",
]

# "Two young men OF North African type ARE walking" -> "... ARE walking":
# here "of ... type" is itself the predicate, so it goes too. This must run
# before the bare _EN_TYPE removal below.
_EN_OF_TYPE_ARE = re.compile(r"\bof\s+" + _ETHNICITY + r"[\s-]+type\s+(?=are\b)", re.IGNORECASE)

# "Face of African type man" / "Face of an African type man" keep "of [an]";
# only the classification word pair itself is discriminating. [\s-]+ also
# catches the hyphenated "African-type" variant.
_EN_TYPE = re.compile(r"\b" + _ETHNICITY + r"[\s-]+type\b", re.IGNORECASE)

_DETECT = re.compile("|".join(_FR_PATTERNS) + "|" + _EN_TYPE.pattern, re.IGNORECASE)
_MATCH_AT_START = re.compile(r"\s*(?:" + "|".join(_FR_PATTERNS) + "|" + _EN_TYPE.pattern + ")",
                              re.IGNORECASE)


def strip_ethnic_type_descriptors(text):
    """Remove ethnic-classification phrasing from a caption, leaving the
    rest of the sentence intact and grammatical. Returns the text unchanged
    (same object) if none of the flagged phrases are present."""
    if not text or not _DETECT.search(text):
        return text

    matched_at_start = bool(_MATCH_AT_START.match(text))

    new_text = _EN_OF_TYPE_ARE.sub("", text)
    for pattern in _FR_PATTERNS:
        new_text = re.sub(pattern, "", new_text, flags=re.IGNORECASE)
    new_text = _EN_TYPE.sub("", new_text)

    # whitespace/punctuation debris left behind by the removal
    new_text = re.sub(r"  +", " ", new_text)
    new_text = re.sub(r",\s*\.", ".", new_text)       # "femme, . " -> "femme. "
    new_text = re.sub(r"\s+([.,])", r"\1", new_text)  # "femme . " -> "femme. "
    new_text = new_text.strip()

    # "an African type man" -> "an man" -> fix the now-mismatched article
    new_text = re.sub(r"\ban(\s+)(?=[^aeiouAEIOU\s])", r"a\1", new_text)

    # the removed clause was the start of the sentence: recapitalize
    if matched_at_start and new_text and new_text[0].islower():
        new_text = new_text[0].upper() + new_text[1:]

    return new_text


# strip_ethnic_descriptors() is the broader follow-up Philippe asked for
# (2026-09-20, after strip_ethnic_type_descriptors() above had already
# removed the "de type X"/"X type" wording): "everything that puts people in
# a specific ethnic category" - i.e. a plain adjective too ("Femme
# africaine", "Asian woman"), not just the classification phrasing. Scoped
# to descriptions of PEOPLE only: a Chinese *restaurant*, Arabic *script* on
# an urn, or African *vegetation* are not a person's ethnicity and are left
# alone - only an ethnicity word immediately adjacent to a person-noun (or,
# in French, its "d'origine X" variant) is removed.
_FR_PERSON = r"(?:femmes?|hommes?|filles?|garçons?|enfants?|individus?|personnes?|couples?|dames?|gens)"
_EN_PERSON = r"(?:m[ae]n|wom[ae]n|girls?|boys?|child(?:ren)?|guys?|persons?|people|couples?|lad(?:y|ies)|gentlem[ae]n)"

_FR_ORIGIN_CLAUSE = re.compile(
    r"d['’]origine\s+(?:africaine?|maghr[ée]bine?|asiatiques?|chinoise?)\b", re.IGNORECASE
)
_FR_ADJ_NEAR_PERSON = re.compile(
    rf"\b({_FR_PERSON})\s+(?:africaine?s?|maghr[ée]bine?s?|asiatiques?|chinoise?s?)\b", re.IGNORECASE
)
# Standalone plural ethnicity noun as the sentence's own subject (e.g.
# "Asiatiques debout dans..."): deleting it outright would leave the
# sentence with no subject, so it's replaced with a neutral noun instead -
# but only when what follows reads as a verb ("debout", a present participle
# in "-ant(s)"), not another noun ("Asiatiques du quartier" is not this
# case, and neither is any pattern _FR_ADJ_NEAR_PERSON already handles).
_FR_SUBJECT_FALLBACK = re.compile(
    r"^(?:Africains?|Asiatiques?)\s+(?=\w+ants?\b|debout\b)", re.IGNORECASE
)

_EN_ORIGIN_CLAUSE = re.compile(r"\bof\s+North African origin\b", re.IGNORECASE)
_EN_ADJ_NEAR_PERSON = re.compile(
    rf"\b(?:North African|African|Asian|Chinese)(-looking)?\s+({_EN_PERSON})\b", re.IGNORECASE
)
# Same reasoning as _FR_SUBJECT_FALLBACK: only fires when followed by a
# present participle ("standing", "drawing", ...), which is the shape of
# every case actually found in this corpus ("Asians standing...", "Africans
# drawing..."). An unusual order like "Asian bust woman" (ethnicity, then a
# non-person noun, then the person noun) matches neither this nor the
# adjacency check above and is deliberately left untouched rather than
# risk producing a broken sentence - flagged for manual review instead.
_EN_SUBJECT_FALLBACK = re.compile(r"^(?:Africans?|Asians?)\s+(?=\w+ing\b)", re.IGNORECASE)


def strip_ethnic_descriptors(text, lang):
    """Remove a plain-adjective ethnicity description of a person (lang is
    "fr" or "en"), leaving descriptions of places/objects/languages (a
    Chinese restaurant, Arabic script, African vegetation) untouched.
    Returns the text unchanged if no person-adjacent ethnicity word is
    found."""
    if not text:
        return text

    original = text
    if lang == "fr":
        before = text
        text = _FR_ORIGIN_CLAUSE.sub("", text)
        text = _FR_ADJ_NEAR_PERSON.sub(r"\1", text)
        if text == before:
            text = _FR_SUBJECT_FALLBACK.sub("Personnes ", text)
    else:
        before = text
        text = _EN_ORIGIN_CLAUSE.sub("", text)
        text = _EN_ADJ_NEAR_PERSON.sub(r"\2", text)
        if text == before:
            text = _EN_SUBJECT_FALLBACK.sub("People ", text)

    if text == original:
        return original

    new_text = re.sub(r"  +", " ", text)
    new_text = re.sub(r",\s*\.", ".", new_text)
    new_text = re.sub(r"\s+([.,])", r"\1", new_text)
    new_text = new_text.strip()

    # "an African-looking man" -> "an man" -> "a man"; case-preserving so a
    # sentence-initial "An X..." -> "A X..." is fixed too.
    new_text = re.sub(r"\b([Aa])n(\s+)(?=[^aeiouAEIOU\s])", r"\1\2", new_text)

    if original[:1].isupper() and new_text[:1].islower():
        new_text = new_text[0].upper() + new_text[1:]

    return new_text
