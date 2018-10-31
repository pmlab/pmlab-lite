from dateutil.parser import parse
import gzip
import xml.etree.ElementTree as xmltree
from pmlab_lite.log import *


def import_from_xes(file):
    """Load a log from the XES format.

    [filename] can be a file or a filename."""
    if isinstance(file, str):
        filename = file
        if filename.endswith('.gz'):
            file = gzip.open(filename, 'rb')
        else:
            pass  # Just send the filename to xmltree.parse
    else:
        filename = file.name

    # construct the new event log  object
    imported_log = EventLog()

    # identify all traces in the log (assuming just one process per log)
    ns = {'xes': 'http://www.xes-standard.org/'}
    tree = xmltree.parse(file)
    root = tree.getroot()
    traces = root.findall('xes:trace', ns)

    # parse all traces in the log
    for t in traces:
        # extract the case id
        case_id = t.find('xes:string[@key="concept:name"]', ns).attrib['value']
        # parse all events in the trace
        for e in t.findall('xes:event', ns):
            # extract the activity name and construct the new event
            activity_name = e.find('xes:string[@key="concept:name"]', ns).attrib['value']
            event = Event(activity_name, case_id)
            # parse all string attributes
            for a in e.findall('xes:string', ns):
                # we need to exclude the name of the event
                if a.attrib['key'] != "concept:name":
                    event[a.attrib['key']] = a.attrib['value']
            # parse all integer attributes
            for a in e.findall('xes:int', ns):
                event[a.attrib['key']] = int(a.attrib['value'])
            # parse all date attributes
            for a in e.findall('xes:date', ns):
                event[a.attrib['key']] = parse(a.attrib['value'])
            # parse all boolean attributes
            for a in e.findall('xes:boolean', ns):
                event[a.attrib['key']] = a.attrib['value'].lower() == 'true'
            imported_log.add_event(event)
    return imported_log


def print_log(l):
    for t in l.get_traces():
        print("TRACE:")
        for e in t:
            print("> ", e.get_activity_name(), e.get_case_id(), e.values())
