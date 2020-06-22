import os
import pickle
import sys


# Gets current path SHOULD BE IN raw-images folder - we check.
fileDir = os.path.dirname(os.path.realpath(__file__))
print('Current Directory:\n\t' + fileDir)


# Read in survey data
try:
    with open("/data/Q0004/SurveysToZip.txt") as f:
        valid_surveys = f.readlines()

    valid_surveys = [x.strip() for x in valid_surveys]

except FileExistsError as err:
    print(err)
    print("Please create a file called SurveysToZip.txt")
    print("On each line include a survey you would like to zip.")
    sys.exit() # Break program


# Gets the list of folders
folderList = [x[0] for x in os.walk(fileDir)]
try:
    folderList.remove(fileDir)
except Exception as err:
    print(err)

# Create an empty dictionary to store the list of files
fullFiles = {}

for folderPath in folderList:

    if folderPath[0] == '.':
        continue

    try:
        survey = folderPath.split('_')[-2]
    except IndexError as err:
        print("Error encountered...")
        print(folderPath)
        print(err)
        print("Continuing.")
        continue

    # Check if survey is one we are interested in.
    if survey not in valid_surveys:
        continue


    # Print current survey
    print('Current Survey: ' + str(survey))

    # Get a list of all the images
    imagesList = os.listdir(folderPath)

    # Save to a dictionary
    fullFiles.update({folderPath: imagesList})


# dump the pickle

pickle_out = open('FileList.pickle', 'wb')
pickle.dump(fullFiles, pickle_out)
pickle_out.close()

print('--- Finished ---')
