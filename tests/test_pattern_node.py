from hpat import (
    PatternNode,
    Match,
)

def test_pattern_node_matches():
    node = PatternNode("Number")
    match = Match("Number", "1", 1, 0)
    assert node.is_matching(match, None) is True

    node = PatternNode("Number", "1")
    match = Match("Number", "1", 1, 0)
    assert node.is_matching(match, None) is True


def test_pattern_node_matches_no_match_value():
    node = PatternNode("Number", "2")
    match = Match("Number", "1", 1, 0)
    assert node.is_matching(match, None) is False


def test_pattern_node_matches_no_match_value_optional():
    node = PatternNode("Number", "2", optional=True)
    match = Match("Number", "1", 1, 0)
    assert node.is_matching(match, None) is False


def test_pattern_node_multiple_concepts():
    node = PatternNode(["Digit", "Letter"])

    match = Match("Digit", "1", 1, 0)
    assert node.is_matching(match, None) is True

    match = Match("Letter", "1", 1, 0)
    assert node.is_matching(match, None) is True

    match = Match("Other", "1", 1, 0)
    assert node.is_matching(match, None) is False


def test_pattern_node_multiple_concepts_with_value():
    node = PatternNode(["Digit", "Letter"], "1")

    match = Match("Letter", "1", 1, 0)
    assert node.is_matching(match, None) is True

    match = Match("Letter", "2", 1, 0)
    assert node.is_matching(match, None) is False


def test_pattern_node_multiple_value():
    node = PatternNode("Character", ["1", "2", "3", "4", "5"])

    match = Match("Character", "1", 1, 0)
    assert node.is_matching(match, None) is True

    match = Match("Character", "2", 1, 0)
    assert node.is_matching(match, None) is True

    match = Match("Character", "6", 1, 0)
    assert node.is_matching(match, None) is False
