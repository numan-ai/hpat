import pytest

from hpat import (
    DataSequence,
    Extractor,
    Pattern,
    PatternNode,
    DictHierarchyProvider,
)


@pytest.mark.skip()
def test_single_concept():
    seq = DataSequence.from_string(" run is ")
    extractor = Extractor([
        Pattern("Letter", [PatternNode("Character", ["r", "u", "n", "i", "s"])]),
        Pattern("Word",
                pre=[PatternNode("Character", " "), ],
                nodes=[PatternNode("Letter", many=True), ],
                post=[PatternNode("Character", " "), ]),
        Pattern("Noun", [PatternNode("Word", "run")]),
        Pattern("Verb", [PatternNode("Word", "run")]),
        Pattern("NounIs", [
            PatternNode("Noun"),
            PatternNode("Word", "is"),
        ]),
    ], DictHierarchyProvider(parents={
        "Verb": ["PartOfSpeech"],
        "Noun": ["PartOfSpeech"],
    }), single_concepts=[
        'PartOfSpeech',
    ])

    extractor.apply(seq)

    assert seq.to_list() == [
        [('Character', ' '), ],
        [('NounIs', 'run is'), ('Noun', 'run'), ('Word', 'run'), ('Verb', 'run'), ('Letter', 'r'), ('Character', 'r')],
        [('NounIs', 'run is'), ('Noun', 'run'), ('Word', 'run'), ('Verb', 'run'), ('Letter', 'u'), ('Character', 'u')],
        [('NounIs', 'run is'), ('Noun', 'run'), ('Word', 'run'), ('Verb', 'run'), ('Letter', 'n'), ('Character', 'n')],
        [('NounIs', 'run is'), ('Character', ' ')],
        [('NounIs', 'run is'), ('Word', 'run'), ('Character', 'i')],
        [('NounIs', 'run is'), ('Word', 'run'), ('Character', 's')],
        [('Character', ' '), ],
    ]
