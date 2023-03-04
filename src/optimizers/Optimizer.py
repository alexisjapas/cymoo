from abc import ABC, abstractmethod


class Optimizer(ABC):
    def __init__(self, problem, nSolutions):
        self.problem = problem
        self.solutions = problem.populate(nSolutions)
        self.nSolutions = nSolutions

    @abstractmethod
    def pre_optimize(self):
        pass

    @abstractmethod
    def optimize(self):
        pass

    @abstractmethod
    def post_optimize(self):
        pass
