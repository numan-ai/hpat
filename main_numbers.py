import random
import string

from hpat import (
    DataSequence,
    Extractor,
    Pattern,
    PatternNode,
    DictHierarchyProvider,
)


def get_extractor():
    word_extractor = Extractor([
        Pattern("Letter", [PatternNode("Character", list(string.ascii_letters))]),
        Pattern("Digits", [PatternNode("Character", list(string.digits))]),
        Pattern("Space", [PatternNode("Character", " ")]),
        Pattern("WordSeparator",
                [PatternNode("Character", list(string.ascii_letters), negate_value=True)]),
        Pattern("Word",
                pre=[PatternNode("WordSeparator"), ],
                nodes=[PatternNode("Letter", many=True), ],
                post=[PatternNode("WordSeparator"), ]),
        Pattern("Number", [
            PatternNode("Digit", many=True),
        ]),
        Pattern("Digit", [
            PatternNode("Word", "zero"),
        ]),
        Pattern("Digit", [
            PatternNode("Word", "one"),
        ]),
        Pattern("Digit", [
            PatternNode("Word", "two"),
        ]),
        Pattern("Digit", [
            PatternNode("Word", "three"),
        ]),
        Pattern("Digit", [
            PatternNode("Word", "four"),
        ]),
        Pattern("Digit", [
            PatternNode("Word", "five"),
        ]),
        Pattern("Digit", [
            PatternNode("Word", "six"),
        ]),
        Pattern("Digit", [
            PatternNode("Word", "seven"),
        ]),
        Pattern("Digit", [
            PatternNode("Word", "eight"),
        ]),
        Pattern("Digit", [
            PatternNode("Word", "nine"),
        ]),

        Pattern("Verb", [
            PatternNode("Word", "run"),
        ]),
        Pattern("Noun", [
            PatternNode("Word", "run"),
        ]),
        Pattern("ToVerb", [
            PatternNode("Word", "to"),
            PatternNode("WordSeparator"),
            PatternNode("Verb", id="724"),
        ]),
    ], DictHierarchyProvider({

    }))
    return word_extractor


def main():
    extractor = get_extractor()

    seq = DataSequence.from_string(" to run ")
    """nine"""

    extractor.apply(seq)
    print(seq.extract("724"))

    seq.display()


if __name__ == '__main__':
    """
    
    negate("one") -> -1
    """
    main()
