import os
import csv
import random
import adjacencylist as G
import edges as E
import copy
import numpy
# for chaitin's algorithm
import interview as I

def make_panel_graph(contents,i):
    fileName = "data/output/panel/test/review-panels"+str(i)+".csv"
    if (not os.path.isfile(fileName)):
        print(fileName + ": file does not exist.")
    data = open(fileName, "r")
    csvData = csv.reader(data)
    graph = G.empty_graph()
    for row in csvData:
        contents[row[0]] = []
        for i in range(len(row)):
            if (i == 0):
                continue
            contents[row[0]].append(row[i])
    for f in contents.keys():
        for c in contents.keys():
            G.add_edge(E.make_edge(f, 0, c), graph)
    keys = list(contents.keys())
    for i in range(len(contents)):
        for j in range(len(contents)):
            if (any(val in contents[keys[i]] for val in contents[keys[j]])):
                if (keys[i] != keys[j]):
                    G.add_edge(E.make_edge(keys[i], 1, keys[j]), graph)
    graph_dict = {}
    for s in graph:
        graph_dict[s] = []
        for (d, w) in graph[s]:
            if (w != 0):
                graph_dict[s].append(d)
    return graph_dict


def write_mci(g):
    dim = G.number_of_nodes(g)
    print("mclheader\nmcltype matrix\ndimensions " + str(dim) + "x" + str(dim) + "\nmclmatrix\nbegin")
    for s in g:
        line = str(s)
        for (d, w) in g[s]:
            if (w != 0):
                line += " " + str(d) + ":" + str(w)
        line += "\t$"
        print(line)


def genetic_algo(graph, color):
    chromosomes = []
    for i in range (50):
        colors = {}
        for i in graph.keys():
            colors[i] = random.randint(0, color - 1)
        chromosomes.append(colors)
    val, child = run(chromosomes, graph, color)
    # if conflict are less than the number of colors then the conflict can be resolved in that many colors hence we can term it as valid solution
    if val == 0:
        return 0 ,child
    return 1000 , []

def find_key(graph, maxx):
    count, final_stack=I.find_key(copy.deepcopy(graph),len(graph))
    print("Minimum possible slots by Chaitin's Algorithm :"+str(count))
    start = count/2
    end = count
    val = end+1
    while(start<=end):
        mid = int((start + end) / 2)
        stack,child=genetic_algo(copy.deepcopy(graph),mid)
        if(stack==0):
            end = mid - 1
            val = mid
        else:
            start = mid + 1
    stack,child=genetic_algo(copy.deepcopy(graph),start)
    
    if(val<=count):
        print("Minimum possible slots by Genetic Algorithm :"+str(val))
    else:
        print("Minimum possible slots by Genetic Algorithm : Not better than chaitin's")

    if(val != count):
        print(val)
        print("*****")
        print(count)
        print(child)
        for i,j in child.items():
            print("Candidate Email: "+str(i)+" :: Slot: "+str(j))
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
    temp = [k for k in range(20)]
    col = [i for i in range(color)]
    count = 0
    fitChild = len(graph)
    generation=20000

    while(count<generation and fitChild!=0):
        temp.pop(0)
        temp.append(fitChild)
        parent1, parent2 = parentSelection(population,count,generation,graph)
        # parent1, parent2 = parentSelection(population,graph)
        child = crossover(parent1, parent2, graph, population)
        child = mutate(child, graph, col)
        fitChild = fitness(child, graph)
        if(count%2000==0):
            print(str(count)+":: fitness:"+str(fitChild))
        if(fitChild==0):
            print("     It stopped on iteration : "+str(count))

        fitP1 = fitness(population[parent1], graph)
        fitP2 = fitness(population[parent2], graph)
        if(len(population)<2):
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


# Parent selection by simulated annealing
def parentSelection(population, count,generation,graph):
    if(count<(generation*0.9999)):
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
        if pf < pf1:
            pf1=pf
            parent1 = i
        elif pf < pf2 :
            pf2=pf
            parent2 = i
    return parent1, parent2

def fitness(chromosome, graph):
    conflict = 0
    for i in chromosome:
        conflict = conflict + fit(i, graph, chromosome[i], chromosome)
    return conflict

def fit(id, graph, col, chromosome):
    conflict = 0
    for val in graph[id]:
        if(col == chromosome[val]):
            conflict = conflict + 1
    return conflict

def mutate(chromosome, graph, colour):
    # Mutate approach one : Assign valid color to node with higher number of conflicts
    # conflictList = {}
    # for i in chromosome:
    #     conflictList[i] = fit(i, graph, chromosome[i], chromosome)
    # conflictList.sort()
    # data= [k for k in conflictList()]

    # Mutate approach two : Assign valid color to node with higher number of edges
    data = [k for k in sorted(graph, key=lambda k: len(graph[k]), reverse=True)]
    for i in data:
        check(i, graph, chromosome[i], chromosome, colour)
    return chromosome

def check(id, graph, col, chromosome, colour):
    adjCol = []
    for d in graph[id]:
        adjCol.append(chromosome[d])
    validCol = Diff(colour, adjCol)
    for val in graph[id]:
        if(col == chromosome[val]):
            if(len(validCol)<1):
                break
            chromosome[val] = validCol[0]
            validCol.pop(0)
def Diff(li1, li2):
    return (list(list(set(li1)-set(li2)) + list(set(li2)-set(li1))))

if __name__ == "__main__":
    for i in range(50):
        print("\nRunning for Review-Panel "+str(i+1))       
        contents = {}
        graph_dict = make_panel_graph(contents,i+1)
        slots=find_key(graph_dict,len(graph_dict))

























