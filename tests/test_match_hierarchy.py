from hpat import (
    DataSequence,
    Extractor,
    DictHierarchyProvider,
    PatternNode,
    Pattern,
)


def test_dict_hierarchy_provider():
    seq = DataSequence.from_string("1+1")

    hierarchy = DictHierarchyProvider({
        "Plus": ["Sign"],
    })

    extractor = Extractor([
        Pattern("Digit", [PatternNode("Character", "1")]),
        Pattern("Plus", [PatternNode("Character", "+")]),
        Pattern("MathOp", [
            PatternNode("Digit"),
            PatternNode("Sign"),
            PatternNode("Digit"),
        ]),
    ], hierarchy=hierarchy)

    extractor.apply(seq)

    assert seq.to_list() == [
        [('MathOp', '1+1'), ('Character', '1'), ('Digit', '1')],
        [('MathOp', '1+1'), ('Character', '+'), ('Plus', '+')],
        [('MathOp', '1+1'), ('Character', '1'), ('Digit', '1')],
    ]
