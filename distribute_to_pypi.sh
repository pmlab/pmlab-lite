#!/bin/bash
#packages need for execution; run in advance if needed:
#python3 -m pip install --user --upgrade setuptools wheel
#python3 -m pip install --user --upgrade twine
#also you may need to grab the path to twine
twinePath=$(which twine)                        #if still not working (output of "which twine) is empty, run this bash script in terminal


#delete all directiories and files, that will be reuploaded / are created by sdist bdist_wheel command
rm -r build dist pmlab_lite.egg-info

#create package files 
python3 setup.py sdist bdist_wheel

#check and upload to twine
$twinePath check dist/*
$twinePath upload dist/*