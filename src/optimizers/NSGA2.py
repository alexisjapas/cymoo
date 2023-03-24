from abc import ABC, abstractmethod
from random import choices

from ..problems.Solution import Solution
from .NSA import NSA, NSAProblemMixin, NSASolutionMixin


class NSGA2(NSA):
    """
    TODO DOCSTRING
    """

    def __init__(self, problem, nSolutions) -> None:
        super().__init__(problem, nSolutions)

    def pre_optimize(self):
        pass

    def optimize(self, ratioKept):
        self.ranking()
        self.crowding_distance()
        self.selection(ratioKept)
        self.offspring_generation()

    def post_optimize(self):
        self.ranking()

    def crowding_distance(self):
        """
        Computes crowding distance for each domination rank.
        """
        for rank in range(1, self.maxRank + 1):
            rankSolutions = [sol for sol in self.solutions if sol.rank == rank]
            # for each dimension, sort solutions according to it and accumulate crowding distance.
            for dim in Solution.optimDirections.keys():
                rankSolutions.sort(key=lambda tup: tup.solution[dim])
                rankSolutions[0].crowdingDistance = float("inf")
                rankSolutions[-1].crowdingDistance = float("inf")
                for s in range(1, len(rankSolutions) - 1):
                    dimensionDynamic = rankSolutions[-1].solution[dim] - rankSolutions[0].solution[dim]
                    if dimensionDynamic != 0:
                        rankSolutions[s].crowdingDistance += (
                            rankSolutions[s + 1].solution[dim] - rankSolutions[s - 1].solution[dim]
                        ) / dimensionDynamic

    def selection(self, ratioKept):
        """
        Drop worst solutions according to their ranks (lower is better),
        if equal in rank, uses crowding distance (higher is better).
        """
        self.solutions.sort(key=lambda sol: (sol.rank, -sol.crowdingDistance))
        self.solutions = self.solutions[: round(ratioKept * self.nSolutions)]

    def offspring_generation(self):
        """
        Generates new solutions by crossing the selected solutions and randomly mutating a gene from this cross.
        Only non-existing solutions are kept.
        Parents are selected with binary tournaments according to their rank (lower is better),
        if equal in rank, uses crowding distance (higher is better).
        Crossover and mutation functions are problem specific and so defined by it.
        """
        parents = self.solutions.copy()
        while len(self.solutions) < self.nSolutions:
            # tournament - select two parent, each between 2 individuals depending on their rank and crowding distance
            parent1 = choices(parents, k=2)
            parent1.sort(key=lambda sol: (sol.rank, -sol.crowdingDistance))
            parent1 = parent1[0]
            parent2 = choices(parents, k=2)
            parent2.sort(key=lambda sol: (sol.rank, -sol.crowdingDistance))
            parent2 = parent2[1]

            # crossover - pick randomly (uniform) genes from parent1 or parent2
            childSolution = self.problem.crossover(parent1, parent2)

            # mutation
            if childSolution is None:
                continue
            childSolution = self.problem.mutate(childSolution)

            # verify not already existing
            if childSolution.parameters in [sol.parameters for sol in self.solutions]:
                continue

            # if solution not in solutions then adopt child
            Solution.maxId += 1
            self.solutions.append(childSolution)

    def __str__(self):
        return "NSGA2"


class NSGA2ProblemMixin(NSAProblemMixin, ABC):
    @abstractmethod
    def crossover(self):
        pass

    @abstractmethod
    def mutate(self):
        pass


class NSGA2SolutionMixin(NSASolutionMixin, ABC):
    pass
