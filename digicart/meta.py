#//*** Tips for converting to EXE
#//*** https://towardsdatascience.com/how-to-easily-convert-a-python-script-to-an-executable-file-exe-4966e253c7e9

#//*** pyinstaller --onefile music.py

import time,sys, threading, socket, binascii, win32gui, os
import vlc #pip install python-vlc
import keyboard #pip install keyboard

#from pynput import keyboard #pip install pynput
#//*** Keyboard basics
#https://www.delftstack.com/howto/python/python-detect-keypress/
#//*** Threading Keyboard listener
#https://stackoverflow.com/questions/14043441/how-to-use-threads-to-get-input-from-keyboard-in-python-3

#//*** pyinstaller --onefile music.py -n kgo_digi_player_v1


folder_path = "./music/1_0_0 - 3pm Playlist"

music_path = "./music/"
music_file_types = [".mp3",".wav", ".aiff"]
config_filename = "player.config"
#//*** Set Default host IP 
h_name = socket.gethostname()
HOST = socket.gethostbyname(h_name)
PORTS = [8001]


#"10.218.116.11" connectport="8760"


def listen_for_digi(input_port):   
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    if input_port not in pc['active_ports']:
        pc['active_ports'].append(input_port)
    do_action("")
    
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
               

            do_action("")
            do_ack = False
            while not pc["quit"]:
                # check for stop
                if not clear_screen:
                    print("-")
                try:
                    data = conn.recv(1024)
                    if not data:
                        break
                    if not clear_screen:
                        print("Received: ", data)

                    handleInput(data)

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