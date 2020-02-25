import random

class Genome:

    fitness = 0.0
    bits = []

    def __init__(self, numBits = 0):
        self.fitness = 0.0
        if (numBits == 0):
            self.bits = []
        else:
            self.bits = []#np.random.random_integers(0, 1 + 1, numBits)
            for _ in range(numBits):
                self.bits.append(random.randint(0, 1))
