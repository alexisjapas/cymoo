import time
from copy import deepcopy
from math import ceil

from problems.Network import Network
from problems.Unit import Unit
from problems.Cable import Cable
from problems.Path import Path
from problems.Task import Task
from .NSA import NSA


class NSWGE(NSA):
    """
    TODO docstring
    """
    def __init__(self, problem: Network, nSolutions) -> None:
        super().__init__(problem, nSolutions)
        self.add_final_node()
        self.init_weights()


    def optimize(self):
        self.solutions.clear()
        for _ in range(self.nSolutions):
            path = self.problem.generate_path(self.problem.maxDepth, self.weights)
            self.remove_finals(path)
            self.solutions.append(path.to_solution(self.problem.task))

        self.ranking()
        self.update_weights(ratio=.5, maximum=25)

        super().optimize()
        return self.weights


    def post_optimization(self):
        self.normalize_weights()
        self.ranking()


    def normalize_weights(self):
        for i in self.weights.keys():
            sumWeights = sum(self.weights[i].values())
            for j in self.weights[i].keys():
                if sumWeights != 0:
                    self.weights[i][j] /= sumWeights
                else:
                    self.weights[i][j] = 1/len(self.weights[i].keys())


    def update_weights(self, ratio, maximum):
        assert ratio <= .5, "Ratio can't be above .5"
        rankDistribution = list(range(1, self.maxRank+1))
        evalPoint= min(maximum, ceil(len(rankDistribution)*ratio))
        values = [0 for _ in rankDistribution]
        for i in range(1, evalPoint+1):
            values[-i] = -(evalPoint-(i-1))
            values[i-1] = evalPoint-(i-1)
        dicUpdate = dict(zip(rankDistribution, values))

        for i in self.weights.keys():
            for j in self.weights[i].keys():
                self.weights[i][j] = (self.weights[i][j], [])

        for i in self.solutions:
            rank = i.rank
            path = i.parameters[0]
            for j in path[:-1]:
                self.weights[j.id][path[path.index(j)+1].id][1].append(dicUpdate[rank])
            self.weights[path[-1].id]['0'][1].append(dicUpdate[rank])

        def _mean(iter):
            if iter == []:
                return 0
            sum = 0
            for i in iter:
                sum +=i
            return sum/len(iter)

        for key1 in self.weights.keys():
            for key2 in self.weights[key1].keys():
                self.weights[key1][key2] = max(0,self.weights[key1][key2][0] + round(_mean(self.weights[key1][key2][1]),3))
        return self.weights


    def add_final_node(self):
        problem = self.problem
        newUnit = Unit('0', 'FINAL')
        problem.units.append(newUnit)
        for unit in problem.units:
            cable = Cable(unit, newUnit)
            problem.cables.append(cable)
        return problem


    def init_weights(self):
        self.weights = {}
        for node in self.problem.units:
            self.weights[node.id] = {}
            # get all linked Nodes
            for node2 in map(lambda x: x.get_other_unit(node),node.cables):
                if node.tag == 'FINAL' and node2.tag != 'FINAL':
                    self.weights[node.id][node2.id] = 0
                elif node2.tag == 'FINAL' and node.tag != 'FINAL':
                    self.weights[node.id][node2.id] = 1
                else:
                    self.weights[node.id][node2.id] = 10
        return 0


    def remove_finals(self, path: Path):
        path.unit = [unit for unit in path.unit if unit.tag != 'FINAL']
        path.cable = path.cable[:len(path.unit)-1]


    def __str__(self):
        return "NSWGE"
