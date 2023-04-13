from hpat import DataSequence, Extractor, Pattern, PatternNode


def test_disabled_one_element():
    seq = DataSequence.from_string("1 + 2")
    extractor = Extractor([
        Pattern("Digit", [PatternNode("Character", ["1", "2"])]),
        Pattern("Space", [PatternNode("Character", " ")]),
        Pattern("Sign", [PatternNode("Character", ["+", "-"])]),
    ])

    extractor.apply(seq)
    seq.disable_elements(["Space"])
    extractor = Extractor([
        Pattern("MathExpr", [
            PatternNode("Digit"),
            PatternNode("Sign"),
            PatternNode("Digit"),
        ]),
    ])
    extractor.apply(seq)

    assert seq.to_list() == [
        [('MathExpr', '1 + 2'), ('Character', '1'), ('Digit', '1'), ],
        [('MathExpr', '1 + 2'), ('Character', ' '), ('Space', ' '), ],
        [('MathExpr', '1 + 2'), ('Character', '+'), ('Sign', '+'), ],
        [('MathExpr', '1 + 2'), ('Character', ' '), ('Space', ' '), ],
        [('MathExpr', '1 + 2'), ('Character', '2'), ('Digit', '2'), ],
    ]


def test_disabled_one_element_pre():
    seq = DataSequence.from_string("1 + 2")
    extractor = Extractor([
        Pattern("Digit", [PatternNode("Character", ["1", "2"])]),
        Pattern("Space", [PatternNode("Character", " ")]),
        Pattern("Sign", [PatternNode("Character", ["+", "-"])]),
    ])

    extractor.apply(seq)
    seq.disable_elements(["Space"])

    extractor = Extractor([
        Pattern("MathExpr", pre=[
            PatternNode("Digit"),
        ], nodes=[
            PatternNode("Sign"),
            PatternNode("Digit"),
        ]),
    ])
    extractor.apply(seq)

    assert seq.to_list() == [
        [('Character', '1'), ('Digit', '1'), ],
        [('Character', ' '), ('Space', ' '), ],
        [('MathExpr', '+ 2'), ('Character', '+'), ('Sign', '+'), ],
        [('MathExpr', '+ 2'), ('Character', ' '), ('Space', ' '), ],
        [('MathExpr', '+ 2'), ('Character', '2'), ('Digit', '2'), ],
    ]
