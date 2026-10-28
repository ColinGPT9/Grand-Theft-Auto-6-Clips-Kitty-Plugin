# SPDX-License-Identifier: MIT
# Copyright (c) 2026 ColinGPT9
"""Offline tests for explicit event language and its limits."""

import pytest

from gta_highlights.taxonomy import CATEGORIES, Cue, classify_tags, classify_text


def categories(text, **kwargs):
    return {cue.category for cue in classify_text(text, **kwargs)}


@pytest.mark.parametrize(("text", "expected"), [
    ("I hit the ramp and immediately spun out.", "crash"),
    ("We lost control of our truck!", "crash"),
    ("Chocamos contra un taxi.", "crash"),
    ("No, que chocamos contra una pared!", "crash"),
    ("Estoy intentando escapar de los agentes, no, que chocamos!", "crash"),
    ("La policia nos persigue.", "chase"),
    ("Escapamos de la policia.", "chase"),
    ("Nos estan disparando.", "combat"),
    ("Holy crap!", "reaction"),
    ("That was so crazy!", "reaction"),
    ("No me lo puedo creer!", "reaction"),
    ("No chocamos, pero ahora chocamos contra un poste.", "crash"),
])
def test_stream_commentary_phrases_keep_their_supported_category(text, expected):
    assert expected in categories(text)


@pytest.mark.parametrize("text", [
    "No chocamos contra un taxi.", "Nunca chocamos.", "No, que no chocamos!",
    "Si chocamos nos atrapan.", "Vamos a chocar.", "Voy a chocar.",
    "Ayer chocamos.", "Anoche chocamos.", "Cada vez chocamos.",
    "En mi sueno chocamos.", "Chocamos. No paso.",
    "Imagine I spun out.", "I am going to spin out.", "I never spun out.",
    "Yesterday I spun out.", "My game crashed.", "Ordinary driving today.",
])
def test_stream_commentary_still_rejects_plans_history_negation_and_software(text):
    assert not categories(text)


@pytest.mark.parametrize(("text", "expected"), [
    ("The cops are chasing me!", "chase"),
    ("We escaped the police.", "chase"),
    ("We crashed into a truck!", "crash"),
    ("That car just flipped.", "crash"),
    ("I landed that jump!", "stunt"),
    ("STUNT JUMP COMPLETE", "stunt"),
    ("I tried the jump but missed the landing.", "stunt"),
    ("We failed that jump.", "stunt"),
    ("There is a shootout outside.", "combat"),
    ("I just got shot.", "combat"),
    ("An NPC just stole my car.", "npc_chaos"),
    ("The pedestrian went flying!", "npc_chaos"),
    ("That was hilarious.", "funny_dialogue"),
    ("I cannot stop laughing.", "funny_dialogue"),
    ("I’m dying laughing!", "funny_dialogue"),
    ("That NPC just said the funniest thing!", "funny_dialogue"),
    ("The NPC just said a line. That punchline killed me!", "funny_dialogue"),
    ("What just happened?", "reaction"),
    ("No way!", "reaction"),
    ("I can’t believe that!", "reaction"),
])
def test_actual_event_or_reaction_has_a_specific_cue(text, expected):
    assert expected in categories(text)


@pytest.mark.parametrize("text", [
    "If we crashed into that truck it would be hilarious.",
    "Imagine a police chase.",
    "We might have a shootout.",
    "Maybe the NPC just stole my car.",
    "I wish I landed that jump.",
    "I am going to say we crashed.",
    "We're gonna start a shootout.",
    "Let's do a police chase.",
    "I want to see a car flipped.",
    "How to avoid a police chase.",
    "How do I do a stunt jump complete?",
    "When you escaped the police, the tutorial ends.",
    "Remember when we crashed into a truck?",
    "Yesterday we crashed.",
    "We did not crash into a truck.",
    "We never crashed into a truck.",
    "There was no shootout.",
    "We didn’t say we crashed.",
    "I don't think the cops are chasing me.",
    "The shootout did not happen.",
    "That police chase was fake.",
    "The shootout wasn't real.",
    "The shootout won't happen.",
    "The shootout isn't happening.",
    "A police chase is coming.",
    "A police chase tomorrow.",
    "That was hilarious, just kidding.",
    "Did we crash?",
    "Did we crash into a truck?",
    "Was that a shootout?",
    "We drive a car past the police and jump over a fence.",
    "Fire at the campfire. I like the kill switch.",
    "User crashmaster has joined with npc_chaos_123.",
    "The NPC just said hello.",
])
def test_unsubstantiated_event_language_is_not_a_cue(text):
    assert classify_text(text) == ()


def test_negation_before_contrast_does_not_erase_later_actual_event():
    cues = classify_text("We did not crash, but then crashed into a truck.")
    assert {cue.category for cue in cues} == {"crash"}
    assert "crashed into a truck" in cues[0].phrase


def test_hypothetical_before_contrast_does_not_erase_later_actual_event():
    assert "crash" in categories("If we crashed it would be bad; but we crashed into a truck.")


def test_conditional_context_is_kept_across_commas():
    assert classify_text("If we get to the bridge, we escaped the police.") == ()


def test_categories_can_coexist_without_repetition_inflating_evidence():
    cues = classify_text("Cops are chasing me. We crashed! We crashed! Oh my god!")
    assert [cue.category for cue in cues] == ["chase", "crash", "reaction"]
    assert all(isinstance(cue, Cue) and 0 <= cue.strength <= 1 for cue in cues)


def test_roleplay_requires_opt_in():
    text = "This is a traffic stop. You are under arrest."
    assert "roleplay" not in categories(text)
    assert "roleplay" in categories(text, roleplay_enabled=True)


def test_tags_are_exact_and_ordered_and_do_not_enable_roleplay():
    cues = classify_tags(("event:combat", "chase", "event:chase", "police", "crashmaster", "roleplay"))
    assert [cue.category for cue in cues] == ["chase", "combat"]
    assert all(cue.phrase.startswith("event:") for cue in cues)
    assert classify_tags(("event:roleplay",), roleplay_enabled=True)[0].category == "roleplay"


def test_empty_input_has_no_cues():
    assert classify_text("") == ()
    assert classify_text("   ") == ()
    assert classify_text(None) == ()


def test_category_list_is_stable_and_complete():
    assert CATEGORIES == ("chase", "crash", "stunt", "combat", "npc_chaos", "funny_dialogue", "roleplay", "reaction", "milestone", "viewer_nominated")


@pytest.mark.parametrize("text", ["Mission passed!", "We completed the heist.", "Final wave cleared!",
                                  "We survived the last wave!", "All six waves survived."])
def test_current_mission_progress_is_a_distinct_game_event(text):
    assert categories(text) == {"milestone"}


@pytest.mark.parametrize("text", ["If we completed the heist we would leave.", "Tomorrow: mission complete!",
                                  "Yesterday we completed the heist.", "We never completed the heist.",
                                  "How to get mission passed.", "If my math is correct, three waves down.",
                                  "Three waves down.", "Two waves down, if my math is correct.",
                                  "Three waves down, only a bazillion mods to go.",
                                  "We could survive the final wave tomorrow.",
                                  "Yesterday we survived the final wave."])
def test_progress_mentions_without_a_current_assertion_are_not_events(text):
    assert not categories(text)
