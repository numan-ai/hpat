from hpat import (
    DataSequence,
    Extractor,
    Pattern,
    PatternNode,
)


def test_at_start():
    seq = DataSequence.from_string("++")
    extractor = Extractor([
        Pattern("Plus", [
            PatternNode("Character", "+", at_start=True),
        ]),
    ])

    extractor.apply(seq)

    assert seq.to_list() == [
        [('Character', '+'), ('Plus', '+'), ],
        [('Character', '+'), ],
    ]


def test_at_end():
    seq = DataSequence.from_string("++")
    extractor = Extractor([
        Pattern("Plus", [
            PatternNode("Character", "+", at_end=True),
        ]),
    ])

    extractor.apply(seq)

    assert seq.to_list() == [
        [('Character', '+'), ],
        [('Character', '+'), ('Plus', '+'), ],
    ]
