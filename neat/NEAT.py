from __future__ import annotations
import random
import math
import json
from types import SimpleNamespace
from typing import List
from typing import Dict
from typing import Tuple

path = 'neat/data/'

with open('neat/config.json', 'r') as f:
    config = json.load(f, object_hook=lambda d: SimpleNamespace(**d))


num_inputs = 0
num_outputs = 0


def init(number_inputs : int, number_outputs : int):
    global num_inputs, num_outputs
    num_inputs = number_inputs
    num_outputs = number_outputs


class Generation(object):
    def __init__(self):
        self.species : List[Species] = []
        self.gen : int = 0
        self.innovation : int = num_outputs
        self.currentSpecies : int = 0
        self.currentIndividual : int = 0
        self.currentFrame : int = 0
        self.maxFitness : int = 0
        self.name : str = "no_name"


    def createGeneration(self, name):
        self.name = name
        for i in range(config.population):
            individual = self.addToSpecies(Individual.basicIndividual(self))
            individual.network = Network(individual)        ## Not necessary


    def evaluateCurrent(self, inputs : List[float]) -> List[float]:
        species = self.species[self.currentSpecies]
        individual = species.individuals[self.currentIndividual]
        individual.network = Network(individual)
        return individual.network.evaluate(inputs)


    def nextGeneration(self):
        self.gen = self.gen + 1
        self.saveGeneration(self.name)
        self.cullSpecies(False)
        self.rankGlobally()
        self.removeStaleSpecies()
        self.rankGlobally()
        for species in self.species: species.calculateAverageFitness()
        self.removeWeakSpecies()
        sum = self.totalAverageFitness()
        children = []
        for species in self.species:
            breed = math.floor(species.averageFitness / sum * config.population) - 1
            for i in range(breed):
                children.append(species.breedChild(self))
        self.cullSpecies(True)
        while len(children) + len(self.species) < config.population:
            species = self.species[random.randint(0, len(self.species)  - 1)]
            children.append(species.breedChild(self))
        for child in children: self.addToSpecies(child)
    

    @staticmethod
    def loadGeneration(path : str) -> Generation:
        with open(path, 'r') as f:
            dict = json.load(f)
        return Generation.__hook(dict)


    @staticmethod
    def __hook(dict) -> Generation:
        g = Generation()
        g.__dict__ = dict
        for i in range(len(g.species)):
            act_species = Species()
            act_species.__dict__ = g.species[i]
            g.species[i] = act_species
            for j in range(len(act_species.individuals)):
                act_individual = Individual()
                act_individual.__dict__ = act_species.individuals[j]
                act_species.individuals[j] = act_individual
                for k in range(len(act_individual.genes)):
                    act_gene = Gene()
                    act_gene.__dict__ = act_individual.genes[k]
                    act_individual.genes[k] = act_gene
        return g
            

    def saveGeneration(self, creatureName : str):
        genNum = self.gen
        for species in self.species:
            for indiv in species.individuals:
                indiv.network = None
        with open(path + creatureName + "/" + str(genNum) + ".neat", 'w') as f:
            f.write(json.dumps(self, default=lambda o: o.__dict__))
            print("Saved generation " + str(self.gen))


    def nextIndividual(self):
        self.currentIndividual = self.currentIndividual + 1
        if self.currentIndividual >= len(self.species[self.currentSpecies].individuals):
            self.currentIndividual = 0
            self.currentSpecies = self.currentSpecies + 1
            if self.currentSpecies >= len(self.species):
                self.currentSpecies = 0
                self.nextGeneration()


    def newInnovation(self):
        self.innovation = self.innovation + 1
        return self.innovation


    def rankGlobally(self):
        globl : List[Individual] = []
        for species in self.species:
            for individual in species.individuals:
                globl.append(individual)
        globl = sorted(globl, key = lambda x : x.fitness)
        for i in range(len(globl)):
            globl[i].globalRank = i


    def totalAverageFitness(self):
        total = 0
        for species in self.species:
            total = total + species.averageFitness
        return total


    def fitnessAlreadyMeasured(self):
        species = self.species[self.currentSpecies]
        individual = species.individuals[self.currentIndividual]
        return individual.fitness != 0


    def addToSpecies(self, individualChild : Individual) -> Individual:
        foundSpecies = False
        for species in self.species:
            if species.individuals == [] or (not foundSpecies and Individual.sameSpecies(individualChild, species.individuals[0])):
                species.individuals.append(individualChild)
                foundSpecies = True
        if not foundSpecies:
            childSpecies = Species()
            childSpecies.individuals.append(individualChild)
            self.species.append(childSpecies)
        return individualChild


    def cullSpecies(self, cutToOne : bool):
        for species in self.species:
            species.individuals = sorted(species.individuals, key = lambda x : x.fitness)
            remaining = math.ceil(len(species.individuals) / 2)
            if cutToOne : remaining = 1
            while len(species.individuals) > remaining: species.individuals.pop(0)


    def removeStaleSpecies(self):
        survived = []
        for species in self.species:
            species.individuals = sorted(species.individuals, key = lambda x : -x.fitness)
            if species.individuals[0].fitness > species.topFitness:
                species.topFitness = species.individuals[0].fitness
                species.staleness = 0
            else: species.staleness = species.staleness + 1
            if species.staleness < config.stale_species or species.topFitness >= self.maxFitness:
                survived.append(species)
        self.species = survived


    def removeWeakSpecies(self):
        survived = []
        sum = self.totalAverageFitness()
        for species in self.species:
            breed = math.floor(species.averageFitness / sum * config.population)
            if breed >= 1: survived.append(species)
        self.species = survived


    def getTopIndividual(self) -> Tuple(int, int):
        top_spec = 0
        top_ind = 0
        top_fit = 0
        for i in range(len(self.species)):
            for j in range(len(self.species[i].individuals)):
                if self.species[i].individuals[j].fitness > top_fit:
                    top_fit = self.species[i].individuals[j].fitness
                    top_spec = i
                    top_ind = j
        return (top_spec, top_ind)

