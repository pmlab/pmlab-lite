from pmlab_lite.log import Event, EventLog
from . import constants as c
import ciso8601
# from datetime import datetime # datetime.fromisoformat is fast, but only implemented from >=3.7
import re
import gzip
from lxml import etree
from tqdm import tqdm
import logging

__START = c.START
__END = c.END
__actions = (__START, __END)

"""
    Note:
    The code for importing (__parse_xes_file, __parse_attribute) is inspired and partly taken from the open source process minind library pm4py (https://pm4py.fit.fraunhofer.de).
    Thanks to all involved researchers / developers, especially Alessandro Berti and Sebastiaan van Zelst, for providing the well documented
    and written code and providing this as an open source project.
"""


def import_xes(file):
    """
        Reads a *.xes-file and returns it as a log data structure.

        Args:
            file: string literal path to a *.xes-file

        Returns:
            log: the log represented as a data structure as in pmlab_lite.log
    """

    print("Processing log...")

    file = __check_file_type(file)
    f = open(file, "rb")

    context = etree.iterparse(f, events=__actions)
    tree = {} #for keeping only what we need to know (we delete elements in iterparse iterator to keep memory usage minimal)
    log = __parse_xes_file(context, tree)

    del context
    f.close()

    return log


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

def __clear_element(element, tree):
    """ Deletes an element from tree, to avoid memory explosion, when not needed anymore"""
    if element in tree:
      del tree[element]
    element.clear()
    if element.getprevious() is not None:
        try:
            del element.getparent()[0]
        except TypeError:
            pass

def __parse_date_ciso(date_str: str):
    """ Parses a date string from an xes log file to a datetime object. Uses external ciso library."""

    return ciso8601.parse_datetime(date_str)

def __parse_attribute(elem, store, key, value, tree):
  #store is basically the parent and can be:

  if len(elem.getchildren()) == 0:  #elem is leaf node, i.e. no further

    if type(store) is list:
      # changes to the store of lists: not dictionaries anymore
      # but pairs of key-values.
      store.append((key, value))
    else:
      store[key] = value

  else:
    if elem.getchildren()[0].tag.endswith(c.VLS):
      store[key] = {c.VAL: value, c.CLN: list()}
      tree[elem] = store[key][c.CLN]
      tree[elem.getchildren()[0]] = tree[elem]
    else:
      store[key] = {c.VAL: value, c.CLN: dict()}
      tree[elem] = store[key][c.CLN]

  return tree

def __parse_xes_file(context, tree):

    log = None
    trace_idx = None
    event = None
    trace_count = 0 #for trace_id

    for action, elem in tqdm(context):

        if action == __START:  # starting to read

            parent = tree[elem.getparent()] if elem.getparent() in tree else None

            if elem.tag.endswith(c.STR):
              if parent is not None:
                tree = __parse_attribute(elem, parent, elem.get(c.KEY), elem.get(c.VAL), tree)
              continue

            elif elem.tag.endswith(c.DTE):
              try:
                date = __parse_date_ciso(elem.get(c.VAL))
                tree = __parse_attribute(elem, parent, elem.get(c.KEY), date, tree)
              except TypeError:
                logging.info("failed to parse date: " + str(elem.get(c.VAL)))
              except ValueError:
                logging.info("failed to parse date: " + str(elem.get(c.VAL)))
              continue

            elif elem.tag.endswith(c.BOL):
                if parent is not None:
                    str_val = str(elem.get(c.VAL)).lower()
                    if str_val == 'true':
                        bool_val = True
                    elif str_val == 'false':
                        bool_val = False
                    else:
                        raise ValueError("failed to parse bool: " + str(elem.get(c.VAL)))
                    tree = __parse_attribute(elem, parent, elem.get(c.KEY), bool_val, tree)
                continue

            elif elem.tag.endswith(c.INT):
                if parent is not None:
                    int_val = int(elem.get(c.VAL))
                    tree = __parse_attribute(elem, parent, elem.get(c.KEY), int_val, tree)
                continue

            elif elem.tag.endswith(c.FLT):
                if parent is not None:
                    float_val = float(elem.get(c.VAL))
                    tree = __parse_attribute(elem, parent, elem.get(c.KEY), float_val, tree)
                continue

            elif elem.tag.endswith(c.EVE):
              if event is not None:
                raise SyntaxError('file contains <event> in another <event> tag')
              if trace_idx is None:
                raise SyntaxError('file contains a <event> element outside of a <trace> element (trace_id is None)')
              event = Event()
              tree[elem] = event
              continue

            elif elem.tag.endswith(c.TRC):
              if trace_idx is not None:
                raise SyntaxError('file contains <trace> in another <trace> tag')
              trace_idx = trace_count
              trace_count += 1
              log.add_trace(trace_idx)
              tree[elem] = log.traces[trace_idx]
              continue

            elif elem.tag.endswith(c.EXT):
              if log is None:
                raise SyntaxError('extension found outside of <log> tag')
              if elem.get(c.NME) is not None and elem.get(c.PRX) is not None and elem.get(c.URI) is not None:
                log.extensions[elem.attrib[c.NME]] = {c.PRX: elem.attrib[c.PRX], c.URI: elem.attrib[c.URI]}
              continue

            elif elem.tag.endswith(c.GLB):
              if log is None:
                raise SyntaxError('global found outside of <log> tag')
              if elem.get(c.SCP) is not None:
                log.globals[elem.attrib[c.SCP]] = {}
                tree[elem] = log.globals[elem.get(c.SCP)]
              continue

            elif elem.tag.endswith(c.CLS):
              if log is None:
                raise SyntaxError('classifier found outside of <log> tag')
              if elem.get(c.KYS) is not None:
                name, attributes  = elem.attrib[c.NME], elem.attrib[c.KYS]
                # resolve special case; refactor with __parse_classifier
                if "'" in attributes:
                  attributes = re.findall(r'\'(.*?)\'', attributes)
                else:
                  attributes = attributes.split()
                log.classifiers[name] = attributes
              continue

            elif elem.tag.endswith(c.LOG):
              if log is not None:
                raise SyntaxError('file contains > 1 <log> tags')
              log = EventLog()
              tree[elem] = log.attributes
              continue

        elif action == __END:

            __clear_element(elem, tree)

            if elem.tag.endswith(c.EVE):
              if trace_idx is not None:
                log.add_event(event, trace_idx)
                event = None
              continue

            elif elem.tag.endswith(c.TRC):
              trace_idx = None
              continue

            elif elem.tag.endswith(c.LOG):
              continue

    return log



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
    __export_attributes(log.attributes, root)

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
