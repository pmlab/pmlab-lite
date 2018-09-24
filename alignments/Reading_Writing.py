import numpy
import os
import xml.etree.ElementTree as ET
#import Variables as V
import xlsxwriter as XL
import re




def Preprocess(model_path, destination_path):
    # this method just writes the Transition , Place names and incident matrix of the Petri net
    # read from PNML file ( with this method test2_1.Reading_PNML()) to the text file in order to be useful
    # for the aggregation techniqes for finding aggregated networks

    transition_id, transitaion_name_modified, transition_obj, place_id, place_name, place_obj, Incident_matrix, initial_place_marking = Reading_PNML(
        model_path)
    trans = []
    places = []

    for i in range(len(transitaion_name_modified)):
        trans.append("T_" + transitaion_name_modified[i])
        #trans.append(transitaion_name_modified[i])

    for i in range(len(place_name)):
        places.append("P_" + place_name[i])
        #places.append(place_name[i])

    # Creating directory for saving the result per each trace
    if not os.path.exists(destination_path + "/results"):
        os.makedirs(destination_path + "/results")

    # path="C:/Users/University/workspace/jav2/result/Place invariant/"+ts.MODEL
    path = destination_path + "/results"

    #initial_place_marking = "P_" + initial_place_marking + "_net"
    initial_place_marking = "P_" + initial_place_marking


    f = open(path + "/Initial_marking.txt", "w")
    f.writelines(initial_place_marking)
    f.close()

    print "len places is:", len(places)
    print "len transition is:", len(trans)

    ##f= open("C:\\Users\\University\\Desktop\\project\\4 november\\Data\\ Places_first.txt","w")
    f = open(path + "/Places_first.txt", "w")

    for i in range(len(places)):
        f.writelines(places[i])
        f.write("\n")

    f.close()

    ##f=open("C:\\Users\\University\\Desktop\\project\\4 november\\Data\\ Transitions_first.txt","w")
    f = open(path + "/Transitions_first.txt", "w")

    for i in range(len(trans)):
        f.writelines(trans[i])
        f.write("\n")

    f.close()

    ##f=open("C:\\Users\\University\\Desktop\\project\\4 november\\Data\\Incident_matrix_first.txt","w")
    f = open(path + "/Incident_Matrix_first.txt", "w")
    for i in range(len(Incident_matrix)):
        for j in range(len(Incident_matrix[0])):
            f.write(str(int(Incident_matrix[i][j])))
            f.write("\n")
        f.write("new_row")
        f.write("\n")

    return trans, places, Incident_matrix, initial_place_marking


##########################################################################

class Transitions:
    def __init__(self, trans_id, trans_text):
        self.id = trans_id
        self.text = trans_text


class Places:
    def __init__(self, place_id, place_text):
        self.id = place_id
        self.text = place_text


class Arcs:
    def __init(self, arc_id, arc_source, arc_target):
        self.id = arc_id
        self.source = arc_source
        self.target = arc_target


##########################################################