class Species(object):
    def __init__(self):
        self.topFitness : int = 0
        self.staleness : int = 0
        self.individuals : List[Individual] = []
        self.averageFitness : float = 0.0
    

    def calculateAverageFitness(self):
        total = 0
        for individual in self.individuals:
            total = total + individual.globalRank
        self.averageFitness = total / len(self.individuals)


    def breedChild(self, generation : Generation):
        child = None
        if random.random() < config.chance.crossover_chance:
            i1 = self.individuals[random.randint(0, len(self.individuals) - 1)]
            i2 = self.individuals[random.randint(0, len(self.individuals) - 1)]
            child = Individual.crossover(i1, i2)
        else:
            g = self.individuals[random.randint(0, len(self.individuals) - 1)]
            child = g.clone()
        child.mutate(generation)
        return child


class Individual:
    def __init__(self):
        self.genes : List[Gene] = []
        self.fitness : int = 0
        self.network : Network = None
        self.maxNeuron : int = 0
        self.globalRank : int = 0
        self.mutationRates : Dict[str, int] = {}
        self.mutationRates["connections"]   = config.chance.mutate_connections_chance
        self.mutationRates["link"]          = config.chance.link_mutation_chance
        self.mutationRates["bias"]          = config.chance.bias_mutation_chance
        self.mutationRates["node"]          = config.chance.node_mutation_chance
        self.mutationRates["enable"]        = config.chance.enable_mutation_chance
        self.mutationRates["disable"]       = config.chance.disable_mutation_chance
        self.mutationRates["step"]          = config.stepsize
    

    @staticmethod
    def basicIndividual(generation: Generation):
        individual = Individual()
        individual.maxNeuron = num_inputs
        individual.mutate(generation)
        return individual
    

    def clone(self) -> Individual:
        copy = Individual()
        copy.genes = self.genes
        copy.fitness = self.fitness
        copy.network = self.network
        copy.maxNeuron = self.maxNeuron
        copy.globalRank = self.globalRank
        copy.mutationRates = self.mutationRates
        return copy


    def randomNeuron(self, notInput):
        neuronBools = {}
        if not notInput:
            for i in range(num_inputs):
                neuronBools[i] = True
        for i in range(num_outputs):
            neuronBools[config.max_nodes + i] = True
        for gene in self.genes:
            if not notInput:
                neuronBools[gene.into] = True
                neuronBools[gene.out] = True
            else:
                if gene.into > num_inputs:
                    neuronBools[gene.into] = True
                    neuronBools[gene.out] = True
        count = sum(map((True).__eq__, neuronBools.values()))
        if count < 1 : n = 0
        else: n = random.randint(0, count - 1)
        for key in neuronBools:
            if n == 0: return key
            n = n - 1
        return 0
    

    def containsLink(self, linkGene):
        for gene in self.genes:
            if gene.into == linkGene.into and gene.out == linkGene.out:
                return True
    

    def pointMutate(self):
        step = self.mutationRates["step"]
        for gene in self.genes:
            if random.random() < config.chance.perturb_chance:
                gene.weight = random.random() * step * 2 - step
            else:
                gene.weight = random.random() * 4 - 2
    

    def linkMutate(self, forceBias, generation : Generation):
        n1 = self.randomNeuron(False)
        n2 = self.randomNeuron(True)
        newLinkGene = Gene()
        newLinkGene.into = n1
        newLinkGene.out = n2
        if forceBias: newLinkGene.into = num_inputs
        if self.containsLink(newLinkGene): return
        newLinkGene.innovation = generation.newInnovation()
        newLinkGene.weight = random.random() * 4 - 2
        self.genes.append(newLinkGene)


    def nodeMutate(self, generation : Generation):
        if len(self.genes) == 0: return
        self.maxNeuron = self.maxNeuron + 1
        gene = self.genes[random.randint(0, len(self.genes) - 1)]
        if not gene.enabled: return
        gene.enabled = False
        gene1 = gene.clone()
        gene1.out = self.maxNeuron
        gene1.weight = 1.0
        gene1.innovation = generation.newInnovation()
        gene1.enabled = True
        self.genes.append(gene1)
        gene2 : Gene = gene.clone()
        gene2.into = self.maxNeuron
        gene2.innovation = generation.newInnovation()
        gene2.enabled = True
        self.genes.append(gene2)


    def enableDisableMutate(self, enable : bool):
        geneCandidates = []
        for gene in self.genes:
            if gene.enabled != enable:
                geneCandidates.append(gene)
        if len(geneCandidates) == 0: return
        gene : Gene = geneCandidates[random.randint(0, len(geneCandidates) - 1)]
        gene.enabled = not gene.enabled


    def mutate(self, generation : Generation):
        for mutation in self.mutationRates:
            if random.randint(1, 2) == 1: self.mutationRates[mutation] = 0.95 * self.mutationRates[mutation]
            else: self.mutationRates[mutation] = 1.05 * self.mutationRates[mutation]
        if random.random() < self.mutationRates["connections"]: self.pointMutate
        p = self.mutationRates["link"]
        while p > 0:
            if random.random() < p: self.linkMutate(False, generation)
            p = p - 1
        p = self.mutationRates["bias"]
        while p > 0:
            if random.random() < p: self.linkMutate(True, generation)
            p = p - 1
        p = self.mutationRates["node"]
        while p > 0:
            if random.random() < p: self.nodeMutate(generation)
            p = p - 1
        p = self.mutationRates["enable"]
        while p > 0:
            if random.random() < p: self.enableDisableMutate(True)
            p = p - 1
        p = self.mutationRates["disable"]
        while p > 0:
            if random.random() < p: self.enableDisableMutate(False)
            p = p - 1
    

    @staticmethod
    def crossover(i1 : Individual, i2 : Individual):
        if i2.fitness > i1.fitness:
            temp = i1
            i1 = i2
            i2 = temp
        child = Individual()
        innovations2 = {}
        for gene in i2.genes:
            innovations2[gene.innovation] = gene
        for gene1 in i1.genes:
            if gene1.innovation in innovations2:
                gene2 :Gene = innovations2[gene1.innovation]
            else: gene2 = None
            if gene2 is not None and random.random() > 0.5 and gene2.enabled:
                child.genes.append(gene2.clone())
            else: child.genes.append(gene1.clone())
        child.maxNeuron = max(i1.maxNeuron, i2.maxNeuron)
        for mutation in i1.mutationRates:
            child.mutationRates[mutation] = i1.mutationRates[mutation]
        return child


    @staticmethod
    def disjoint(i1 : Individual, i2 : Individual):
        inn1 = {}
        for gene in i1.genes:
            inn1[gene.innovation] = True
        inn2 = {}
        for gene in i2.genes:
            inn2[gene.innovation] = True
        disjointGenes = 0
        for gene in i1.genes:
            if gene.innovation not in inn2: disjointGenes = disjointGenes + 1
        for gene in i2.genes:
            if gene.innovation not in inn1: disjointGenes = disjointGenes + 1
        return disjointGenes / max(len(i1.genes), len(i2.genes))


    @staticmethod
    def weights(i1 : Individual, i2 : Individual):
        inn2 = {}
        for gene in i2.genes:
            inn2[gene.innovation] = gene
        sum = 0
        coincident = 0
        for gene in i1.genes:
            if gene.innovation in inn2:
                gene2 : Gene = inn2[gene.innovation]
                sum = sum + abs(gene.weight - gene2.weight)
                coincident = coincident = 1
        return sum / coincident if coincident != 0 else -1


    @staticmethod
    def sameSpecies(i1 , i2):
        dd = config.delta.delta_disjoint * Individual.disjoint(i1, i2)
        dw = config.delta.delta_weights * Individual.weights(i1, i2)
        return dw + dd < config.delta.delta_threshold and dw + dd >= 0


