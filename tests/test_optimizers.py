import importlib
import os
import sys
import pytest


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def get_optimizer_modules():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    optimizers_dir = os.path.join(base_dir, 'src', 'optimizers')
    optimizer_files = [
        f[:-3] for f in os.listdir(optimizers_dir) if f.endswith(".py") and not f.startswith("__")
    ]
    return optimizer_files


@pytest.mark.parametrize("module_name", get_optimizer_modules())
def test_integrates_required_classes(module_name):
    module = importlib.import_module(f"src.optimizers.{module_name}")

    base_module = importlib.import_module("src.optimizers.Optimizer")
    Optimizer = base_module.Optimizer
    OptimizerProblemMixin = base_module.OptimizerProblemMixin
    OptimizerSolutionMixin = base_module.OptimizerSolutionMixin

    classes = [cls for cls in module.__dict__.values() if isinstance(cls, type)]

    has_optimizer = any(issubclass(cls, Optimizer) for cls in classes)
    has_problem_mixin = any(issubclass(cls, OptimizerProblemMixin) for cls in classes)
    has_solution_mixin = any(issubclass(cls, OptimizerSolutionMixin) for cls in classes)

    error_message = []
    if not has_optimizer:
        error_message.append(f"{module_name} must have a class inheriting from the Optimizer class")
    if not has_problem_mixin:
        error_message.append(f"{module_name} must have a class inheriting from the OptimizerProblemMixin class")
    if not has_solution_mixin:
        error_message.append(f"{module_name} must have a class inheriting from the OptimizerSolutionMixin class")

    assert has_optimizer and has_problem_mixin and has_solution_mixin, "; ".join(error_message)
