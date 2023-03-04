from abc import ABC, abstractmethod

from .Solution import Solution


class Problem(ABC):
    def __init__(self, optimDirections):
        Solution.optimDirections = optimDirections

    @abstractmethod
    def pre_optimize(self):pass

    @abstractmethod
    def post_optimize(self):pass

    @abstractmethod
    def populate(self):pass
