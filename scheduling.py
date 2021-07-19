import os
import csv
import random
import adjacencylist as G
import edges as E
import copy
import numpy
# for chaitin's algorithm
import interview as I



def genetic_algo(graph, color):
    # mid is the color

    # chromosomes is the population, ie, list of colors (basically, list of graphs)
    chromosomes = []
    for i in range (50):
        colors = {}
        # for i in graph.keys():
        #     colors[i] = random.randint(0, color - 1)
        colors = {i: (random.randint(0, color - 1)) for i in graph.keys()}
        # colors = {"candidate_id": random_number}
        chromosomes.append(colors)
    # chromosomes is a list of dictionaries
    val, child = run(chromosomes, graph, color)
    # if conflict are less than the number of colors then the conflict can be resolved in that many colors hence we can term it as valid solution
    # conflict = 0 -> final colored graph
    if val == 0:
        return 0 ,child
    # Doubt    
    return 1000 , []

def find_key(graph, maxx):
    """
    
    """
    # using count as the limiting factor for genetic
    count, final_stack=I.find_key(copy.deepcopy(graph),len(graph))
    # This function returns the final stack and return the minimum number of colors from Chaitin's
    # count: minimum number of colors
    # final_stack: final stack as a list
    start = int(count / 2)
    end = count
    val = count
    # mid is the color
    while(start<=end):
        mid = int((start + end) / 2)
        stack,child=genetic_algo(copy.deepcopy(graph),mid)
        if(stack==0):
            end = mid - 1
            val = mid
        else:
            start = mid + 1
    # Checking if ans from Genetic = ans from Chaitin's
    if(val != count):
        print(val)
        print("*****")
        print(count)
        print(child)
        for i,j in child.items():
            print("Candidate Email: "+str(i)+" :: Slot: "+str(j))
    # If same, then print the Chaitin's slots
    else :
        colour_slots = I.slot_allotment(val, graph, final_stack)
        print("\nSlots alloted to each Interview-Panel:\n")
        k = 0
        for i in colour_slots:
            k += 1
            print("\nInterview-Panel: " + str(k) + " || candidate id: " + str(i) + " || prof id: " + str(
                contents[i]) + " \n------->>Slot: " + str(colour_slots[i]))
    return val


def run(population, graph, color):
    temp = list(range(20))
    col = list(range(color))
    count = 0
    fitChild = len(graph)
    generation=300

    while(count<generation and fitChild!=0):
        # print("Iteration"+str(count))
        temp.pop(0)
        temp.append(fitChild)
        parent1, parent2 = parentSelection(population,count,generation,graph)
        # parent1, parent2 = parentSelection(population,graph)
        child = crossover(parent1, parent2, graph, population)
        child = mutate(child, graph, col)
        fitChild = fitness(child, graph)

        # print("fitness of child "+str(fitChild))

        fitP1 = fitness(population[parent1], graph)
        fitP2 = fitness(population[parent2], graph)
        if(len(population) < 2):
            return fitChild ,child
        if(fitChild < fitP1 and fitChild < fitP2):
            if(fitP1<fitP2):
                population.pop(parent2)
            else:
                population.pop(parent1)
            population.append(child)
        elif(fitChild < fitP1):
            population.pop(parent1)
            population.append(child)
        elif(fitChild < fitP2):
            population.pop(parent2)
            population.append(child)
        count = count + 1
    return fitChild ,child
    # returning fitness of the child and child itself


def crossover(parent1, parent2, graph, population):
    vals = list(graph.keys())
    vals.sort()
    crosspoint = random.randint(0, len(vals) - 1)
    child = {}

    for i in range(crosspoint):
        child[vals[i]] = population[parent1][vals[i]]
    for i in range(crosspoint, len(vals)):
        child[vals[i]] = population[parent2][vals[i]]
    return child
    # child is a dictionary (same as a parent dictionary)


# Parent selection by simulated annealing
def parentSelection(population, count,generation,graph):
    if(count<(generation*0.75)):
        return parentSelectionMethod1(population)
    return parentSelectionMethod2(population,graph)

def parentSelectionMethod1(population):
    parent1 = random.randint( 0, len(population) - 1)
    parent2 = random.randint(0, len(population) - 1)
    return parent1, parent2

def parentSelectionMethod2(population, graph):
    pf1 = len(graph)
    pf2 = len(graph)
    parent1 = random.randint(0, len(population) - 1)
    parent2 = random.randint(0, len(population) - 1)
    for i in range(len(population)):
        pf = fitness(population[i], graph)
        # pf is more -> less desirable
        # we choose parents that have the least conflict
        if pf < pf1:
            pf1=pf
            parent1 = i
        elif pf < pf2 :
            pf2=pf
            parent2 = i
    return parent1, parent2
def fitness(chromosome, graph):
    # chromosome is a dictionary
    conflict = 0
    # chromosome is a dict
    for i in chromosome:
        conflict = conflict + fit(i, graph, chromosome[i], chromosome)
    return conflict

def fit(id, graph, col, chromosome):
    # id = email id of candidate (key of chromosome dictionary)
    # graph = {'cand1': [cand2]}
    # col = color of the node
    # chromosome is a dictionary
    # print(f"id is: {id}, graph[id] is {graph[id]}")
    conflict = 0
    # graph[id] contains all cands that are adjacent to the current candidate
    for val in graph[id]:
        # val is an adjacent cand
        # chromosome[val] is basically color of that adjacent node
        if(col == chromosome[val]):
            conflict = conflict + 1
    return conflict

"""Coloring the entire graph and returning, but not optimally"""
def mutate(chromosome, graph, colour):
    # colour is the list of all colours
    # chromosome is the child chromosome

    # conflictList = {}
    # for i in chromosome:
    #     conflictList[i] = fit(i, graph, chromosome[i], chromosome)
    # conflictList.sort()
    # data= [k for k in conflictList()]
    data = list(sorted(graph, key=lambda k: len(graph[k]), reverse=True))
    # data is list of emailids sorted in descending order of no of adjacent nodes 
    for i in data:
        check1(i, graph, chromosome[i], chromosome, colour)
    return chromosome

# def mutateSelectMethod():
#   if(count<(generation*0.5)):
#         return parentSelectionMethod1(population)
#   else:
#         return parentSelectionMethod2(population,graph)

"""Just coloring the adjacent nodes"""
def check1(id, graph, col, chromosome, colour):
    adjCol = []
    # for d in graph[id]:
    #     adjCol.append(chromosome[d])
    adjCol = [chromosome[d] for d in graph[id]]
    # adjCol list of adjacent colors to the current id
    validCol = Diff(colour, adjCol)
    # validCol is the list of valid colors for that id (candidate/node)
    for val in graph[id]:
        if(col == chromosome[val]):
            if(len(validCol)<1):
                break
            chromosome[val] = validCol[0]
            # coloring the adjacent nodes from one of the valid colors
            validCol.pop(0)

def check2(id, graph, col, chromosome, colour):
    # adjCol = []
    # for d in graph[id]:
    #     adjCol.append(chromosome[d])
    # adjCol = [chromosome[d] for d in graph[id]]
    # adjCol list of adjacent colors to the current id
    for val in graph[id]:
        if(col == chromosome[val]):
            if(len(colour)<1):
                break
            chromosome[val] = random.choice(colour)

def Diff(li1, li2):
    return (list(list(set(li1)-set(li2)) + list(set(li2)-set(li1))))

if __name__ == "__main__":
    contents = {}
    graph_dict = I.make_panel_graph(contents)
    slots=find_key(graph_dict,len(graph_dict))
    print("\nMinimum number of slots to conduct the interview are:")
    print(slots)
