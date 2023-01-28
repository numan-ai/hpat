import abc
from collections import defaultdict


class HierarchyProvider(abc.ABC):
    @abc.abstractmethod
    def get_parents(self, concept: str) -> list[str]:
        pass

    @abc.abstractmethod
    def get_children(self, concept: str) -> list[str]:
        pass


class DictHierarchyProvider(HierarchyProvider):
    def __init__(self, parents: dict[str, list[str]]):
        self.parents = parents
        self.children = self._build_children(parents)

    def get_parents(self, concept: str) -> list[str]:
        try:
            return self.parents[concept]
        except KeyError:
            return []

    def get_children(self, concept: str) -> list[str]:
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
