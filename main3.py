import pickle
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


TAG_MAP = {
    'NOUN': 'Noun',
    'PROPN': 'Noun',
    'CCONJ': 'Conjunction',
    'ADP': 'Adposition',
    'ADV': 'Adverb',
    'PRON': 'Pronoun',
    'VERB': 'Verb',
    'ADJ': 'Adjective',
    'DET': 'Determinant',
}


def main():
    word_extractor = get_word_extractor()

    with open('datasets/frequencies/freqs.pkl', 'rb') as f:
        freqs = pickle.load(f)

    sent = ' ' + random.choice(SENTENCES.strip().split('\n')).lower() + ' '
    seq = DataSequence.from_string(sent)  # SENTENCES.replace('\n', ' '))
    word_extractor.apply(seq)

    print(sent)
    for _ in range(max(25 - len(seq.get_slots('Word')), 0)):
        print()

    for slot in seq.get_slots('Word'):
        word = seq.value[slot[0]: slot[1]]
        count_sum = sum(freqs[word].values())
        for tag, count in freqs[word].items():
            try:
                tag = TAG_MAP[tag]
            except KeyError:
                continue
            seq.add_concept(tag, slot[0], slot[1] - slot[0], weight=count / count_sum)

    # seq.display()

    for slot in seq.get_slots('Word'):
        value = seq.value[slot[0]: slot[1]]
        if value in {'the', 'a', 'is', 'and', 'are', 'was', 'has', 'had', 'that', 'not', 'which', 'or', 'be', 'has', 'been', 'had', 'an', 'of', 'to', 'with', 'as', 'from', 'by'}:
            print(value)
            continue

        size = slot[1] - slot[0]

        concepts = []

        for match in seq.elements[slot[0]].matches:
            if match.size != size or match.concept == 'Word':
                continue
            concepts.append(f"{match.concept}[{match.weight*100:.0f}%]")

        print('\t' + ', '.join(concepts))


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
