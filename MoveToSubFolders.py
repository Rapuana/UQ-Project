import os
import pickle
import shutil
import argparse
import sys

parser = argparse.ArgumentParser(description = "Inputs")

parser.add_argument("-region", type = str)

regions = ['IndianOcean', 'AUS', 'Pacific', 'Asia', 'Atlantic']

region = parser.parse_args().region

if region not in regions:
    print('Error: Please select a region from:\n' + ' '.join(regions))
    print('You chose: ' + region)
    exit()
else:
    output = os.path.join('/data', 'Q0004', 'raw-images-outputs', region)
    if not os.path.exists(output): os.makedirs(output)
    region_dir = os.path.join('/data', 'Q0004', 'raw-images-' + region)



# Survey: ImageID: _ Dir.CR2
# 46010, 46011, don't have R
# 46039 (1 missing R image)

# This requires the ID_list.pickle:

try:
    PickleIn = open('/data/Q0004/ID_list.pickle', 'rb')
    ExpectedID = pickle.load(PickleIn)
    PickleIn.close()
except FileNotFoundError as err:
    print(err)
    print('Please make sure you have ID_list.pickle in /data/Q0004/')
    sys.exit()


try:
    PickleIn = open('FileList.pickle', 'rb')
    fileDict = pickle.load(PickleIn)
    PickleIn.close()
except FileNotFoundError as err:
    print(err)
    sys.exit()

AllFilesAccountedFor = []
MissingFiles = []

Verb = False

# List of unique Directories
uniqueDir = []

# Create an empty dict for directions and badID
listOfDirections = {}
badID = {}
badMoves = {}
directoryDictionary = {}
SurveyExtras = {}

if region == 'AUS':
    Dir_map_15014 = {'a' : 'D', 'b' : 'R', 'c' : 'L'}
    Dir_map = {'a' : 'L', 'b' : 'D', 'c' : 'R'}
else: # Add other countries here
    Dir_map = {'a' : 'L', 'b' : 'D', 'c' : 'R'}


# We need to make sure that the files are correct:

Region = ''


# Read in survey data.
if not os.path.exists(os.path.join("/data", "Q0004", "SurveysToZip.txt")):
    print("Please create a file called SurveysToZip.txt")
    print("On each line include a survey you would like to zip.")
    sys.exit() # Break program
else:
    with open(os.path.join("/data", "Q0004", "SurveysToZip.txt")) as f:
        valid_surveys = f.readlines()

    valid_surveys = [x.strip() for x in valid_surveys]


