from random import choices

from problems.Solution import Solution
from .NSA import NSA


class NSGA2(NSA):
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
        self.create_solutions(self.nSolutions)
        self.ranking()
        ## UPDATE WEIGHTS
        self.update_weights(ratio=.5, maximum=25)
        #=======#
        #  OLD  #
        #=======#
 
        # self.crowding_distance()
        # self.selection(ratioKept)
        # self.offspring_generation()

    def post_optimize(self):
        self.normalize_weights()
        self.remove_final_node()
        self.ranking()

    def add_final_node(self):
        self.problem.add_final_node()

    def remove_final_node(self):
        self.problem.remove_final_node()

    def init_weights(self):
        self.weights = []
        for _ in range(len(self.problem.task)):
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

    def create_solutions(self, nSolutions):
        solutions = []
        for i in range(len(self.problem.task)):
            solutions.append(self.problem.populate(nSolutions, self.weights[i]))
        self.solutions = list(zip(*solutions))
       

    def __str__(self):
        return "NSWGE"
