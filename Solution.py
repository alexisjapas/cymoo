from dataclasses import dataclass


@dataclass
class Solution:
    id: int
    solution: tuple
    rank: int = 0
    crowding_distance: float = 0


if __name__ == "__main__":
    sol = Solution(1, (2, 4))
    print(sol)

