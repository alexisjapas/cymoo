from random import choices
from abc import ABC, abstractmethod



from math import ceil
from .NSA import NSA, NSAProblemMixin, NSASolutionMixin


class NSWGE(NSA):
    """
    TODO DOCSTRING
    """
    def __init__(self, problem, nSolutions) -> None:
        super().__init__(problem, nSolutions)

    def pre_optimize(self):
        self.add_final_node()
        self.init_weights()

    def optimize(self):
        self.solutions.clear()
        ## CREATE N SOLUTIONS
        self.solutions = self.problem.populate(self.nSolutions, self.weights)
        self.ranking()
        ## UPDATE WEIGHTS
        self.update_weights(ratio=.5, maximum=25)

    def post_optimize(self):
        self.normalize_weights()
        self.remove_final_node()
        self.ranking()
        self.get_pareto()

    def normalize_weights(self):
        for i in range(len(self.problem.tasks)):
            weights = self.weights[i]
            for j in weights.keys():
                sumWeights = sum(weights[j].values())
                for k in weights[j].keys():
                    if sumWeights != 0:
                        weights[j][k] /= sumWeights
                    else:
                        weights[j][k] = 1/len(weights[j].keys())

    def update_weights(self, ratio, maximum):
        assert ratio <= .5, "Ratio can't be above .5"
        rankDistribution = list(range(1, self.maxRank+1))
        evalPoint = min(maximum, ceil(len(rankDistribution)*ratio))
        values = [0 for _ in rankDistribution]
        for i in range(1, evalPoint+1):
            values[-i] = -(evalPoint-(i-1))
            values[i-1] = evalPoint-(i-1)
        dicUpdate = dict(zip(rankDistribution, values))
        for weight in self.weights:
            for i in weight.keys():
                for j in weight[i].keys():
                    weight[i][j] = (weight[i][j], [])
            for i in self.solutions:
                rank = i.rank
                path = i.parameters[0]['units']
                for j in path[:-1]:
                    weight[j.id][path[path.index(j)+1].id][1].append(dicUpdate[rank])
                weight[path[-1].id]['0'][1].append(dicUpdate[rank])

            def _mean(iterable):
                if len(iterable) == 0:
                    return 0
                return sum(iterable)/len(iterable)
            for key1 in weight.keys():
                for key2 in weight[key1].keys():
                    weight[key1][key2] = max(round(_mean(weight[key1][key2][1]), 3) + weight[key1][key2][0],0)

    def add_final_node(self):
        self.problem.add_final_node()

    def remove_final_node(self):
        self.problem.remove_final_node()

    def init_weights(self):
        self.weights = []
        for _ in range(len(self.problem.tasks)):
            weight = {}
            for node in self.problem.units:
                weight[node.id] = {}
                for node2 in map(lambda x: x.get_other_unit(node), node.cables):
                    if node.tag == 'FINAL' and node2.tag != 'FINAL':
                        weight[node.id][node2.id] = 0
                    elif node2.tag == 'FINAL' and node.tag != 'FINAL':
                        weight[node.id][node2.id] = 1
                    else:
                        weight[node.id][node2.id] = 10
            self.weights.append(weight)

    def __str__(self):
        return "NSWGE"
    
class NSWGEProblemMixin(NSAProblemMixin, ABC):
    @abstractmethod
    def add_final_node(self):
        pass

    @abstractmethod
    def remove_final_node(self):
        pass

class NSWGESolutionMixin(NSASolutionMixin, ABC):
    pass
