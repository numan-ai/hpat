from hpat import (
    Pattern,
    PatternNode,
)


def test_pattern_get_node():
    pattern = Pattern("MathExp", [
        PatternNode("Number"),
        PatternNode("Sign"),
        PatternNode("Number"),
    ])
    assert pattern.get_node(0)[0].concept == "Number"
    assert pattern.get_node(1)[0].concept == "Sign"
    assert pattern.get_node(2)[0].concept == "Number"