for folder in fileDict.keys():

    if Region == '':
        Region = folder.split('_')[1][0:2]

    survey = folder.split('_')[-2]

    if survey not in valid_surveys:
        continue

    # Clear the dict
    listOfDirections.clear()
    uniqueDir.clear()
    directoryDictionary.clear()

    print('current Survey ' + survey)

    currentList = ExpectedID[int(survey)]

    for file in fileDict[folder]: # Now we are looping over each general term
        # Firstly check that the extension is correct IF NOT add to bad
        if file[-4:] != '.CR2':
            try:
                # Add this ID to a list
                badID[survey].append(folder + '/' + file)
            except KeyError:
                badID.update({survey: [folder + '/' + file]})

            continue


        """
        What this try statement is doing is basically saying that if our ID value is set up as expected,
        and the direction is also set up as expected then we will move the files and set up the subfolders.
        """
        try:
            ID = str(int(file[-9:-5])).zfill(4)
            Dir = file[-5]
            # If we don't have a known direction, skip.
            if Dir not in ['D', 'L', 'R']:
                if survey == '15014':
                    Dir = Dir_map_15014[Dir]
                else:
                    Dir = Dir_map[Dir]

        except ValueError:
            try:
                ID = str(int(file[-8:-4])).zfill(4)
                Dir = 'D'
            except Exception as err:
                print(err)






        # Check whether this is a unique direction, append as a string
        if Dir not in uniqueDir:
            uniqueDir.append(str(Dir))


        # Check whether the current ID is required
        if ID in currentList:
            # Yes - add it to the list
            try:
                # Check whether the ID already exists if it does we take it and add
                # to it the direction we already have
                listOfDirections[ID] = listOfDirections[ID] + str(Dir)
            except KeyError:
                listOfDirections.update({ID: str(Dir)})

        else:
            # No
            try:
                # Add this ID to a list
                badID[survey].append(folder + '/' + file)
            except KeyError:
                badID.update({survey: [folder + '/' + file]})

    """
        I also need to deal with the directories that don't have multiple directions/wrong amount
        This is mostly important for Australia.
    """

    nUnique = len(uniqueDir)
    # Firstly lets Check the number of unique directories
    if nUnique == 3:
        # Perfect
        print('Three Unique directories found.')
        print('We found: ' + ' '.join(uniqueDir))

        pass
    else:
        print('The number of unique directories is not equal to 3, but instead ' + str(len(uniqueDir)) + '\n')
        print('We found: ' + ' '.join(uniqueDir))


    print('Creating Directories now')
    for Dir in uniqueDir: # Create the directories
        try:
            os.makedirs(folder + '/' + Dir)
            print('Created: ' + folder + '/' + Dir)
        except OSError as err:
            print('--- NOT CREATED ---')
            print(err)
            print(folder + '/' + Dir)

        if os.path.exists(folder + '/' + Dir):
            pass
        else:
            print('-------------------')

        # Save the directory in a dictionary
        directoryDictionary.update({Dir: folder + '/' + Dir})


    moveCount = 0

    # Loop over all files and start moving
    for file in fileDict[folder]:

        try:
            if (folder + '/' + file) in badID[survey]:
                continue
        except KeyError:
            pass # It isn't in and we can continue!

        # Get the ID again:
        try:
            ID = str(int(file[-9:-5])).zfill(4)
            Dir = file[-5]
            # If we don't have a known direction, skip.
            if Dir not in ['D', 'L', 'R']:
                if survey == '15014':
                    Dir = Dir_map_15014[Dir]
                else:
                    Dir = Dir_map[Dir]

        except ValueError:
            try:
                ID = str(int(file[-8:-4])).zfill(4)
                Dir = 'D'
            except Exception as err:
                print(err)

        # Now we check that the current ID in the ID List has all files that are needed.
        if len(listOfDirections[ID]) != nUnique:
            # Then this is fine - just make a note by not removing it from the copied list.
            try:
                currentList.remove(ID)
                missingDir = ID
                for direction in uniqueDir:
                    if direction not in listOfDirections[ID]:
                        missingDir += direction

                currentList.append(missingDir)
            except ValueError:
                pass
            # Now we add the ID And the directions we have:

            pass
        else:
            # We have all the files we need - lets remove the ID from currentList
            try:
                currentList.remove(ID)
            except ValueError:
                pass


        # Using the ID we will check the ID LIST
        dst = directoryDictionary[Dir] + '/' + survey + ID + '_' + Dir + '.CR2'
        src = folder + '/' + file
        if Verb:
            print(src + '---->')
            print('\t\t' + dst)

        moveCount += 1
        if moveCount % 50 == 0:
            print('Current survey: ' + survey + ' - Files moved: ' + str(moveCount))

        try:
            # We will skip if the destination already exists.
            if os.path.exists(dst):
                pass
            else:
                shutil.move(src, dst)

        except FileNotFoundError as err:
            try:
                badMoves[survey].append([dst, err])
            except KeyError:
                badMoves.update({survey: [dst, err]})

    # Check if the files have all been accounted for.
    if not currentList:
        print('All files are accounted for in survey: ' + survey)
        AllFilesAccountedFor.append(survey)
    else:
        print('Some files missing for Survey: ' + survey)
        MissingFiles.append(survey)
        try:
            SurveyExtras[survey].append(currentList)
        except KeyError:
            SurveyExtras.update({survey: currentList})


# # Now I need to create a folder in Q0004 that has all the stuff for it.
# fileOut = '/data/Q0004/SurveyCheckOutputs' + Region
#
# if not os.path.exists(fileOut):
#     os.makedirs(fileOut)

if not bool(SurveyExtras): # dictionary is empty
    print("All files have been accounted for.")
else:
    pickle_out = open(os.path.join(output, 'SurveyExtras' + Region + '.pickle'), 'wb')
    pickle.dump(SurveyExtras, pickle_out)
    pickle_out.close()


pickle_out = open(os.path.join(output, 'BadMoves' + Region + '.pickle'), 'wb')
pickle.dump(BadMoves, pickle_out)
pickle_out.close()


pickle_out = open(os.path.join(output,'badID' + Region + '.pickle'), 'wb')
pickle.dump(badID, pickle_out)
pickle_out.close()


print('Finished')

try:
    print('Here are the results')
    print(' * ----------------------------- * ')
    print(' * -- ALL FILES ACCOUNTED FOR -- * ')
    for i in range(int(len(AllFilesAccountedFor) / 5)):
        print(' * ' + ' '.join(AllFilesAccountedFor[i*5:(i+1)*5]) + ' * ')



    if len(AllFilesAccountedFor) % 5 != 0:
        print(' '.join(AllFilesAccountedFor[-(len(AllFilesAccountedFor) - len(AllFilesAccountedFor) % 5):]))

    print(' * ----------------------------- * ')

    print('\n')

    print(' * ----------------------------- * ')
    print(' * - Missing IDs OR Directions - * ')
    for i in range(int(len(MissingFiles) / 5)):
        print(' * ' + ' '.join(MissingFiles[i*5:(i+1)*5]) + ' * ')

    if len(MissingFiles) % 5 != 0:
        print(' * ' + ' '.join(MissingFiles[-(len(MissingFiles) - len(MissingFiles) % 5):]))

    print(' * ----------------------------- * ')

    print('If there are any "Missing Files" please send Sam the files located in')
    print(fileOut)
except:
    pass
