from abc import ABC, abstractmethod


class Problem(ABC):
    def __init__(self):pass

    @abstractmethod
    def pre_optimize(self):pass

    @abstractmethod
    def post_optimize(self):pass

    @abstractmethod
    def populate(self):pass
