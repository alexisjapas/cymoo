from NSGA2 import NSGA2


class MOO:
    def __init__(self, problem, optimizer, n_solutions):
        self.problem = problem
        self.optimizer = optimizer(problem)
        self.population = problem.populate(n_solutions)

    def plot(self):
        pass

    def optimize(self, optimizer, n_iter, **kwargs):
        while n_iter > 0:
            optimizer.optimize(self.population, **kwargs)


if __name__ == "__main__":
    problem = Network()
    optimizer = NSGA2
    moo = MOO(problem, optimizer, 1000)
    moo.optimize(optimizer, 100, ratio_kept=0.5)

