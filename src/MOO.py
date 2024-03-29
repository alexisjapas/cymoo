import inspect
import io
import random
from time import sleep

import imageio
import numpy
import ujson
from dotenv import load_dotenv
from matplotlib import pyplot as plt
from PIL import Image
from tqdm import tqdm

from .optimizers.Optimizer import OptimizerProblemMixin, OptimizerSolutionMixin
from .problems.Solution import Solution


load_dotenv()


class MOO:
    """
    TODO DOCSTRING
    """

    def __init__(self, problem):
        self.problem = problem

    def check_required_mixins(self, optimizer_class, problem_instance, solution_instance):
        problem_mixin = None
        solution_mixin = None

        module = inspect.getmodule(optimizer_class)
        for name, cls in inspect.getmembers(module, inspect.isclass):
            if issubclass(cls, OptimizerProblemMixin):
                problem_mixin = cls
            elif issubclass(cls, OptimizerSolutionMixin):
                solution_mixin = cls

        if problem_mixin is None or solution_mixin is None:
            raise ValueError(f"Unable to find mixin classes for {optimizer_class.__name__} optimizer.")

        if not isinstance(problem_instance, problem_mixin):
            raise TypeError(
                f"The problem instance must implement the {problem_mixin.__name__} mixin for \
                {optimizer_class.__name__} optimizer."
            )

        if not issubclass(solution_instance, solution_mixin):
            raise TypeError(
                f"The solution instance must implement the {solution_mixin.__name__} mixin for \
                {optimizer_class.__name__} optimizer."
            )

    def optimize(
            self,
            optimizer,
            nSolutions: int,
            nIterations: int,
            imDir: str = None,
            saveDir: str = None,
            export: bool = False,
            **kwargs,
        ):
        """
        Loop to uses the chosen optimizer to optimize solutions. At each iteration, create a matplotlib scatterplot.
        Uses plots at the end to generate a GIF.
        """

        # check that the problem and its solution implements correct mixins
        self.check_required_mixins(optimizer, self.problem, self.problem.get_solution_class())

        def _create_frame(t, pareto: bool, maxX, maxY, maxZ):
            fig = plt.figure()
            ax = fig.add_subplot(projection="3d")

            if pareto:
                maxX, maxY, maxZ = get_maxes()
                values = get_pareto_values()
                ax.scatter(*tuple(values.values()))
                plt.title(
                    f"{self.optimizer} - Pareto optimums: {len(list(values.values())[0])} values\nIteration n°{t}",
                    fontsize=12,
                )
            else:
                ax.scatter(
                    *tuple(
                        [sol.solution[dim] for sol in self.optimizer.solutions]
                        for dim in Solution.optimDirections.keys()
                    )
                )
                plt.title(
                    f"{self.optimizer} - All solutions\nIteration n°{t}",
                    fontsize=12,
                )

            ax.set_xlim3d(0, maxX)
            ax.set_ylim3d(0, maxY)
            ax.set_zlim3d(0, maxZ)
            ax.set_xlabel("Processing time (s)")
            ax.set_ylabel("Cost (€)")
            ax.set_zlabel("Pollution (gCO2)")

            imgBuf = io.BytesIO()
            plt.savefig(imgBuf, transparent=False, facecolor="white")
            im = Image.open(imgBuf)
            im = numpy.array(im)
            imgBuf.close()
            plt.close()
            return im

        def get_pareto_values():
            values = {
                dim: [sol.solution[dim] for sol in self.optimizer.pareto_solutions]
                for dim in Solution.optimDirections.keys()
            }
            return values

        def get_maxes():
            maxX, maxY, maxZ = tuple(
                max([sol.solution[dim] for sol in self.optimizer.pareto_solutions])
                for dim in Solution.optimDirections.keys()
            )
            return maxX, maxY, maxZ

        # reset and/or prepare problem for optimization
        self.problem.pre_optimize()

        # set optimizer
        self.optimizer = optimizer(self.problem, nSolutions)

        # optimization
        print(f"Optimizing with {self.optimizer}...")
        maxX, maxY, maxZ = tuple(
            max([sol.solution[dim] for sol in self.optimizer.solutions]) for dim in Solution.optimDirections.keys()
        )
        frames = []
        pareto_frames = []
        self.optimizer.pre_optimize()
        export_solutions = {}
        for n in tqdm(range(1, nIterations + 1)):
            frames.append(_create_frame(n, False, maxX, maxY, maxZ))
            pareto_frames.append(_create_frame(n, True, maxX, maxY, maxZ))
            for s in Solution.optimDirections.keys():
                if s not in export_solutions:
                    export_solutions[s] = {}
                export_solutions[s][n] = get_pareto_values()[s]
            self.optimizer.optimize(**kwargs)
            self.optimizer.get_pareto()

        # post optimization (NSWGE norm)
        self.optimizer.post_optimize()

        if export:
            with open(f"{saveDir}/{self.optimizer}.json", "w") as f:
                ujson.dump(export_solutions, f)

        # Create GIF with frames of each iteration
        if imDir is not None:
            imageio.mimsave(f"{imDir}/{self.optimizer}.gif", frames, fps=1)
            imageio.mimsave(f"{imDir}/{self.optimizer}_pareto.gif", pareto_frames, fps=1)

        # Display final solutions and count
        print("Displaying pareto solutions...")
        for sol in self.optimizer.pareto_solutions:
            print(sol.solution)
            sleep(0.2)
        print()

        return (self.optimizer.pareto_solutions, f"{optimizer}")

    @staticmethod
    def relative_efficiency(X, Y, optimDirections, verbose=False):
        """
        Computes the number of solutions of X undominated by Y solutions. Verbose function enable to print results.
        """


        def _relative_efficiency(X, Y, optimDirections):
            undominatedValues = X[0].copy()
            for x in X[0]:
                for y in Y[0]:
                    if all(
                        [
                            y.solution[dim] < x.solution[dim]

                            if optimDir == "min"

                            else y.solution[dim] > x.solution[dim]
                            for dim, optimDir in optimDirections.items()
                        ]
                    ):
                        while x in undominatedValues:
                            undominatedValues.remove(x)
                        break
            return undominatedValues

        undominatedX = _relative_efficiency(X, Y, optimDirections)
        scoreX = round(len(undominatedX) / len(X[0]))

        undominatedY = _relative_efficiency(Y, X, optimDirections)
        scoreY = round(len(undominatedY) / len(Y[0]))

        if verbose:
            print(f"Relative efficiency: {scoreX * 100} % of {X[1]} solutions are undominated by {Y[1]} solutions")
            print(f"Relative efficiency: {scoreY * 100} % of {Y[1]} solutions are undominated by {X[1]} solutions")

        return scoreX, scoreY
