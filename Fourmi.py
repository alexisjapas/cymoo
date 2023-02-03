import time
from copy import deepcopy
from math import ceil

from Network import Network
from Network.Unit import Unit
from Network.Cable import Cable
from Network.Path import Path
from Task import Task


class Fourmi():
    """
    TODO docstring
    """
    def __init__(self, problem: Network) -> None:
        self.problem = problem
        self.solutions = []


    def optimize(self, nIter: int, nPath: int, pathDepth: int, task: Task):
        self.add_final_node()
        self.init_weights()
        self.solutions = []
        for i in range(nIter):
            start = time.time()
            self.solutions.clear()
            for _ in range(nPath):
                path = self.problem.generatePath(pathDepth, self.weights)
                self.removeFinals(path)
                self.solutions.append(path.toSolution(task))

            self.ranking()
            self.update_weights(ratio=.5, maximum=25)
            temps = time.time() - start
            print(f'Iter {i}/{nIter} : {temps} secondes')
        self.normalize_weights()
        return self.weights


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
            for node2 in map(lambda x: x.getOtherUnit(node),node.cables):
                if node.tag == 'FINAL' and node2.tag != 'FINAL':
                    self.weights[node.id][node2.id] = 0
                elif node2.tag == 'FINAL' and node.tag != 'FINAL':
                    self.weights[node.id][node2.id] = 1
                else:
                    self.weights[node.id][node2.id] = 10
        return 0


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
                    if all([solBis.solution[i] < sol.solution[i] if optiDir == 'min' else solBis.solution[i] > sol.solution[i] for i, optiDir in enumerate(self.problem.optim_directions)]):
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


    def removeFinals(self, path: Path):
        path.unit = [unit for unit in path.unit if unit.tag != 'FINAL']
        path.cable = path.cable[:len(path.unit)-1]
