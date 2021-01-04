import numpy as np
import math
import random as rand

## --------- CONSTANTS ---------

## Number of inputs in the network
INPUTS = 16
## Number of outputs in the network
OUTPUTS = 2

## Population size in each generation
POPULATION = 300
## Maximum number of nodes in a network, with outputs taking up indices m = MAX_NODES and m+1.
MAX_NODES = 10000

## Quantities used to determine whether two individuals are of the same species
DELTA_DISJOINT = 2
DELTA_WEIGHTS = 0.4
DELTA_THRESHOLD = 1.0

STALE_SPECIES = 15

## Mutation chance constants
MUTATE_CONNECTIONS_CHANCE = 0.25
PERTURB_CHANCE = 0.90
CROSSOVER_CHANCE = 0.75
LINK_MUTATE_CHANCE = 2.0
NODE_MUTATE_CHANCE = 0.5
BIAS_MUTATION_CHANCE = 0.4
STEP_SIZE = 0.1
DISABLE_MUTATION_CHANCE = 0.4
ENABLE_MUTATION_CHANCE = 0.2


## --------- CLASSES ---------

class Generation:
    def __init__(self):
        self.species = np.array([])             # list of species in the given generation
        self.species = self.species.astype(int)
        self.gen = 0                            # the generation number
        self.innovation = OUTPUTS               # current innovation
        self.currentSpecies = 0                 # selected species
        self.currentIndividual = 0              # selected individual
        self.currentFrame = 0                   # current iteration in-game
        self.maxScore = 0                       # max score in generation

    @staticmethod
    def initializeGeneration(generation):
        generation = Generation()
        for i in range(POPULATION):
            generation.addToSpecies(Individual.basicIndividual())
        ## TODO: intialize run ##

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)
    
    def newInnovation(self):
        self.innovation = self.innovation + 1
        return self.innovation

    def rankGlobally(self):
        globl = []
        for species in self.species:
            for individual in species.individuals:
                globl.insert(individual)
        globl = sorted(globl, key = lambda x : x.fitness)
        for i in range(globl.count):
            globl[i].globalRank = i

    def totalAverageFitness(self):
        total = 0
        for species in self.species:
            total = total + species.averageFitness
        return total

    def cullSpecies(self, cutToOne):
        for species in self.species:
            l = list(species.individuals)
            l = sorted(l, key = lambda x: x.fitness)
            species.individuals = np.array(l)
            remaining = math.ceil(species.individuals.size / 2)
            if cutToOne: remaining = 1
            while species.individuals.size > remaining: np.delete(species.individuals, -1)

    def removeStaleSpecies(self):
        survived = []
        for species in self.species:
            l = list(species.individuals)
            l = sorted(l, key = lambda x : x.fitness)
            species.individuals = np.array(l)
            if species.individuals[0].fitness > species.topFitness:
                species.topFitness = species.individuals[0].fitness
                species.staleness = 0
            else: species.staleness = species.staleness + 1
            if species.staleness < STALE_SPECIES or species.topFitness >= self.maxFitness: survived.insert(species)
        self.species = np.array(survived)

    def removeWeakSpecies(self):
        survived = []
        sum = self.totalAverageFitness()
        for species in self.species:
            breed = math.floor(species.averageFitness / sum * POPULATION)
            if breed >= 1: survived.insert(species)
        self.species = np.array(survived)

    def addToSpecies(self, individualChild):
        foundSpecies = False
        for species in self.species:
            if not foundSpecies and Individual.sameSpecies(individualChild, species.genomes[1]):
                species.individuals.insert(individualChild)
                foundSpecies = True
        if not foundSpecies:
            childSpecies = Species()
            childSpecies.individuals.insert(individualChild)
            self.species.insert(childSpecies)

    def newGeneration(self):
        self.cullSpecies(False)
        self.rankGlobally()
        self.removeStaleSpecies()
        self.rankGlobally()
        for species in self.species(): species.calculateAverageFitness()
        self.removeWeakSpecies()
        sum = self.totalAverageFitness()
        children = []
        for species in self.species():
            breed = math.floor(species.averageFitness / sum * POPULATION) - 1
            for i in range(breed):
                children.insert(species.breedChildren())
        self.cullSpecies(True)
        while children.count + self.species.size < POPULATION:
            species = self.species[rand.randint(0, self.species.size - 1)]
            children.insert(species.breedChild())
        for child in children: self.addToSpecies(child)
        self.generation = self.generation + 1
        ## TODO: SAVE TO FILE ##

    def evaluteCurrent(self):
        species = self.species[self.currentSpecies]
        individual = species.individuals[self.currentIndividual]
        inputs = [] ## TODO: get inputs from game ##
        ## TODO: write code to handle output controls to game ##

    def nextIndividual(self):
        self.currentIndividual = self.currentIndividual + 1
        if self.currentIndividual >= self.species[self.currentSpecies].individuals.size:
            self.currentIndividual = 0
            self.currentSpecies = self.currentSpecies + 1
            if self.currentSpecies >= self.currentSpecies.size:
                self.newGeneration()
                self.currentSpecies = 1

    def fitnessAlreadyMeasured(self):
        species = self.species[self.currentSpecies]
        individual = species.individuals[self.currentIndividual]
        return individual.fitness != 0
