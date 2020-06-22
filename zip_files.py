import os
import sys
import argparse
import pickle
import shutil
# import tarfile # No longer needed.
import csv
import time

# See file structure below

# NOTES:
# Check if a file is size = 0. If so check what to do with it.

# Ideally we should do this when we zip it up.

# Q0004
# |
# L zipup.py <- Needs to be placed here
# |
# L raw-images-AUS
# | |
# | L Survey Folders
# |   |
# |   L Left
# |   |
# |   L Right
# |   |
# |   L Down
# |
# L raw-images-IndianOcean
# | |
# | L Survey Folders
# |
# L raw-images-Pacific
# | |
# | L Survey Folders
# |
# L raw-images-Asia
# | |
# | L Survey Folders
# |
# L raw-images-Atlantic
# | |
# | L Survey Folders

regions = ['IndianOcean', 'AUS', 'Pacific', 'Asia', 'Atlantic']


"""
FUNCTIONS ---------------------------------------------------------------------
"""

def get_directory_size(directory):
    """Returns the `directory` size in bytes."""
    total = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total += os.path.getsize(fp)

    return total

def get_file_size(directory):
    """Returns the `file` size in bytes."""

    try:
        st = os.stat(directory)
        return st.st_size
    except:
        return -1

def make_tarfile(output_filename, source_dir):
    """Creates a .tgz file with no return"""
    # Make a check as to whether the file already exists.
    if not os.path.exists(output_filename):
        global cores
        tar_str = "tar cf - " + source_dir + " | pigz -p " + str(cores) + " --fast > " + output_filename
        print("Zipping: " + source_dir)
        start = time.time()
        os.system(tar_str)
        end = time.time()
        print("Finished: " + str(round(end-start, 3)) + " seconds.")

def save_outputs():
    print('PREPARING TO SAVE OUTPUTS')
    # Grab all variables we need.
    global csv_output
    global file_name_list
    global file_path_list
    global unique_csv_output
    global unique_csv_folder

    # Begin saving
    print("OPENING FILE")
    with open(csv_output, 'a') as csv_file:
        print("SAVING OUTPUTS")
        csv_writer = csv.writer(csv_file)
        for name, path in zip(file_name_list, file_path_list):
            csv_writer.writerow([name, path])

        print("FINISHED SAVING OUTPUTS")

    print("FILE CLOSED")

    print("OPENING FILE")
    with open(unique_csv_output, 'a') as csv_file:
        print("SAVING OUTPUTS")
        csv_writer = csv.writer(csv_file)
        for unique_folder in unique_csv_folder:
            csv_writer.writerow(unique_folder)

        print("FINISHED SAVING OUTPUTS")

    print("FILE CLOSED")

def inputCores():
    message = "Please input the number of cores as 1, 2, 3"
    while True:
        try:
            userInput = int(input(message))
        except ValueError:
            print("Not an interger!")
            continue
        else:
            if userInput == -1:
                print("opting to exit")
                sys.exit()
            elif (userInput <= 0) or (userInput >= 4):
                print("Needs to be 1, 2, or 3.")
                continue
            else:
                return userInput
                break

def pause_wait_for_input():
    print("SURVEY DIRECTION FINISHED - PAUSING FOR 30 seconds")
    print("PLEASE INTERRUPT USING ctrl + c AFTER THE TIMER STARTS AND BEFORE" )
    print("IT FINISHES")
    print("TIMER STARTING")
    global cores
    try:
        for countdown in range(30):
            print(str(30 - countdown) + ' seconds')
            time.sleep(1)
    except KeyboardInterrupt:
        print("Interrupted.")
        print("If you would like to stop the program please enter -1")
        return inputCores()

    return cores





"""
END FUNCTIONS -----------------------------------------------------------------
"""

parser = argparse.ArgumentParser(description = 'Inputs for zipping files')

parser.add_argument("-region",
                    type = str,
                    help = 'Select region from: ' + ' '.join(regions))

parser.add_argument("-test",
                    type = bool,
                    default = False,
                    help = "To test the file before committing.")

parser.add_argument("-cores",
                    type = int,
                    default = 3,
                    help = "The number of cores the zipping function uses through pigz")

