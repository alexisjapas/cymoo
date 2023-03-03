from random import choices

from problems.Solution import Solution
from .NSA import NSA


class NSRA(NSA):
    """
    TODO DOCSTRING
    """
    def __init__(self, problem, nSolutions) -> None:
        super().__init__(problem, nSolutions)

    def pre_optimize(self):pass

    def optimize(self, ratioKept):
        self.ranking()
        self.crowding_distance()
        self.selection(ratioKept)
        self.solutions.extend(self.problem.populate(self.nSolutions - round(ratioKept*self.nSolutions)))

    def post_optimize(self):
        self.ranking()

    def crowding_distance(self):
        """
        Computes crowding distance for each domination rank.
        """
        for rank in range(1, self.maxRank+1):
            rankSolutions = [sol for sol in self.solutions if sol.rank == rank]
            # for each dimension, sort solutions according to it and accumulate crowding distance.
            for iDim in range(len(rankSolutions[0].solution)):
                rankSolutions.sort(key=lambda tup: tup.solution[iDim])
                rankSolutions[0].crowdingDistance = float("inf")
                rankSolutions[-1].crowdingDistance = float("inf")
                for s in range(1, len(rankSolutions)-1):
                    dimensionDynamic = rankSolutions[-1].solution[iDim] - rankSolutions[0].solution[iDim]
                    if dimensionDynamic != 0:
                        rankSolutions[s].crowdingDistance += (rankSolutions[s+1].solution[iDim] - rankSolutions[s-1].solution[iDim]) / dimensionDynamic

    def selection(self, ratioKept):
        """
        Drop worst solutions according to their ranks (lower is better), if equal in rank, uses crowding distance (higher is better).
        """
        self.solutions.sort(key=lambda sol: (sol.rank, -sol.crowdingDistance))
        self.solutions = self.solutions[:round(ratioKept*self.nSolutions)]

    def __str__(self):
        return "NSRA"