class Gene():
    def __init__(self):
        self.into : int = 0
        self.out : int = 0
        self.weight : float = 0.0
        self.enabled : bool = True
        self.innovation : int = 0


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
        self.incoming : List[Gene] = []
        self.value : float = 0.0


class Network():
    def __init__(self, individual: Individual):
        self.neurons : Dict[int, Neuron] = {}
        for i in range(num_inputs):
            self.neurons[i] = Neuron()
        for i in range(num_outputs):
            self.neurons[config.max_nodes + i] = Neuron()
        individual.genes = sorted(individual.genes, key = lambda x : x.out)
        for gene in individual.genes:
            if gene.enabled:
                if gene.out not in self.neurons:
                    self.neurons[gene.out] = Neuron()
                neuron : Neuron = self.neurons[gene.out]
                neuron.incoming.append(gene)
                if gene.into not in self.neurons:
                    self.neurons[gene.into] = Neuron()
    

    def evaluate(self, inputs : List[float]) -> List[float]:
        for i in range(num_inputs):
            self.neurons[i].value = normalize(inputs[i])
        
        for i in self.neurons:
            sum = 0
            for incomingGene in self.neurons[i].incoming:
                incomingNeuron : Neuron = self.neurons[incomingGene.into]
                sum = sum + incomingGene.weight * incomingNeuron.value
            if len(self.neurons[i].incoming) > 0:
                self.neurons[i].value = sigmoid(sum)
        outputs = []
        for i in range(num_outputs):
            outputs.append(self.neurons[config.max_nodes + i].value)
        return outputs


def normalize(x):
    return (x % math.pi) / math.pi * 2 - 1


def sigmoid(x):
    return 2 / (1 + math.exp(-4.9 * x)) - 1


def run():
    g = Generation()
    init(7,7)
    g.createGeneration("human")
    s = g.species[g.currentSpecies]
    i = s.individuals[g.currentIndividual]
    i.network = Network(i)
    return g, s, i


if __name__ == "__main__":
    run()
