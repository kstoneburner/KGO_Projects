#//*** Tips for converting to EXE
#//*** https://towardsdatascience.com/how-to-easily-convert-a-python-script-to-an-executable-file-exe-4966e253c7e9

#//*** pyinstaller --onefile music.py

import time,sys, threading, socket, binascii,  os
import vlc #pip install python-vlc
import keyboard #pip install keyboard

#//*********************************************
#//*** Original SQL Section
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
print(pyodbc.drivers())
#//*********************************************
#//*********************************************
#//*********************************************



#//*** Maximize columns and rows displayed by pandas
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', None)

# Some other example server values are
# server = 'localhost\sqlexpress' # for a named instance
# server = 'myserver,port' # to specify an alternate port
server = 'tcp:OM-CASF-DB01' 
server = 'OM-CASF-DLSQL' 
# server = '10.218.97.2'
database = 'DaletDB' 

with open('./ignore_folder/misc.json') as f:
    data = json.loads(f.read())

username = data["user"] 
password = data["password"]
del data
#cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cnxn = pyodbc.connect('Trusted_Connection=yes;DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()



folder_path = "./music/1_0_0 - 3pm Playlist"

music_path = "./music/"

config_filename = "rp.config"
#//*** Set Default host IP 
h_name = socket.gethostname()
HOST = socket.gethostbyname(h_name)
PORTS = [10522]


#//*** Clear the Screen on each action. False aids in debugging.
clear_screen = True
fullscreen = True

action_queue = []
rp = {

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
                value = value.strip()

                print(f">{key}<")
                print(f">{value}<")

                if key == "HOST":
                    HOST = value

                if key == "PORTS":
                    PORTS = []
                    for x in value.split(","):
                        try:
                            PORTS.append( int(x.strip()) )
                        except:
                            pass

                if key == "music_path":
                    music_path = value

                    if not os.path.isdir(music_path):
                        print("music_path does not point to a valid folder")
                        print("The default music sub-folder is: ./music/")
                        sys.exit()

                if key == "music_file_types":
                    music_file_types = []
                    for x in value.split(","):
                        x = x.strip()

                        if "." in x:
                            music_file_types.append(x)

                    if len(music_file_types) == 0:
                        print("No music file types specified. Did you forget the period?\n\tExample: .mp3, .wav")
                        sys.exit()

                if key == "video_file_types":
                    video_file_types = []
                    for x in value.split(","):
                        x = x.strip()

                        if "." in x:
                            video_file_types.append(x)

                if key == "clear_screen":

                    if value.lower() == "false":
                        clear_screen = False
                    
                    print(clear_screen)



def listen_for_digi(input_port):   
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    if input_port not in pc['active_ports']:
        pc['active_ports'].append(input_port)
    
    
    PORT = input_port

    with soc as s:
        s.bind((HOST, PORT))
        s.listen()
        #pc["conn"], pc["addr"] 
        conn,addr = s.accept()
        print("=====")
        
        with conn: 
            pc['addr'].append(addr[0])
            if not clear_screen:
                print(f"Connected by {pc['addr']}")
                #print(pc["conn"])
               

            do_ack = False
            while not pc["quit"]:
                # check for stop
                if not clear_screen:
                    print("-")
                try:
                    data = conn.recv(1024)
                    if not data:
                        break
                    #if not clear_screen:
                    print("Received: ", data)
                    conn.sendall(data)

                    #handleInput(data)

                    #if not do_ack:
                    #    do_ack = True
                    #    conn.sendall(data)
                except:
                    pass

        #//*** Connection Closed 

        #//*** Close Local Side of Connection
        conn.close()

        #//*** Close the Socket
        s.close()

        #//*** Remove the Address from the Connected List
        pc['addr'].remove(addr[0])

        #//*** Start New Socket listener
        listen_for_digi(PORT)

        #//*** Destroy any remaining Resources
        return

def handleInput(raw_data):
    print("HandleInput")
    print(raw_data)


print("Begin")


#keeb = threading.Thread(target = capture_keystroke_threaded)
#keeb.daemon = True
#keeb.start()

#//*** Build a listener for each port in PORTS
"""
for port in PORTS:
    listener = threading.Thread(target = listen_for_digi, args=[port])
    listener.daemon = True
    listener.start()
    time.sleep(.5)
"""
#if clear_screen:
#    os.system('cls')

"""
while True:
    time.sleep(.01)

    if len(action_queue) > 0:
        element = action_queue.pop(0)

        if element['action'] == 'DIGI_PLAY':
            do_action(element['action'],element['cut'])
        else:
            do_action(element['action'])
        #time.sleep(1)
        


    #//*** Check current Action
    if pc["action"] != None:
        do_action(pc["action"])
        pc["action"] = None

    if rp["quit"]:
        print("QUITTING")
        sys.exit()
"""
 

print("END")





