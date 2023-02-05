from random import choices, randint, gauss, uniform
from time import sleep

from NSA import NSA
from Solution import Solution


class NSGA2(NSA):
    """
    TODO DOCSTRING
    """
    def __init__(self, problem, nSolutions) -> None:
        super().__init__(problem, nSolutions)


    def optimize(self, ratioKept):
        self.ranking()
        self.crowding_distance()
        self.selection(ratioKept)
        self.offspring_generation()
        super().optimize()

        return 0


    def post_optimization(self):
        self.ranking()


    def crowding_distance(self):
        """
        Computes crowding distance for each domination rank.
        """
        for rank in range(1, self.maxRank+1):
            currentRankSolutions = [sol for sol in self.solutions if sol.rank == rank]
            sortedCrs = [sorted(currentRankSolutions, key=lambda tup: tup.solution[t]) for t in range(len(currentRankSolutions[0].solution))]
            for i in range(len(sortedCrs)):
                sortedCrs[i][0].crowdingDistance = float("inf")
                sortedCrs[i][-1].crowdingDistance = float("inf")
            for iDim, dimSolutions in enumerate(sortedCrs):
                for i in range(1, len(dimSolutions)-1):
                    if dimSolutions[-1].solution[iDim] - dimSolutions[0].solution[iDim] != 0:
                        dimSolutions[i].crowdingDistance += (dimSolutions[i+1].solution[iDim] - dimSolutions[i-1].solution[iDim]) / (dimSolutions[-1].solution[iDim] - dimSolutions[0].solution[iDim])
        return 0


    def selection(self, ratioKept):
        self.solutions.sort(key=lambda sol: (sol.rank, -sol.crowdingDistance))
        self.solutions = self.solutions[:round(ratioKept*self.nSolutions)]
        return 0


    def offspring_generation(self):
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
            #if not childSolution.parameters in [sol.parameters for sol in self.solutions]:
            Solution.maxId += 1
            self.solutions.append(childSolution)
        return 0


    def __str__(self):
        return "NSGA2"
