import random
import re
import math
import os

# #####
# Below you can set all the values the way you want to optimise the algorithm, and insert problem instances
# #####

# The problem instance: distance matrix of a TSP
distanceMatrix = [[0, 12, 24, 2.5, 2, 3, 3, 7],
          [4, 0, 4, 2, 2.5, 2, 5, 8],
          [2, 10, 0, 5, 2, 2.5, 6, 9],
          [2.5, 2, 3, 0, 2, 2, 7, 10],
          [2, 2.5, 2, 13, 0, 12, 8, 1],
          [1, 2, 2.5, 2, 7, 0, 3, 51],
          [3, 4, 5, 6, 7, 8, 0, 4],
          [1, 2, 3, 4, 5, 6, 7, 0,]]

# Alternatively you can provide a file in .tsp-format. Set 'fromFile' to 'True' and provide the path to the file.
fromFile = False
fileName = os.path.dirname(os.path.abspath(__file__)) + "lu980.tsp.txt"

# Choose the size of the population and how many generations you want to run
populationSize = 100
nrOfGenerations = 10000

# The survival ratio determines the proportion of the population that survives.
# So it signifies our willingness to explore the potential of currently bad solutions. If this proportion is high
# we have a higher genetic diversity, but also less exploration per generation, so a slower development.
survivalRatio = 0.4

# Two types of reproduction are implemented: asexual (cloning) and sexual (cross-over),
# if reproductionTypeRatio is 1, only cloning is used,
# if it is 0, only sexual reproduction is used. Otherwise a proportion of both.
reproductionTypeRatio = 0.5

# If elite is true then only the best solutions survive, instead of also some random ones.
elite = False

# It prints the best solution of every generation
printValues = True

######
# Don't change code below here, unless you really want to :p
######

###############################################################################################


# This reads the problem instance from a file in .tsp-format if specified above.
file = None
TSPmap = None
cityList = None
if fromFile:
    file = open(fileName)
    line = None
    while line != "NODE_COORD_SECTION":
        line = file.readline().strip()
        print(line)

    cityList = []
    line = file.readline()
    while line != "":
        city = re.match(r'^\d*\s(\d+\.\d+)\s(\d+\.\d+).*$', line)
        if city is not None:
            cityList.append((float(city.group(1)), float(city.group(2))))
        line = file.readline()

    TSPmap = []
    for i in range(len(cityList)):
        distanceToI = []
        for j in range(len(cityList)):
            distanceToI.append(math.sqrt((abs(cityList[i][0] - cityList[j][0]))**2 + abs(cityList[i][1] - cityList[j][1])**2))

        TSPmap.append(distanceToI)
# Otherwise it uses the problem instance provided above in the distance matrix.
else:
    TSPmap = distanceMatrix

# The number of cities of the problem instance.
nrOfCities = len(TSPmap)

# Create a first random population of solutions
def make_population():
    population = []
    for i in range(populationSize):
        population.append(Individual())
    return population

# This function executes one generation of dying solutions and new solutions being born.
def generation(population):

    # Sort the solutions by merit (they've already calculated their own fitness upon being created)
    population.sort(key=lambda x: x.cost)

    # Determine the number of solutions allowed to survive from the given survival ratio
    # and how many room that leaves for children.
    survivors = int(len(population) * survivalRatio)
    nr_of_children = len(population) - survivors

    nr_of_cloned_children = int(nr_of_children*reproductionTypeRatio)
    
    # If the elite variable is set to false, we want to keep some solutions that don't look promising 
    # yet alive anyway, to keep the genetic varation in the population high. We do this by replacing some of the 
    # solutions that endid up in the surviving part of the array (beginning of the array), with some of the solutions 
    # that ended up in the 'dying' part of the array (the rest of the array, border is determines by survivalRatio).
    if elite is False:
        elites = int(len(population) * (survivalRatio*survivalRatio))
        rest = population[elites+1:]
        random.shuffle(rest)
        population[elites+1:] = rest

    for i in range(nr_of_cloned_children):
        population[survivors+i] = population[random.choice(range(survivors))].reproduce()

    for i in range(nr_of_children - nr_of_cloned_children):
        population[survivors+i+nr_of_cloned_children] = population[random.choice(range(survivors))].reproduce(population[random.choice(range(survivors))])
    return population

