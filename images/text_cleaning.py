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