def Reading_PNML(model_path):
    place_id = []
    place_name = []
    place_obj = []

    transition_id = []
    transition_name = []
    transition_obj = []

    arcs = []

    temp1 = 0
    temp2 = 0
    temp3 = 0
    init_mark_model = []
    Incident_matrix = []

    # add='C:/Users/University/Desktop/New folder 2/'+ MODEL+'_petri_pnml.xml'
    # add='C:/Users/University/Documents/chert/plg.pnml.xml'
    add = model_path
    tree = ET.parse(add)
    root = tree.getroot()

    # Reading the places ID and its text. place_id is of the form ['n1',..] and  temp1 is of the form {'id': 'n1'}
    # place name is of the form:  ["place_0",...]

    for p in root.iter("place"):
        temp1 = p.attrib
        place_id.append(temp1['id'])
        # for p in root.iter("place"):
        temp2 = p.find("name").find("text").text
        place_name.append(temp2)
        # creating place object
        temp3 = Places(temp1['id'], temp2)
        place_obj.append(temp3)

    # Reading transitions from PNML file, trnasition_id is of the form ['n318',...], temp1 is of the form {'id': 'n318'}
    # and transition_name is of the form ['A+complete',....]

    for trans in root.iter("transition"):
        temp1 = trans.attrib
        transition_id.append(temp1['id'])
        # for trans in root.iter("transition"):
        temp2 = trans.find("name").find("text").text

        # This part was added to work with realistc data set, bpi2012
        # Here we changed the "_" in the name of transition with "*"
        # -------
        # some real transitions of the model is like A\\n, B\\n, we must remove \\n
        # the ones come from PLG model generator
        # temp2=temp2.strip("\\n")

        if (" " in temp2):
            temp2 = temp2.replace(" ", "*")

        if ("_" in temp2):
            temp2 = temp2.replace("_", "*")
            # -----------
        transition_name.append(temp2)
        temp3 = Transitions(temp1['id'], temp2)
        transition_obj.append(temp3)

    # Reading arcs for PNML, the lis arcs is of the form arcs=[{'source': 'n78', 'id': 'arc635', 'target': 'n447'},....]
    for ar in root.iter("arc"):
        arcs.append(ar.attrib)





    # Calculating initial marking from PNML
    # init_mark is of the form [None, None, None, None, None, None, None, <Element 'initialMarking' at 0xa27ad0c>, None,.....]

    # init_mark_model is of the form=[None, None, None, None, None, None, None, <Element 'initialMarking' at 0x15a128d0> ,....]
    for place in root.iter("place"):
        init_mark_model.append(place.find("initialMarking"))

    init_mark_model_list = []
    for i in range(len(init_mark_model)):
        if (init_mark_model[i] != None):
            init_mark_model_list.append(1)
        else:
            init_mark_model_list.append(0)
    initial_place_marking = place_name[init_mark_model_list.index(1)]

    # Calculating incident matrix using Matrix method
    Incident_matrix = Matrix(transition_id, place_id, arcs)

    # Some preparations
    # transitaion_name is of the form ['A+complete',....] and transitaion_name_modified is of the form ['A',....]
    transitaion_name_modified = Preparation(transition_name)

    return transition_id, transitaion_name_modified, transition_obj, place_id, place_name, place_obj, Incident_matrix, initial_place_marking
    # return place_id, place_name, place_obj


####################################################################################

# This is an internal function
def Matrix(transitions, places, arcs):
    # trnasition_id is of the form ['n318',...],
    # place_id is of the form ['n1',..]
    # arcs is of the form arcs=[{'source': 'n78', 'id': 'arc635', 'target': 'n447'},....]
    incident_matrix = numpy.zeros((len(places), len(transitions)), dtype=numpy.int)

    for i in range(len(arcs)):
        s = arcs[i]['source']
        t = arcs[i]['target']

        if ((s in transitions) and (t in places)):
            pl = places.index(t)
            tr = transitions.index(s)

            incident_matrix[pl][tr] = 1

        elif ((t in transitions) and (s in places)):
            pl = places.index(s)
            tr = transitions.index(t)

            incident_matrix[pl][tr] = -1

    return incident_matrix


#############################################################################
# this is an internal function
def Preparation(transition_name):
    t = []
    t = transition_name[:]
    # print " the lenght of t is:", len(t)
    tn = []
    temp = 0
    for i in range(len(t)):
        # temp=t[i].split("+")
        tn.append(t[i].split("+")[0])

    # print "the len tn is:", len(tn),

    return tn

#############################################################################

