### xes element constants
EVE = 'event'
TRC = 'trace'
LOG = 'log'
EXT = 'extension'
GLB = 'global'
SCP = 'scope'
CLS = 'classifier'
PRX = 'prefix'
URI = 'uri'
NME = 'name'
KEY = 'key'
VAL = 'value'
KYS = 'keys'
VLS = 'values'
CLN = 'children'
BOL = 'boolean'
INT = 'int'
FLT = 'float'

STR = 'string'
DTE = 'date'

### holds the equivalent xes type names for the python type names
xes_typenames = {"str": 'string',
                 "datetime": 'date',
                 "Timestamp": 'date',
                 "int": 'int',
                 "float": 'float',
                 "bool": 'boolean',
                 "dict": 'list'
                }

NAMESPACES = {'xes': 'http://www.xes-standard.org/'}
ATTR_TYPES = ['string', 'date', 'boolean', 'int']

### lxml iterparse constants
START = 'start'
END = 'end'
