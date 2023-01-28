import copy
import uuid
from collections import defaultdict
from dataclasses import dataclass, field


def _get_match_id():
    return str(uuid.uuid4())


@dataclass(slots=True)
class Match:
    """ Describes match result"""
    concept: str
    value: any
    size: int
    start_idx: int
    id: str = field(repr=False, default_factory=_get_match_id)
    # is this match a result of an assumption
    assumed: bool = False
    # in case match depends on non-confirmed matches,
    # we want to deleted it if matches are invalidated
    depends_on_matches: list[str] = field(default_factory=list)
    extractions: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list), repr=False)
    weight: float = 1

    def __repr__(self):
        weight_str = ""
        if self.weight != 1:
            weight_str = f" {self.weight * 100:.0f}%"
        return f"<{self.concept} \"{self.value}\" [{self.size}]{weight_str}>"

    def dependencies_present(self, seq):
        match_ids = seq.get_all_match_ids()
        return not bool(set(self.depends_on_matches).difference(match_ids))


@dataclass(slots=True)
class MatchAssumption:
    sequence_start_idx: int
    sequence_end_idx: int
    assumed_concept: str
    weight: float = 1.0


@dataclass(slots=True)
class MatchState:
    """ Keeps state of matching progress
    Pattern matching is a process of generating matching states.
    When a matching state is fulfilled it can be saved as Match.
    Matching state can be fulfilled many times while going through the sequence.
    This ensures backtracking.
    """
    sequence_idx: int = 0
    pattern_idx: int = 0
    # where the match starts, can't set to 0, because of PRE
    sequence_start_idx: int = None
    # where the match ends
    sequence_end_idx: int = None
    many_optional: bool = False
    # {kb_node_id: [val1, val2]}
    extractions: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list), repr=False)
    assumptions: list['MatchAssumption'] = field(default_factory=list, repr=False)
    depends_on_matches: list[str] = field(default_factory=list, repr=False)

    def get_next(self,
                 next_pattern: bool = True,
                 element_advancement: int = 1,
                 many_optional: bool = False) -> 'MatchState':
        return MatchState(
            sequence_idx=self.sequence_idx + element_advancement,
            pattern_idx=(self.pattern_idx + 1) if next_pattern else self.pattern_idx,
            sequence_start_idx=self.sequence_start_idx,
            sequence_end_idx=self.sequence_end_idx,
            many_optional=many_optional,
            extractions=copy.deepcopy(self.extractions),
            assumptions=copy.copy(self.assumptions),
            depends_on_matches=copy.copy(self.depends_on_matches),
        )

    def get_matches(self, seq, concept, weight):
        for match_id in self.depends_on_matches:
            match = seq.match_by_id[match_id]
            weight = min(weight, match.weight)

        matches = []
        main_match = Match(
            concept=concept,
            value=seq.value[self.sequence_start_idx: self.sequence_end_idx],
            size=self.sequence_end_idx - self.sequence_start_idx,
            start_idx=self.sequence_start_idx,
            assumed=False,
            depends_on_matches=self.depends_on_matches.copy(),
            extractions=copy.deepcopy(self.extractions),
            weight=weight,
        )
        matches.append(main_match)

        for asmp in self.assumptions:
            matches.append(Match(
                concept=asmp.assumed_concept,
                value=seq.value[asmp.sequence_start_idx: asmp.sequence_end_idx],
                size=asmp.sequence_end_idx - asmp.sequence_start_idx,
                start_idx=asmp.sequence_start_idx,
                assumed=True,
                depends_on_matches=[main_match.id, ],
                weight=asmp.weight,
            ))
        return matches

    def get_value(self, seq):
        return seq.value[self.sequence_start_idx: self.sequence_end_idx]
