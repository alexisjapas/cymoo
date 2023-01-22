class NSGA2():
    def __init__(self):
        pass

    def nsga2_ranking(self, X, optim_direction):
        """
        Computes each rank of a set of solutions.
        """
        def _nsga2_ranking(X, ranks, rank):
            """
            Recursive implementation of the function.
            """
            dominated_values = []
            undominated_values = X.copy()
            for x in X:
                for x_bis in X:
                    if all([x_bis[i] < x[i] if opti_dir == 'min' else x_bis[i] > x[i] for i, opti_dir in enumerate(optim_direction)]):
                        dominated_values.append(x)
                        undominated_values.remove(x)
                        break
            ranks[rank] = undominated_values
            if dominated_values:
                ranks = _nsga2_ranking(dominated_values, ranks, rank+1)
            return ranks

        return _nsga2_ranking(X, {}, 1)

    def crowding_distance(self, ranks):
        """
        Computes crowding distance for each domination rank.
        """
        distances = {}
        for i, X in ranks.items():
            sorted_X = [sorted(X, key=lambda tup: tup[t]) for t in range(len(X[0]))]
            X_distances = [0 for _ in range(len(X))]
            X_distances[0] = float("inf")
            X_distances[-1] = float("inf")

            for j_dim, dim in enumerate(sorted_X):
                if dim != sorted_X[0]:
                    X_distances.reverse()
                for j in range(1, len(X)-1):
                    X_distances[j] += dim[j+1][j_dim] - dim[j-1][j_dim]
                if dim != sorted_X[0]:
                    X_distances.reverse()
            distances[i] = X_distances

        return distances

    def relative_efficiency(self, X, Y, optim_direction):
        """
        Number of solutions of X undominated by Y solutions.
        """
        undominated_values = X
        for x in X:
            for y in Y:
                if all([y[i] < x[i] if opti_dir == 'min' else y[i] > x[i] for i, opti_dir in enumerate(optim_direction)]):
                    if x in undominated_values:
                        undominated_values.remove(x)
                    break

        return len(undominated_values)


if __name__ == "__main__":
    optim_dir = ["min", "min"]
    vX = [(2.08, 5.34), (5.92, 2.08), (4.18, 3.69), (6.69, 6.67), (7.19, 1.8), (9.89, 8.49), (5.23, 7.41), (9.61, 7.28), (1.9, 6.48), (4.68, 1.47)]
    print(len(vX))

    vY = [(8.01, 8.11), (0.65, 7.33), (8.08, 7.46), (1.21, 5.01), (6.34, 4.05), (4.08, 6.15), (2.35, 6.48), (3.33, 4.26), (3.68, 9.68), (8.45, 2.68)]
    print(len(vY))


    nsga2 = NSGA2()
    print("RANKING")
    ranks_vX = nsga2.nsga2_ranking(vX, optim_dir)
    print(ranks_vX, '\n')

    ranks_vY = nsga2.nsga2_ranking(vY, optim_dir)
    print(ranks_vY, '\n')

    print("DISTANCES")
    print(nsga2.crowding_distance(ranks_vX), '\n')
    print(nsga2.crowding_distance(ranks_vY), '\n')

    print("EFFICIENCY")
    print(nsga2.relative_efficiency(ranks_vX[1], ranks_vY[1], optim_dir))
    print(nsga2.relative_efficiency(ranks_vY[1], ranks_vX[1], optim_dir))
