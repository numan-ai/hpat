import abc
from collections import defaultdict
from typing import List, Dict


class HierarchyProvider(abc.ABC):
    @abc.abstractmethod
    def get_parents(self, concept: str) -> List[str]:
        pass

    @abc.abstractmethod
    def get_children(self, concept: str) -> List[str]:
        pass


class DictHierarchyProvider(HierarchyProvider):
    def __init__(self, parents: Dict[str, List[str]]):
        self.parents = parents
        self.children = self._build_children(parents)

    def get_parents(self, concept: str) -> List[str]:
        try:
            result = set()

            for parent in self.parents[concept]:
                result.add(parent)
                result.update(self.get_parents(parent))

            return sorted(list(result))
        except KeyError:
            return []

    def get_children(self, concept: str) -> List[str]:
        try:
            return self.children[concept]
        except KeyError:
            return []

    @staticmethod
    def _build_children(parents):
        children = defaultdict(list)
        for child, pars in parents.items():
            for parent in pars:
                children[parent].append(child)

        return children
