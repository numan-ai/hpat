from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

from hpat.match import Match


@dataclass
class DataElement:
    value: Optional[any] = None
    matches: list[Match] = field(default_factory=list)

    def contains_match(self, match: Match) -> bool:
        for saved in self.matches:
            if saved.concept != match.concept:
                continue
            if saved.size != match.size:
                continue
            if saved.start_idx != match.start_idx:
                continue
            # if saved.depends_on_matches != match.depends_on_matches:
            #     continue

            return True
        return False

    def add_match(self, match: Match) -> bool:
        if not self.contains_match(match):
            self.matches.append(match)
            return True
        return False


@dataclass
class DataSequence:
    value: str
    elements: list[DataElement]
    extractions: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))
    consolidated: bool = False
    match_by_id: dict[str, Match] = field(default_factory=dict)

    def __post_init__(self):
        for ele in self.elements:
            for match in ele.matches:
                self.match_by_id[match.id] = match

    def add_concept(self, concept, start_idx: int, size: int, weight: float = 1.0) -> bool:
        return self.add_match(Match(
            concept=concept,
            value=self.value[start_idx: start_idx + size],
            size=size,
            start_idx=start_idx,
            weight=weight,
        ))

    def add_match(self, match: Match) -> bool:
        """ Adds match if it is new and returns whether is was added
        May add many overlapping matches with the same concept if they do not align perfectly.
        """
        if not match.dependencies_present(self):
            return False

        self.consolidated = False
        added_new_match = False
        for idx in range(match.size):
            added = self.elements[match.start_idx + idx].add_match(match)
            added_new_match |= added
            if added:
                self.match_by_id[match.id] = match
        return added_new_match

    def revoke_match(self, match_id: str):
        """ Removes match by its id and all matches that depend on it
        This may happen when an assumed match was invalidated.
        """
        self.consolidated = False
        to_revoke = []
        for node in self.elements:
            to_remove = []
            for match in node.matches:
                if match_id in match.depends_on_matches:
                    to_revoke.append(match.id)
                elif match_id == match.id:
                    to_remove.append(match)

            for match in to_remove:
                del self.match_by_id[match.id]
                node.matches.remove(match)

        for match_id in to_revoke:
            self.revoke_match(match_id)

    def consolidate(self):
        """ Takes all matches and finds all extractions """
        if self.consolidated:
            return

        self.extractions.clear()

        matches = []
        match_ids = set()

        for node in self.elements:
            for match in node.matches:
                if match.id not in match_ids:
                    matches.append(match)
                    match_ids.add(match.id)

        for match in matches:
            for pattern_node_id, values in match.extractions.items():
                self.extractions[pattern_node_id].extend(values)

        self.consolidated = True

    def display(self):
        for node in self.elements:
            matches = sorted(node.matches, key=lambda x: (x.size, len(x.concept)), reverse=True)
            print(', '.join([repr(x) for x in matches]))

    def to_list(self):
        result = []
        for node in self.elements:
            matches = sorted(node.matches, key=lambda x: (x.size, len(x.concept)), reverse=True)
            result.append([
                (match.concept, match.value)
                for match in matches
            ])
        return result

    def extract(self, pattern_node_id: str):
        if not self.consolidated:
            raise Exception("Must consolidate first")
        return self.extractions.get(pattern_node_id, [])

    @classmethod
    def from_string(cls, text):
        return cls(
            value=text,
            elements=[
                DataElement(ch, [Match(concept='Character', value=ch, size=1, start_idx=i)])
                for i, ch in enumerate(text)
            ]
        )

    def get_all_match_ids(self) -> set[str]:
        match_ids = set()

        for elem in self.elements:
            for match in elem.matches:
                match_ids.add(match.id)

        return match_ids

    def get_match_importance(self, match_id: str) -> int:
        """ Returns number of dependant matches"""
        return len(self.get_dependant_matches(match_id))

    def get_dependant_matches(self, match_id) -> set[str]:
        deps = set()

        for elem in self.elements:
            for match in elem.matches:
                if match_id in match.depends_on_matches:
                    deps.add(match.id)
                    deps.update(self.get_dependant_matches(match_id.id))

        return deps

    def get_slots(self, concept: str) -> list[tuple[int, int]]:
        """ Returns slots (positions) for a given concept,
        slot is a tuple of (start_idx, end_idx).
        """
        result = []
        for idx, elem in enumerate(self.elements):
            for match in elem.matches:
                if match.start_idx != idx:
                    continue
                if match.concept != concept:
                    continue
                result.append((match.start_idx, match.start_idx + match.size))

        return result
