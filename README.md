# EvolutionaryComputationTSP
Here you'll find a small python program for finding a good solution to a TSP problem with evolutionary algorithm. It has been written for the  Computation Thinking course at the Amsterdam University College in 2017.

As input to the program you can provide a file with points in a 2D space according to the TSPLIB format. A good source for such example problems is: http://www.math.uwaterloo.ca/tsp/data/

Alternatively edit the distance matrix in the GeneticTSP file.

There are several variables you can play with to optimize the algorithm:
  - Population size
  - Number of generations it runs
  - How many not-so-good-looking-so-far solutions you keep alive to keep genetic diversity on your population
  - The ratio of types of reproduction used each generation: mutation or sexual reproduction
