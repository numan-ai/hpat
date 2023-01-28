from hpat import (
    DataSequence,
    Match,
)
from hpat.match import (
    MatchAssumption,
    MatchState,
)


def test_data_sequence_add_match_simple():
    seq = DataSequence.from_string("apple")
    seq.add_match(Match("Apple", value="apple", size=5, start_idx=0))
    assert seq.to_list() == [
        [("Apple", "apple"), ("Character", "a")],
        [("Apple", "apple"), ("Character", "p")],
        [("Apple", "apple"), ("Character", "p")],
        [("Apple", "apple"), ("Character", "l")],
        [("Apple", "apple"), ("Character", "e")],
    ]


def test_data_sequence_add_match_twice_duplicated():
    seq = DataSequence.from_string("apple")
    seq.add_match(Match("Apple", value="apple", size=5, start_idx=0))
    seq.add_match(Match("Apple", value="apple", size=5, start_idx=0))
    assert seq.to_list() == [
        [("Apple", "apple"), ("Character", "a")],
        [("Apple", "apple"), ("Character", "p")],
        [("Apple", "apple"), ("Character", "p")],
        [("Apple", "apple"), ("Character", "l")],
        [("Apple", "apple"), ("Character", "e")],
    ]


def test_data_sequence_add_match_twice_different_size():
    seq = DataSequence.from_string("apple")
    seq.add_match(Match("Apple", value="apple", size=5, start_idx=0))
    seq.add_match(Match("Apple", value="appl", size=4, start_idx=0))
    assert seq.to_list() == [
        [("Apple", "apple"), ("Apple", "appl"), ("Character", "a")],
        [("Apple", "apple"), ("Apple", "appl"), ("Character", "p")],
        [("Apple", "apple"), ("Apple", "appl"), ("Character", "p")],
        [("Apple", "apple"), ("Apple", "appl"), ("Character", "l")],
        [("Apple", "apple"), ("Character", "e")],
    ]


def test_data_sequence_add_match_twice_different_start_idx():
    seq = DataSequence.from_string("apple")
    seq.add_match(Match("Apple", value="appl", size=4, start_idx=0))
    seq.add_match(Match("Apple", value="pple", size=4, start_idx=1))
    assert seq.to_list() == [
        [("Apple", "appl"), ("Character", "a")],
        [("Apple", "appl"), ("Apple", "pple"), ("Character", "p")],
        [("Apple", "appl"), ("Apple", "pple"), ("Character", "p")],
        [("Apple", "appl"), ("Apple", "pple"), ("Character", "l")],
        [("Apple", "pple"), ("Character", "e")],
    ]


def test_data_sequence_revoke_match():
    seq = DataSequence.from_string("a")
    seq.add_match(Match("Apple", value="a", size=1, start_idx=0, id='0'))

    assert seq.to_list() == [
        [("Character", "a"), ("Apple", "a")],
    ]

    seq.revoke_match('0')

    assert seq.to_list() == [[("Character", "a"), ]]


def test_data_sequence_revoke_match_chain():
    seq = DataSequence.from_string("a")
    seq.add_match(Match("Apple1", value="a", size=1, start_idx=0, id='1'))
    seq.add_match(Match("Apple2", value="a", size=1, start_idx=0, id='2'))
    seq.add_match(Match("Apple3", value="a", size=1, start_idx=0, id='3',
                        depends_on_matches=['2', ]))
    seq.add_match(Match("Apple4", value="a", size=1, start_idx=0, id='4',
                        depends_on_matches=['3', ]))

    assert seq.to_list() == [
        [("Character", "a"), ("Apple1", "a"), ("Apple2", "a"), ("Apple3", "a"), ("Apple4", "a")],
    ]

    seq.revoke_match('2')

    assert seq.to_list() == [[("Character", "a"), ("Apple1", "a")]]


def test_data_sequence_get_matches_with_assumption():
    seq = DataSequence.from_string("a")
    state = MatchState(
        sequence_start_idx=0,
        sequence_end_idx=1,
        assumptions=[
            MatchAssumption(0, 1, "Noun"),
        ]
    )
    matches = state.get_matches(seq, "Apple", weight=1.0)
    assert len(matches) == 2
    main_match = matches[0]
    assert main_match.concept == 'Apple'

    for match in matches:
        seq.add_match(match)

    assert seq.to_list() == [
        [("Character", "a"), ("Apple", "a"), ("Noun", "a")],
    ]

    seq.revoke_match(main_match.id)

    assert seq.to_list() == [[("Character", "a"), ]]
