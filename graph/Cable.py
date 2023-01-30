
class Cable:
    def __init__(self, vitesse, debit, device1, device2) -> None:
        self.distance = device1.distanceWith(device2) # Distance entre les deux device, metre
        self.vitesse = vitesse #  Vitesse de transmission des donnése, metre/seconde
        self.debit = debit # Debit de transmission seconde/bit
        self.devices = (device1, device2)
        device1.connect(self)
        device2.connect(self)
        pass

    def __str__(self) -> str:
        return f'Cable Between {self.devices[0]} and {self.devices[1]},\n dist: {self.distance}'