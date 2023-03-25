from abc import ABC

from ..problems.Solution import Solution
from .Optimizer import Optimizer, OptimizerProblemMixin, OptimizerSolutionMixin


class NSA(Optimizer, ABC):
    def __init__(self, problem, nSolutions) -> None:
        super().__init__(problem, nSolutions)
        self.ranking()
        self.get_pareto()

    def ranking(self) -> int:
        """
        Computes domination rank of each solution of the population.
        """

        def _ranking(solutions, rank) -> int:
            """
            Set the rank of non-dominated solutions argument to rank argument.
            This function is called recursively with remaining dominated solutions and rank set to rank+1 as long as
            there are any.
            """
            # eliminates dominated solutions from undominated
            dominatedValues = []
            undominatedValues = solutions.copy()
            for sol in solutions:
                for solBis in solutions:
                    # if sol is dominated in all dimensions by another solution
                    # then it is eliminated from the non-dominated solutions
                    if sol.solution != solBis.solution and all(
                        [
                            solBis.solution[dim] <= sol.solution[dim]
                            if optimDir == "min"
                            else solBis.solution[dim] >= sol.solution[dim]
                            for dim, optimDir in Solution.optimDirections.items()
                        ]
                    ):
                        dominatedValues.append(sol)
                        undominatedValues.remove(sol)
                        break

            # set undominated solutions rank
            for sol in undominatedValues:
                self.solutions[self.solutions.index(sol)].rank = rank

            # recall if there are any dominated left otherwise returns the maximum rank
            if dominatedValues:
                rank = _ranking(dominatedValues, rank + 1)
            return rank

        self.maxRank = _ranking(self.solutions, 1)

    def get_pareto(self):
        """
        Returns unique pareto solutions of the population.
        """
        # get pareto
        pareto_solutions = [sol for sol in self.solutions if sol.rank == 1]

        # remove duplicates
        self.pareto_solutions = []
        for sol in pareto_solutions:
            if sol.parameters not in [s.parameters for s in self.pareto_solutions]:
                self.pareto_solutions.append(sol)


class NSAProblemMixin(OptimizerProblemMixin, ABC):
    pass


class NSASolutionMixin(OptimizerSolutionMixin, ABC):
    pass
