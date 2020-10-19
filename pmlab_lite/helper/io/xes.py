from dateutil.parser import parse
import gzip
#import xml.etree.ElementTree as ET      #lxml should be faster (~ factor 2.0)
from lxml import etree
from pmlab_lite.log import *
from tqdm import tqdm


def import_from_xes(file):
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
    for t in tqdm(traces):
        # extract the case id
        case_id = t.find(ns+'string[@key="concept:name"]', namespace).attrib['value']
        # parse all events in the trace
        for e in t.findall(ns+'event', namespace):
            # extract the activity name and construct the new event
            activity_name = e.find(ns+'string[@key="concept:name"]', namespace).attrib['value']
            event = Event(activity_name, case_id)
            # parse all string attributes
            for a in e.findall(ns+'string', namespace):
                # we need to exclude the name of the event
                if a.attrib['key'] != "concept:name":
                    event[a.attrib['key']] = a.attrib['value']
            # parse all integer attributes
            for a in e.findall(ns+'int', namespace):
                event[a.attrib['key']] = int(a.attrib['value'])
            # parse all date attributes
            for a in e.findall(ns+'date', namespace):
                event[a.attrib['key']] = parse(a.attrib['value'])
            # parse all boolean attributes
            for a in e.findall(ns+'boolean', namespace):
                event[a.attrib['key']] = a.attrib['value'].lower() == 'true'
            log.add_event(event)
    
    return log