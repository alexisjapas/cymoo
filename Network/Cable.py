class Cable:
    pass

from .Unit import Unit

class Cable:
    def __init__(self, frm: Unit, to: Unit, **kwargs) -> None:
        self.frm = frm
        self.to = to
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.frm.connect(self)
        self.to.connect(self)

    def getOtherUnit(self, unit: Unit):
        if unit == self.frm:
            return self.to
        elif unit == self.to:
            return self.frm
        else:
            raise ValueError("The unit is not part of this cable")

    def toNeo4J(self):
        dictionary = {key: value for key, value in self.__dict__.items() if key != 'frm' and key != 'to'}
        expression = f'(id{self.frm.id})-[:CABLE {dictionary}]->(id{self.to.id})'
        return expression.replace('\'', '')

    def __str__(self) -> str:
        expression = f'Cable: ({self.frm.id})-({self.to.id}), '
        for key, value in self.__dict__.items():
            if key != 'frm' and key != 'to':
                expression += f'{key}: {value}, '
        return expression