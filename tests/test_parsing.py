from hpat import DataSequence, Extractor, Pattern, PatternNode


def test_parsing_simple():
    seq = DataSequence.from_string("1 + 2")
    extractor = Extractor([
        Pattern("Digit", [PatternNode("Character", list("0123456789"))]),
        Pattern("Sign", [PatternNode("Character", ["+", "-"])]),
        Pattern("Space", [PatternNode("Character", " ")]),
        Pattern("MathExpr", [
            PatternNode("Digit", id='left'),
            PatternNode("Space"),
            PatternNode("Sign", id='op'),
            PatternNode("Space"),
            PatternNode("Digit", id='right'),
        ]),
    ])

    extractor.apply(seq)
    match = seq.elements[0].matches[-1]

    assert match.structure == {
        "concept": "MathExpr",
        "data": {
            "left": "1",
            "op": "+",
            "right": "2",
        },
    }


def test_parsing_many():
    seq = DataSequence.from_string("1 + 23")
    extractor = Extractor([
        Pattern("Digit", [PatternNode("Character", list("0123456789"))]),
        Pattern("Sign", [PatternNode("Character", ["+", "-"])]),
        Pattern("Space", [PatternNode("Character", " ")]),
        Pattern("MathExpr", [
            PatternNode("Digit", id='left'),
            PatternNode("Space"),
            PatternNode("Sign", id='op'),
            PatternNode("Space"),
            PatternNode("Digit", id='right', many=True),
        ]),
    ])

    extractor.apply(seq)
    match = seq.elements[0].matches[-1]

    assert match.structure == {
        "concept": "MathExpr",
        "data": {
            "left": "1",
            "op": "+",
            "right": ["2", "3"],
        },
    }


def test_parsing_nested():
    seq = DataSequence.from_string("1 + 23")
    extractor = Extractor([
        Pattern("Digit", [PatternNode("Character", list("0123456789"))]),
        Pattern("Sign", [PatternNode("Character", ["+", "-"])]),
        Pattern("Space", [PatternNode("Character", " ")]),
        Pattern("Number", [PatternNode("Digit", id='digits', many=True)]),
        Pattern("MathExpr", [
            PatternNode("Number", id='left'),
            PatternNode("Space"),
            PatternNode("Sign", id='op'),
            PatternNode("Space"),
            PatternNode("Number", id='right'),
        ]),
    ])

    extractor.apply(seq)
    match = seq.elements[0].matches[-1]

    assert match.structure == {
        "concept": "MathExpr",
        "data": {
            "left": {
                "concept": "Number",
                "data": {
                    "digits": ["1", ],
                },
            },
            "op": "+",
            "right": {
                "concept": "Number",
                "data": {
                    "digits": ["2", "3", ],
                },
            }
        },
    }


def test_parsing_many_nested():
    seq = DataSequence.from_string("1 + 23")
    extractor = Extractor([
        Pattern("Digit", [PatternNode("Character", list("0123456789"), id='digit')]),
        Pattern("Sign", [PatternNode("Character", ["+", "-"])]),
        Pattern("Space", [PatternNode("Character", " ")]),
        Pattern("MathExpr", [
            PatternNode("Digit", id='left', many=True),
            PatternNode("Space"),
            PatternNode("Sign", id='op'),
            PatternNode("Space"),
            PatternNode("Digit", id='right', many=True),
        ]),
    ])

    extractor.apply(seq)
    match = seq.elements[0].matches[-1]

    assert match.structure == {
        "concept": "MathExpr",
        "data": {
            "left": [{
                "concept": "Digit",
                "data": {
                    "digit": "1",
                },
            }, ],
            "op": "+",
            "right": [{
                "concept": "Digit",
                "data": {
                    "digit": "2",
                },
            }, {
                "concept": "Digit",
                "data": {
                    "digit": "3",
                },
            }, ],
        },
    }
