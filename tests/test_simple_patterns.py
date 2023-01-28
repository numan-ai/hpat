from hpat import (
    DataSequence,
    Extractor,
    Pattern,
    PatternNode,
)


def test_match_single_node_patterns():
    seq = DataSequence.from_string("1+1")
    extractor = Extractor([
        Pattern("Digit", [PatternNode("Character", "1")]),
        Pattern("Plus", [PatternNode("Character", "+")]),
    ])

    extractor.apply(seq)

    assert seq.to_list() == [
        [('Character', '1'), ('Digit', '1')],
        [('Character', '+'), ('Plus', '+')],
        [('Character', '1'), ('Digit', '1')],
    ]


def test_two_node_patterns():
    seq = DataSequence.from_string(" 11")
    extractor = Extractor([
        Pattern("Digit", [PatternNode("Character", "1")]),
        Pattern("DoubleDigit", [PatternNode("Digit"), PatternNode("Digit")]),
    ])

    extractor.apply(seq)

    assert seq.to_list() == [
        [('Character', ' ')],
        [('DoubleDigit', '11'), ('Character', '1'), ('Digit', '1')],
        [('DoubleDigit', '11'), ('Character', '1'), ('Digit', '1')],
    ]


def test_pattern_node_many():
    seq = DataSequence.from_string("111")
    extractor = Extractor([
        Pattern("Digit", [PatternNode("Character", "1")]),
        Pattern("ManyDigits", [PatternNode("Digit", many=True)]),
    ])

    extractor.apply(seq)

    assert seq.to_list() == [
        [('ManyDigits', '111'), ('ManyDigits', '11'), ('ManyDigits', '1'), ('Character', '1'), ('Digit', '1')],
        [('ManyDigits', '111'), ('ManyDigits', '11'), ('ManyDigits', '11'), ('ManyDigits', '1'), ('Character', '1'), ('Digit', '1')],
        [('ManyDigits', '111'), ('ManyDigits', '11'), ('ManyDigits', '1'), ('Character', '1'), ('Digit', '1')],
    ]


def test_pattern_node_optional_skipped():
    seq = DataSequence.from_string("11")
    extractor = Extractor([
        Pattern("Digit", [PatternNode("Character", "1")]),
        Pattern("Space", [PatternNode("Character", " ")]),
        Pattern("SomethingElse", [
            PatternNode("Digit"), PatternNode("Space", optional=True), PatternNode("Digit")
        ]),
    ])

    extractor.apply(seq)

    assert seq.to_list() == [
        [('SomethingElse', '11'), ('Character', '1'), ('Digit', '1')],
        [('SomethingElse', '11'), ('Character', '1'), ('Digit', '1')],
    ]


def test_pattern_node_optional_found():
    seq = DataSequence.from_string("1 1")
    extractor = Extractor([
        Pattern("Digit", [PatternNode("Character", "1")]),
        Pattern("Space", [PatternNode("Character", " ")]),
        Pattern("SomethingElse", [
            PatternNode("Digit"), PatternNode("Space", optional=True), PatternNode("Digit")
        ]),
    ])

    extractor.apply(seq)

    assert seq.to_list() == [
        [('SomethingElse', '1 1'), ('Character', '1'), ('Digit', '1')],
        [('SomethingElse', '1 1'), ('Character', ' '), ('Space', ' ')],
        [('SomethingElse', '1 1'), ('Character', '1'), ('Digit', '1')],
    ]


def test_pattern_node_optional_many_found():
    seq = DataSequence.from_string("1  1")
    extractor = Extractor([
        Pattern("Digit", [PatternNode("Character", "1")]),
        Pattern("Space", [PatternNode("Character", " ")]),
        Pattern("SomethingElse", [
            PatternNode("Digit"),
            PatternNode("Space", optional=True, many=True),
            PatternNode("Digit")
        ]),
    ])

    extractor.apply(seq)

    assert seq.to_list() == [
        [('SomethingElse', '1  1'), ('Character', '1'), ('Digit', '1')],
        [('SomethingElse', '1  1'), ('Character', ' '), ('Space', ' ')],
        [('SomethingElse', '1  1'), ('Character', ' '), ('Space', ' ')],
        [('SomethingElse', '1  1'), ('Character', '1'), ('Digit', '1')],
    ]


