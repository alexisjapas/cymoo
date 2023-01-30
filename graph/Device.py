from .Cable import Cable
import math

class Device:
    def __init__(self, id, puissance, position, debitTraitement, pollution, cout ) -> None:
        self.id = id
        self.puissance = puissance # Puissance de traitement de la tâche, instruction/secondes.
        self.position = position # Position du serveur sur la grille.
        self.debitTraitement = debitTraitement # Debit de passage des données, secondes/bit
        self.pollution = pollution # Pollution par secondes de run, CO_2/secondes
        self.cout = cout # Cout par secondes d'utilisation, $/secondes
        self.cables = []
        pass

    def connect(self, cable):
        self.cables.append(cable)
        pass

    def distanceWith(self, device):
        p1 = self.position
        p2 = device.position
        if(len(p1) != len(p2)):
            print('LOG DIFFERENT DISTANCE DISTANCE WIDTH')
            return 0
        distance = 0
        for couple in zip(p1,p2):
            distance += pow(couple[0]-couple[1], 2)
        return math.sqrt(distance)


    def __str__(self) -> str:
        return f'id: {self.id}, puissance: {self.puissance}, position: {self.position}'