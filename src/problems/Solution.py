from abc import ABC, abstractmethod
from typing import ClassVar


class Solution(ABC):
    maxId: ClassVar[int] = 0
    optimDirections: ClassVar[dict] = {}

    def __init__(self, _id: int = None, parameters: dict = {}, solution: dict = {}) -> None:
        assert any(Solution.optimDirections)  # check optimization directions are setup
        if _id is None:
            self._id = Solution.maxId
            Solution.maxId += 1
        else:
            self._id = _id
        self.parameters = parameters
        self.solution = solution

    @abstractmethod
    def compute_solution(self):
        pass
