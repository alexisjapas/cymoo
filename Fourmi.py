from Network import Network
from Network.Unit import Unit
from Network.Cable import Cable
from Network.Path import Path
from math import ceil
from Task import Task
from copy import deepcopy

class Fourmi():
    def __init__(self, problem : Network) -> None:
        self.problem = problem
        self.solutions = []
        

    def optimize(self, nPath: int, pathDepth: int, task: Task): 
        self.addFinalNode()
        self.initWeights()
        for _ in range(nPath):
            path = self.problem.generatePath(pathDepth, self.weights)
            self.removeFinals(path)
            self.solutions.append(path.toSolution(task))

        self.ranking()
        self.updateWeights()


        return self.solutions

    def updateWeights(self, ratio):
        assert ratio>.5, "Ratio can't be above .5"
        rankDistribution = list(range(1,self.max_rank+1))
        evalPoint= min(5, ceil(len(rankDistribution)*ratio))
        positivDistrib = rankDistribution[:evalPoint]
        negativDistrib = rankDistribution[len(rankDistribution)-evalPoint:]
        positive = list(zip(positivDistrib, positivDistrib[::-1]))
        negative = list(zip(negativDistrib, [-i for i in positivDistrib]))
        positive = {i:j for i,j in positive}
        negative = {i:j for i,j in negative}
        
        
        
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
                else:
                    self.weights[node.id][node2.id] = 1
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