def Reading_log_all(log_path, destination_path, trans):
    print"##########################################"
    # print" The actual body of gets started"

    # Reading log from "log.txt"
    total_trace = []
    # for k in range(500):
    # f=open("C:/Users/University/Desktop/Net and log/log_test/Real_log/BPIC15_2_log/BPIC15_2_log_%d.txt" %k)
    # f=open("C:/Users/University/Desktop/Net and log/log_test/Real_log/BPIC15_4_log/BPIC15_4_log_19.txt" ,"r")
    # f=open('C:/Users/University/Documents/chert/plg.txt','r')

    log_temp, case_name = Read_XES(log_path)
    # f=open(log_path, 'r')


    # This part only writes separate traces to the txt files
    for i in range(len(log_temp)):
        if not os.path.exists(destination_path + "/logs"):
            os.makedirs(destination_path + "/logs")
        # h=open(destination_path+"/logs"+"/trace_%i.txt" %i,"w")
        h = open(destination_path + "/logs" + "/trace_%i.txt" % case_name[i], "w")

        for j in range(len(log_temp[i])):
            h.write(log_temp[i][j] + " ")
        h.close()

    # reading all the lines, each line is
    '''temp=f.readlines()
    log_temp=[]
    for i in range(len(temp)):
        trace=temp[i].strip("\n").split(" ")
        log_temp.append(trace)

    temp=[]
    #print"The log before adding [T]:",log_temp
    f.close()'''

    # --------------------------
    #  this part is temporarili, remove it after use and use the above block
    # import checknevis as ch
    # log_temp=ch.Read_txt(log_path)
    # ---------------------------------------

    log = []
    for k in range(len(log_temp)):
        for i in range(len(log_temp[k])):
            # Just for working with realistic examples"
            # ----------
            if ("_" in log_temp[k][i]):
                log_temp[k][i] = log_temp[k][i].replace("_", "*")
            if (" " in log_temp[k][i]):
                log_temp[k][i] = log_temp[k][i].replace(" ", "#")
            # ----------

            log_temp[k][i] = ("T_" + log_temp[k][i])
            ###log.append(log_temp[i])

    # finding uniqe traces
    total_trace = []
    dictionary_log = dict()

    k = 0
    for i in range(len(log_temp)):
        if (log_temp[i] not in total_trace):
            total_trace.append(log_temp[i])
            # This dictionary is only for tracking which traces are realted each uniqe trace
            # dictionary_log[k]=[i]
            # dictionary_log[k]=str(i)
            dictionary_log[k] = str(case_name[i])
            k += 1
        elif (log_temp[i] in total_trace):
            trace_index = total_trace.index(log_temp[i])
            # dictionary_log[trace_index].append(i)
            # dictionary_log[trace_index]=dictionary_log[trace_index]+','+str(i)
            dictionary_log[trace_index] = dictionary_log[trace_index] + ',' + str(case_name[i])


            # print "the log after adding [T]:",log

    print "++++++++++++++++++++++++++++++++++++++++"

    # --------------------------------------------------------------
    ###--------------------Attention----------------------
    ###In some situations where we creat a model from the given log, using inductive miner in ProM, it is possible to have a model that
    # do not contain all the distinct events in the log, for example it is possible to have a model with transitions t1,t3,t5 which created
    # from this log=[[t1,t2,t5],[t1,t3,t5,t4],[t1,t5,t3]]. In order to avoid the future problem we remove thees type of events from the trace
    # when we want to pass the trace to the ILP, Also the Prom Does the same!
    # path="C:/Users/University/workspace/jav2/result/Place invariant/"+MODEL
    path = destination_path
    # trans, places, Incident_matrix,initial_place_marking=CCW.Preprocess()
    events_not_replayed = []

    '''for i in range(len(total_trace)):
        temp=[]
        #temp2=[]
        for j in range(len(total_trace[i])):
            if(total_trace[i][j] in trans):
                temp.append(total_trace[i][j])
            elif(total_trace[i][j] not in trans):
                events_not_replayed.append(total_trace[i][j])
        total_trace[i]=temp
        #events_not_replayed.append(temp2)
    if(len(events_not_replayed)!=0):
        #Wrintg not replayed events
        f=open(path+"/Events not replayed.txt","w")
        for i in range(len(events_not_replayed)):
                f.write(events_not_replayed[i]+" ")
        f.close()'''

    trans = V.transition
    places = V.p_name
    Incident_matrix = V.Inc_matrix
    initial_place_marking = V.initial_place_marking

    events_not_replayed = []

    for i in range(len(total_trace)):
        temp = []
        # temp2=[]
        for j in range(len(total_trace[i])):
            if (total_trace[i][j] in trans):
                temp.append(total_trace[i][j])
            elif (total_trace[i][j] not in trans):
                events_not_replayed.append(total_trace[i][j])
        total_trace[i] = temp
        # events_not_replayed.append(temp2)
    if (len(events_not_replayed) != 0):
        # Wrintg not replayed events
        events_not_replayed = list(set(events_not_replayed))
        f = open(path + "/Events not replayed.txt", "w")
        for i in range(len(events_not_replayed)):
            f.write(events_not_replayed[i] + " ")
        f.close()




    return total_trace, dictionary_log



    # ---------------------------------------------------------
    # print " total_trace:", total_trace[0]
    # return total_trace[0]
#############################################################################
#### Reading XES file

