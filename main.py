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
        Pattern("Coma", [
            PatternNode("Character", value=",")]),
        Pattern("Dot", [
            PatternNode("Character", value=".")]),
        Pattern("Letter", [PatternNode("Character", list(string.ascii_letters))]),
        Pattern("SentenceEnd", [PatternNode("Character", ["!", "?", ".", ";"])]),
        Pattern("WordSeparator",
                [PatternNode("Character", list(string.ascii_letters), negate_value=True)]),
        Pattern("Word",
                pre=[PatternNode("WordSeparator"), ],
                nodes=[PatternNode("Letter", many=True), ],
                post=[PatternNode("WordSeparator"), ]),
        Pattern("NounIsAdjective",
                nodes=[
                    PatternNode("Subject"),
                    PatternNode("Space"),
                    PatternNode("Word", "is"),
                    PatternNode("Space"),
                    PatternNode("Adjective"),
                ]),
        # this assumes that first noun is active and second is passive,
        # the assumption can be removed by introducing concepts of forward and revers directionality
        # for the verbs - some verbs have active participant in front of them and
        # passive after them, while some have it reversed, we need to store it in database
        # just as parts of speech.
        Pattern("PassiveActivity",
                nodes=[
                    PatternNode("Subject", assume="ActiveParticipant"),
                    PatternNode("Space"),
                    PatternNode("PassiveVerb"),
                    PatternNode("Space"),
                    PatternNode("Subject", assume="PassiveParticipant"),
                ]),
        # Pattern("Activity",
        #         nodes=[
        #             PatternNode("Subject"),
        #             PatternNode("Space"),
        #             PatternNode("Verb"),
        #             PatternNode("Space"),
        #             PatternNode("Subject"),
        #         ]),
        # Pattern("Activity",
        #         nodes=[
        #             PatternNode("Subject"),
        #             PatternNode("Space"),
        #             PatternNode("Verb"),
        #         ]),
        Pattern("Activity",
                nodes=[
                    PatternNode("Subject"),
                    PatternNode("Space"),
                    PatternNode("Verb"),
                    PatternNode("Space"),
                    PatternNode("Subject"),
                    PatternNode("Space"),
                    PatternNode("Subject"),
                ]),
        Pattern("ComplexActivity",
                nodes=[
                    PatternNode("Activity"),
                    PatternNode("Space"),
                    PatternNode("Preposition"),
                    PatternNode("Space"),
                    PatternNode("Subject"),
                ]),
        Pattern("Determinant",
                nodes=[
                    PatternNode("Word", ['the', 'a']),
                ]),
        Pattern("Adjective",
                nodes=[
                    PatternNode("Word", ['older', 'younger', 'sympathetic', 'cold',]),
                ]),

        Pattern("Name",
                nodes=[
                    PatternNode("Word", ['Tommy', 'Timmy',]),
                ]),

        # Nouns
        Pattern("Noun",
                nodes=[
                    PatternNode("Word", ['ice', 'cream', 'father', 'look', 'cold']),
                ]),
        Pattern("PluralNoun",
                nodes=[
                    PatternNode("Word", ['students',]),
                ]),
        Pattern("CompoundNoun",
                nodes=[
                    PatternNode("Determinant"),
                    PatternNode('Space'),
                    PatternNode('Adjective', many=True),
                    PatternNode('Space'),
                    PatternNode(["Noun", "Pronoun"]),
                ]),
        Pattern("CompoundNoun",
                nodes=[
                    PatternNode('Determinant'),
                    PatternNode('Space'),
                    PatternNode(["Noun",]),
                ]),
        Pattern("CompoundNoun",
                nodes=[
                    PatternNode('Adjective', many=True),
                    PatternNode('Space'),
                    PatternNode(["Noun", "Pronoun"]),
                ]),
        Pattern("CompoundNoun",
                nodes=[
                    PatternNode("PossessivePronoun"),
                    PatternNode('Space'),
                    PatternNode(["Noun", "CompoundNoun"]),
                ]),
        Pattern("CompoundNoun",
                nodes=[
                    PatternNode(["Noun", "CompoundNoun"]),
                    PatternNode('Space'),
                    PatternNode(["Noun", "CompoundNoun"]),
                ]),

        # End Nouns

        # Pronouns
        Pattern("Pronoun", nodes=[
            PatternNode("Word", ['ones',]),]),
        Pattern("SubjectivePronoun", nodes=[
            PatternNode("Word", ['I', 'we', 'you', 'he', 'she', 'it', 'they'])]),
        Pattern("ObjectivePronoun", nodes=[
            PatternNode("Word", ['me', 'us', 'you', 'him', 'her', 'it', 'them'])]),
        Pattern("PossessiveAdjective", nodes=[
            PatternNode("Word", ['my', 'our', 'your', 'his', 'her', 'its', 'their'])]),
        Pattern("PossessivePronoun", nodes=[
            PatternNode("Word", ['mine', 'ours', 'yours', 'his', 'hers', 'its', 'theirs'])]),
        Pattern("ReflexivePronoun", nodes=[
            PatternNode("Word", ['myself', 'ourselves', 'yourself', 'yourselves', 'himself',
                                 'herself', 'itself', 'themselves'])]),
        # End Pronouns


        Pattern("UsedByChildren",
                nodes=[
                    PatternNode("Word", 'bunk'),
                    PatternNode("Space"),
                    PatternNode("Word", 'bed'),
                ]),

        # Verbs
        Pattern("Verb", nodes=[
            PatternNode("Word", [
                'bullying', 'were', 'look', 'was', 'is',
            ]),
        ]),
        Pattern("PastVerb", nodes=[
            PatternNode("Word", [
                'rescued', 'dropped', 'giggled', 'gave',
            ]),
        ]),
        Pattern("CompoundVerb",
                nodes=[
                    PatternNode("Word", ['were', 'was', 'is', 'has']),
                    PatternNode('Space'),
                    PatternNode("Verb"),
                ]),
        Pattern("ModalVerb", nodes=[
            PatternNode("Word", ['can', 'may', 'must', 'shall', 'will', 'could',
                                 'might', 'must', 'should', 'would'])]),
        Pattern("PassiveVerb",
                nodes=[
                    PatternNode("Letter", many=True),
                    PatternNode("Letter", 'e'),
                    PatternNode("Letter", 'd'),
                ], inside='Verb'),
        Pattern("PassiveVerb",
                nodes=[
                    PatternNode("Verb", ['was', 'were', 'is', 'will']),
                    PatternNode("Space"),
                    PatternNode("Letter", many=True),
                    PatternNode("Letter", 'i'),
                    PatternNode("Letter", 'n'),
                    PatternNode("Letter", 'g'),
                ], inside='CompoundVerb'),
        Pattern("PassiveVerb",
                nodes=[
                    PatternNode("Verb", ['was', 'were', 'is', 'will']),
                    PatternNode("Space"),
                    PatternNode('PassiveVerb')
                ]),
        # End Verbs

        # TODO: replace this with a better expansion of MorallyUnacceptableActivity of Verb
        Pattern("MorallyUnacceptableVerb",
                nodes=[
                    PatternNode("Verb", 'were'),
                    PatternNode("Space"),
                    PatternNode("Verb", ['bullying']),
                ]),
        Pattern("Verb",
                nodes=[
                    PatternNode("Word", ['run', 'lifted']),
                ]),
        Pattern("Noun",
                nodes=[
                    PatternNode("Word", ['run', 'bed', 'boy', ]),
                ]),
        Pattern("Noun",
                pre=[
                    PatternNode("Determinant"),
                    PatternNode("Space"),
                ],
                nodes=[
                    PatternNode("Word"),
                ]),
        Pattern("Adjective",
                nodes=[
                    PatternNode("Word", ['fun', 'bunk']),
                ]),

        Pattern("PrepositionOfDirection",
                nodes=[
                    PatternNode("Word", ['onto', ]),
                ]),
        Pattern("PrepositionOfDirection",
                nodes=[
                    PatternNode("Word", ['onto', ]),
                ]),
    ], DictHierarchyProvider({
        'PrepositionOfDirection': ['Preposition', ],
        'PrepositionOfTime': ['Preposition', ],
        'PrepositionOfPlace': ['Preposition', ],
        'Plus': ['Sign', ],
        'Minus': ['Sign', ],
        'Verb': ['StructuralVerb', ],
        'PastVerb': ['Verb', ],
        'CompoundVerb': ['StructuralVerb', ],
        'PassiveVerb': ['StructuralVerb', ],
        'PluralNoun': ['Noun', ],
        'CompoundNoun': ['Subject', ],
        'Noun': ['Subject', ],
        'ProperNoun': ['Noun', ],

        'SubjectivePronoun': ['Pronoun', 'Subject', ],
        'ObjectivePronoun': ['Pronoun', 'Subject', ],
        'PossessiveAdjective': ['Pronoun', 'Adjective'],
        'PossessivePronoun': ['Pronoun', ],
        'ReflexivePronoun': ['Pronoun', 'Subject', ],

        # 'GroupNoun': ['Noun', ],
        # 'SingularNoun': ['Noun', 'Subject', ],

        'ActionVerb': ['Verb', ],
        'AuxiliaryVerb': ['Verb', ],
        'TransitiveVerb': ['Verb', ],
        'IntransitiveVerb': ['Verb', ],
        'ModalVerb': ['Verb', ],
        'PhrasalVerb': ['Verb', ],
        'IrregularVerb': ['Verb', ],
        'RegularVerb': ['Verb', ],
        'FiniteVerb': ['Verb', ],
        'InfiniteVerb': ['Verb', ],

        'PassiveActivity': ['Activity', ],

        'Name': ['ProperNoun', ],
    }))

    seq = DataSequence.from_string(
        " the man lifted the boy onto his bunk bed ")

    # seq = DataSequence.from_string(
    #     " the man lifted the boy onto his shoulders ")

    data = [
        ("ComplexActivity", "the man lifted the boy onto his bunk bed"),
        ("Ownership", "bunk bed", "his"),
        ("Ownership", "bunk bed", "boy"),
        ("UsedBy", "bunk bed", "Children"),
    ]

    extractor.apply(seq)
    seq.display(hide={'Letter', 'Character', 'WordSeparator'})

    """
    people do not assume every possible concept and then filter wrong ones out.
    we make a single assumption and in case we get more information we update it.
    how do we make the initial guess and are there situations were we can't make it?
    updates of the guess are made in the same way as initial guesses, just with more info.
    is it possible that our initial guesses are made using statistics?
    
    sequential associations??
    """
    """
    directed graph
    every vertex is of form: (x, y, z, Concept, list of features)
    every edge has one of two types: item or part
    features are inherited by "part" edges
    edge types have defaults based on the concepts
    """


if __name__ == '__main__':
    main()
