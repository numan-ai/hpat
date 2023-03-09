import string

from hpat import (
    Extractor,
    Pattern,
    PatternNode,
    DictHierarchyProvider, DataSequence,
)


def main():
    extractor = Extractor([
        Pattern("Digit", [
            PatternNode("Character", value=list(string.digits))]),
        Pattern("Number",
                pre=[PatternNode("Space"), ],
                nodes=[PatternNode("Digit", many=True), ],
                post=[PatternNode("Space"), ]),
        Pattern("Space", [
            PatternNode("Character", value=" ")]),
        Pattern("Plus", [
            PatternNode("Character", value="+")]),
        Pattern("Minus", [
            PatternNode("Character", value="-")]),
        Pattern("SimpleMathExpression", [
            PatternNode("Number"),
            PatternNode("Space", optional=True),
            PatternNode("Sign"),
            PatternNode("Space", optional=True),
            PatternNode("Number"),
        ]),
        Pattern("Letter", [PatternNode("Character", list(string.ascii_letters))]),
        Pattern("SentenceEnd", [PatternNode("Character", ["!", "?", "."])]),
        Pattern("WordSeparator",
                [PatternNode("Character", list(string.ascii_letters), negate_value=True)]),
        Pattern("Word",
                pre=[PatternNode("WordSeparator"), ],
                nodes=[PatternNode("Letter", many=True), ],
                post=[PatternNode("WordSeparator"), ]),
        Pattern("Verb",
                nodes=[PatternNode("Word", 'run'), ]),
        Pattern("Noun",
                nodes=[PatternNode("Word", 'run'), ]),
    ], DictHierarchyProvider({
        'Plus': ['Sign',],
        'Minus': ['Sign',],
    }))

    seq = DataSequence.from_string(" 732 + 94 ")
    extractor.apply(seq)
    seq.display()


if __name__ == '__main__':
    main()
