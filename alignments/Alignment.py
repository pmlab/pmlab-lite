import Reading_Writing as WR
import numpy
import scipy.sparse as sc
import scipy as sc
import Queue
import copy

#Priority Queue to store state nodes
q=Queue.PriorityQueue()

class Node:
    def __init__(self):
        #Shows a marking node
        self.marking__vector=[]
        self.active_transition=[]
        self.parent_node=''
        self.observed_trace_remain=[]
        self.alignment_Up_to=[] #It is of the form ((t1,t1),(t2,-),(-,t3))
        self.cost_from_init_marking= sum([0 if (x[0] and x[1])!= '-' else 1  for x in self.alignment_Up_to]) #Computing steps weight in an alignment
        self.cost_to_final_marking=10000
        self.total_cost=self.cost_to_final_marking+self.cost_from_init_marking

    def Find_active_transition(self, incidence_matrix):
        #Finding active transitions
        #Looping over transitions of the model to see which one is active given the marking of that node
        for i in range(0, incidence_matrix.shape[1]):
            if( numpy.all(incidence_matrix[:,i]+self.marking_vector>=0) ) :
                if(i not in self.active_transition):
                    self.active_transition.append(i)


##################################################################



    #This function calls other functions to investigate the current node
    def Investigate(self,incidence_matrix, trans, places, final_marking, distance_matrix, vertices):
        '''

        :param incidence_matrix: Incidence matrix of the Petri net (numpy index)
        :param trans: A list of transitions of the model
        :param places: A list of places of the model
        :param final_marking: Final marking of the model, like "p8'
        :param distance_matrix: Distance matrix computed from Floyed algorithm
        :param vertices: Names of vertices of the distance matrix
        :return:
        '''
        
        #Finding active transitions
        self.Find_active_transition(incidence_matrix)

        #Huersitic evaluation of active transitions
        for i in self.active_transition:
            #Computing the distance of an active transition to the final marking (a place in case of WF net)
            d=distance_matrix[vertices.index(trans[i]), vertices.index(final_marking)]
            self.cost_to_final_marking=d

            #This is a synchronous move
            try:
                if(trans[i]== self.observed_trace_remain[0]):
                    print "We are in synchronous move"
                    #Creating a new node
                    node_child=Node()
                    #Updating the current marking for that node by firing trans[i]
                    node_child.marking_vector = self.marking_vector+incidence_matrix[:,i]
                    node_child.parent_node=self



                    #Updating the remaining observed trace
                    node_child.observed_trace_remain=self.observed_trace_remain[1:]
                    node_child.alignment_Up_to=self.alignment_Up_to + [(self.observed_trace_remain[0], trans[i])]
                    node_child.cost_to_final_marking=d
                    node_child.cost_from_init_marking = sum([0 if ( (x[0] != '-')  and  (x[1] != '-') )  else 100 for x in node_child.alignment_Up_to])/ float(len(node_child.alignment_Up_to))
                    

                    # Updating active transitions for the child node
                    node_child.active_transition = copy.deepcopy(self.active_transition)
                    node_child.active_transition.remove(i)
                    node_child.total_cost = node_child.cost_to_final_marking+ node_child.cost_from_init_marking
                    

                    #Putting the node in the priority queue
                    q.put((node_child.total_cost, node_child))


                #This is a move in model

                elif(trans[i]!= self.observed_trace_remain[0]):
                    print "We are in asynchronous move in model"
                    # Creating a new node
                    node_child = Node()
                    # Updating the current marking for that node by firing trans[i]
                    node_child.marking_vector = self.marking_vector + incidence_matrix[:, i]
                    node_child.parent_node = self


                    # Updating the remaining observed trace
                    node_child.observed_trace_remain = self.observed_trace_remain[:]
                    node_child.alignment_Up_to=self.alignment_Up_to + [('-',trans[i])]
                    node_child.cost_to_final_marking = d
                    node_child.cost_from_init_marking = sum([0 if ( (x[0] != '-')  and  (x[1] != '-') )  else 100 for x in node_child.alignment_Up_to])/ float(len(node_child.alignment_Up_to))
                    

                    # Updating active transitions for the child node
                    node_child.active_transition = copy.deepcopy(self.active_transition)
                    node_child.active_transition.remove(i)
                    node_child.total_cost = node_child.cost_to_final_marking + node_child.cost_from_init_marking
                    

                    # Putting the node in the priority queue
                    q.put((node_child.total_cost, node_child))

                    #-----------------------------------------------------------
                    #Here we can have move in log as well!
                    print "We are in asynchronous move in log"
                    # Creating a new node
                    node_child = Node()
                    # Updating the current marking for that node
                    node_child.marking_vector = self.marking_vector
                    node_child.parent_node = self

                    # Updating the remaining observed trace
                    node_child.observed_trace_remain = self.observed_trace_remain[1:]
                    node_child.alignment_Up_to = self.alignment_Up_to + [(self.observed_trace_remain[0], '-')]
                    node_child.cost_to_final_marking = self.cost_to_final_marking
                    node_child.cost_from_init_marking = sum([0 if ( (x[0] != '-')  and  (x[1] != '-') )  else 100 for x in node_child.alignment_Up_to])/ float(len(node_child.alignment_Up_to))
                    p

                    # Updating active transitions for the child node
                    node_child.active_transition = copy.deepcopy(self.active_transition)
                    
                    node_child.total_cost = node_child.cost_to_final_marking + node_child.cost_from_init_marking
                    

                    # Putting the node in the priority queue
                    q.put((node_child.total_cost, node_child))

            except IndexError:

                print "We are in asynchronous move in model EXCEPTION"
                # Creating a new node
                node_child = Node()
                # Updating the current marking for that node by firing trans[i]
                node_child.marking_vector = self.marking_vector + incidence_matrix[:, i]
                node_child.parent_node = self

                # Updating the remaining observed trace
                node_child.observed_trace_remain = self.observed_trace_remain[:]
                node_child.alignment_Up_to = self.alignment_Up_to + [('-', trans[i])]
                node_child.cost_to_final_marking = d
                node_child.cost_from_init_marking = sum([0 if ( (x[0] != '-')  and  (x[1] != '-') )  else 100 for x in node_child.alignment_Up_to])/ float(len(node_child.alignment_Up_to))
                
                # Updating active transitions for the child node
                node_child.active_transition = copy.deepcopy(self.active_transition)
                node_child.active_transition.remove(i)
                
                node_child.total_cost = node_child.cost_to_final_marking + node_child.cost_from_init_marking

                # Putting the node in the priority queue
                q.put((node_child.total_cost, node_child))