def test_pattern_node_optional_many_skipped():
    seq = DataSequence.from_string("11")
    extractor = Extractor([
        Pattern("Digit", [PatternNode("Character", "1")]),
        Pattern("Space", [PatternNode("Character", " ")]),
        Pattern("SomethingElse", [
            PatternNode("Digit"),
            PatternNode("Space", optional=True, many=True),
            PatternNode("Digit")
        ]),
    ])

    extractor.apply(seq)

    assert seq.to_list() == [
        [('SomethingElse', '11'), ('Character', '1'), ('Digit', '1')],
        [('SomethingElse', '11'), ('Character', '1'), ('Digit', '1')],
    ]


def test_big_pattern_in_big_pattern():
    seq = DataSequence.from_string(" word ")
    extractor = Extractor([
        Pattern("Letter", [PatternNode("Character", "w")]),
        Pattern("Letter", [PatternNode("Character", "o")]),
        Pattern("Letter", [PatternNode("Character", "r")]),
        Pattern("Letter", [PatternNode("Character", "d")]),
        Pattern("Word",
                pre=[PatternNode("Character", " "), ],
                nodes=[PatternNode("Letter", many=True), ],
                post=[PatternNode("Character", " "), ]),
        Pattern("Noun", [PatternNode("Word",)]),
    ])

    extractor.apply(seq)

    assert seq.to_list() == [
        [('Character', ' '), ],
        [('Word', 'word'), ('Noun', 'word'), ('Character', 'w'), ('Letter', 'w')],
        [('Word', 'word'), ('Noun', 'word'), ('Character', 'o'), ('Letter', 'o')],
        [('Word', 'word'), ('Noun', 'word'), ('Character', 'r'), ('Letter', 'r')],
        [('Word', 'word'), ('Noun', 'word'), ('Character', 'd'), ('Letter', 'd')],
        [('Character', ' '), ],
    ]


def test_pattern_two_big_nodes():
    seq = DataSequence.from_string(" one two ")
    extractor = Extractor([
        Pattern("Letter", [PatternNode("Character", ["o", "n", "e", "t", "w", "o"])]),
        Pattern("Word",
                pre=[PatternNode("Character", " "), ],
                nodes=[PatternNode("Letter", many=True), ],
                post=[PatternNode("Character", " "), ]),
        Pattern("Noun", [
            PatternNode("Word",),
            PatternNode("Character", " "),
            PatternNode("Word",),
        ]),
    ])

    extractor.apply(seq)

    assert seq.to_list() == [
        [('Character', ' '), ],
        [('Noun', 'one two'), ('Word', 'one'), ('Character', 'o'), ('Letter', 'o')],
        [('Noun', 'one two'), ('Word', 'one'), ('Character', 'n'), ('Letter', 'n')],
        [('Noun', 'one two'), ('Word', 'one'), ('Character', 'e'), ('Letter', 'e')],
        [('Noun', 'one two'), ('Character', ' '), ],
        [('Noun', 'one two'), ('Word', 'two'), ('Character', 't'), ('Letter', 't')],
        [('Noun', 'one two'), ('Word', 'two'), ('Character', 'w'), ('Letter', 'w')],
        [('Noun', 'one two'), ('Word', 'two'), ('Character', 'o'), ('Letter', 'o')],
        [('Character', ' '), ],
    ]


def test_negative_pattern_concept():
    seq = DataSequence.from_string("a23")
    extractor = Extractor([
        Pattern("Digit", [PatternNode("Character", ["1", "2", "3", ])]),
        Pattern("Test", [
            PatternNode("Digit", negate=True),
            PatternNode("Digit",),
            PatternNode("Digit",),
        ]),
    ])

    extractor.apply(seq)

    assert seq.to_list() == [
        [('Test', 'a23'), ('Character', 'a')],
        [('Test', 'a23'), ('Character', '2'), ('Digit', '2')],
        [('Test', 'a23'), ('Character', '3'), ('Digit', '3')],
    ]


