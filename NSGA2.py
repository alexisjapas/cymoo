from random import choices, randint, gauss, uniform
from time import sleep

from Solution import Solution


class NSGA2():
    def __init__(self, problem, nSolution, minDepth, maxDepth):
        self.problem = problem
        self.solutions = problem.populate(nSolution, minDepth, maxDepth)


    def ranking(self):
        """
        Computes each rank of a set of solutions.
        """
        def _ranking(solutions, rank):
            """
            Recursive implementation of the function.
            """
            dominated_values = []
            undominated_values = solutions.copy()
            for sol in solutions:
                for sol_bis in solutions:
                    if all([sol_bis.solution[i] < sol.solution[i] if opti_dir == 'min' else sol_bis.solution[i] > sol.solution[i] for i, opti_dir in enumerate(self.problem.optim_directions)]):
                        sol.rank = rank
                        dominated_values.append(sol)
                        undominated_values.remove(sol)
                        break
            for sol in undominated_values:
                self.solutions[self.solutions.index(sol)].rank = rank
            if dominated_values:
                rank = _ranking(dominated_values, rank+1)
            return rank

        self.max_rank = _ranking(self.solutions, 1)
        return 0

    def crowding_distance(self):
        """
        Computes crowding distance for each domination rank.
        """
        for rank in range(1, self.max_rank+1):
            current_rank_solutions = [sol for sol in self.solutions if sol.rank == rank]
            sorted_crs = [sorted(current_rank_solutions, key=lambda tup: tup.solution[t]) for t in range(len(current_rank_solutions[0].solution))]
            sorted_crs[0][0].crowding_distance = float("inf")
            sorted_crs[0][-1].crowding_distance = float("inf")
            for i_dim, dim_solutions in enumerate(sorted_crs):
                for i in range(1, len(dim_solutions)-1):
                    dim_solutions[i].crowding_distance += (dim_solutions[i+1].solution[i_dim] - dim_solutions[i-1].solution[i_dim]) / (dim_solutions[-1].solution[i_dim] - dim_solutions[0].solution[i_dim])
        return 0

    def selection(self, ratio_kept):
        self.solutions.sort(key=lambda sol: (sol.rank, -sol.crowding_distance))
        self.solutions = self.solutions[:round(ratio_kept*self.population_size)]
        return 0

    def offspring_generation(self, mutation_strength):
        parents = self.solutions.copy()
        while len(self.solutions) < self.population_size:
            # tournament - select two parent, each between 2 individuals depending on their rank and crowding distance
            parent_1 = choices(parents, k=2)
            parent_1.sort(key=lambda sol: (sol.rank, -sol.crowding_distance))
            parent_1 = parent_1[0]
            parent_2 = choices(parents, k=2)
            parent_2.sort(key=lambda sol: (sol.rank, -sol.crowding_distance))
            parent_2 = parent_2[1]

            # crossover - pick randomly (uniform) genes from parent_1 or parent_2
            #child_solution = [parent_1.solution[i] if randint(0, 1) else parent_2.solution[i] for i in range(len(self.optim_direction))]
            child_solution = self.problem.crossover(parent_1, parent_2)

            # mutation
            child_solution = self.problem.mutate(child_solution)

            # if solution not in solutions then adopt child
            if not child_solution in [sol.solution for sol in self.solutions]:
                Solution.max_id += 1
                self.solutions.append(child_solution)
        return 0

    def optimize(self, ratio_kept):
        self.ranking()
        self.crowding_distance()
        self.solutions.sort(key=lambda sol: sol.id, reverse=True)
        self.selection(ratio_kept)
        self.offspring_generation(0.1)


if __name__ == "__main__":
    from matplotlib import pyplot as plt


    # Parameters
    population_size = 1000
    optim_dir = ["min", "min"]
    X = [tuple(uniform(0, 100) for _ in range(len(optim_dir))) for _ in range(population_size)]

    # Initializing NSGA2
    nsga2 = NSGA2(X, optim_dir)
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
