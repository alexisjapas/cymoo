from dataclasses import dataclass
from typing import ClassVar


@dataclass
class Solution:
    id: int
    solution: tuple
    parameters: list
    rank: int = 0
    crowding_distance: float = 0
    max_id: ClassVar[int] = 0


if __name__ == "__main__":
    sol = Solution(1, (2, 4), [])
    print(sol)
    Solution.max_id = 10
    print(Solution.max_id)
