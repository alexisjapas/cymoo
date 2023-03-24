class Unit:
    pass


from .Cable import Cable


class Unit:
    """
    TODO DOCSTRING
    """

    def __init__(self, id: str, tag: str = "UNIT", **kwargs) -> None:
        self.id = id
        self.tag = tag
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.cables: list[Cable] = []

    def connect(self, cable: Cable):
        self.cables.append(cable)

    def to_Neo4j(self):
        dictionary = {key: value for key, value in self.__dict__.items() if key != "cables" and key != "tag"}
        repr = f"(id{self.id}:{self.tag}" + "{"
        for key, value in dictionary.items():
            repr += f'{key}: "{value}", '
        repr = repr[:-2]
        repr += "})"
        return repr

    def __str__(self) -> str:
        string = f"Unit: {self.id}, "
        for key, value in self.__dict__.items():
            if key != "id" and key != "cables":
                string += f"{key}: {value}, "
        return string

    def __repr__(self) -> str:
        return f"UNIT: {self.id[-5:]}, TAG: {self.tag} >>>"
