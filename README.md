# pmlab-lite

[![PyPI version](https://badge.fury.io/py/pmlab-lite.svg)](https://badge.fury.io/py/pmlab-lite)
[![Certificate: XES](https://img.shields.io/badge/Certificate-XES-brightgreen.svg)](https://www.tf-pm.org/news/pmlab-lite-0-4-5-has-been-xes-certified)
[![License: MIT](https://img.shields.io/badge/License-GPL-brightgreen.svg)](https://opensource.org/licenses/GPL-3.0)

---
A Process Mining scripting environment.
Containing the following functionalities among others:
* _Petri Net_ modelling, exploring and execution
* Reading and working with _Event Logs_
* Executing state of the art _Process Mining_ techniques
* such as the _Inductive Miner_ for _Process Model Discovery_
* or the A*-algorithm for computing _Alignments_ in _Conformance Checking_


### Installation

Install pmlab-lite from pypi using pip:
```sh
$ pip3 install pmlab-lite
```

### Testing
In the test folder involved parties can _create test files_ and _run the test files_.

Create test-files in the test-directory following the naming convention: *test_\*.py*
```sh
pmlab-lite
 ├── pmlab_lite
 │     ├── ...
 │     ├── pn
 │     │    └── ...
 │     └── __init__.py
 ├── test
 │     ├── test_pn.py
 │     ├── ...
 │     └── test_*.py
 ├── .gitignore
 ├── LICENSE
 ├── README.md
 ├── distribute_to_pypi.sh
 └── setup.py    
```

Run the test-file from the top-level-directory using following command:
``` sh
$ python3 -m unittest test.test_*
```
### Certification
[XES certified](https://www.tf-pm.org/news/pmlab-lite-0-4-5-has-been-xes-certified) by the IEEE Task Force on Process Mining.

### License
GNU General Public License 3.0