# Current Directory
# init_dir = os.path.join('data', 'Q0004')
init_dir = os.path.dirname(os.path.realpath(__file__))
# This should come out as /data/Q0004

# Now I need to look at the regions:
region = parser.parse_args().region

# get test status
TESTRUN = parser.parse_args().test

# Cores
cores = parser.parse_args().cores

if (cores < 1) or (cores > 3):
    print('Incorrect number of cores selected.')
    print('If you would like to exit enter -1')
    cores = inputCores()

# Check the current region is correct
if region not in regions:
    print('Error: Please select a region from:\n' + ' '.join(regions))
    print('You chose: ' + region)
    sys.exit()
else:
    output = os.path.join(init_dir, 'raw-images-' + region + '-tar')
    # Make the folder for the outputs.
    if not os.path.exists(output): os.makedirs(output)
    region_dir = os.path.join(init_dir, 'raw-images-' + region)


"""
Create initial dictionaries and values
"""

# Max images in folders
max_images_in_folders = 50

file_name_list = []
file_path_list = []

"""
Saving images - create a csv which has image name (should be surveyID_dir.CR2)
in the first column and then the second column would be the file location.
"""
# Text document name:
csv_output = os.path.join(init_dir, 'Zipping_Outputs', region)
if TESTRUN: csv_output += '/TEST'

try:
    os.makedirs(csv_output)
except FileExistsError:
    pass
except KeyboardInterrupt:
    sys.exit()
except Exception as err:
    print("Unexpected error, except it was expected, and thus excepted.")
    print(err)
    print('saving instead in initial folder')
    print('10 second cooldown begins now.')
    print(time.sleep(10))
    csv_output = init_dir

# Unique list
unique_csv_folder = []
unique_csv_output = os.path.join(csv_output, 'UniqueFileLocations_'+region + '.csv')

# Update csv_output with name (.csv name)
csv_output = os.path.join(csv_output, 'FileLocations_' + region + '.csv')

# Read in survey data.
if not os.path.exists(os.path.join("data", "Q0004", "SurveysToZip.txt")):
    print("Please create a file called SurveysToZip.txt")
    print("On each line include a survey you would like to zip.")
    sys.exit() # Break program
else:
    with open(os.path.join("data", "Q0004", "SurveysToZip.txt")) as f:
        valid_surveys = f.readlines()

    valid_surveys = [x.strip() for x in valid_surveys]


if os.path.exists(region_dir):
    surveyList = next(os.walk(region_dir))[1]
else:
    print("Path does not exist")
    print(region_dir)
    sys.exit() # break program because no folder is there.


"""
-------------------------------------------------------------------------------
*                   Begin the for loop over all surveys.                      *
-------------------------------------------------------------------------------
"""