# For better understanding of how it works open a XES file(small one) with http://xmlgrid.net
# Remember that the XES file must be preprocessed such that only contain complete actions
def Read_XES(path):
    add = path
    tree = ET.parse(add)
    root = tree.getroot()

    # --New Added 30 August 2016-------------------------------------------
    # Some XML files have Namesapce and it is declered at the root like and represented by xmlns like: <pnml xmlns="http://www.pnml.org/version-2009/grammar/pnml">.
    # So in order to acces the tags inside the XML file, the name space must be mentioned!, The general form is like "{name_sapce}tag",
    # For example for reading places tags, the code is like below:
    #   for p in root.iter("{ http://www.pnml.org/version-2009/grammar/pnml }place"):
    #       print p
    # ------
    # First we need to extract the namespace, namely the value of xmlns
    # root.tag='{http://www.pnml.org/version-2009/grammar/pnml}pnml' but we need '{http://www.pnml.org/version-2009/grammar/pnml}'
    # For this issue we use regular expression library (re) of python
    m = re.match('\{.*\}', root.tag)
    # checking whether m is empty or no
    if (m):
        namespace = m.group(0)
    else:
        namespace = ''
        # ------------------------------------------------------------



    temp = []
    log = []
    case_name = []
    print "We are before for"
    for t in root.iter(namespace +"trace"):
        # ----
        # Reading the case number, like "instance_294"
        for name in t.iter(namespace +"string"):
            # print name.attrib['key']
            if (name.attrib['key'] == 'concept:name'):
                temp_name = name.attrib['value']
                temp_name = temp_name.split("_")[1]
                case_name.append(int(temp_name))
                break
        # print "The caee_name:",case_name
        # ---------------------
        for e in t.iter(namespace +"event"):
            for r in e.iter(namespace +"string"):
                # print r.attrib
                if (r.attrib['key'] == 'concept:name'):
                    # print r.attrib['value']
                    temp.append(r.attrib['value'])


                    # print "the temp is:", temp
        log.append(temp)
        temp = []

        # print t.attrib

    print "We are after for"
    print "The len log is:", len(log)
    print "the len case_name:", len(case_name)
    ###-------
    # re-arranging the position of the log, starting from zero
    # Before arranging case_name[0]='297' and log[0]= case 297
    # After  arranging, case_name[0]='0' and log[0]=case 0
    # Example:

    #    >>> list1 = [3,2,4,1, 1]
    #    >>> list2 = ['three', 'two', 'four', 'one', 'one2']
    #    >>> list1, list2 = zip(*sorted(zip(list1, list2)))
    #    >>> list1
    #        (1, 1, 2, 3, 4)
    #    >>> list2
    #        ('one', 'one2', 'two', 'three', 'four')

    print "The len log is:", log
    print "the len case_name:", case_name
    ##case_name, log=zip(*sorted(zip(case_name,log)))

    # ---------------------------------------

    ##printting the mean length of the traces
    men = 0
    for i in range(len(log)):
        men += len(log[i])
    print "the mean lenght of traces:", men / len(log)

    return log, case_name
##########################################################################
#This function is for writing to excel
def Write_to_Excel(alignment, destination):

    header=["Case_id", "Time", "Model Fitness", "Replayability", "Alignment"]

    #Openning a file
    f=XL.Workbook(destination+"/result.xlsx")
    worksheet=f.add_worksheet()

    row=0
    col=0

    #writing headers
    for item in header:
        worksheet.write(row, col, item)
        col+=1

    #Writing the alignment
    temp=''
    for move in alignment:
        if(">>" not in move):
            temp+="[L/M]"+move[0].split("T_")[1]+"|"
        elif(move[0]==">>"):
            temp += "[M]" + move[1].split("T_")[1] + "|"
        elif (move[1] == ">>"):
            temp += "[L]" + move[0].split("T_")[1] + "|"


    col=header.index("Alignment")
    row+=1
    worksheet.write(row,col,temp)

    f.close()

