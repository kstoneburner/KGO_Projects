"""
References:

How to combine videos using ffMPEG
https://creatomate.com/blog/how-to-join-multiple-videos-into-one-using-ffmpeg
"""



#//*** Tips for converting to EXE
#//*** https://towardsdatascience.com/how-to-easily-convert-a-python-script-to-an-executable-file-exe-4966e253c7e9

#//*** pyinstaller --onefile music.py

from rundown_player import *

import time,sys, threading, socket, binascii,  os, re
import vlc #pip install python-vlc
#import keyboard #pip install keyboard

#from pynput import keyboard #pip install pynput
#//*** Keyboard basics
#https://www.delftstack.com/howto/python/python-detect-keypress/
#//*** Threading Keyboard listener
#https://stackoverflow.com/questions/14043441/how-to-use-threads-to-get-input-from-keyboard-in-python-3
#//*** pyinstaller --onefile music.py -n kgo_digi_player_v1

#//*********************************************
#//*** SQL Section
#//*********************************************
#//*** This thread helped with the connection
#//***https://stackoverflow.com/questions/37692780/error-28000-login-failed-for-user-domain-user-with-pyodbc

#//**** Update the ODBC Driver
#//**** https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver15
import pyodbc
import datetime
import json
from datetime import date, timedelta
import pandas as pd
import numpy as np 
print(pyodbc.drivers())

#//*********************************************
#//*** SQL Setup/Initialization
#//*********************************************

#//*** Pandas Display Options
#//*** Maximize columns and rows displayed by pandas
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', None)

# Some other example server values are
# server = 'localhost\sqlexpress' # for a named instance
# server = 'myserver,port' # to specify an alternate port

#//*** These Values sre shifted to rp.config
#server = 'tcp:OM-CASF-DB01' 
#server = 'OM-CASF-DLSQL' 
# server = '10.218.97.2'
#database = 'DaletDB' 


#//*********************************************
#//*********************************************
#//*********************************************





with open('./ignore_folder/misc.json') as f:
    data = json.loads(f.read())

username = data["user"] 
password = data["password"]
del data

print(username + ":" + password)


folder_path = "./music/1_0_0 - 3pm Playlist"

music_path = "./music/"

config_filename = "rp.config"
#//*** Set Default host IP 
h_name = socket.gethostname()
HOST = socket.gethostbyname(h_name)
PORTS = [10522]
rundown_names = ["5PM Weekday"]
playout_paths = ["\\\\om-casf-dlbr06\\MEDIA"]


#//*** Clear the Screen on each action. False aids in debugging.
clear_screen = True
fullscreen = True

action_queue = []
stats = {

    #//*** Build Playlist
    "playlist" : [],
    "play_counter" : 0,
    "display_name" : "",
    "playing" : False,
    "quit" : False,
    "action" : None,
    #"socket" : socket.socket(socket.AF_INET, socket.SOCK_STREAM),
    "addr" : [],
    "selected_cut" : None,
    "cut_index" : None,
    "cut" : {},
    "active_ports" : []
    
}   

config = {
    
}

#//*** Process Config File
#//*** Allows for Comments after # sign
#//*** All values are explictly defined.
if os.path.exists(config_filename):
    print("Process Config File")
    with open(config_filename) as f:
        for line in f:
            
            #//*** strip out everything after # comment
            if "#" in line:
                line = line.split("#")[0]


            #//*** Look for lines with values:
            if "=" in line:

                key,value = line.split("=")

                #//*** Strip all whitespace from key & value
                key = key.strip()
                value = value.strip().replace("\n","")

                print(f">{key}<")
                print(f">{value}<")

                if key == "server":
                    config['server'] = value

                if key == "database":
                    config['database'] = value

# Some other example server values are
# server = 'localhost\sqlexpress' # for a named instance
# server = 'myserver,port' # to specify an alternate port
#server = 'tcp:OM-CASF-DB01' 
#server = 'OM-CASF-DLSQL' 
# server = '10.218.97.2'
#database = 'DaletDB' 



#//*** Connect to DataBase
cnxn = pyodbc.connect('Trusted_Connection=yes;DRIVER={SQL Server};SERVER='+config['server']+';DATABASE='+config['database']+';UID=user;PWD=password')
#cursor = cnxn.cursor()


#//*** Build the Date Range to search for Shows.
#//*** Start with Shows based on Today Only
#//*** This *can* and probably will need to scale to future dates.

offset_days = 0
#//*** Today's date range starts with today's date beginning at 00:00:00 and Tomorrow's Date at 00:00:00
todayStart = str(date.today() + timedelta(days=offset_days))
todayEnd = str(date.today() + timedelta(days=offset_days+1))
date_range = f"'{todayStart}T00:00:00' AND '{todayEnd}T00:00:00'"

today_shows = []



for rundown_target in rundown_names:



    #//*** Query the Database to build relevant info to build a playlist
    #//*** From rundown_player.py
    rp = build_rundown_info(rundown_target,date_range,config,cnxn)



    print(rp['storyOrder'])

    for title_id in rp['storyOrder']:
        #print(title_id)
        story = rp['stories'][title_id]
        out = ""
        out += story['pageNumber'] + " " + story['title'] + "\t" 
        for filename in story['mos']:
            out += filename + ".mxf "
        print(out)
        #print("=======")




