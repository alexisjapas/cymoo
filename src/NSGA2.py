from random import choices, randint, gauss, uniform
from time import sleep

from Solution import Solution


class NSGA2():
    """
    TODO DOCSTRING
    """
    def __init__(self, problem, nSolutions, minDepth, maxDepth):
        self.problem = problem
        self.solutions = problem.populate(nSolutions, minDepth, maxDepth)
        self.populationSize = len(self.solutions) - 1


    def ranking(self):
        """
        Computes each rank of a set of solutions.
        """
        def _ranking(solutions, rank):
            """
            Recursive implementation of the function.
            """
            dominatedValues = []
            undominatedValues = solutions.copy()
            for sol in solutions:
                for solBis in solutions:
                    if all([solBis.solution[i] < sol.solution[i] if optimDir == 'min' else solBis.solution[i] > sol.solution[i] for i, optimDir in enumerate(self.problem.optimDirections)]):
                        sol.rank = rank
                        dominatedValues.append(sol)
                        undominatedValues.remove(sol)
                        break
            for sol in undominatedValues:
                self.solutions[self.solutions.index(sol)].rank = rank
            if dominatedValues:
                rank = _ranking(dominatedValues, rank+1)
            return rank

        self.maxRank = _ranking(self.solutions, 1)
        return 0


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
        self.solutions = self.solutions[:round(ratioKept*self.populationSize)]
        return 0


    def offspring_generation(self):
        parents = self.solutions.copy()
        while len(self.solutions) < self.populationSize:
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

            # if solution not in solutions then adopt child
            #if not childSolution.parameters in [sol.parameters for sol in self.solutions]:
            Solution.maxId += 1
            self.solutions.append(childSolution)
        return 0


    def optimize(self, ratioKept):
        self.ranking()
        self.crowding_distance()
        self.selection(ratioKept)
        self.offspring_generation()


if __name__ == "__main__":
    from matplotlib import pyplot as plt


    # Parameters
    populationSize = 1000
    optimDir = ["min", "min"]
    X = [tuple(uniform(0, 100) for _ in range(len(optimDir))) for _ in range(populationSize)]

    # Initializing NSGA2
    nsga2 = NSGA2(X, optimDir)
    plt.ion()
    figure, ax = plt.subplots()
    val, = ax.plot([sol.solution[0] for sol in nsga2.solutions], [sol.solution[1] for sol in nsga2.solutions], 'bo')

    # Optimize
    for _ in range(100):
        nsga2.optimize(0.5)
        val.set_xdata([sol.solution[0] for sol in nsga2.solutions])
        val.set_ydata([sol.solution[1] for sol in nsga2.solutions])
        figure.canvas.draw()
        figure.canvas.flush_events()
        sleep(0.1)
    print("Optimization done successfully.")
