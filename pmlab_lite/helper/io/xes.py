from dateutil.parser import parse
import gzip
#import xml.etree.ElementTree as ET      #lxml should be faster (~ factor 2.0)
from lxml import etree
from pmlab_lite.log import *
from tqdm import tqdm


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

    # parse all traces in the log
    for trace in tqdm(traces):
        
        # extract the case id
        case_id = trace.find(ns+'string[@key="concept:name"]', namespace).attrib['value']
        
        # parse all events in the trace
        for evnt in trace.findall(ns+'event', namespace):
            
            # extract the activity name and construct the new event
            concept_name = evnt.find(ns+'string[@key="concept:name"]', namespace).attrib['value']
            event = Event(concept_name, case_id)

            # parse all string attributes
            for a in evnt.findall(ns+'string', namespace):
                # we need to exclude the name of the event
                if a.attrib['key'] != "concept:name":
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
    
    log.len = len(log.traces)
    log.num_events = len(log.events)

    return log


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