class Species:
    def __init__(self):
        self.topScore = 0                       # top score in species
        self.staleness = 0                      # measure of no improvement
        self.individuals = np.array([])         # list of individuals belonging to this species
        self.averageScore = 0                   # average score

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)
    
    def calculateAverageFitness(self):
        total = 0
        for individual in self.individuals:
            total = total + individual.globalRank
        self.averageFitness = total / self.individuals.size
    
    def breedChild(self):
        child = None
        if rand.random < CROSSOVER_CHANCE:
            i1 = self.individuals[rand.randint(0, self.individuals.size - 1)]
            i2 = self.individuals[rand.randint(0, self.individuals.size - 1)]
            child = Individual.crossover(i1, i2)
        else:
            g = self.individuals[rand.randint(0, self.individuals.size - 1)]
            child = g.clone()
        child.mutate()
        return child


class Individual:
    def __init__(self):
        self.genes = np.array([])               # list of genes of the individual
        self.score = 0                          # score
        self.network = None                     # network of the individual
        self.maxneuron = 0                      # ???
        self.globalRank = 0                     # global rank
        self.mutationRates = {}                 # hashtable of mutation rates
        self.mutationRates["connections"] = MUTATE_CONNECTIONS_CHANCE
        self.mutationRates["link"] = LINK_MUTATE_CHANCE
        self.mutationRates["bias"] = BIAS_MUTATION_CHANCE
        self.mutationRates["node"] = NODE_MUTATE_CHANCE
        self.mutationRates["enable"] = ENABLE_MUTATION_CHANCE
        self.mutationRates["disable"] = DISABLE_MUTATION_CHANCE
        self.mutationRates["step"] = STEP_SIZE
    
    @staticmethod
    def basicIndividual():
        individual = Individual()
        individual.maxneuron = INPUTS
        individual.mutate()
        return individual()

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def clone(self):
        """ Returns a clone of itself. """
        copy = Individual()
        copy.genes = self.genes
        copy.score = self.score
        copy.network = self.network
        copy.maxneuron = self.maxneuron
        copy.globalRank = self.globalRank
        copy.mutationRates = self.mutationRates
        return copy
    
    def randomNeuron(self, notInput):
        """ Returns a random neuron in self.genes. If notInput is true, it returns a non-input. """
        neuronBools = []
        if not notInput:
            for i in range(INPUTS):
                neuronBools[i] = True
        for i in range(OUTPUTS):
            neuronBools[MAX_NODES + i] = True
        for gene in self.genes:
            if not notInput:
                neuronBools[gene.into] = True
                neuronBools[gene.out] = True
            else:
                if gene.into > INPUTS:
                    neuronBools[gene.into] = True
                    neuronBools[gene.out] = True
        count = (neuronBools == True).size
        n = rand.randint(0, count - 1)
        for key in neuronBools:
            if n == 0: return key
            n = n - 1
        return 0
    
    def containsLink(self, linkGene):
        """ Returns true if self.genes contains a gene with the same "in"/"out"-neurons as linkGene """
        for gene in self.genes:
            if gene.into == linkGene.into and gene.out == linkGene.out:
                return True

    def pointMutate(self):
        """ Mutate weights of each gene """
        step = self.mutationRates["step"]
        for gene in self.genes:
            if rand.random() < PERTURB_CHANCE:
                gene.weight = rand.random() * step * 2 - step
            else:
                gene.weight = rand.random() * 4 - 2

    def linkMutate(self, forceBias, generation):
        """ Adds link between two random neurons. REQUIRES: generation must exist """
        n1 = self.randomNeuron(False)   # Could be input
        n2 = self.randomNeuron(True)    # Not input
        newLinkGene = Gene()
        newLinkGene.into = n1
        newLinkGene.out = n2
        if forceBias: newLinkGene.into = INPUTS
        if self.containsLink(newLinkGene): return
        newLinkGene.innovation = generation.newInnovation()
        newLinkGene.weight = rand.random() * 4 - 2
        self.genes.insert(newLinkGene)

    def nodeMutate(self, generation):
        """ Adds neuron between gene """
        if self.genes.size == 0: return
        self.maxneuron = self.maxneuron + 1
        gene = self.genes[rand.randint(1,self.genes.size)]
        if not gene.enabled: return
        gene.enabled = False
        gene1 = gene.clone()
        gene1.out = self.maxneuron
        gene1.weight = 1.0
        gene1.innovation = generation.newInnovation()
        gene1.enabled = True
        self.genes.insert(gene1)
        gene2 = gene.clone()
        gene2.into = self.maxneuron
        gene2.innovation = generation.newInnovation()
        gene2.enabled = True
        self.genes.insert(gene2)
    
    def enableDisableMutate(self, enable):
        """ Enable or disable a random gene """
        geneCandidates = []
        for gene in self.genes:
            if gene.enabled != enable:
                geneCandidates.insert(gene)
        if geneCandidates.count == 0: return
        gene = geneCandidates[rand.randint(0, geneCandidates.count - 1)]
        gene.enabled = not gene.enabled

    def mutate(self, generation):
        for mutation in self.mutationRates:
            if rand.randint(1,2) == 1: self.mutationRates[mutation] = 0.95 * self.mutationRates[mutation]
            else: self.mutationRates[mutation] = 1.05 * self.mutationRates[mutation]
        if rand.random < self.mutationRates["connections"]: self.pointMutate
        p = self.mutationRates["link"]
        while p > 0:
            if rand.random() < p: self.linkMutate(False, generation)
            p = p - 1
        p = self.mutationRates["bias"]
        while p > 0:
            if rand.random() < p: self.linkMutate(True, generation)
            p = p - 1
        p = self.mutationRates["node"]
        while p > 0:
            if rand.random() < p: self.nodeMutate(generation)
            p = p - 1
        p = self.mutationRates["enable"]
        while p > 0:
            if rand.random() < p: self.enableDisableMutate(True)
            p = p - 1
        p = self.mutationRates["disable"]
        while p > 0:
            if rand.random() < p: self.enableDisableMutate(False)
            p = p - 1

    @staticmethod
    def crossover(i1, i2):
        if i2.fitness > i1.fitness:
            temp = i1
            i1 = i2
            i2 = temp
        child = Individual()
        innovations2 = np.array([])
        for gene in i2.genes:
            innovations2[gene.innovation] = gene
        for gene1 in i1.genes:
            gene2 = innovations2[gene1.innovation]
            if gene2 is not None and rand.random > 0.5 and gene2.enabled:
                child.genes.insert(gene2.clone())
            else:
                child.genes.insert(gene1.clone())
        child.maxneuron = max(i1.maxneuron, i2.maxneuron)
        for mutation in i1.mutationRates:
            child.mutationRates[mutation] = i1.mutationRates[mutation]
        return child

    @staticmethod
    def disjoint(i1, i2):
        inn1 = []
        for gene in i1.genes:
            inn1[gene.innovation] = True
        inn2 = []
        for gene in i2.genes:
            inn2[gene.innovation] = True
        disjointGenes = 0
        for gene in i1.genes:
            if not i2[gene.innovation]: disjointGenes = disjointGenes + 1
        for gene in i2.genes:
            if not i1[gene.innovation]: disjointGenes = disjointGenes + 1
        return disjointGenes / max(i1.genes.size, i2.genes.size)


    @staticmethod
    def weights(i1, i2):
        inn2 = []
        for gene in i2.genes:
            i2[gene.innovation] = gene
        sum = 0
        coincident = 0
        for gene in i1.genes:
            if i2[gene.innovation] is not None:
                gene2 = i2[gene.innovation]
                sum = sum + abs(gene.weight - gene2.weight)
                coincident = coincident + 1
        return sum / coincident


    @staticmethod
    def sameSpecies(i1, i2):
        dd = DELTA_DISJOINT * Individual.disjoint(i1, i2)
        dw = DELTA_WEIGHTS * Individual.weights(i1, i2)
        return dw + dd < DELTA_THRESHOLD


