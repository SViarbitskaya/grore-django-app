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

_ETHNICITY = r"(?:North African|African|Asian|Maghreb\w*|Creole)"

_FR_PATTERNS = [
    r"de type\s+nord[- ]africaines?",
    r"de type\s+nord[- ]africains?",
    r"de type\s+africaines?",
    r"de type\s+africains?",
    r"de type\s+maghr[ée]bines?",
    r"de type\s+maghr[ée]bins?",
    r"de type\s+asiatiques?",
    r"de type\s+cr[ée]oles?",  # missed in September, found by the 2026-10 audit
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


# ---------------------------------------------------------------------------
# 2026-10 caption translation audit, approved by Philippe Mairesse. Applied by
# clean_caption_pair() below, from both the fix_caption_translations command
# and data migration 0016 (so Demarchic and production get it on deploy).
# ---------------------------------------------------------------------------

def _match_case(original, replacement):
    return replacement[0].upper() + replacement[1:] if original[:1].isupper() else replacement


def _tidy(original, text):
    """Whitespace/punctuation/article debris after removing words."""
    if text == original:
        return original
    text = re.sub(r"  +", " ", text)
    text = re.sub(r",\s*([.,])", r"\1", text)
    text = re.sub(r"\s+([.,])", r"\1", text)
    text = text.strip()
    text = re.sub(r"\b([Aa])n(\s+)(?=[^aeiouAEIOU\s])", r"\1\2", text)
    if original[:1].isupper() and text[:1].islower():
        text = text[0].upper() + text[1:]
    return text


# "Homme brun" means a dark-haired man, but the English said "brown man" -
# which reads as skin colour. "châtain" is a lighter brown hair colour. Only
# "brown" directly before a person noun is touched (a brown sofa, brown eyes
# or "brown-haired" are left alone), and only when the French has the word.
_EN_PERSON_AFTER_COLOUR = (
    r"(?:(?:young|little)\s+)?"
    r"(?:m[ae]n|wom[ae]n|girls?|boys?|child(?:ren)?|toddlers?|bab(?:y|ies)|"
    r"teenagers?|persons?|people|couples?|kids?)\b"
)
_EN_LIGHT_BROWN_PERSON = re.compile(r"\blight[\s-]brown\s+(?=" + _EN_PERSON_AFTER_COLOUR + ")", re.IGNORECASE)
_EN_BROWN_PERSON = re.compile(r"\bbrown\s+(?=" + _EN_PERSON_AFTER_COLOUR + ")", re.IGNORECASE)
_FR_BRUN = re.compile(r"\bbrun(?:e|s|es)?\b", re.IGNORECASE)
_FR_CHATAIN = re.compile(r"\bch[âa]tains?\b", re.IGNORECASE)


def fix_brown_hair_translation(fr, en):
    if not fr or not en:
        return en
    has_brun, has_chatain = _FR_BRUN.search(fr), _FR_CHATAIN.search(fr)
    if not (has_brun or has_chatain):
        return en
    new = _EN_LIGHT_BROWN_PERSON.sub(lambda m: _match_case(m.group(0), "light-brown-haired "), en)
    hair = "dark-haired " if has_brun else "brown-haired "
    return _EN_BROWN_PERSON.sub(lambda m: _match_case(m.group(0), hair), new)


# Skin colour of a person ("à la peau sombre", "femme noire", "dark-skinned",
# "black girl") removed in both languages. The English black/white rule only
# runs when the French itself describes skin colour, so "white man" for a
# man in white clothes, or "Black and white." photo notes, are never touched.
_FR_SKIN_PERSON = _FR_PERSON[:-1] + r"|fillettes?|nourrissons?|bébés?)"
_FR_SKIN_CLAUSE = re.compile(
    r"\s*(?:à|et)\s+(?:la\s+)?peau\s+(?:sombre|fonc[ée]e|noire|mate|claire|blanche)\b", re.IGNORECASE
)
_FR_SKIN_ADJ = re.compile(rf"\b({_FR_SKIN_PERSON})\s+(?:noire?s?|blanche?s?|blancs?)\b", re.IGNORECASE)
# These can only describe a person's skin, so they go even when only the
# English mentions it (some translations added a skin colour the French
# never had, e.g. "Visage souriant d'enfant" -> "...child with dark skin").
_EN_SKIN_COMPOUND = re.compile(r"\b(?:dark|light|fair|olive|black|brown)-skinned\s+", re.IGNORECASE)
_EN_SKIN_PHRASE = re.compile(r",?\s*(?:with|and)\s+(?:dark|black|brown)\s+skin\b", re.IGNORECASE)
_EN_SKIN_ADJ = re.compile(r"\b(?:black|white)\s+(?=" + _EN_PERSON_AFTER_COLOUR + ")", re.IGNORECASE)


def strip_skin_colour(fr, en):
    new_fr = fr
    if fr:
        new_fr = _FR_SKIN_ADJ.sub(r"\1", _FR_SKIN_CLAUSE.sub("", fr))
    new_en = en
    if en:
        new_en = _EN_SKIN_PHRASE.sub("", _EN_SKIN_COMPOUND.sub("", en))
        if new_fr != fr:
            new_en = _EN_SKIN_ADJ.sub("", new_en)
        new_en = _tidy(en, new_en)
    return (_tidy(fr, new_fr) if fr else fr), new_en


# "amorce" here is the film leader at the start of a roll, not "primer".
_FR_AMORCE = re.compile(r"\bamorces?\b", re.IGNORECASE)
_EN_PRIMER = re.compile(r"\bprimer\b", re.IGNORECASE)


# "Amorce ?" / "Amorce ???" - an internal "is this the film leader?" query -
# becomes a plain "Amorce." / "Film leader.".
_FR_AMORCE_QUERY = re.compile(r"\b(Amorce)\s*\?+", re.IGNORECASE)
_EN_FILM_LEADER_QUERY = re.compile(r"\b(Film leader)\s*\?+", re.IGNORECASE)


def drop_film_leader_query(fr, en):
    if fr:
        fr = _FR_AMORCE_QUERY.sub(r"\1.", fr)
    if en:
        en = _EN_FILM_LEADER_QUERY.sub(r"\1.", en)
    return fr, en


def fix_film_leader_translation(fr, en):
    if not fr or not en or not _FR_AMORCE.search(fr):
        return en
    return _EN_PRIMER.sub(lambda m: _match_case(m.group(0), "film leader"), en)


# One-off corrections by image identifier: (old substring, new substring)
# pairs applied to the text the pattern steps above leave behind. A pair
# whose old text is no longer there (caption hand-edited since the audit)
# is skipped, never forced.
_AFRO_AMERICAN_SINGER = {"fr": [("Chanteuse afro-américaine en", "Chanteuse en")],
                         "en": [("African-American singer in", "Singer in")]}

CAPTION_CORRECTIONS = {
    # Internal cataloguing notes ("???", "je ne sais pas ce que c'est")
    # replaced by a neutral description.
    "A1292": {"fr": [("front\u00a0???.", "front.")], "en": [("forehead???.", "forehead.")]},
    "A1415": {"fr": [("devant l’entrée de\u00a0??? Fragment", "devant une entrée. Fragment")],
              "en": [("in front of the entrance to ??? Torn", "in front of an entrance. Torn")]},
    "A2441": {"fr": [("???? vue non identifiée, contact, dia, film\u00a0?", "Vue non identifiée.")],
              "en": [("???? unidentified view, contact, slide, film?", "Unidentified view.")]},
    "A5215": {"fr": [("je ne sais pas ce que c’est\u00a0????", "Vue non identifiée.")],
              "en": [("I don’t know what it is????", "Unidentified view.")]},
    "A5223X": {"fr": [("Ciel bleu\u00a0?.", "Ciel bleu.")], "en": [("Blue sky?.", "Blue sky.")]},
    # also "enceinte" (loudspeaker) mistranslated "Pregnant"
    "A5324": {"fr": [("Enceinte\u00a0? radar\u00a0? je ne sais pas ce que c’est\u00a0?.", "Vue non identifiée.")],
              "en": [("Pregnant ? radar? I don't know what it is?.", "Unidentified view.")]},
    "A6625": {"fr": [("Cadre\u00a0?.", "Cadre.")], "en": [("Frame ?.", "Frame.")]},
    "X1320X": {"fr": [("Pliée\u00a0????", "Pliée.")], "en": [("Folded ????", "Folded.")]},
    "X2185": {"fr": [("Jeune buffle, bison ?.", "Jeune buffle ou bison.")],
              "en": [("Young buffalo, bison?", "Young buffalo or bison.")]},
    "X4113": {"fr": [("Vue non identifiée, Gravats\u00a0??? Fragment.", "Vue non identifiée, gravats. Fragment.")],
              "en": [("Unidentified View, Rubble??? Fragment.", "Unidentified view, rubble. Fragment.")]},
    "X5345": {"fr": [("Planche contact\u00a0???", "Planche contact.")], "en": [("Contact sheet???", "Contact sheet.")]},
    "X6458X": {"fr": [("Schéma de moteur\u00a0???", "Schéma de moteur.")],
               "en": [("Engine diagram???", "Engine diagram.")]},
    # "homme" translated as the informal "guy" (left over once the September
    # cleanup removed "African"/"Asian" in front of it)
    "A1525": {"en": [("Face of young guy with shirt.", "Face of young man in a shirt.")]},
    "A1556": {"en": [("Guy sitting cross-legged", "Man sitting cross-legged")]},
    "A3310": {"en": [("Guy face with yellow jacket.", "Face with yellow jacket.")]},
    "A5621X": {"en": [("Guy man face with striped tie.", "Man's face with striped tie.")]},
    "X3136X": {"en": [("Young smiling guy hugs", "Smiling young man hugs")]},
    # ethnicity of a person missed by the September cleanup (its regexes
    # deliberately skip unusual word orders like "Asian bust woman")
    "X5622": {"en": [("Asian bust woman.", "Bust of a woman.")]},
    "X6436X": _AFRO_AMERICAN_SINGER,
    "X6437X": _AFRO_AMERICAN_SINGER,
    "X6438X": _AFRO_AMERICAN_SINGER,
    "X6439X": _AFRO_AMERICAN_SINGER,
    # other mistranslations
    "A1111": {"en": [("Race field with", "Racecourse with")]},
    "A1304": {"en": [("with wife and child", "with a woman and a child")]},
    "A1372": {"en": [("Pipes and pipes.", "Ducts and pipes.")]},
    "A3615": {"en": [("Brown head.", "Head with dark hair.")]},
    "X5278": {"en": [("Brown-haired man", "Dark-haired man"), ("library in background", "bookcase in background")]},
    "X5665X": {"en": [("Feet for growing marinière mussels.", "Stakes for mussel farming.")]},
    "X6288": {"en": [("Notre-Dame Cathedral square and square.",
                      "Notre-Dame Cathedral forecourt and garden square.")]},
}


def apply_caption_corrections(identifier, fr, en):
    corrections = CAPTION_CORRECTIONS.get(identifier, {})
    for old, new in corrections.get("fr", ()):
        if fr and old in fr:
            fr = fr.replace(old, new)
    for old, new in corrections.get("en", ()):
        if en and old in en:
            en = en.replace(old, new)
    return fr, en


def clean_caption_pair(identifier, fr, en):
    """Every approved caption cleanup, in order: the September ethnicity
    removals, then the 2026-10 audit fixes. Idempotent, so it is safe to
    run on data that has already been partly or fully cleaned."""
    fr = strip_ethnic_descriptors(strip_ethnic_type_descriptors(fr), "fr")
    en = strip_ethnic_descriptors(strip_ethnic_type_descriptors(en), "en")
    en = fix_brown_hair_translation(fr, en)
    fr, en = strip_skin_colour(fr, en)
    en = fix_film_leader_translation(fr, en)
    fr, en = drop_film_leader_query(fr, en)
    return apply_caption_corrections(identifier, fr, en)
