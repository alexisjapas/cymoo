def nsgaii_ranking(X, ranks={}, rank=1):
    dominated_values = []
    undominated_values = X.copy()
    for x in X:
        for x_bis in X:
            if x_bis[0] < x[0] and x_bis[1] < x[1]:
                dominated_values.append(x)
                if x in undominated_values:
                    undominated_values.remove(x)
                break
    ranks[rank] = undominated_values
    if dominated_values:
        ranks = nsgaii_ranking(dominated_values, ranks, rank+1)

    return ranks


def crowding_distance(ranks):
    """
    Works only on same rank items.
    """
    print(ranks)
    distances = {}
    for i in range(1, len(ranks)+1):
        X = ranks[i]
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


def relative_efficiency(X, Y, optim_direction):
    dominated = []
    undominated_values = X.copy()
    for x in X:
        for y in Y:
            if y[0] < x[0] and y[1] < x[1]:
                if x in undominated_values:
                    undominated_values.remove(x)
                break

    return len(undominated_values)



if __name__ == "__main__":
    X = [(2.08, 5.34), (5.92, 2.08), (4.18, 3.69), (6.69, 6.67), (7.19, 1.8), (9.89, 8.49), (5.23, 7.41), (9.61, 7.28), (1.9, 6.48), (4.68, 1.47)]
    print(len(X))

    Y = [(8.01, 8.11), (0.65, 7.33), (8.08, 7.46), (1.21, 5.01), (6.34, 4.05), (4.08, 6.15), (2.35, 6.48), (3.33, 4.26), (3.68, 9.68), (8.45, 2.68)]
    print(len(Y))

    print("RANKING")
    ranks_X = nsgaii_ranking(X)
    print(ranks_X, '\n')

    ranks_Y = nsgaii_ranking(Y)
    print(ranks_Y, '\n')

    print("DISTANCES")
    print(crowding_distance(ranks_X), '\n')
    print("ahaha")
    print(crowding_distance(ranks_Y), '\n')

    print("EFFICIENCY")
    print(relative_efficiency(ranks_X[1], ranks_Y[1], "é"))
