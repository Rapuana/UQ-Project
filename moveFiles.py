# moveFiles

import os
import shutil
import csv
import argparse

# Console argument parser
parser = argparse.ArgumentParser(description='Inputs for moving files.')

# Set file argument which allows the user to specify a CSV script.
parser.add_argument("-file",
                    default = 'FilesToMove.csv',
                    type = str,
                    help = 'This is the file name that we use to copy files.')

# debug argument for printing extra information
parser.add_argument("-debug",
                    default = False,
                    type = bool,
                    help = 'Use optional debugging features, boolean as True or False')

# argument for squishing copy version.
parser.add_argument("-nocopy",
                    default = False,
                    type = bool,
                    help = 'If TRUE does not copy files or create folders')

# Allow the user to set a breaknumber
parser.add_argument("-breakNumber",
                    default = 0,
                    type = int,
                    help = 'Maximum files to loop over. If 0, all files are looped over')

parser.add_argument("-outputNames",
                    default = "",
                    type = str,
                    help = "prefix to the goodOutput.csv filenames")

parser.add_argument("-group",
                    default = 0,
                    type = int,
                    help = "Groups to move")

# Extract arguments and set to variables
args = parser.parse_args()
breakNumber = args.breakNumber
debug = args.debug
copyFiles = not args.nocopy
prefix = args.outputNames
group_to_move = args.group

# Set up counters
nfiles = 0
goodfiles = 0
badfiles = 0

# Set names for csv files
if not prefix:
    goodFileNameOutput = "GoodOutput.csv"
    badFileNameOutput = "BadOutput.csv"
else:
    goodFileNameOutput = prefix + "_GoodOutput.csv"
    badFileNameOutput = prefix + "_BadOutput.csv"

# Readers and writers for good and bad outputs
goodOutput = open(goodFileNameOutput, mode = 'a')
goodWriter = csv.writer(goodOutput)

# Function to write lines to goodoutput
def good(fileFrom, fileTo, writer):
    if debug:
        print('Writer Line')

    writer.writerow([fileFrom, fileTo])

# Create a function that writes to bad file. We will open and close this one
# specifically as we assume that it is not going to be used often.
def bad(fileFrom, fileTo, err):
    with open(badFileNameOutput, mode = 'a') as csvfileBad:
        badWriter = csv.writer(csvfileBad)
        badWriter.writerow([fileFrom, fileTo, err])
    csvfileBad.close()

# Open the file, and loop over all lines in it.
with open(args.file) as csvfile:
    reader = csv.reader(csvfile)
    if debug:
        print('CSV file opened!\n')
        print(reader)
    for row in reader:

        if row == []:
            continue


        if (int(float(row[0])) != group_to_move) & (group_to_move != 0): # Skip over groups we do not want to copy
            continue

        if (nfiles >= breakNumber) & (breakNumber != 0):
            break

        # Create file paths for source and destination
        dst = row[2] + '/' + row[3]
        src = row[1] + '/' + row[3]

        if os.path.exists(dst):
            # This line skips if the file has already been copied and exists.
            continue

        # Check if the file exists
        if (not os.path.exists(row[2])) and (copyFiles):
            print('Creating folder: \n\t' + row[2])
            os.makedirs(row[2])

        # Copy the files
        if not debug:
            print(' : Copying: ' + src + '\n :\t\t---> to:   ' + dst)

        try:
            if copyFiles and (not os.path.exists(dst)):
                shutil.copyfile(src, dst)

            goodfiles += 1
            good(src, dst, goodWriter)

            if debug:
                print('dst: ' + dst)
                print('src: ' + src)

        except Exception as err:
            print("-- WARNING --")
            print("File Not Copied")
            print(err)
            badfiles += 1
            bad(src, dst, err)
        except KeyboardInterrupt as err:
            break
        finally:
            nfiles += 1
            if (not debug):
                print(' :\n : -- : TOTAL : [' + str('{: >6d}'.format(nfiles)) + ']')
                print(' : -- :  GOOD : [' + str('{: >6d}'.format(goodfiles)) + ']')
                print(' : -- :   BAD : [' + str('{: >6d}'.format(badfiles)) + ']')
                print(' :')

# Print the end result.
print('Total files copied: ' + str('{: >6d}'.format(nfiles)))
print('              good: ' + str('{: >6d}'.format(goodfiles)))
print('               bad: ' + str('{: >6d}'.format(badfiles)))
csvfile.close()
goodOutput.close()
