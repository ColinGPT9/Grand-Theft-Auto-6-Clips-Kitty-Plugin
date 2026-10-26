# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ColinGPT9
"""Conservative text cues for GTA footage, without object recognition.

These rules describe what was said or explicitly tagged, not what a camera
proved. A caller must retain that provenance when explaining a highlight.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

CATEGORIES = (
    "chase", "crash", "stunt", "combat", "npc_chaos", "funny_dialogue",
    "roleplay", "reaction", "milestone",
)
CATEGORY_LABELS = {
    "chase": "Chase",
    "crash": "Crash",
    "stunt": "Stunt",
    "combat": "Combat",
    "npc_chaos": "NPC chaos",
    "funny_dialogue": "Funny dialogue",
    "roleplay": "Roleplay",
    "reaction": "Reaction",
    "milestone": "Mission progress",
}


@dataclass(frozen=True)
class Cue:
    """A phrase that supports one category, with a bounded rule strength."""

    category: str
    phrase: str
    strength: float


# Every pattern has word boundaries: a substring such as "fire" in "campfire"
# or "crash" in a username is never sufficient.
_RULES = (
    ("chase", 0.88, r"(?:cops|police) (?:are |were |keep |kept )?(?:chasing|following|after) (?:me|us)"),
    ("chase", 0.82, r"(?:police|cop|high speed) chase"),
    ("chase", 0.86, r"(?:escaped|lost|outran|evaded) (?:the )?(?:cops|police)"),
    ("crash", 0.90, r"(?:i|we|he|she|they|you) (?:(?:just|actually|really|totally|suddenly) )?crashed"),
    ("crash", 0.88, r"crashed (?:right |straight )?into\b(?: [\w']+){0,4}"),
    ("crash", 0.84, r"(?:car|truck|bike|vehicle) (?:(?:just|completely) )?(?:flipped|rolled|exploded)"),
    ("crash", 0.86, r"(?:head on collision|massive pileup|huge pileup|multi car pileup)"),
    ("crash", 0.84, r"(?:spun out|spinning out|lost control of (?:the|my|our) (?:car|truck|bike))"),
    ("crash", 0.88, r"(?:chocamos|choqu[eé]|se estrell[oó] (?:el|mi|nuestro) (?:auto|coche|carro))"),
    ("chase", 0.86, r"(?:la polic[ií]a|los polic[ií]as) (?:me|nos) (?:persigue|persiguen|est[aá]n persiguiendo)"),
    ("chase", 0.86, r"(?:escapamos|escap[eé]|huimos) de (?:la polic[ií]a|los polic[ií]as)"),
    ("combat", 0.83, r"(?:nos|me) (?:disparan|est[aá]n disparando|emboscaron)"),
    ("stunt", 0.91, r"(?:landed|nailed|stuck) (?:(?:that|the|a) )?(?:jump|stunt|backflip|frontflip|landing)"),
    ("stunt", 0.91, r"stunt jump (?:complete|completed|successful)"),
    ("stunt", 0.86, r"pulled off (?:(?:that|the|a) )?(?:stunt|jump|backflip|barrel roll)"),
    ("stunt", 0.82, r"(?:did|landed) (?:(?:a|the|that) )?(?:backflip|frontflip|barrel roll)"),
    ("stunt", 0.85, r"(?:missed|failed) (?:(?:that|the|a) )?(?:landing|jump|stunt|backflip)"),
    ("combat", 0.85, r"(?:shootout|firefight|gunfight|shots fired)"),
    ("combat", 0.87, r"(?:i|we|he|she|they|you) (?:(?:just|actually) )?(?:got shot|got ambushed)"),
    ("combat", 0.84, r"(?:blew up|shot down) (?:the|that|a) (?:car|truck|helicopter|chopper|plane|tank)"),
    ("npc_chaos", 0.89, r"(?:npc|pedestrian) (?:(?:just|actually|suddenly) )?(?:stole|attacked|punched|rammed|carjacked)\b(?: [\w']+){0,4}"),
    ("npc_chaos", 0.85, r"(?:npc|pedestrian) (?:just )?(?:went flying|ran into|walked into|started fighting)"),
    ("npc_chaos", 0.79, r"npc chaos"),
    ("funny_dialogue", 0.88, r"(?:that|this) (?:was|is) (?:absolutely |so )?hilarious"),
    ("funny_dialogue", 0.86, r"(?:that's|that is|this is) (?:absolutely |so )?hilarious"),
    ("funny_dialogue", 0.89, r"i (?:cannot|can't|can not) stop laughing"),
    ("funny_dialogue", 0.88, r"(?:i'm|i am|we're|we are) (?:literally )?dying (?:of laughter|laughing)"),
    ("funny_dialogue", 0.84, r"(?:the funniest thing|that made me laugh|that cracked me up)"),
    ("funny_dialogue", 0.81, r"(?:that punchline|what a punchline|everyone (?:is|was) laughing|we're laughing so hard)"),
    ("roleplay", 0.80, r"(?:traffic stop|under arrest|you have the right to remain silent|in character|roleplay scene)"),
    ("reaction", 0.79, r"(?:no way|oh my god|oh my goodness|what just happened|are you kidding me)"),
    ("reaction", 0.82, r"i (?:can't|cannot|can not) believe (?:that|this|it)"),
    ("reaction", 0.79, r"(?:holy (?:shit|crap)|that was (?:fucking |so |absolutely )?crazy|no me lo (?:creo|puedo creer))"),
    ("milestone", 0.86, r"(?:mission|heist) (?:passed|complete|completed|failed)"),
    ("milestone", 0.84, r"(?:passed|completed|finished|failed) (?:the|this|that|a) (?:mission|heist)"),
    ("milestone", 0.88, r"(?:final|last) wave (?:cleared|complete|completed|survived)"),
    ("milestone", 0.88, r"survived (?:the )?(?:final|last) wave"),
    ("milestone", 0.88, r"all (?:(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten) )?waves (?:cleared|completed|survived)"),
)
_COMPILED_RULES = tuple(
    (category, strength, re.compile(r"\b(?:" + pattern + r")\b"))
    for category, strength, pattern in _RULES
)

_NORMALIZATION = str.maketrans({"’": "'", "‘": "'", "‐": " ", "‑": " ", "–": " ", "—": " ", "-": " "})
_SENTENCES = re.compile(r"[^.!?;\n]+[.!?;]?")
_CONTRAST = re.compile(r"\b(?:but|however|yet|pero)\b")
_HYPOTHETICAL = re.compile(
    r"\b(?:if|unless|suppose|supposing|imagine|hypothetically|wish|wishing|"
    r"would|could|might|maybe|perhaps|should|si|imagina|quiz[aá]s|tal vez|ojal[aá])\b"
)
_PLANNING = re.compile(
    r"\b(?:going to|gonna|will|shall|about to|plan to|planning to|want to|"
    r"wanna|trying to|try to|let's|lets|tomorrow|next time|is coming|"
    r"vamos a|voy a|iba a|quiero|ma[nñ]ana|la pr[oó]xima vez)\b"
)
_INSTRUCTION = re.compile(
    r"\b(?:how to|how do (?:i|we|you)|tutorial|tips for|to avoid|you can|"
    r"when you|whenever|usually|every time|remember when|remember that|last time|yesterday|"
    r"last (?:week|month|year|night)|(?:days?|weeks?|months?|years?) ago|"
    r"retelling|in my dream|in the (?:movie|story)|my plan|ayer|anoche|la semana pasada|"
    r"en mi sue[nñ]o|recuerdo cuando|cada vez|c[oó]mo evitar)\b"
)
_RETRACTED = re.compile(
    r"\b(?:not real|fake|did not happen|didn't happen|never happened|"
    r"just a joke|only joking|just kidding|"
    r"(?:isn't|wasn't|aren't|weren't|is not|was not|are not|were not) (?:real|happening|true)|"
    r"(?:won't|will not|doesn't|does not) happen|no pas[oó]|no ocurri[oó]|era una broma|fue un sue[nñ]o)\b"
)
_NEGATION = re.compile(
    r"\b(?:no|not|never|without|don't|doesn't|didn't|isn't|aren't|wasn't|"
    r"weren't|hasn't|haven't|hadn't|can't|cannot|couldn't|wouldn't|won't|"
    r"ain't|stop saying|stopped saying|nunca|jam[aá]s|sin)\b"
)


def _clauses(text: str):
    """Keep conditional context across commas; reset at explicit contrast."""
    normalized = text.lower().translate(_NORMALIZATION)
    # A historical/planned frame can span several sentences in one supplied
    # utterance. Only explicit contrast/current-time language resets it.
    framed = False
    if _RETRACTED.search(normalized):
        return
    for sentence in _SENTENCES.findall(normalized):
        # A question about an event does not establish that it happened.
        # Familiar reaction questions do express a reaction, handled below.
        question = sentence.rstrip().endswith("?")
        for clause in _CONTRAST.split(sentence):
            clause = re.sub(r"\s+", " ", clause).strip(" ,.!?;")
            if clause:
                # Spanish "no, que ..." is an alarmed interjection. A real
                # negator inside the following clause remains effective.
                clause = re.sub(r"\bno,\s+(?=que\b)", "", clause)
                if re.search(r"\bcrashed (?:straight |right )?into (?:no|none)\b", clause):
                    continue
                if _CONTRAST.search(sentence) or re.search(r"\b(?:now|right now|this time|ahora)\b", clause):
                    framed = False
                if _INSTRUCTION.search(clause) or _PLANNING.search(clause) or _HYPOTHETICAL.search(clause):
                    framed = True
                if not framed:
                    yield clause, question


def classify_text(text: str, *, roleplay_enabled: bool = False) -> tuple[Cue, ...]:
    """Return at most one explicit, non-hypothetical cue per category.

    Rule strengths are text specificity, not calibrated probabilities. Broad
    gameplay nouns and future plans deliberately produce no cues. Roleplay
    phrases are considered only when the caller explicitly enables them.
    """
    if not isinstance(text, str) or not text.strip():
        return ()
    best: dict[str, Cue] = {}
    for clause, question in _clauses(text):
        if (_HYPOTHETICAL.search(clause) or _INSTRUCTION.search(clause)
                or _RETRACTED.search(clause) or _PLANNING.search(clause)):
            continue
        for category, strength, pattern in _COMPILED_RULES:
            if category == "roleplay" and not roleplay_enabled:
                continue
            if question and category != "reaction":
                continue
            for match in pattern.finditer(clause):
                # Restrict negation to nearby preceding language. A contrast
                # such as "didn't crash, but then crashed into ..." has its
                # own clause, and can therefore recover a positive event.
                prefix = " ".join(clause[:match.start()].split()[-8:])
                if _NEGATION.search(prefix) or (category != "reaction" and re.search(r"\b(?:no|not|never|none)\b", match.group(0))):
                    continue
                cue = Cue(category, match.group(0), strength)
                if category not in best or strength > best[category].strength:
                    best[category] = cue
    return tuple(best[category] for category in CATEGORIES if category in best)


def classify_tags(tags: tuple[str, ...], *, roleplay_enabled: bool = False) -> tuple[Cue, ...]:
    """Read exact explicit event tags; trust/provenance is the caller's job.

    Arbitrary captions, broad tags such as "police", and similar-looking
    substrings are intentionally ignored.
    """
    found: set[str] = set()
    for tag in tags:
        if not isinstance(tag, str):
            continue
        value = tag.strip().lower()
        if value.startswith("event:"):
            value = value[6:]
        if value in CATEGORIES and (value != "roleplay" or roleplay_enabled):
            found.add(value)
    return tuple(Cue(category, "event:" + category, 0.90) for category in CATEGORIES if category in found)


__all__ = ["CATEGORIES", "CATEGORY_LABELS", "Cue", "classify_tags", "classify_text"]