for survey_folder in surveyList:

    # Get current survey path save as pwd_survey
    pwd_survey = os.path.join(region_dir, survey_folder)
    print('Current Folder: ' + pwd_survey)

    # Get the survey number, saved as a string
    try:
        survey = pwd_survey.split('_')[-2]
    except IndexError as err:
        print("INDEX ERROR")
        print("For the current folder we are unable to find the survey")
        print(err)
        print(pwd_survey)
        try:
            survey = str(int(survey_folder))
        except ValueError as err_1:
            print("UNABLE TO FIND SURVEY FOR FOLDER:")
            print(pwd_survey)
            continue


    # Check whether this survey is valid or not.
    if survey not in valid_surveys:
        print('Survey not in list: ' + survey + ' --- Skipping')
        continue # Skip to next


    # Now lets get the subfolders
    direction_list = next(os.walk(pwd_survey))[1]

    # If there are no subfolders then this survey is finished and we move on.
    if direction_list == []:
        print("Survey is completed: " + survey)
        continue

    # There are subfolders, now we loop over them (these will be directions)
    for direction in direction_list:

        # Get the working directory of the direction folder
        pwd_dir = os.path.join(pwd_survey, direction)
        print('Current Folder: ' + pwd_dir)

        # Get a list of folders
        folder_list = next(os.walk(pwd_dir))[1]

        # Get a list of files, and then sort the files.
        image_list = [f for f in os.listdir(pwd_dir) if (os.path.isfile(os.path.join(pwd_dir, f)) & (f[-4:] == '.CR2'))]
        image_list.sort()

        # Set a boolean for moving files and for zipping files
        #   At current zip_files is technically unused but added in for clarity
        move_files = True
        zip_folders = False

        # initialize current_folder_count to 0
        current_folder_count = 0

        # Check if there are folders.
        if len(folder_list) > 0:
            print('There are ' + str(len(folder_list)) + ' folders.')
            # Yes there are folders. Now check if there are images.
            if len(image_list) > 0:
                # Yes there are images. Now we get the folder with the highest
                # folder value and save it.
                for pre_folder in folder_list:
                    current_folder_count = max(int(pre_folder.split('_')[-1]), current_folder_count)

                    # Check if the folder has already been zipped.
                    # If it has not then we will redo them all (make_tarfile will check).
                    current_folder_zip_path = os.path.join(output, survey_folder, folder + '.tgz')
                    if os.path.exists(current_folder_zip_path):
                        zip_folders = True

            else:
                # Folders, and no images. Thus we do not move the images.
                # move_files = False

                # Maybe we don't want this.
                zip_folders = True

        # Create output location
        try:
            os.makedirs(os.path.join(output, survey_folder))
        except FileExistsError:
            pass

        """
        Zipping pre-existing folders ONLY section
        """
        if zip_folders:

            # Loop over folders in folder_list
            for folder in folder_list:
                current_folder_path = os.path.join(pwd_dir, folder) # current_folder_path
                current_folder_size = get_directory_size(current_folder_path) / 1000000
                print('Zipping directory: ' + current_folder_path)
                print('Size: ' + str(current_folder_size) + ' MB')

                current_folder_output = os.path.join(output, survey_folder, folder)
                # zip the files
                if not TESTRUN:
                    try:
                        make_tarfile(current_folder_output + '.tgz' , current_folder_path)
                    except KeyboardInterrupt:
                        print("KEYBOARD INTERRUPT ON ZIPPING: CLEANING UP")
                        print("CURRENT SURVEY = " + survey + "DIR = " + direction)
                        print("WAS ZIPPING: " + current_folder_output + '.tgz')
                        if os.path.exists(current_folder_output + '.tgz'):
                            print("FILE FOUND --- REMOVING NOW")
                            os.remove(os.path.exists(current_folder_output + 'tgz'))
                            print("REZIPPING: THIS MAY TAKE A FEW SECONDS")
                            make_tarfile(current_folder_output + '.tgs', current_folder_path)
                            # SAVING INFORMATION
                            print("FINISHED ZIPPING. SAVING RELEVANT FILES.")
                            save_outputs()
                            file_name_list.clear()
                            file_path_list.clear()
                            print("EXITTING NOW")
                            sys.exit()




        """
        Moving and Zipping section
        """
        # Initialize the number of images moved.
        image_count = 0

        # Initialize the current folder we are on (will be 0 + 1 on first loop)
        # We set to 0 and add one for dealing with potential pre-existing folders
        current_folder_count += 1

        # Initialize the current name for the zip file.
        zip_folder_name = survey + '_' + direction + '_' + str(current_folder_count)

        # Check whether this zip_folder_name exists already in list.
        if zip_folder_name not in unique_csv_folder:
            unique_csv_folder.append(zip_folder_name)

        # Loop over all images
        for image in image_list:
            # Set the current folder path (the location the image will move to)
            current_folder_path = os.path.join(pwd_dir, zip_folder_name)

            # Count the number of images we have moved.
            image_count += 1

            # Get the ID (will be specifically set)
            ID = image[-10:-6] # Should be set from here

            # For saving:
            file_name_list.append(image)
            file_path_list.append(os.path.join(survey_folder, zip_folder_name))

            # Make the directory for the current folder path.
            try:
                os.makedirs(current_folder_path)
                print('Making directory: ' + current_folder_path)
            except FileExistsError:
                pass

            # set up source and destination variables
            src = os.path.join(pwd_dir, image)
            dst = os.path.join(current_folder_path, image)

            # For testing purposes - print the source and destination then exit.
            if TESTRUN:
                print(src)
                print(dst)
                print("Exiting now.")
                sys.exit()

            # Start to move the files.
            if not TESTRUN:
                try: # Try to move the files
                    shutil.move(src, dst)
                except FileNotFoundError as err:
                    # file not found error. Ignore this...
                    print(err)
                    # Save to bad csv.
                except FileExistsError as err:
                    # If the file already exists in the folder location we don't want to move
                    print(err)
                except KeyboardInterrupt:
                    # Keyboard interrupt.
                    print("KEYBOARD INTERRUPT ON MOVE: CLEANING UP")
                    print("CURRENT SURVEY = " + survey + "DIR = " + direction)
                    # We save the outputs that we currently have and then exit.
                    save_outputs()
                    print("EXITTING NOW")
                    sys.exit()


            # If we reach the desired number of images in the sub_folder:
            if image_count == max_images_in_folders:

                # Set the location that we will move the zipped file to.
                current_folder_output = os.path.join(output, survey_folder, direction, zip_folder_name)

                # Reset the image_count to 0
                image_count = 0

                # Get sizes of files to zipped.
                current_folder_size = get_directory_size(current_folder_path) / 1000000
                print('Zipping directory: ' + current_folder_path)
                print('Size: ' + str(round(current_folder_size,2)) + ' MB')

                # If not currently in a testrun, then we will zip.
                if not TESTRUN:
                    try:
                        make_tarfile(current_folder_output + '.tgz' , current_folder_path)
                    except KeyboardInterrupt:
                        print("KEYBOARD INTERRUPT ON ZIPPING: CLEANING UP")
                        print("CURRENT SURVEY = " + survey + "DIR = " + direction)
                        print("WAS ZIPPING: " + current_folder_output + '.tgz')
                        if os.path.exists(current_folder_output + '.tgz'):
                            print("FILE FOUND --- REMOVING NOW")
                            os.remove(os.path.exists(current_folder_output + 'tgz'))
                            print("REZIPPING: THIS MAY TAKE A FEW SECONDS")
                            make_tarfile(current_folder_output + '.tgs', current_folder_path)
                            # SAVING INFORMATION
                            print("FINISHED ZIPPING. SAVING RELEVANT FILES.")
                            save_outputs()
                            file_name_list.clear()
                            file_path_list.clear()
                            print("EXITTING NOW")
                            sys.exit()

                    except Exception as err:
                        print(err)


                # Prepare for the next folder.
                # Add to the current_folder_count
                current_folder_count += 1

                # Initialize the current name for the zip file.
                zip_folder_name = survey + '_' + direction + '_' + str(current_folder_count)

                # Check whether this zip_folder_name exists already in list.
                if zip_folder_name not in unique_csv_folder:
                    unique_csv_folder.append(zip_folder_name)

            # <--- image loop

        if image_count > 0:
            # zip the file
            current_folder_path = os.path.join(pwd_dir, zip_folder_name)
            current_folder_output = os.path.join(output, survey_folder, zip_folder_name)
            current_folder_size = get_directory_size(current_folder_path) / 1000000
            print('Zipping directory: ' + current_folder_path)
            print('Size: ' + str(round(current_folder_size, 2)) + ' MB')

            # Zip the file
            try:
                make_tarfile(current_folder_output + '.tgz' , current_folder_path)
            except KeyboardInterrupt:
                print("KEYBOARD INTERRUPT ON ZIPPING: CLEANING UP")
                print("CURRENT SURVEY = " + survey + "DIR = " + direction)
                print("WAS ZIPPING: " + current_folder_output + '.tgz')
                if os.path.exists(current_folder_output + '.tgz'):
                    print("FILE FOUND --- REMOVING NOW")
                    os.remove(os.path.exists(current_folder_output + 'tgz'))
                    print("REZIPPING: THIS MAY TAKE A FEW SECONDS")
                    make_tarfile(current_folder_output + '.tgs', current_folder_path)
                    # SAVING INFORMATION
                    print("FINISHED ZIPPING. SAVING RELEVANT FILES.")
                    save_outputs()
                    file_name_list.clear()
                    file_path_list.clear()
                    print("EXITTING NOW")
                    sys.exit()

        # We save the outputs at the end of each direction
        save_outputs()
        file_name_list.clear()
        file_path_list.clear()

        # <--- direction loop (R, L, D)
        cores = pause_wait_for_input()
    # <--- survey loop
# <--- __main__

print('finished and closing')
