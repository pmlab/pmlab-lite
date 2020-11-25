from dateutil.parser import parse
import gzip
from lxml import etree
from pmlab_lite.log import *
from . import constants as  c
from tqdm import tqdm
import re


def import_from_xes(file):
    """
        Reads a *.xes-file and returns it as a log data structure. 

        Args:
            file: string literal path to a *.xes-file 

        Returns:
            log: the log represented as a data structure as in pmlab_lite.log
    """

    log = EventLog()

    if isinstance(file, str):
          filename = file
          if filename.endswith('.gz'):
              file = gzip.open(filename, 'rb')
          else:
              pass  # Just send the filename to xmltree.parse
    else:
          filename = file.name

    namespace = {'xes': 'http://www.xes-standard.org/'}
    ns=''
    tree = etree.parse(file)
    root = tree.getroot()
    if (namespace['xes'] in root.tag):          #some xes files have namespaces before their tags so find can't normally find tags, e.g. bpi12 and bpi14 log
        ns += 'xes:' 

    traces = root.findall(ns+'trace', namespace)
    classifiers = root.findall(ns+'classifier', namespace)

    if classifiers:
        for classifier in classifiers:
            name = classifier.attrib['name']
            attributes = classifier.attrib['keys']
            #resolve special case: wo 
            if "'" in attributes:
                attributes = re.findall(r'\'(.*?)\'', attributes)
            else:
                attributes = attributes.split()
            log.classifiers[name] = attributes 

    # parse all traces in the log
    for trace in tqdm(traces):
        
        # extract the case id
        if trace.find(ns+'string[@key="concept:name"]', namespace) is not None:
            case_id = trace.find(ns+'string[@key="concept:name"]', namespace).attrib['value']
        else:
            case_id = None
        
        # parse all events in the trace
        for evnt in trace.findall(ns+'event', namespace):
            
            event = Event(case_id)
            """ # extract the activity name and construct the new event                                 #why is there a special case for concept:name??
            if evnt.find(ns+'string[@key="concept:name"]', namespace) is not None:
                concept_name = evnt.find(ns+'string[@key="concept:name"]', namespace).attrib['value']
                event["concept:name"] = concept_name """

            # parse all string attributes
            for a in evnt.findall(ns+'string', namespace):
                # we need to exclude the name of the event
                #if a.attrib['key'] != "concept:name":
                event[a.attrib['key']] = a.attrib['value']
            
            # parse all integer attributes
            for a in evnt.findall(ns+'int', namespace):
                event[a.attrib['key']] = int(a.attrib['value'])
            
            # parse all date attributes
            for a in evnt.findall(ns+'date', namespace):
                event[a.attrib['key']] = parse(a.attrib['value'])
            
            # parse all boolean attributes
            for a in evnt.findall(ns+'boolean', namespace):
                event[a.attrib['key']] = a.attrib['value'].lower() == 'true'
            
            log.add_event(event)

    return log


def export_to_xes(log: EventLog, target_path: str):
    """Exprots an EventLog structure as stored by pmlab_lite to an *.xes-file.

    Args:
        log (EventLog): The Event Log to be exported.
        target_path (str): The path- and filename of the exported *.xes-file, e.g. "some_file.xes".
    """
    
    root = etree.Element('log')

    __export_classifiers(log, root)
    __export_traces(log, root)

    tree = etree.ElementTree(root)

    tree.write(target_path, pretty_print=True, xml_declaration=True, encoding="utf-8")

def __export_classifiers(log: EventLog, root):
    for classi in log.classifiers.keys():
        classi_attributes = ['\'' + attr + '\'' if ' ' in attr else attr for attr in log.classifiers[classi]]
        classifier = etree.SubElement(root, 'classifier')
        
        classifier.set('name', classi)
        classifier.set('keys', " ".join(classi_attributes))

def __export_traces(log: EventLog, root):
    #if we had trace attributes we would also add them here
    for trc in log.traces.keys():
        trace = etree.SubElement(root, 'trace')
        __export_events_of_trace(log.traces[trc], trace)

def __export_events_of_trace(trc: list, trace):
    for evnt in trc:
        event = etree.SubElement(trace, 'event')
        __export_attributes(evnt, event)

#this function should be made more generic as log, trace... can lso hold attributes to be exported
def __export_attributes(evnt: dict, event):
    for log_attr, log_attr_val in evnt.items():
        log_attr_type = type(log_attr_val).__name__
        xes_attr_type = __log_to_xes_attribute_type(log_attr_type)
        xes_attr_value = __get_xes_attribute_value(xes_attr_type, log_attr_val)

        attribute = etree.SubElement(event, xes_attr_type)
        attribute.set('key', log_attr)
        attribute.set('value', xes_attr_value)

def __log_to_xes_attribute_type(log_attr_type) -> str:
    if log_attr_type in c.xes_typenames:
        return c.xes_typenames[log_attr_type]
    else:
        return 'string'

def __get_xes_attribute_value(xes_attr_type, log_attr_val):
    if xes_attr_type == 'date':
        return log_attr_val.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + log_attr_val.strftime('%z')[0:3] + ':' + log_attr_val.strftime('%z')[3:]
    elif xes_attr_type == 'boolean':
        return str(log_attr_val).lower()
    else:
        return str(log_attr_val)

def load_xes(file):
    """A faster load of a log, which only stores the attributes name, timestamp, resource and transition per event.
       The data structure of a log then looks as follows:
        log = [ ... 
                {'trace_id: 12, events: [ {'name': a, 'timestamp': b, 'resource': c, 'transition': d  }, {...}, ...] },
                {'trace_id: 13, events: [ {'name': a, 'timestamp': b, 'resource': c, 'transition': d  }, {...}, ...] },
                ... ]

    Args:
        file (string): path to a *.xes-file

    Returns:
        list: The log as a dats strucure described above
    """

    log = []
    
    tree = etree.parse(file)
    data = tree.getroot()
    
    # find all traces
    traces = data.findall('{http://www.xes-standard.org/}trace')
    
    for t in tqdm(traces):
        trace_id = None
        
        # get trace id
        for a in t.findall('{http://www.xes-standard.org/}string'):
            if a.attrib['key'] == 'concept:name':
                trace_id = a.attrib['value']
        
        events = []
        # events
        for event in t.iter('{http://www.xes-standard.org/}event'):
            
            e = {'name': None, 'timestamp': None, 'resource': None, 'transition': None}
            
            for a in event:
                e[a.attrib['key'].split(':')[1]] = a.attrib['value']

            events.append(e)
        
        # add trace to log
        log.append({'trace_id': trace_id, 'events': events})

    return log