def test_negative_pattern_value():
    seq = DataSequence.from_string("223")
    extractor = Extractor([
        Pattern("Digit", [PatternNode("Character", ["1", "2", "3", ])]),
        Pattern("Test", [
            PatternNode("Digit", "1", negate=True),
            PatternNode("Digit",),
            PatternNode("Digit",),
        ]),
    ])

    extractor.apply(seq)

    assert seq.to_list() == [
        [('Test', '223'), ('Character', '2'), ('Digit', '2')],
        [('Test', '223'), ('Character', '2'), ('Digit', '2')],
        [('Test', '223'), ('Character', '3'), ('Digit', '3')],
    ]


def test_negative_pattern_value_many():
    seq = DataSequence.from_string(" 223 ")
    extractor = Extractor([
        Pattern("Digit", [PatternNode("Character", ["1", "2", "3", ])]),
        Pattern("Test", [
            PatternNode("Character", " "),
            PatternNode("Digit", "1", negate=True, many=True),
            PatternNode("Character", " "),
        ]),
    ])

    extractor.apply(seq)

    assert seq.to_list() == [
        [('Test', ' 223 '), ('Character', ' '), ],
        [('Test', ' 223 '), ('Character', '2'), ('Digit', '2')],
        [('Test', ' 223 '), ('Character', '2'), ('Digit', '2')],
        [('Test', ' 223 '), ('Character', '3'), ('Digit', '3')],
        [('Test', ' 223 '), ('Character', ' '), ],
    ]


def test_negative_pattern_optional():
    seq = DataSequence.from_string("12")
    extractor = Extractor([
        Pattern("Digit", [PatternNode("Character", ["1", "2", "3", ])]),
        Pattern("Test", [
            PatternNode("Digit", "1", negate=True, optional=True),
            PatternNode("Character", "2"),
        ]),
    ])

    extractor.apply(seq)

    assert seq.to_list() == [
        [('Test', '12'), ('Character', '1'), ('Digit', '1')],
        [('Test', '12'), ('Character', '2'), ('Digit', '2'), ('Test', '2')],
    ]


def test_negative_pattern_optional2():
    seq = DataSequence.from_string("22")
    extractor = Extractor([
        Pattern("Digit", [PatternNode("Character", ["1", "2", "3", ])]),
        Pattern("Test", [
            PatternNode("Digit", "1", negate=True, optional=True),
            PatternNode("Character", "2"),
        ]),
    ])

    extractor.apply(seq)

    assert seq.to_list() == [
        [('Test', '22'), ('Character', '2'), ('Digit', '2'), ('Test', '2')],
        [('Test', '22'), ('Character', '2'), ('Digit', '2'), ('Test', '2')],
    ]


def test_negative_pattern_negate_dont_advance():
    seq = DataSequence.from_string("22")
    extractor = Extractor([
        Pattern("Digit", [PatternNode("Character", ["1", "2", "3", ])]),
        Pattern("Test", [
            PatternNode("Digit", "1", negate=True, advance=False),
            PatternNode("Character", "2"),
        ]),
    ])

    extractor.apply(seq)

    assert seq.to_list() == [
        [('Character', '2'), ('Digit', '2'), ('Test', '2')],
        [('Character', '2'), ('Digit', '2'), ('Test', '2')],
    ]


def test_negative_pattern_dont_advance():
    seq = DataSequence.from_string("22")
    extractor = Extractor([
        Pattern("Digit", [PatternNode("Character", ["1", "2", "3", ])]),
        Pattern("Test", [
            PatternNode("Character", advance=False),
            PatternNode("Digit", "2"),
        ]),
    ])

    extractor.apply(seq)

    assert seq.to_list() == [
        [('Character', '2'), ('Digit', '2'), ('Test', '2')],
        [('Character', '2'), ('Digit', '2'), ('Test', '2')],
    ]
