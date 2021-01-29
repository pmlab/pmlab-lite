# pmlab-lite
---

A Process Mining scripting environment.
Containing the following functionality among other:
* _Petri Net_ modelling, exploring and execution
* Reading and working with _Event Logs_
* Executing state of the art _Process Mining_ techniques
* such as the _Inductive Miner_ for _Process Model Discovery_
* or the A*-algorithm for computing _Alignments_ in _Conformance Checking_


### Installation
pmlab-lite requires graphviz to run the helper functions that draw petri nets to .PDF-files.

So optionally get graphviz through your package manager:
```sh
$ sudo apt-get install graphviz               #example for ubuntu/debian systems
```
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

### License
GNU General Public License 3.0