# Returns the best solution in a population (sorted or not)
def findbest(population):
    best = population[0]
    for i in population:
        if i.cost < best.cost:
            best = i
    return best


# Class for individual solutions in a population of solutions to a TSP
class Individual:

    # The solutions's genome, a permutation of cities to visit
    gene = list()

    # Create a new solution. If no gene is given, it wil give itself a random one.
    # It immediately computes it's own fitness.
    def __init__(self, gene=None):
        if gene is None:
            self.gene = self.create()
        else:
            if len(gene) != nrOfCities:
                raise Exception
            self.gene = gene
        self.cost = self.evaluate()

    # If you call reproduce without providing a partner, it will clone with a mutation.
    # If you call reproduce with a partner as argument, it will do a cross-over with this partner.
    # Returns a new solution with the resulting genome.
    def reproduce(self, partner=None):
        if partner is None:
            child = self.__reproduce_clone()
        else:
            child = self.__reproduce_sexual(partner)
        return child

    # The asexual reproduction method: cloning with a mutation.
    def __reproduce_clone(self):
        cut1 = random.choice(range(nrOfCities-2))
        cut2 = (random.choice(range(nrOfCities-2-cut1))) + cut1 + 2
        reverse_part = self.gene[cut1:cut2+1]
        reverse_part.reverse()
        new_gene = []
        if cut1 > 0:
            new_gene = new_gene + self.gene[0:cut1]
        new_gene = new_gene + reverse_part
        if cut2 < nrOfCities-1:
            new_gene = new_gene + self.gene[cut2+1:nrOfCities]

        return Individual(new_gene)

    # Edge Recombination Crossover (a way of combining two permutations into a new valid permutation)
    def __reproduce_sexual(self, partner):

        child_gene = []

        # Construct neighbor lists
        neighbor_sets = [set() for _ in range(nrOfCities)]
        for i in range(nrOfCities):
            # Add the neighbors of the first city, according to parents
            if i == 0:
                neighbor_sets[i].add(self.gene.index(nrOfCities-1))
            elif i == nrOfCities - 1:
                neighbor_sets[i].add(self.gene.index(0))
            else:
                neighbor_sets[i].add(self.gene.index(i-1))
                neighbor_sets[i].add(self.gene.index(i+1))
                neighbor_sets[i].add(partner.gene.index(i-1))
                neighbor_sets[i].add(partner.gene.index(i+1))

        # Take the first city of one of the parents
        city = self.gene[0]

        # Pick an edge from that city from one of the parents
        while len(child_gene) < nrOfCities:

            child_gene.append(city)
            for i in neighbor_sets:
                i.discard(city)

            if bool(neighbor_sets[city]):
                min = nrOfCities
                for i in neighbor_sets[city]:
                    if len(neighbor_sets[i]) < min:
                        min = len(neighbor_sets[i])
                        city = i

            else:
                difference = set(range(nrOfCities)) - (set(child_gene))
                if len(difference) > 0:
                    city = difference.pop()

        child = Individual(child_gene)
        return child

    def create(self):
        created_list = list(range(nrOfCities))
        random.shuffle(created_list)
        return created_list

    def evaluate(self):
        cost = 0
        for i in range(nrOfCities-1):
            cost += TSPmap[self.gene[i]][self.gene[i+1]]
        cost += TSPmap[self.gene[nrOfCities-1]][self.gene[0]]
        return cost


# This method governs the passing of generations, and lets us know what the best solution is every generation.
def run():
    if populationSize < 2:
        print("Reproducing solo doesn't work")
        exit()
    population = make_population()
    best = findbest(population)
    print("Best solution in population 1: length: " + str(best.cost) + ", solution: " + str(best.gene))
    for i in range(nrOfGenerations-1):
        population = generation(population)
        if printValues is True:
            best = findbest(population)
            print("Best solution in population " + str(i + 2) + ": length: "+ str(best.cost) + ", solution: " + str(best.gene))
    return findbest(population)

best = run()
print("Best solution found has length: " + str((best.cost)) + ", solution: " + str(best.gene))

