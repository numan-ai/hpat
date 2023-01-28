import random
import string

from hpat import (
    DataSequence,
    Extractor,
    Pattern,
    PatternNode,
    DictHierarchyProvider,
)


SENTENCES = """
The African hunting dog is a wild dog. 
The alpaca belongs to the camel family and resembles the llama.
Anteaters are curious-looking animals.
Antelopes are a group of plant-eating mammals that belong to the same family as sheep, goats, and cattle.
Apes are the animals that are most closely related to humans.
Baboons are large monkeys that move around both on the ground and in trees.
The African penguin is a small bird that lives in southern Africa.
The African fish eagle is a species, or type, of sea eagle.
The blue crane is the national bird of South Africa.
A natural satellite in astronomy is a smaller body which moves around a larger body.
Jupiter is the largest planet in the Solar System.
Jupiter is a gas giant, both because it is so large and made up of gas.
Jupiter can be seen even without using a telescope.
The Solar System is the Sun and all the objects that orbit around it.
The Sun is orbited by planets, asteroids, comets and other things.
A star is a massive ball of plasma (very hot gas) held together by gravity.
The energy of stars comes from nuclear fusion.
The star nearest to Earth is the Sun.
Gamma rays are electromagnetic waves with the smallest wavelengths in the electromagnetic spectrum.
Gamma rays are produced by some types of radioactive atoms.
Both gamma rays and x-rays are photons with very high energies, and gamma have even more energy.
Electromagnetism is the study of the electromagnetic field.
The electromagnetic radiation is thought to be both a particle and a wave.
A photon is an elementary particle.
Photons have energy and momentum.
Proteins are long-chain molecules built from small units known as amino acids.
A polypeptide is a single linear polymer chain of amino acids.
Many proteins are enzymes that catalyze (help to happen) biochemical reactions and are vital to metabolism.
Muscles contain a lot of protein.
A molecule is the smallest amount of a chemical substance that can exist.
Forestry means working to take care of forests.
A forest is a piece of land with many trees.
A tree is a tall plant with a trunk and branches made of wood.
An ecosystem (or ecological system) is a large community of living organisms (plants, animals and microbes) in a particular area.
A desert is an arid (very dry) biome.
Canada is a country in North America, located to the north of the United States.
"""


def read_all():
    # with open('datasets/part_of_speech/nouns.csv') as f:
    #     nouns = [x.lower() for x in f.read().split()]

    with open('datasets/nouns.csv') as f:
        nouns = [x.lower().split(',')[0] for x in f.read().split()]

    with open('datasets/part_of_speech/articles.csv') as f:
        articles = [x.lower().split(',')[0] for x in f.read().split()]

    with open('datasets/part_of_speech/verbs.csv') as f:
        verbs = [x.lower() for x in f.read().split()]

    with open('datasets/part_of_speech/adjectives.csv') as f:
        adjectives = [x.lower() for x in f.read().split()]

    with open('datasets/part_of_speech/coordinative_conjunctions.csv') as f:
        coordinative_conjunctions = [x.lower() for x in f.read().split()]

    with open('datasets/part_of_speech/correlating_conjunctions.csv') as f:
        correlating_conjunctions = [x.lower() for x in f.read().split()]

    with open('datasets/part_of_speech/subordinating_conjunctions.csv') as f:
        subordinating_conjunctions = [x.lower() for x in f.read().split()]

    with open('datasets/part_of_speech/prepositions.csv') as f:
        prepositions = [x.lower() for x in f.read().split()]

    return nouns, articles, verbs, adjectives, \
        coordinative_conjunctions, correlating_conjunctions, subordinating_conjunctions, \
        prepositions


