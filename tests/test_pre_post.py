from hpat import (
    DataSequence,
    Extractor,
    Pattern,
    PatternNode,
)


def test_pre_post():
    seq = DataSequence.from_string(" +++ ")
    extractor = Extractor([
        Pattern("TestPattern", [
            PatternNode("Character", "+", many=True),
        ], pre=[
            PatternNode("Character", " "),
        ], post=[
            PatternNode("Character", " "),
        ], id='pat1'),
    ])

    extractor.apply(seq)

    assert seq.to_list() == [
        [('Character', ' '), ],
        [('TestPattern', '+++'), ('Character', '+'), ],
        [('TestPattern', '+++'), ('Character', '+'), ],
        [('TestPattern', '+++'), ('Character', '+'), ],
        [('Character', ' '), ],
    ]

    assert seq.extract('pat1') == ['+++', ]


def test_no_pre():
    seq = DataSequence.from_string("+++ ")
    extractor = Extractor([
        Pattern("TestPattern", [
            PatternNode("Character", "+", many=True),
        ], pre=[
            PatternNode("Character", " "),
        ], post=[
            PatternNode("Character", " "),
        ], id='pat1'),
    ])

    extractor.apply(seq)

    assert seq.to_list() == [
        [('Character', '+'), ],
        [('Character', '+'), ],
        [('Character', '+'), ],
        [('Character', ' '), ],
    ]

    assert seq.extract('pat1') == []


def test_no_post():
    seq = DataSequence.from_string(" +++")
    extractor = Extractor([
        Pattern("TestPattern", [
            PatternNode("Character", "+", many=True),
        ], pre=[
            PatternNode("Character", " "),
        ], post=[
            PatternNode("Character", " "),
        ], id='pat1'),
    ])

    extractor.apply(seq)

    assert seq.to_list() == [
        [('Character', ' '), ],
        [('Character', '+'), ],
        [('Character', '+'), ],
        [('Character', '+'), ],
    ]

    assert seq.extract('pat1') == []
