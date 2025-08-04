class Aristas:
    def __init__(self):
        self.aristas = []

    def setArista(self, lineItem):
        self.aristas.append(lineItem)

    def allAristas(self):
        return self.aristas

    def removeArista(self, lineItem):
        if lineItem in self.aristas:
            self.aristas.remove(lineItem)