#######################################################################
# This is Floyd() algorithm for computing the distance of a node to the final marking  as a heuristic
def Floyd_with_Labels(inc_matrix, places, transitions):
    '''
    :param inc_matrix: Incidence matrix of the model (numpy)
    :param places: A list containing places
    :param transitions: A list containing transitions
    :return: A distance_matrix and nemaes of rows and colomns
    '''
    

    # storing all vertices in a list
    # vert is like= ['P_p1', 'P_p3','P_p4',....,'T_t4','T_t5','T_t6',]
    vertices = places + transitions

    # Creating the initial matrix with value 100000 for each element
    matrix = numpy.full((len(vertices), len(vertices)), dtype=int, fill_value=10000000)

    # Filling matrix with corresponding values
    for p in places:

        # Setting diagonal elements to zero
        ind = vertices.index((p))
        matrix[ind, ind] = 0

        # Reading corresponding row of inc_matrix
        ind2 = places.index(p)
        row = inc_matrix[ind2, :]
        for i in range(len(row)):
            if (row[i] <= -1):
                t = transitions[i]
                ind3 = vertices.index(t)
                matrix[ind][ind3] = 1
    del ind

    for t in transitions:

        ind = vertices.index(t)
        matrix[ind][ind] = 0

        ind2 = transitions.index(t)
        column = inc_matrix[:, ind2]

        for i in range(len(column)):
            if (column[i] >= 1):
                p = places[i]
                ind3 = vertices.index(p)
                matrix[ind][ind3] = 1

    del ind


    # Using scipy library to compute distance matrix
    distance_matrix = sc.sparse.csgraph.floyd_warshall(matrix, directed=True)

    print "Distance matrix was computed!"
    return distance_matrix, vertices

######################################################################################################

#A-star algorithm
def Astar(model_path, log_path, destination_path, final_marking=['end']):
     '''

    :param model_path: Address to the PNML file
    :param log_path:  Address to the log file
    :param destination_path: Destination address to write some files
    :param final_marking: Final marking of the Petri net, like 'p8'
    :return:
    '''

    #Reading the model
    trans, places, Incident_matrix , initial_place_marking=WR.Preprocess(model_path, destination_path)
    

    ###---------------------------------------------------------------------------------------------------
    # This part is only to read a single trace from a txt file, just for testing. Otherwise remove this part
    # and use the above part.
    f = open(log_path)
    trace = f.read()
    trace = trace.strip(' ').split(' ')
    for i in range(len(trace)):
        trace[i] = "T_" + trace[i]
    total_trace = []
    total_trace.append(trace)
    final_marking="P_" + final_marking
# -----------------------------------------------------------------------------------------------------

    #Creating initial marking vector
    init_mark_vector=list(numpy.repeat(0,len(places)))
    init_mark_vector[places.index(initial_place_marking)]=1
    

    #Creating Final marking vector
    final_mark_vector = list(numpy.repeat(0,len(places)))
    final_mark_vector[places.index(final_marking)] = 1
    



    #Heuristic function. Computed only once
    distance_matrix, vertices=Floyd_with_Labels(Incident_matrix,places,trans)



    #Creating initial node in the search space
    current_node=Node()
    current_node.marking_vector=init_mark_vector[:]
    current_node.observed_trace_remain=total_trace[0]


   
    explore=1
    candidate_nodes=[]
    while ( explore):
        #Investigating the current node
        current_node.Investigate(Incident_matrix, trans, places, final_marking, distance_matrix, vertices)

        #Find the best bode to explore
        #q.get returns tuples like (12,node) where the first is the total cost of the node, and second is the node object
        current_node=q.get()[1]
        if ( numpy.all(current_node.marking_vector ==final_mark_vector) and len(current_node.observed_trace_remain)==0 ):
            candidate_nodes.append(current_node)
            if(len(candidate_nodes)>5):
                explore=0


    return trans, places, Incident_matrix , initial_place_marking, init_mark_vector, candidate_nodes, total_trace, distance_matrix, vertices