def get_word_extractor():
    word_extractor = Extractor([
        Pattern("Letter", [PatternNode("Character", list(string.ascii_letters))]),
        Pattern("Digits", [PatternNode("Character", list(string.digits))]),
        Pattern("Space", [PatternNode("Character", " ")]),
        Pattern("SentenceEnd", [PatternNode("Character", ["!", "?", "."])]),
        Pattern("Coma", [PatternNode("Character", ",")]),
        Pattern("WordSeparator",
                [PatternNode("Character", list(string.ascii_letters), negate_value=True)]),
        Pattern("Word",
                pre=[PatternNode("WordSeparator"), ],
                nodes=[PatternNode("Letter", many=True), ],
                post=[PatternNode("WordSeparator"), ]),
    ], DictHierarchyProvider({

    }))
    return word_extractor


def main():
    (
        nouns, articles, verbs, adjectives, coordinative_conjunctions, correlating_conjunctions,
        subordinating_conjunctions, prepositions
    ) = read_all()
    word_extractor = get_word_extractor()

    # seq = DataSequence.from_string("""
# Alligators are large lizardlike animals with long, rounded snouts and powerful tails.
# Alligators belong to the group of animals called reptiles.
# Alligators live along the edges of swamps, lakes, and slow-moving rivers.
# """.replace('\n', ' '))

    sent = ' ' + random.choice(SENTENCES.strip().split('\n')).lower() + ' '
    seq = DataSequence.from_string(sent)  # SENTENCES.replace('\n', ' '))

    word_extractor.apply(seq)

    # seq.add_concept()

    for slot in seq.get_slots('Word'):
        word = seq.value[slot[0]: slot[1]]
        if word.lower() in nouns:
            seq.add_concept('Noun', slot[0], slot[1] - slot[0])

        if word.lower() in articles:
            seq.add_concept('Article', slot[0], slot[1] - slot[0])

        if word.lower() in verbs:
            seq.add_concept('Verb', slot[0], slot[1] - slot[0])

        if word.lower() in adjectives:
            seq.add_concept('Adjective', slot[0], slot[1] - slot[0])

        if word.lower() in coordinative_conjunctions:
            seq.add_concept('CoordinativeConjunction', slot[0], slot[1] - slot[0])

        if word.lower() in correlating_conjunctions:
            seq.add_concept('CorrelatingConjunction', slot[0], slot[1] - slot[0])

        if word.lower() in subordinating_conjunctions:
            seq.add_concept('SubordinatingConjunction', slot[0], slot[1] - slot[0])

        if word.lower() in prepositions:
            seq.add_concept('Preposition', slot[0], slot[1] - slot[0])

    # seq.display()

    for slot in seq.get_slots('Word'):
        value = seq.value[slot[0]: slot[1]]
        # if value in {'the', 'a', 'is', 'and', 'not', 'which', 'or', 'be', 'has', 'been', 'had', 'an', 'of', 'to', 'with'}:
        print(value)
            # continue

        size = slot[1] - slot[0]

        concepts = []

        for match in seq.elements[slot[0]].matches:
            if match.size != size or match.concept == 'Word':
                continue
            concepts.append(match.concept)

        print(concepts)


    """
    Pattern("Article", [
        PatternNode("Word", ["the", "an", "a", ]),
    ]),
    Pattern("Conjunction", [
        PatternNode("Word", ["and", "or", "but", ]),
    ]),
    Pattern("PropositionOfPlace", [
        PatternNode("Word", ["on", "in", "at"]),
    ]),
    Pattern("PropositionOfTime", [
        PatternNode("Word", ["on", "in", "at"]),
    ]),
    Pattern("PropositionOfDirection", [
        PatternNode("Word", ["to", "towards", "into"]),
    ]),
    Pattern("PropositionOfAgency", [
        PatternNode("Word", ["by", ]),
    ]),
    Pattern("PropositionOfInstrument", [
        PatternNode("Word", ["by", "with", "on", ]),
    ]),
    
    "PluralNoun": ["Noun"],
    "PropositionOfPlace": ["Proposition"],
    "PropositionOfTime": ["Proposition"],
    "PropositionOfDirection": ["Proposition"],
    "PropositionOfAgency": ["Proposition"],
    "PropositionOfInstrument": ["Proposition"],
    "Adjective": ["AdjectiveGroup"],
    """


if __name__ == '__main__':
    main()
