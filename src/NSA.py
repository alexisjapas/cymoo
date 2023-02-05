from abc import ABC, abstractmethod


class NSA(ABC):
    @abstractmethod
    def __init__(self, problem, nSolutions):
        self.problem = problem
        self.solutions = problem.populate(nSolutions)
        self.nSolutions = nSolutions
        self.ranking()
        self.get_pareto()


    @abstractmethod
    def optimize(self):
        self.get_pareto()


    @abstractmethod
    def post_optimization(self):pass


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


    def get_pareto(self):
        # get pareto
        pareto_solutions = [sol for sol in self.solutions if sol.rank == 1]

        # remove duplicates
        self.pareto_solutions = []
        for sol in pareto_solutions:
            if sol.parameters not in [s.parameters for s in self.pareto_solutions]:
                self.pareto_solutions.append(sol)
