import os
import time
import json
from pprint import pprint


root_filename = "IGNITE"

def find_most_recent_file(directory):
    # Ensure the target directory exists and is accessible
    if not os.path.isdir(directory):
        print(f"Error: The directory '{directory}' does not exist or is inaccessible.")
        return None
    
    most_recent_file = None
    last_modified_time = 0.0  # Time in seconds since epoch

    try:
        for filename in os.listdir(directory):
            if ".json" not in filename.lower():
                continue
            if root_filename.lower() not in filename.lower():
                continue
            full_path = os.path.join(directory, filename)
            if os.path.isfile(full_path):
                mod_time = os.path.getmtime(full_path)
                if mod_time > last_modified_time:
                    last_modified_time = mod_time
                    most_recent_file = filename
    except Exception as e:
        print(f"An error occurred while accessing the directory: {e}")
        return None

    return most_recent_file, last_modified_time, full_path

def main():
    target_dir = r"L:\Vinten\Exports"
    result = find_most_recent_file(target_dir)
    
    if result == None:
        #//*** No Results Found Quit Here
        print("No files found in the directory.")
        return

    most_recent, mod_time, full_path = result
    formatted_mod_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mod_time))
    print(f"The most recent file is '{most_recent}' (last modified on {formatted_mod_time}).")

    # Open the JSON file for reading
    with open(full_path, 'r') as f:
        # Load its contents into a Python dictionary
        vinten = json.load(f)

    # Now, data contains the parsed JSON content
    print(vinten['ModuleData']['GridModule'])
    print(vinten['ModuleData']['GridModule'].keys())
    print(vinten.keys())
    print(vinten['ShotConfigs'])




if __name__ == "__main__":
    main()