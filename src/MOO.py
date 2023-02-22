import random
import imageio
import io
import numpy
from dotenv import load_dotenv
from PIL import Image
from tqdm import tqdm
from time import sleep
from matplotlib import pyplot as plt


load_dotenv()


class MOO:
    """
    TODO DOCSTRING
    """
    def __init__(self, problem):
        self.problem = problem

    def optimize(self, optimizer, nSolutions, nIterations, save_dir="imgs", seed=None, **kwargs):
        """
        Loop to uses the chosen optimizer to optimize solutions. At each iteration, create a matplotlib scatterplot. Uses plots at the end to generate a GIF.
        A seed can be used for reproductivity.
        """
        def _create_frame(t, pareto: bool, maxX, maxY, maxZ):
            fig = plt.figure()
            ax = fig.add_subplot(projection="3d")

            if pareto:
                maxX, maxY, maxZ = tuple(max([sol.solution[i] for sol in self.optimizer.pareto_solutions]) for i in range(len(self.problem.optimDirections)))
                values = tuple([sol.solution[i] for sol in self.optimizer.pareto_solutions] for i in range(len(self.problem.optimDirections)))
                ax.scatter(*values)
                plt.title(f'{self.optimizer} - Pareto optimums: {len(values[0])} values\nIteration n°{t}', fontsize=12)
            else:
                ax.scatter(*tuple([sol.solution[i] for sol in self.optimizer.solutions] for i in range(len(self.problem.optimDirections))))
                plt.title(f'{self.optimizer} - All solutions\nIteration n°{t}', fontsize=12)

            ax.set_xlim3d(0, maxX)
            ax.set_ylim3d(0, maxY)
            ax.set_zlim3d(0, maxZ)
            ax.set_xlabel("Processing time (s)")
            ax.set_ylabel("Cost (€)")
            ax.set_zlabel("Pollution (gCO2)")

            imgBuf = io.BytesIO()
            plt.savefig(imgBuf, transparent=False, facecolor='white')
            im = Image.open(imgBuf)
            im = numpy.array(im)
            imgBuf.close()
            plt.close()
            return im

        # set random seed for reproductivity
        if seed is not None:
            random.seed(seed)
        else:
            random.seed()

        # reset and/or prepare problem for optimization
        self.problem.pre_optimize()

        # set optimizer
        self.optimizer = optimizer(self.problem, nSolutions)

        # optimisation
        print(f"Optimizing with {self.optimizer}...")
        maxX, maxY, maxZ = tuple(max([sol.solution[i] for sol in self.optimizer.solutions]) for i in range(len(self.problem.optimDirections)))
        frames = []
        pareto_frames = []
        for n in tqdm(range(1, nIterations+1)):
            frames.append(_create_frame(n, False, maxX, maxY, maxZ))
            pareto_frames.append(_create_frame(n, True, maxX, maxY, maxZ))
            self.optimizer.optimize(**kwargs)
            self.optimizer.get_pareto()

        # post optimization (NSWGE norm)
        self.optimizer.post_optimize()

        # Create GIF with frames of each iteration
        imageio.mimsave(f"{save_dir}/{self.optimizer}.gif", frames, fps=1)
        imageio.mimsave(f"{save_dir}/{self.optimizer}_pareto.gif", pareto_frames, fps=1)

        # Display final solutions and count
        print("Displaying pareto solutions...")
        for sol in self.optimizer.pareto_solutions:
            print(sol.parameters[0])
            sleep(0.2)
        print()

        return (self.optimizer.pareto_solutions, f"{optimizer}")

    @staticmethod
    def relative_efficiency(X, Y, optimDirections, verbose=False):
        """
        Computes the number of solutions of X undominated by Y solutions. Verbose function enable to print results.
        """
        undominatedValues = X[0].copy()
        for x in X[0]:
            for y in Y[0]:
                if all([y.solution[i] < x.solution[i] if opti_dir == 'min' else y.solution[i] > x.solution[i] for i, opti_dir in enumerate(optimDirections)]):
                    while x in undominatedValues:
                        undominatedValues.remove(x)
                    break

        if verbose:
            print(f"Relative efficiency: {round(len(undominatedValues) / len(X[0]) * 100)} % of {X[1]} solutions are undominated by {Y[1]} solutions")

        return len(undominatedValues) / len(X[0])
