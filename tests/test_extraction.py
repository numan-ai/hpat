from hpat import (
    DataSequence,
    Extractor,
    Pattern,
    PatternNode,
)


def test_extraction_simple():
    seq = DataSequence.from_string(" 132 ")
    extractor = Extractor([
        Pattern("Digit", [PatternNode("Character", "1")]),
        Pattern("Digit", [PatternNode("Character", "2")]),
        Pattern("Digit", [PatternNode("Character", "3")]),
        Pattern("Number", [
            PatternNode("Character", " "),
            PatternNode("Digit", many=True),
            PatternNode("Character", " "),
        ], id='pat1'),
    ])

    extractor.apply(seq)

    assert seq.to_list() == [
        [('Number', ' 132 '), ('Character', ' '), ],
        [('Number', ' 132 '), ('Character', '1'), ('Digit', '1')],
        [('Number', ' 132 '), ('Character', '3'), ('Digit', '3')],
        [('Number', ' 132 '), ('Character', '2'), ('Digit', '2')],
        [('Number', ' 132 '), ('Character', ' '), ],
    ]

    assert seq.extract('pat1') == [' 132 ']


def test_extraction_():
    seq = DataSequence.from_string("132")
    extractor = Extractor([
        Pattern("Digit", [PatternNode("Character", "1")]),
        Pattern("Digit", [PatternNode("Character", "2")]),
        Pattern("Digit", [PatternNode("Character", "3")]),
        Pattern("Number", [
            PatternNode("Digit", many=True, id="node1"),
        ], id='pat1'),
    ])

    extractor.apply(seq)

    assert seq.to_list() == [
        [('Number', '132'), ('Number', '13'), ('Character', '1'), ('Number', '1'), ('Digit', '1')],
        [('Number', '132'), ('Number', '13'), ('Number', '32'), ('Character', '3'), ('Number', '3'), ('Digit', '3')],
        [('Number', '132'), ('Number', '32'), ('Character', '2'), ('Number', '2'), ('Digit', '2')],
    ]

    assert seq.extract('pat1') == ['1', '13', '132', '3', '32', '2']