class Gene():
    def __init__(self):
        self.into = 0           # the index of the neuron going into the gene
        self.out = 0            # the index of the neuron the gene goes to
        self.weight = 0.0       # the weight of the gene
        self.enabled = True     # whether the gene is enabled
        self.innovation = 0     # innovation number associated with the gene
    
    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def clone(self):
        copy = Gene()
        copy.into = self.into
        copy.out = self.out
        copy.weight = self.weight
        copy.enabled = self.enabled
        copy.innovation = self.innovation
        return copy


class Neuron():
    def __init__(self):
        self.incoming = np.array([])    # list of incoming genes
        self.value = 0.0                # value of neuron

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)


class Network():
    def __init__(self, individual):
        self.neurons = np.array([])
        for i in range(INPUTS):
            self.neurons[i] = Neuron()
        for i in range(OUTPUTS):
            self.neurons[MAX_NODES + i] = Neuron()
        l = list(individual.genes)
        l = sorted(l, key = lambda x : x.out)
        individual.genes = np.array(l)
        for gene in individual.genes:
            if gene.enabled:
                if self.neurons[gene.out] == None:
                    self.neurons[gene.out] = Neuron()
                neuron = self.neurons[gene.out]
                neuron.incoming.insert(gene)
                if self.neurons[gene.into] == None:
                    self.neurons[gene.into] = Neuron

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def evaluate(self, inputs):
        for i in range(INPUTS):
            self.neurons[i].value = normalize(inputs[i])
            
        for neuron in self.neurons:
            sum = 0
            for incomingGene in neuron.incoming:
                incomingNeuron = self.neurons[incomingGene.into]
                sum = sum + incomingGene.weight * incomingNeuron.value
            if neuron.incoming.size  > 0:
                neuron.value = sigmoid(sum)
        outputs = np.array([False, False])
        for i in range(OUTPUTS):
            outputs[i] = self.neurons[MAX_NODES + i].value > 0
        return outputs


def normalize(x):
    return math.log2(x) / 16

def sigmoid(x):
    return 2 / (1 + math.exp(-4.9 * x)) - 1

