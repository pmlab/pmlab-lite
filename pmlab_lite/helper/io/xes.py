from dateutil.parser import parse
import gzip
from lxml import etree
from pmlab_lite.log import Event, EventLog
from . import constants as  c
from tqdm import tqdm
import re

NAMESPACES = {'xes': 'http://www.xes-standard.org/'}
ATTR_TYPES = ['string', 'date', 'boolean', 'int']

def import_from_xes(file):
    """
        Reads a *.xes-file and returns it as a log data structure. 

        Args:
            file: string literal path to a *.xes-file 

        Returns:
            log: the log represented as a data structure as in pmlab_lite.log
    """

    filename = __check_file_type(file)
    log = EventLog()
    tree = etree.parse(file)
    root = tree.getroot()
    ns = __check_namespace(root, 'xes')

    __import_extensions(log, root,ns)
    __import_globals(log, root,ns)
    __import_classifiers(log, root, ns)
    __import_log_attributes(log, root, ns)
    __import_traces(log, root, ns)

    return log

def __import_extensions(log: EventLog, root, ns: str):
    for ext in root.findall(ns+'extension', NAMESPACES):
        log.extensions[ext.attrib['name']] = {'prefix': ext.attrib['prefix'], 'uri': ext.attrib['uri']}

def __import_globals(log: EventLog, root, ns: str):
    globals = root.findall(ns+'global', NAMESPACES)
    for g in globals:
        scope = g.attrib['scope']
        log.globals[scope] = {}
        for attr_type in ATTR_TYPES:
            for attr in g.findall(ns+attr_type, NAMESPACES):
                key, value = __get_xes_key_value(attr, attr_type)
                log.globals[scope][key] = value

def __import_classifiers(log: EventLog, root, ns: str):
    classifiers = root.findall(ns+'classifier', NAMESPACES)

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

def __import_log_attributes(log: EventLog, root, ns: str):
    for attr_type in ATTR_TYPES:
        for attr in root.findall(ns+attr_type, NAMESPACES):
            key, value = __get_xes_key_value(attr, attr_type)
            log.metadata[key] = value

def __import_traces(log: EventLog, root, ns: str):
    traces = root.findall(ns+'trace', NAMESPACES)

    for trace in tqdm(traces):
        
        # extract the case id
        if trace.find(ns+'string[@key="concept:name"]', NAMESPACES) is not None:
            case_id = trace.find(ns+'string[@key="concept:name"]', NAMESPACES).attrib['value']
        else:
            case_id = None
        log.add_trace(case_id)
        
        __import_trace_attributes(log, case_id, trace, ns)
        __import_events(log, case_id, trace, ns)

def __import_trace_attributes(log: EventLog, case_id, root, ns: str):
    for attr_type in ATTR_TYPES:
        for attr in root.findall(ns+attr_type, NAMESPACES):
            key, value = __get_xes_key_value(attr, attr_type)
            log.traces[case_id][key] = value

def __import_events(log: EventLog, case_id, root, ns):
    for e in root.findall(ns+'event', NAMESPACES):
            
        event = Event(case_id)

        for attr_type in ATTR_TYPES:
            for attr in e.findall(ns+attr_type, NAMESPACES):
                key, value = __get_xes_key_value(attr, attr_type)
                event[key] = value

        log.add_event(event)

def __get_xes_key_value(xes_attr, attr_type):
    """
        Parses XES Attributes depending on their respective data type.
        
        Returns the key, value as strings.
    """
    key = xes_attr.attrib['key']

    if attr_type == 'date':
        value = parse(xes_attr.attrib['value'])
    elif attr_type == 'int':
        value = int(xes_attr.attrib['value'])
    elif attr_type == 'boolean':
        value = xes_attr.attrib['value'].lower() == 'true'
    else:
        value = xes_attr.attrib['value']

    return key, value 

def __check_file_type(file) -> str:
    """
        Checks for possiblities of files to input in the importer. 
        
        Returns the needed filename as a string.
    """

    if isinstance(file, str):
        filename = file
        if filename.endswith('.gz'):
            file = gzip.open(filename, 'rb')
        else:
            pass  # Just send the filename to xmltree.parse
    else:
        filename = file.name

    return filename

def __check_namespace(root, namespace: str) -> str:
    """ 
        Checks for a special case of namespaces that occur in some XES files.
        They have NAMESPACES before their tags so "etree.find" can't normally find tags, e.g. bpi12 and bpi14 log.

        Returns the needed namespace tag as a String.
    """

    if (NAMESPACES[namespace] in root.tag):
        return 'xes:'
    else:
        return ''


def export_to_xes(log: EventLog, target_path: str):
    """Exprots an EventLog structure as stored by pmlab_lite to an *.xes-file.

    Args:
        log (EventLog): The Event Log to be exported.
        target_path (str): The path- and filename of the exported *.xes-file, e.g. "some_file.xes".
    """
    
    root = etree.Element('log')

    __export_extensions(log, root)
    __export_globals(log, root)
    __export_classifiers(log, root)
    __export_log_attributes(log, root)
    __export_traces(log, root)

    tree = etree.ElementTree(root)
    tree.write(target_path, pretty_print=True, xml_declaration=True, encoding="utf-8")

def __export_extensions(log: EventLog, root):
    for key in log.extensions:
        extension = etree.SubElement(root, 'extension')
        extension.set('name', key)
        extension.set('prefix', log.extensions[key]['prefix'])
        extension.set('uri', log.extensions[key]['uri'])

def __export_globals(log: EventLog, root):
    for scope in log.globals:
        g = etree.SubElement(root, 'global')
        g.set('scope', scope)
        __export_attributes(log.globals[scope], g)

def __export_classifiers(log: EventLog, root):
    for classi in log.classifiers.keys():
        classi_attributes = ['\'' + attr + '\'' if ' ' in attr else attr for attr in log.classifiers[classi]]
        classifier = etree.SubElement(root, 'classifier')
        
        classifier.set('name', classi)
        classifier.set('keys', " ".join(classi_attributes))

def __export_log_attributes(log: EventLog, root):
    __export_attributes(log.metadata, root)

def __export_traces(log: EventLog, root):
    for case_id in log.traces.keys():
        trace = etree.SubElement(root, 'trace')
        trace_attr = {key:log.traces[case_id][key] for key in log.traces[case_id] if key!='events'} #don't consider the events as a trace attribute, alternate solution: make all atributes a subdict
        __export_attributes(trace_attr, trace)
        __export_events_of_trace(log.traces[case_id]['events'], trace)

def __export_events_of_trace(trc: list, root):
    for evnt in trc:
        event = etree.SubElement(root, 'event')
        __export_attributes(evnt, event)

def __export_attributes(attributes: dict, root):
    for log_attr, log_attr_val in attributes.items():
        log_attr_type = type(log_attr_val).__name__
        xes_attr_type = __log_to_xes_attribute_type(log_attr_type)
        xes_attr_value = __get_xes_attribute_value(xes_attr_type, log_attr_val)

        attribute = etree.SubElement(root, xes_attr_type)
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