###################################################
#This method is not used!
def Reading_PNML2(model_path):




    # return place_id, place_name, place_obj
    place_id = []
    place_name = []
    place_obj = []

    transition_id = []
    transition_name = []
    transition_obj = []

    arcs = []

    temp1 = 0
    temp2 = 0
    temp3 = 0
    init_mark_model = []
    Incident_matrix = []

    # add='C:/Users/University/Desktop/New folder 2/'+ MODEL+'_petri_pnml.xml'
    # add='C:/Users/University/Documents/chert/plg.pnml.xml'
    add = model_path
    tree = ET.parse(add)
    root = tree.getroot()

    # --New Added 30 August 2016-------------------------------------------
    # Some XML files have Namesapce and it is declered at the root like and represented by xmlns like: <pnml xmlns="http://www.pnml.org/version-2009/grammar/pnml">.
    # So in order to acces the tags inside the XML file, the name space must be mentioned!, The general form is like "{name_sapce}tag",
    # For example for reading places tags, the code is like below:
    #   for p in root.iter("{ http://www.pnml.org/version-2009/grammar/pnml }place"):
    #       print p
    # ------
    # First we need to extract the namespace, namely the value of xmlns
    # root.tag='{http://www.pnml.org/version-2009/grammar/pnml}pnml' but we need '{http://www.pnml.org/version-2009/grammar/pnml}'
    # For this issue we use regular expression library (re) of python
    m = re.match('\{.*\}', root.tag)
    # checking whether m is empty or no
    if (m):
        namespace = m.group(0)
    else:
        namespace = ''
    # ------------------------------------------------------------

    # Reading the places ID and its text. place_id is of the form ['n1',..] and  temp1 is of the form {'id': 'n1'}
    # place name is of the form:  ["place_0",...]

    for p in root.iter(namespace +"place"):
        temp1 = p.attrib
        place_id.append(temp1['id'])
        # for p in root.iter("place"):
        temp2 = p.find(namespace +"name").find(namespace +"text").text
        place_name.append(temp2)
        # creating place object
        temp3 = Places(temp1['id'], temp2)
        place_obj.append(temp3)

    # Reading transitions from PNML file, trnasition_id is of the form ['n318',...], temp1 is of the form {'id': 'n318'}
    # and transition_name is of the form ['A+complete',....]

    for trans in root.iter(namespace +"transition"):
        temp1 = trans.attrib
        transition_id.append(temp1['id'])
        # for trans in root.iter("transition"):
        temp2 = trans.find(namespace +"name").find(namespace +"text").text

        # This part was added to work with realistc data set, bpi2012
        # Here we changed the "_" in the name of transition with "*"
        # -------
        # some real transitions of the model is like A\\n, B\\n, we must remove \\n
        # the ones come from PLG model generator
        # temp2=temp2.strip("\\n")

        '''if (" " in temp2):
            temp2 = temp2.replace(" ", "*")

        if ("_" in temp2):
            temp2 = temp2.replace("_", "*")'''
            # -----------
        transition_name.append(temp2)
        temp3 = Transitions(temp1['id'], temp2)
        transition_obj.append(temp3)

    # Reading arcs for PNML, the lis arcs is of the form arcs=[{'source': 'n78', 'id': 'arc635', 'target': 'n447'},....]
    for ar in root.iter(namespace +"arc"):
        arcs.append(ar.attrib)





    # Calculating initial marking from PNML
    # init_mark is of the form [None, None, None, None, None, None, None, <Element 'initialMarking' at 0xa27ad0c>, None,.....]

    # init_mark_model is of the form=[None, None, None, None, None, None, None, <Element 'initialMarking' at 0x15a128d0> ,....]
    for place in root.iter(namespace +"place"):
        init_mark_model.append(place.find(namespace +"initialMarking"))

    init_mark_model_list = []
    for i in range(len(init_mark_model)):
        if (init_mark_model[i] != None):
            init_mark_model_list.append(1)
        else:
            init_mark_model_list.append(0)
    initial_place_marking = place_name[init_mark_model_list.index(1)]

    # Calculating incident matrix using Matrix method
    Incident_matrix = Matrix(transition_id, place_id, arcs)

    # Some preparations
    # transitaion_name is of the form ['A+complete',....] and transitaion_name_modified is of the form ['A',....]
    transitaion_name_modified = Preparation(transition_name)
    ##print "transition name:", transition_name

    return transition_id, transitaion_name_modified, transition_obj, place_id, place_name, place_obj, Incident_matrix, initial_place_marking
    # return place_id, place_name, place_obj



# This is a temporal method, only to modify the name of the trace, for example:
# changing  "C4Z-318346582" to "C4Z-318346582_1"
def XES_trace_name_modify(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # --New Added 30 August 2016-------------------------------------------
    # Some XML files have Namesapce and it is declered at the root like and represented by xmlns like: <pnml xmlns="http://www.pnml.org/version-2009/grammar/pnml">.
    # So in order to acces the tags inside the XML file, the name space must be mentioned!, The general form is like "{name_sapce}tag",
    # For example for reading places tags, the code is like below:
    #   for p in root.iter("{ http://www.pnml.org/version-2009/grammar/pnml }place"):
    #       print p
    # ------
    # First we need to extract the namespace, namely the value of xmlns
    # root.tag='{http://www.pnml.org/version-2009/grammar/pnml}pnml' but we need '{http://www.pnml.org/version-2009/grammar/pnml}'
    # For this issue we use regular expression library (re) of python
    m = re.match('\{.*\}', root.tag)
    # checking whether m is empty or no
    if (m):
        namespace = m.group(0)
    else:
        namespace = ''

      # ------------------------------------------------------------
    print "The name space is:",namespace

    k = 0
    for t in root.iter(namespace +"trace"):
        for name in t.iter(namespace +"string"):
            print name.attrib['key']
            if (name.attrib['key'] == 'concept:name'):
                name.attrib['value'] = name.attrib['value'].replace("_", "-")
                name.attrib['value'] = name.attrib['value'] + "_" + str(k)
                k = k + 1
                break

    tree.write('C:/Users/taymouri/Desktop/model temp/trash2/modified.xml')





