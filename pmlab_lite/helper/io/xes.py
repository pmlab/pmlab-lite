import gzip
import xml.etree.ElementTree as xmltree
from pmlab_lite.log import *


def import_from_xes(file):
    """Load a log from the XES format.

    [filename] can be a file or a filename."""
    if isinstance(file, str):  # a filename
        filename = file
        if filename.endswith('.gz'):
            file = gzip.open(filename, 'rb')
        else:
            pass  # Just send the filename to xmltree.parse
    else:
        filename = file.name
    tree = xmltree.parse(file)
    root = tree.getroot()
    traces = root.findall('{http://www.xes-standard.org/}trace')
    imported_log = EventLog()
    for t in traces:
        case_id = t.find('{http://www.xes-standard.org/}string[@key="concept:name"]').attrib['value']
        for e in t.findall('{http://www.xes-standard.org/}event'):
            activity_name = e.find('{http://www.xes-standard.org/}string[@key="concept:name"]').attrib['value']
            timestamp = e.find('{http://www.xes-standard.org/}date[@key="time:timestamp"]').attrib['value']
            event = Event(activity_name, case_id)
            for a in e:
                if a.attrib['key'] != "concept:name":
                    event[a.attrib['key']] = a.attrib['value']
            imported_log.add_event(event)
    return imported_log


def print_log(l):
    for t in l.get_traces():
        print("TRACE:")
        for e in t:
            print("> ", e.get_activity_name(), e.get_case_id(), e.get_attributes())