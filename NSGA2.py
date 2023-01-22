from Solution import Solution


class NSGA2():
    def __init__(self, X, optim_direction):
        self.X = X
        self.solutions = [Solution(i, x) for i, x in enumerate(X)]
        self.optim_direction = optim_direction

    def default_solutions(self, X):
        self.solutions = [Solution(i, x) for i, x in enumerate(X)]
        return 0

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
                    if all([sol_bis.solution[i] < sol.solution[i] if opti_dir == 'min' else sol_bis.solution[i] > sol.solution[i] for i, opti_dir in enumerate(self.optim_direction)]):
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
                    dim_solutions[i].crowding_distance += dim_solutions[i+1].solution[i_dim] - dim_solutions[i-1].solution[i_dim]
        return 0

    def selection(self, crowding_distances, n_kept):
        pass

    def relative_efficiency(self, X, Y, optim_direction):
        """
        Number of solutions of X undominated by Y solutions. DEPRECATED.
        """
        undominated_values = X
        for x in X:
            for y in Y:
                if all([y[i] < x[i] if opti_dir == 'min' else y[i] > x[i] for i, opti_dir in enumerate(optim_direction)]):
                    if x in undominated_values:
                        undominated_values.remove(x)
                    break

        return len(undominated_values)

    def optimize(self, ratio_kept):
        default_solutions(self.X)
        self.ranking()
        self.crowding_distance()
        selected = self.selection(distances, round(len(X) * ratio_kept))


if __name__ == "__main__":
    # Parameters
    X = [(2.08, 5.34), (5.92, 2.08), (4.18, 3.69), (6.69, 6.67), (7.19, 1.8), (9.89, 8.49), (5.23, 7.41), (9.61, 7.28), (1.9, 6.48), (4.68, 1.47)]
    optim_dir = ["min", "min"]

    # Initializing NSGA2
    nsga2 = NSGA2(X, optim_dir)

    # Optimize
    # final_sols = nsga2.optimize(0.5)
    # final_sols2 = nsga2.optimize(0.2)

    # Tests
    print(nsga2.solutions)
    print()
    nsga2.ranking()
    for sol in nsga2.solutions:
        print(sol)

    nsga2.crowding_distance()
    for sol in nsga2.solutions:
        print(sol)

