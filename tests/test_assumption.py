from hpat import DataSequence, Extractor, Pattern, PatternNode


def test_assumption_no_conflict():
    seq = DataSequence.from_string("+1+")
    extractor = Extractor([
        Pattern("Digit", [PatternNode("Character", "1")]),
        Pattern("TestPattern", [
            PatternNode("Character", "+"),
            PatternNode("Digit", assume="OddDigit"),
            PatternNode("Character", "+"),
        ]),
    ])

    extractor.apply(seq)

    assert seq.to_list() == [
        [('TestPattern', '+1+'), ('Character', '+'), ],
        [('TestPattern', '+1+'), ('Character', '1'), ('OddDigit', '1'), ('Digit', '1'), ],
        [('TestPattern', '+1+'), ('Character', '+'), ],
    ]
