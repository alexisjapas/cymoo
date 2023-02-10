from dataclasses import dataclass
from typing import ClassVar


@dataclass
class Solution:
    id: int
    solution: tuple
    parameters: tuple
    rank: int = 0
    crowdingDistance: float = 0
    maxId: ClassVar[int] = 0


if __name__ == "__main__":
    sol = Solution(1, (2, 4), parameters=[])
    Solution.maxId = 10
    print(sol)

