import random
import wx

from gameMap import GameMap
from genome import Genome

class Bob:
    def __init__(self,
        crossoverRate,
	    mutationRate,
	    populationSize,
	    chromosomeLength,
	    geneLength,
	    entrance,
	    exit_,
	    matrix,
	    rows,
	    columns):
        self.crossoverRate = crossoverRate
        self.mutationRate = mutationRate
        self.populationSize = populationSize
        self.chromosomeLength = chromosomeLength
        self.geneLength = geneLength
        self.entrance = entrance
        self.exit_ = exit_
        self.matrix = matrix
        self.rows = rows
        self.columns = columns
        self.genomes = []
        self.bobMap = GameMap(matrix, entrance, exit_, rows, columns)
        self.bobBrain = GameMap(matrix, entrance, exit_, rows, columns)
        self.totalFitnessScore = 0.0
        self.generation = 0
        self.busy = False
        self.startMsg = 'Press Return to start a new run'
        self.stopMsg = 'Press Space to stop'

    def Mutate(self, bits):
        """ Iterates through each genome flipping the bits according to the mutation rate. """
        for i in range(len(bits)):
            # Do we flip this bit?
            if random.uniform(0, 1) < self.mutationRate:
                # Flip the bit.
                bits[i] = 1 - bits[i]
        return bits

    def Crossover(self, mom, dad, baby1, baby2):
        """ Takes 2 parent vectors, selects a midpoint and then swaps the ends of
        each genome creating 2 new genomes which are stored in baby1 and baby2. """
        # Just return parents as offspring dependent on the rate or if parents are the same.
        if random.uniform(0, 1) > self.crossoverRate or mom == dad:
            return mom, dad
        # Determine a crossover point.
        cp = random.randint(0, self.chromosomeLength - 1)

        # Swap the bits.
        baby1 = mom[0:cp]
        baby2 = dad[0:cp]

        baby1.extend(dad[cp:])
        baby2.extend(mom[cp:])

        return baby1, baby2

    def RouletteWheelSelection(self):
        """ Selects a member of the population by using roulette wheel selection as described in the text. """
        slice_ = random.uniform(0, 1) * self.totalFitnessScore
        cfTotal = 0.0
        selectedGenome = 0
        for i in range(self.populationSize):
            genome = self.genomes[i]
            cfTotal += genome.fitness
            if cfTotal > slice_:
                selectedGenome = i
                break
        return selectedGenome

    def updateFitnessScores(self):
        """ Updates the genomes fitness with the new fitness scores and calculates
        the highest fitness and the fittest member of the population. Also sets
        m_pFittestGenome to point to the fittest. If a solution has been found
        (fitness == 1 in this example) then the run is halted by setting busy
        to false. """
        self.fittestGenome = 0
        self.bestFitnessScore = 0
        self.totalFitnessScore = 0
        tempMemory = GameMap(self.matrix, self.entrance, self.exit_, self.rows, self.columns)
        # Update the fitness scores and keep a check on fittest so far.
        for i in range(self.populationSize):
            # Decode each genomes chromosome into a vector of directions.
            directions = self.Decode(self.genomes[i].bits)
            # Get its fitness score.
            fitness, tm = self.bobMap.TestRoute(directions, tempMemory)
            self.genomes[i].fitness = fitness
            # Update total.
            self.totalFitnessScore += self.genomes[i].fitness
            # If this is the fittest genome found so far, store results.
            if self.genomes[i].fitness > self.bestFitnessScore:
                self.bestFitnessScore = self.genomes[i].fitness
                self.fittestGenome = i
                self.bobBrain.memory = tm
                # Has Bob found the exit?
                if self.genomes[i].fitness == 1.0:
					# If so, stop the run.
                    self.busy = False
            tempMemory.resetMemory()

    def Decode(self, bits):
        """ Decodes a vector of bits into a vector of directions (ints).
        North = 0, South = 1, East = 2, West = 3 """
        directions = []
        # Step through the chromosome a gene at a time.
        for gene in range(0, len(bits), self.geneLength):
            # Get the gene at this position.
            thisGene = []
            for bit in range(0, self.geneLength):
                thisGene.append(bits[gene + bit])
            directions.append(self.BitToInt(thisGene))
        return directions

    def BitToInt(self, list_):
        """ Converts a vector of bits into decimal. Used by decode. """
        value = 0
        multiplier = 1
        for bit in range(len(list_) - 1, -1, -1):
            value += list_[bit] * multiplier
            multiplier *= 2
        return value

    def createInitialPopulation(self):
        """ Creates an initial population of random bit strings. """
        self.genomes = [Genome for i in range(self.populationSize)]
        for i in range(self.populationSize):
            self.genomes[i] = Genome(self.chromosomeLength)
        # Reset all variables.
        self.generation = 0
        self.fittestGenome = 0
        self.bestFitnessScore = 0
        self.totalFitnessScore = 0

    def run(self):
        """ This is the function that starts everything. It is mainly another windows
        message pump using PeekMessage instead of GetMessage so we can easily and
        dynamically make updates to the window while the GA is running.
        Basically, if there is no msg to be processed another Epoch is performed. """
        # The first thing we have to do is create a random population of genomes.
        self.createInitialPopulation()
        self.busy = True

    def render(self, mapWidth, mapHeight, canvas):
        """ Given a surface to render to this function renders the map and the best
        path if relevant. cxClient/cyClient are the dimensions of the client window. """
        self.mapWidth = mapWidth
        self.mapHeight = mapHeight
        self.canvas = canvas
        # Render the map.
        self.bobMap.render(mapWidth, mapHeight, self.canvas)

        # Render the best route.
        self.bobBrain.memoryRender(mapWidth, mapHeight, self.canvas)
        # # Render additional information.
        font = wx.Font(12, wx.SCRIPT, wx.NORMAL, wx.NORMAL)
        self.canvas.SetFont(font)
        self.canvas.DrawText('Generation: ' + str(self.generation), 10, 0)

        if not self.busy:
            canvas.DrawText(self.startMsg, (self.mapHeight - len(self.startMsg)) / 2, self.mapHeight - 20)
            self.bobMap.drawGates(self.mapWidth, self.mapHeight, canvas)
        else:
            canvas.DrawText(self.stopMsg, (self.mapHeight - len(self.startMsg)) / 2, self.mapHeight - 20)

    def epoch(self):
        """ This is the workhorse of the GA. It first updates the fitness scores of
        the population then creates a new population of genomes using the
        selection, crossover and mutation operators we have discussed. """
        self.updateFitnessScores()
        # Now to create a new population.
        newBabies = 0
        # Create some storage for the baby genomes.
        babyGenomes = []
        while newBabies < self.populationSize:
            # Select 2 parents.
            mom = self.genomes[self.RouletteWheelSelection()]
            dad = self.genomes[self.RouletteWheelSelection()]
            # Operator: crossover
            baby1 = Genome()
            baby2 = Genome()

            bits1, bits2 = self.Crossover(mom.bits, dad.bits, baby1.bits, baby2.bits)
            baby1.bits = bits1
            baby2.bits = bits2

            # Operator: mutate
            baby1.bits = self.Mutate(baby1.bits)
            baby2.bits = self.Mutate(baby2.bits)

			# Add to new population.
            babyGenomes.append(baby1)
            babyGenomes.append(baby2)

            newBabies += 2
        # Copy babies back into starter population.
        self.genomes = babyGenomes

        # Increment the generation counter.
        self.generation += 1

    def stop(self):
        self.busy = False
