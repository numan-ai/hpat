import copy
import enum
from dataclasses import dataclass, field
from typing import Optional, Union, List, Tuple

from hpat.data_sequence import DataSequence
from hpat.hierarchy import HierarchyProvider
from hpat.match import (
    MatchState,
    Match,
    MatchAssumption,
)


class PatternNodeOrigin(enum.Enum):
    PRE = enum.auto()
    BODY = enum.auto()
    POST = enum.auto()


@dataclass
class PatternNode:
    concept: Union[str, List[str]]
    value: any = None
    optional: bool = False
    many: bool = False
    assume: str = None
    assumption_weight: float = 1.0
    id: Optional[str] = None
    # this pattern should or shouldn't match
    negate: bool = False
    # must match concept, but not the value/values
    negate_value: bool = False
    # if False, sequence_idx won't change
    advance: bool = True
    # requires to be in the start of text
    at_start: bool = False
    # requires to be in the end of text
    at_end: bool = False
    # if True, at_start will be carried over
    many_start: bool = False
    # if True, at_end will be carried over
    # TODO: many end does not make sense
    many_end: bool = False

    def get_next_states(self, matches, seq: DataSequence, state: MatchState,
                        hierarchy: HierarchyProvider, origin: PatternNodeOrigin):
        next_states = []

        original_state = copy.deepcopy(state)

        for match in matches:
            if match.start_idx != state.sequence_idx:
                continue

            is_matching = self.is_matching(match, seq, state, hierarchy)
            if self.negate:
                is_matching = not is_matching

            if not is_matching:
                continue

            state = copy.deepcopy(original_state)

            element_advancement = match.size
            if not self.advance:
                element_advancement = 0

            if origin is PatternNodeOrigin.BODY:
                state.sequence_end_idx += element_advancement

            if self.id is not None:
                state.extractions[self.id].append(match.value)
            if self.assume is not None:
                state.assumptions.append(MatchAssumption(
                    sequence_start_idx=match.start_idx,
                    sequence_end_idx=match.start_idx + match.size,
                    assumed_concept=self.assume,
                    weight=self.assumption_weight,
                ))

            new_state = state.get_next(element_advancement=element_advancement)
            if self.id:
                if match.structure:
                    new_state.add_data(self.id, copy.deepcopy(match.structure), many=self.many)
                else:
                    new_state.add_data(self.id, copy.deepcopy(match.value), many=self.many)

            new_state.depends_on_matches.append(match.id)
            next_states.append(new_state)
            if self.many:
                new_state = state.get_next(next_pattern=False,
                                           element_advancement=element_advancement,
                                           many_optional=True)
                new_state.depends_on_matches.append(match.id)
                next_states.append(new_state)
                if self.id:
                    if match.structure:
                        new_state.add_data(self.id, copy.deepcopy(match.structure), many=self.many)
                    else:
                        new_state.add_data(self.id, copy.deepcopy(match.value), many=self.many)

        state = original_state

        if self.is_optional(state):
            new_state = state.get_next(element_advancement=0)
            next_states.append(new_state)

        return next_states

    def is_matching(self, match: Match, seq: DataSequence | None,
                    state: MatchState, hierarchy: HierarchyProvider = None) -> bool:
        """ State is matching if data element contains concept of the pattern.
        """
        at_start = self.at_start
        at_end = self.at_end

        if state.many_optional:
            # second+ many node
            if not self.many_start:
                at_start = False
            if not self.many_end:
                at_end = False

        if at_start and match.start_idx != 0:
            return False
        if at_end and (match.start_idx + match.size) != len(seq.value):
            return False

        matching_concepts = {match.concept, }
        if hierarchy is not None:
            matching_concepts.update(set(hierarchy.get_parents(match.concept)))

        if isinstance(self.concept, str):
            this_concepts = {self.concept, }
        else:
            this_concepts = set(self.concept)

        if not this_concepts.intersection(matching_concepts):
            return False

        if self.value is None:
            return True

        values = self.value
        if not isinstance(values, list):
            values = [values, ]

        if self.negate_value:
            return match.value not in values
        else:
            return match.value in values

    def is_optional(self, state: MatchState) -> bool:
        """ Pattern also is optional when it is repeating and was matched.
        """
        return self.optional or (self.many and state.many_optional)


@dataclass
class Pattern:
    concept: str
    nodes: List[PatternNode]
    pre: List[PatternNode] = field(default_factory=list)
    post: List[PatternNode] = field(default_factory=list)
    id: Optional[str] = None
    # requires pattern to match inside specified concepts,
    # must cover them start-to-end
    inside: Optional[str] = None
    weight: float = 1.0
    rules: list = field(default_factory=list)

    def match(self, seq: DataSequence, state: MatchState,
              hierarchy: HierarchyProvider = None) -> List[Match]:
        next_states = [state]
        matches = []

        while next_states:
            new_states = []
            for state in next_states:
                if self.is_state_completed(state):
                    if self.id:
                        value = seq.value[state.sequence_start_idx: state.sequence_end_idx]
                        state.extractions[self.id].append(value)
                    matches.extend(state.get_matches(seq, self.concept, self.weight))

                new_states.extend(self.get_next_states(seq, state, hierarchy))
            next_states = new_states

        return matches

    def get_next_states(self, seq: DataSequence, state: MatchState,
                        hierarchy: HierarchyProvider) -> List[MatchState]:
        try:
            matches: List[Match] = seq.elements[state.sequence_idx].matches
            # this line should go before the "disabled" check, so that
            # we don't return "new_state" if there is no next pattern node
            pattern_node, node_origin = self.get_node(state.pattern_idx)

            if seq.elements[state.sequence_idx].disabled:
                new_state = copy.deepcopy(state)
                new_state.sequence_idx += 1
                if new_state.sequence_end_idx is not None:
                    new_state.sequence_end_idx += 1
                return [new_state, ]
        except IndexError:
            return []

        if node_origin is PatternNodeOrigin.BODY and state.sequence_start_idx is None:
            state.sequence_start_idx = state.sequence_idx
            state.sequence_end_idx = state.sequence_idx

        return pattern_node.get_next_states(matches, seq, state, hierarchy, node_origin)

    def is_state_completed(self, state: MatchState) -> bool:
        """ Returns if the state is completed and can be saved to sequence"""
        if state.pattern_idx < (len(self.nodes) + len(self.pre) + len(self.post)):
            return False
        return True

    def get_node(self, node_idx) -> Tuple[PatternNode, PatternNodeOrigin]:
        """ This is introduced in case of nested pattern nodes (in groups),
        """
        len_pre = len(self.pre)
        len_body = len(self.nodes)
        if node_idx < len_pre:
            return self.pre[node_idx], PatternNodeOrigin.PRE
        elif node_idx < len_pre + len_body:
            return self.nodes[node_idx - len_pre], PatternNodeOrigin.BODY
        return self.post[node_idx - len_pre - len_body], PatternNodeOrigin.POST
