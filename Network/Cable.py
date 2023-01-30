class Cable:
    pass

from Unit import Unit

class Cable:
    def __init__(self,
    speed: float, # Speed of the flow of information ~ Meters / Second
    flow: float, # Number of second needed to transfer one Bit
    deviceFrom: Unit, # Unit From which the cable start
    deviceTo: Unit, # Unit From which the cable end
    distance: float = None # Distance between the two Units ~ Meters, If None, is calculated
    ) -> None:
        self.speed = speed;
        self.flow = flow;
        self.deviceFrom = deviceFrom;
        self.deviceTo = deviceTo;
        if distance:
            self.distance = distance;
        else:
            self.distance = deviceFrom.distanceWithOtherUnit(deviceTo)