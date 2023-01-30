from .Device import Device
from .Cable import Cable
import random
import uuid
class Network:
    def __init__(self, devices = [], cables = []) -> None:
        self.devices: list = devices
        self.cables: list = cables

    def generateSimpleStructure(self, nPersonalDevice: int, params: list):
        ## Vide le réseau actuel
        self.devices.clear()
        self.cables.clear()
        generatedDevice = []
        for _ in range(nPersonalDevice):
            id = str(uuid.uuid4()).replace('-','')
            puissance = params[0]['puissance']()
            position = params[0]['position']()
            debitTraitement = params[0]['debitTraitement']()
            pollution = params[0]['pollution']()
            cout = params[0]['cout']()
            device = Device(id, puissance, position, debitTraitement, pollution, cout)
            generatedDevice.append(device)
            self.devices.append(device)
            self.generateSimpleStructureNext(device, params[1:])
        
        for dev1 in generatedDevice:
            for dev2 in generatedDevice:
                if dev1 != dev2 and dev1.id < dev2.id:
                    vitesse = params[0]['vitesse']()
                    debit = params[0]['debit']()
                    newCable = Cable(vitesse, debit, dev1, dev2)
                    self.cables.append(newCable)

    def generateSimpleStructureNext(self, device: Device, params: list):
        if len(params) == 0:
            return 
        for _ in range(params[0]['nNextLayer']()):
            ## Créer Nouveau Device
            id = str(uuid.uuid4()).replace('-','')
            puissance = params[0]['puissance']()
            position = params[0]['position']()
            debitTraitement = params[0]['debitTraitement']()
            pollution = params[0]['pollution']()
            cout = params[0]['cout']()
            newDevice = Device(id, puissance, position, debitTraitement, pollution, cout)
            self.devices.append(newDevice)
            ## Crée Cable entre Device
            vitesse = params[0]['vitesse']()
            debit = params[0]['debit']()                        
            newCable = Cable(vitesse, debit, device, newDevice)
            self.cables.append(newCable)
            ## Relancer Fonction
            self.generateSimpleStructureNext(newDevice, params[1:])

    def uploadToNeo4J(self):
        query = 'CREATE'
        for device in self.devices:
            ## Structure Upload Device
            # 'CREATE (id:DEVICE {id:id, puissance:puissance, position:position, debitTraitement:debitTraitement, pollution:pollution, cout:cout})'
            locStr= '{'
            for i in range(len(device.position)):
                locStr+=' loc'+str(i)+': '+str(device.position[i])+','
            if locStr.endswith(','):
                locStr = locStr[:-1]
            locStr+='}'
            query += ' (id'+str(device.id)+':DEVICE {id:\''+str(device.id)+'\', puissance:'+str(device.puissance)+', debitTraitement:'+str(device.debitTraitement)+', pollution:'+str(device.pollution)+', cout:'+str(device.cout)+'})-[:LOCATION]->(:LOCATION '+locStr+'),'
        for cable in self.cables:
            ## Structure Upload Cable
            # 'CREATE (id1)-[:CABLE {vitesse: vitesse, debit: debit}]->(id2)'
            query += ' (id'+str(cable.devices[0].id)+')-[:CABLE {vitesse: '+str(cable.vitesse)+', debit: '+str(cable.debit)+'}]->(id'+str(cable.devices[1].id)+'),'
            query += ' (id'+str(cable.devices[1].id)+')-[:CABLE {vitesse: '+str(cable.vitesse)+', debit: '+str(cable.debit)+'}]->(id'+str(cable.devices[0].id)+'),'
        if query.endswith(','):
            query = query[:-1]
        return query

if __name__ == '__main__':
    reseau = Network();

    paramsLayerOne = {
        'puissance': lambda: 1,
        'position': lambda: (random.randint(-10,10),random.randint(-10,10)),
        'debitTraitement': lambda: 1,
        'pollution': lambda: 1,
        'cout': lambda: 1,
        'vitesse': lambda: 1,
        'debit': lambda: 1,
        'nNextLayer': lambda: 2
    }

    reseau.generateSimpleStructure(2, [paramsLayerOne, paramsLayerOne])

    for i in reseau.devices:
        print(i)
    for i in reseau.cables:
        print(i)

    