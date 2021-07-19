import os
import csv
import adjacencylist as G
import edges as E
import copy


# This function returns the final stack and return the minimum number of colors
def find_key(graph,maxx):
    """
    eg 
    maxx = 5
    end = 5

    loop 1: 
    mid = 3
    stack = [3, 2, 1, 4, 5]
    end = 2
    ans = 3
    final_stack = [3, 2, 1, 4, 5]

    loop 2:
    start = 1
    end = 2
    mid = 1
    stack = []
    start = 2

    loop3: 
    start = 2, end = 2
    mid = 2
    len(stack) = 0
    start = 3
    """
    start=1
    end=maxx
    final_stack = []
    while(start<=end):
        mid=int((start+end)/2)
        stack=chaitin_algo(copy.deepcopy(graph),mid)
        if(len(stack)==0):
            start=mid+1
        else:
            end=mid-1
            ans=mid
            final_stack=stack
    return ans, final_stack

def delete_node(Dict,key):
    del Dict[key]

    for s in Dict:
        if key in Dict[s]:
            Dict[s].remove(key)

    # print(temp)
    # print(Dict)


def chaitin_algo(Dict,k):
    # Dict format = graph_dict in the make_panel_graph function
    stack=[]
    # print(graph)
    while(len(Dict)>0):
        i=0
        temp=0
        while(i<len(Dict)):
            keys_list = list(Dict)
            # len(Dict[keys_list[i]]) = no. of candidates connected to a candidate in graph_dict
            if(len(Dict[keys_list[i]])<k):
                stack.append(keys_list[i])
                delete_node(Dict,keys_list[i]) 
                temp=1
            else:
                i+=1

        if(temp==0):
            stack.clear()
            break
    return stack

# Basically coloring the graph here
def slot_allotment(slots,graph, final_stack):
    colour_dict={}
    keys_list = list(graph)
    # keys_listis just the list of candidates
    # for s in keys_list:
    #     colour_dict[s]=0
    colour_dict = {s:0 for s in keys_list}
    #colour_dict = [0 for s in keys_list]
    
    while(len(final_stack)>0):
        key=final_stack.pop()
        for count in range(1,slots+1):
            # count = color
            temp=0
            for val in graph[key]:
                if(colour_dict[val]==count):
                    temp=1
                    break
            if(temp==0):
                colour_dict[key]=count
                break
    return colour_dict
    # {candidate: number (denotes color)}


def make_panel_graph(contents):
    fileName = "data/output/panel/review-panels.csv"
    if (not os.path.isfile(fileName)):
        print(fileName + ": file does not exist.")
    data = open(fileName, "r")
    csvData = csv.reader(data)
    graph = G.empty_graph()
    for row in csvData:
        contents[row[0]] = []
        for i in range(len(row)):
            if(i == 0):
                continue
            contents[row[0]].append(row[i])
    # contents = {
    #   "cand1": ["prof1", prof2, ....],
    #   "cand2": ["prof1", prof2, ...],
    # }
    # print(contents)

    #keys, graph = adding_edges_all_nodes(contents, graph)    
    
    keys = list(contents.keys())
    # Adds edge from a candidate to a candidate if they both have a same prof

    graph = adding_weight_to_edges(contents, graph, keys)
    
    # graph = {
    #   'candidate1@gmail.com': [('candidate1@gmail.com', 0), ('candidate2@gmail.com', 0), ('candidate3@gmail.com', 1)], 
    #   'candidate2@gmail.com': [('candidate1@gmail.com', 0), ('candidate2@gmail.com', 0), ('candidate3@gmail.com', 0)], 
    # 'candidate3@gmail.com': [('candidate1@gmail.com', 1), ('candidate2@gmail.com', 0), ('candidate3@gmail.com', 0)]}

    
    graph_dict = create_graph_dictionary(graph)

    return graph_dict

def create_graph_dictionary(graph):
  graph_dict = {}
  for s in graph:
        graph_dict[s] = []
        for (d, w) in graph[s]:
            if(w != 0):
                graph_dict[s].append(d)
  return graph_dict

  # returns graph_dict = 
  # { 'candidate1@gmail.com': ['candidate3@gmail.com'], 
  #   'candidate2@gmail.com': [], 
  #   'candidate3@gmail.com': ['candidate1@gmail.com']}
  


#def adding_edges_all_nodes(contents, graph):
#  for f in contents.keys():
#      for c in contents.keys():
#        G.add_edge(E.make_edge(f, 0, c), graph)
#  keys = list(contents.keys())
#  return keys, graph
#  # keys = list of candidates

def adding_weight_to_edges (contents, graph, keys):
  for i in range(len(contents)):
    for j in range(len(contents)):
      if(any(val in contents[keys[i]] for val in contents[keys[j]])):
        if(keys[i]!=keys[j]):
          G.add_edge(E.make_edge(keys[i], 1, keys[j]), graph)
  return graph


def print_interview_slots (colour_slots, contents):
    k=0
    for i in colour_slots:
        k+=1
        print("\nInterview-Panel: "+str(k)+" || candidate id: "+str(i)+" || prof id: "+ str(contents[i])+" \n------->>Slot: "+str(colour_slots[i]))



# def print_review_panels():
#   fout = open("data/output/interview-slots/panel-slots.txt", "w")
#   count=0
#   for app in review_panels:
#     fout.write("\n***************************************************")
#     count+=1
#     fout.write("\nInterview-panel : "+str(count))
#     fout.write("\n" + app)
#     panel = functools.reduce(lambda x, y: x + "\n\t" + y[0], review_panels[app][:PANEL_SIZE], "\n")
#     fout.write(panel)
#     fout.write("\n***************************************************")
#   fout.close()

##################################################################################
if __name__ == "__main__":

    contents={}
    graph_dict=make_panel_graph(contents)
    # graph_dict is { 'candidate1@gmail.com': ['candidate3@gmail.com'], 
    #   'candidate2@gmail.com': [], 
    #   'candidate3@gmail.com': ['candidate1@gmail.com']}

    slots, final_stack=find_key(graph_dict,len(graph_dict))

    colour_slots=slot_allotment(slots,graph_dict, final_stack)
    print("\nSlots alloted to each Interview-Panel:\n")

    print_interview_slots(colour_slots, contents)

    print("\n\nMinimum number of slots for this dataset: "+str(slots))
    


"""
No of candidates: 300, panel-size: 3 ----> no of slots: 44 
No of candidates: 300, panel-size: 4 ----> no of slots: 69
No of candidates: 300, panel-size: 5 ----> no of slots: 97
No of candidates: 300, panel-size: 6 ----> no of slots: 124
No of candidates: 300, panel-size: 7 ----> no of slots: 152
"""