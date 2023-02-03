from Network import Network
from Network.Unit import Unit
from Network.Cable import Cable
from Network.Path import Path
from math import ceil
from Task import Task
from copy import deepcopy
import time

class Fourmi():
    def __init__(self, problem : Network) -> None:
        self.problem = problem
        self.solutions = []
        

    def optimize(self,nIter: int ,nPath: int, pathDepth: int, task: Task): 
        self.addFinalNode()
        self.initWeights()
        self.solutions = []
        for i in range(nIter):
            start = time.time()
            self.solutions.clear()
            for _ in range(nPath):
                path = self.problem.generatePath(pathDepth, self.weights)
                self.removeFinals(path)
                self.solutions.append(path.toSolution(task))

            self.ranking()
            self.updateWeights(ratio=.5, maximum=25)
            temps = time.time() - start
            print(f'Iter {i}/{nIter} : {temps} secondes')
        self.normalizeWeights()
        return self.weights

    def normalizeWeights(self):
        for i in self.weights.keys():
            sumWeights = sum(self.weights[i].values())
            for j in self.weights[i].keys():
                if sumWeights != 0:
                    self.weights[i][j] /= sumWeights
                else:
                    self.weights[i][j] = 1/len(self.weights[i].keys())

    def updateWeights(self, ratio, maximum):
        assert ratio <= .5, "Ratio can't be above .5"
        rankDistribution = list(range(1,self.max_rank+1))
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

        def mean(iter):
            if iter == []:
                return 0
            sum = 0
            for i in iter:
                sum +=i
            return sum/len(iter)

        for key1 in self.weights.keys():
            for key2 in self.weights[key1].keys():
                self.weights[key1][key2] = max(0,self.weights[key1][key2][0] + round(mean(self.weights[key1][key2][1]),3))
        return self.weights
        
    def addFinalNode(self):
        problem = self.problem
        newUnit = Unit('0', 'FINAL')
        problem.units.append(newUnit)
        for unit in problem.units:
            cable = Cable(unit, newUnit)
            problem.cables.append(cable)
        return problem

    def initWeights(self):
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

    def removeFinals(self, path: Path):
        path.unit = [unit for unit in path.unit if unit.tag != 'FINAL']
        path.cable = path.cable[:len(path.unit)-1]