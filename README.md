# UQ-Project
Python Scripts from Project to move images from UQ.

Usage:

- ID_Finder.py is used by running with python3 ID_Finder.py through command line. The file requires that ID_list.pickle is in the same directory as the ID_Finder.py script. Upon running, the console will prompt the user to input a survey and an ID - and will return an _estimate_ of the location of the file. As the ID's are ordered numerically, if the file is not in the suggested file, it may be found in one of the neighbouring files.

Known issues:

- Exitting out of scripts before they are finished has potential to cause issues
- The zip-files.py script needs to be run twice in order to work as desired. A fix for this issue was not pursued.
