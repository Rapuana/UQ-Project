"""
ID finder: This script assists people in finding roughly the file locations of
images in zip files. This is not exact but will provide a rough estimate beyond
searching through trial and error. NOTE: All images are located in zip files in
numerical order so if you are searching for 950, and this script points you to
folder number 20, and the maximum ID in 20 is 945, then the image will be
located in 21.
"""

import pickle

with open('ID_list.pickle', 'rb') as f:
    try:
        ID_list = pickle.load(f)
    except FileNotFoundError as err:
        print(err)
        print('Make sure the current directory contains ID_list.pickle')



def check_ID(ID):
    # Check that the inputted ID value is correct
    try:
        int(ID)
    except ValueError:
        print('The ID needs to be a 4-digit integer')
        return False

    if len(ID) != 4:
        return False
    else:
        return True

def check_survey(survey):
    # Check that the inputted survey value is correct
    try:
        if int(survey) not in ID_list.keys():
            print('Not a valid survey')
            return False
        else:
            return True
    except ValueError:
        print('The survey needs to be a 5-digit valid integer')
        return False



# Initialize the input (for while loop)
continue_input = True

Indian = [36001,36002,36003,36004,36005,36006,36007,36008,36009,36010,36011,
36012,36013,36014,36015,36016,36017,36018,36019,36020,36021,36022,36023,36024,
36025,36026,36027,36028,36029,37001,37002,37003,37004,37005,37006,37007,37008,
37009,37010,37011,37012,37013,37014,37015,37016,37017,37018,37019,37020,37021,
37022,37025,37026,37027,37028,37029,37030,37031,37032,37033,37034,37035,37036,
37037,37038,37039,46001,46002,46003,46004,46006,46007,46008,46009,46010,46011,
46014,46015,46020,46021,46022,46027,46028,46029,46030,46031,46032,46033,46035,
46037,46038,46039]

while continue_input:
    # Get input
    survey = input("Select the survey, requires a 5 digit number: ")
    ID = input("Select the ID, requires a 4 digit number: ")

    print("You have chosen Survey: " + survey + " and ID: " + ID)

    validate = check_ID(ID) and check_survey(survey)

    if survey in Indian:
        modulo = 30
    else:
        modulo = 50

    Folder_count = 1
    ID_found = False
    # Now we take the list of ID's from the dictionary.
    for count, list_ID in enumerate(ID_list[int(survey)]):
        if (count + 1) % modulo == 0:
            Folder_count += 1

        if str(ID) == str(list_ID): # convert both to string for safety's sake
            ID_found = True
            print('The folder location for given survey and ID is: ' + str(Folder_count))
            break # Break out of loop

    if not ID_found:
        print("ID not found in the given survey")

    print("If you would like to find another ID and survey, press Enter")
    quit_script = input("Else, press 'q' to quit. ")

    if quit_script == 'q':
        continue_input = False
