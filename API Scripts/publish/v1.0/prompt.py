
#//***************************************************************
#//*** this Stack is insecure and does not use proper SSL. 
#//*** For use on a closed network
#//***************************************************************
#//*** Local Windows Documenatation Path
#//*** \\om-casf-kgofs01\Public\Apps\Autoscript
#//***************************************************************4

#Logging Tutorial: https://realpython.com/python-logging/#starting-with-pythons-logging-module
#Powershell Live monitor Log: Get-Content someFile.txt -wait

#//*** The Login tht accesses Dalet ust have elevated privledges. Sufficient to access the database.

#//*** Compile to exe with this prompt:
#// pyinstaller --onefile prompt.py -n kgo_rosstalk_prompt


import requests, configparser, pyodbc, re, socket, logging
from urllib3.exceptions import InsecureRequestWarning
from logging.handlers import RotatingFileHandler

# Suppress the warnings from urllib3
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

#//***************************************************************

import time,sys, threading, socket, binascii, os, win32gui


# Authentication in Requests with HTTPBasicAuth

import json,os,keyboard

from pprint import pprint

#from requests.auth import HTTPBasicAuth
#from requests_oauthlib import OAuth1Session

from oauthlib.oauth2 import LegacyApplicationClient

from requests_oauthlib import OAuth2Session

logger = None #//*** defining for Global Scope

#RotatingFileHandler(filename, maxBytes=10*1024*1024, backupCount=5)
g = {
    "actions" : [], #//**** Used as an action queue. Actions are queued and triggered in order. The idea is to wait until an action is finished before starting the next.
    "quit" : False,
    "api_root" : "/api/v1/",
    "token" : None,
    'token_expires_at' : None,

    'load_pcr' : {
        "source_id" : None,
        "ro_api" : "ro/",

    },
    'dalet' : {
        'server' : None,
        'database' : None,
        'username' : None,
        'password' : None


    },
    'cue_type' : ['PGM','PST'],
    'clients' : { },

}

actions_rostalk_get = {
    "PROMPT PROMPT" : "prompt", #//*** Returns the current prompt status
}

actions_rosstalk_no_parameters = [
    "CommandJumpToTop", 
    "CommandJumpPrevStory",
    "CommandJumpNextStory",
    "CommandRecueStory",
    "CommandBlankScreenToggle",
    "CommandBlankScreenOn",
    "CommandBlankScreenOff",
    "CommandInvertVideoToggle",
    "CommandInvertVideoOn",
    "CommandInvertVideoOff",
    "CommandLivePromptToggle",
    "CommandLivePromptOn",
    "CommandLivePromptOff",
    "CommandDeactivateAutoScroll",
    "CommandCueMarkerHide",
    "CommandCueMarkerShow",
    "CommandCueMarkerToggle",
    "CommandScrollPastSoundOnTape",
    "CommandScrollPastInstruction",
    "CommandScrollPastSlugline",
    "CommandScrollToStoryText",
    "CommandNudgeReverse",
    "CommandNudgeForwards",
    "CommandActivateFixedSpeedScrollForwards",
    "CommandActivateFixedSpeedScrollReverse",
    "CommandFasterFixedSpeedScroll",
    "CommandSlowerFixedSpeedScroll",
    "CommandNextSubject",
    "CommandPreviousSubject",
    "CommandFirstSubject",
    "CommandLastSubject",
    "CommandVoiceOperatorOn",
    "CommandVoiceOperatorOff",
    "CommandVoiceOperatorToggle",
    "CommandVoiceDirectorToggle",
    "JumpToSelectedStory",
    "CommandMoveToNextRunorder",
    "CommandMoveToPreviousRunorder",
]

actions_rosstalk_with_parameters = []

actions_rostalk_post = {

    
}

def docommand():
    print("docommand")
    username = g['username']
    password = g['password']
    client_id = "KGO_PROMPT_AUTOMATION"
    client_secret = "1234"

    url = "https://172.24.124.148:443"
    url = f"https://{g['prompt_ip']}:{g['prompt_port']}"

    
    token_url = f'{url}/Token'
    api_url = url+g['api_root']

    headers = { 
        "Character encoding" : "UTF-8",
        "Data format" : "JSON"
    }


    oauth = OAuth2Session(client=LegacyApplicationClient(client_id=client_id))

    token = oauth.fetch_token(token_url=token_url,
            username=username, password=password, verify=False, client_id=client_id)

    #print("Token:")
    #print(token['access_token'])
    
    headers['Authorization'] = token['access_token']
    headers = {'Authorization': 'Bearer ' + token['access_token']}
    print(headers)

    #response = oauth.get("https://172.24.124.148:443/api/v1/prompt")
    print("=============")

    response = requests.get(api_url+"prompt", headers=headers, verify = False)
    print(response.json())

    response = requests.get(api_url+"commands", headers=headers, verify=False)
    
    commands = response.json()['commands']

    for obj in commands:
        if obj['requires_parameter'] == True:
            print(obj['name'])


    #parameters = {
    #    "name" : "CommandMoveToPreviousRunorder"
    #}

    #response = requests.post("https://172.24.124.148:443/api/v1/commands", headers=headers, verify=False, json = parameters)
    #pprint((response.json()))

    #response = requests.get(api_url+"ro/c3fd6433-c979-4fca-a4bc-707a0fde1d87", headers=headers, verify=False)
    #pprint((response.json()))

def start_listener(input_host, input_port):   
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    
    HOST = input_host
    PORT = input_port
    
    with soc as s:
        s.bind((HOST, PORT))
        s.listen()
        #pc["conn"], pc["addr"] 
        conn,addr = s.accept()
        
        
        with conn: 
           
            #//*** Receive Data, Convert to String
            data = conn.recv(1024).decode("utf-8")

            #//*** Strip trailing newline if it exisits
            if (data[-2:] == "\r\n"):
                data = data[:-2]

            
            print(f"Received + Queued: {data}")

            logger.debug(f"RECEIVE:{HOST}:{PORT} - [{data}]")

            #//*** Queue the action as a tuple, storing data and connection
            g["actions"].append((data,conn))
 
            #//*** Moved Action Handling to the Main Loop
            #action = handleInput(data)

            #handleAction(action,data,conn)

            #print("HandleInput: "+)

            #if not do_ack:
            #    do_ack = True
            #    conn.sendall(data)

        #//*** Connection Closed 

        #//*** Close Local Side of Connection
        conn.close()

        #//*** Close the Socket
        s.close()

        #//*** Remove the Address from the Connected List
        #pc['addr'].remove(addr[0])

        #//*** Start New Socket listener
        start_listener(HOST,PORT)

        #//*** Destroy any remaining Resources
        return

def handleInput(input_data):

    print (input_data)
    valid_commands = [ "LOAD_PCR_RUNDOWN", "GET_ALL_COMMANDS","prompt"]

    input_data = input_data.split(" ")[0]
    #//**** Process and Validate incomming Data
    if input_data in actions_rosstalk_no_parameters:

        #print("This is a passthru action")
        return "passthru"

    elif "LOAD_PCR_RUNDOWN" in input_data:
    #    #print("LETS LOAD a PCR Rundown")
        return "LOAD_PCR_RUNDOWN"

    elif "JUMP_TO_PCR" in input_data:
        return "JUMP_TO_PCR"

    elif input_data in valid_commands:
        #print("LETS LOAD a PCR Rundown")
        return input_data

    elif "getPairing" in input_data:
        return input_data

    else:
        print("Unknown Requested action: " + input_data)

    return None

def handleAction(action,input_data,conn):

    def validateToken():

        #//*** Get a Token if we don't have one
        if g['token'] == None:
            print("Getting Token")
            token_url = f'{url}/Token'



            oauth = OAuth2Session(client=LegacyApplicationClient(client_id=client_id))

            token = oauth.fetch_token(token_url=token_url,
                    username=username, password=password, verify=False, client_id=client_id)

            print("Token:")
            print(token)
            print(token['access_token'])

            #//*** Save Token to Global Value
            g['token'] = token['access_token']

            #//*** Store Token Expiration -100000ms (100s) to give us 100 seconds of wriggle room
            g['token_expires_at'] = int(token['expires_at'])-100000
            return
        
        #//********************************
        #//*** Validate Current Token
        #//********************************
        #print("Validating Token")
        #print(f"Now: {int(time.time())}  Expires: {g['token_expires_at']} Remaining: {g['token_expires_at'] - int(time.time())}")
        
        #//*** Validate Remaining Token Time
        #//*** If < 0, Delete the Token, Re-Run function to get new token
        if (g['token_expires_at'] - int(time.time())) <= 0:
            print("Token Expired: Delete Token and Re-Validate")
            g['token'] = None
            g['token_expires_at'] = None
            validateToken()
        else:
            #print("Token Valid")
            pass

    def getMOSSourceID():
        print("Getting MOS Source ID")
        temp_url = f"{api_url}{g['load_pcr']['ro_api']}"

        response = requests.get(temp_url, headers=headers, verify=False)

        print(response.json())

        #//*** Validate Response
        if response.ok:
            #//*** Convert to JSON
            response_obj = response.json()
            response.close()

            #//*** Validate Source Key Exists
            if 'sources' in response_obj.keys():
                
                #//*** Loop through Sources. One of these will contain the source ID.
                for source in response_obj['sources']:

                    #//*** Validate Source Name Exists
                    if 'source_type' in source.keys():

                        #//*** Check if source_name matches mos_name
                        #//*** if source['source_type'] == g['load_pcr']['mos_name']:
                        if source['source_type'] == 'MOS':
                            
                            #//*** Validate Source ID field exists
                            if 'source_id' in source.keys():
                                print(g['load_pcr'])
                                #//*** Assign source_id
                                g['load_pcr']['source_id'] = source['source_id']
                                print("Assigning source_id: " + g['load_pcr']['source_id'])
                                return True
            return False


    username = g['username']
    password = g['password']
    client_id = "KGO_PROMPT_AUTOMATION"
    url = f"https://{g['prompt_ip']}:{g['prompt_port']}"
    api_url = url+g['api_root']

    headers = { 
        "Character encoding" : "UTF-8",
        "Data format" : "JSON"
    }

    try:

        validateToken()

    except Exception as Argument:
        logger.exception(f"Error in ValidateToken. Trouble Connecting to: {url}. Is the Automation Service Running on the Prompter?")
        print(f"Trouble Connecting to: {url}")
        print("Is the Automation Service running on the Prompter?")
        print("Settings --> Automation Interface --> START")
        print("QUITTING ACTION")
        return

    #//*** Build Header with Token
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        'Authorization': 'Bearer ' + g['token']
        }
    
    print("Action: "+str(action))

    if action == None:
        return

    

    elif action == "passthru":

        print ("Sending Passthru: " + input_data)


        #//*** Send Request passing through input_data

        #//*** Build POST Parameter using PassThru Value
        parameters = { "name" : input_data }

        try:
            response = requests.post(f"{api_url}/commands", headers=headers, verify=False, json = parameters)

        except Exception as Argument:
            logger.exception(f"Trouble Connecting to: {url}.")
            print(f"Trouble Connecting to: {url}")
            print("QUITTING ACTION")
            return

        

        #//*** Returning Response Values, Currently Not Working
        print(str(response.text))
        print(response.url)
        #conn.sendall(response.text.encode("UTF-8"))

        conn.close()
    elif action == "LOAD_PCR_RUNDOWN":

        #http://10.218.116.111/server/floordirector/api/v1/shots?
        input_elems = input_data.split(" ")
        
        pcr = input_elems[1]


        if pcr in g['load_pcr'].keys():
            print("Valid PCR Found")

            #//*** Get the url and Add the Endpoint
            pcr_url = g['load_pcr'][pcr] + g['load_pcr']['fd_info_endpoint']

            print("pcr_url:")
            print(pcr_url)
            try:
                response = requests.get(pcr_url)
            except Exception as Argument:
                logger.exception("Cannot Connect to: "+pcr_url)
                print("Cannot Connect to: "+pcr_url)
                return
            response_obj = response.json()
            print("response_obj:")
            print(response_obj)

            if 'info' in response_obj.keys():
                if 'playingRundownName' in response_obj['info'].keys():
                    print("Active Rundown: " + response_obj['info']['playingRundownName'])
                    active_rundown = response_obj['info']['playingRundownName']

                    response.close()

                    if g['load_pcr']['source_id'] == None:
                        if not getMOSSourceID():
                            print("Trouble getting the MOS Source ID. Skipping Load Action")
                            return
                    temp_url = f"{api_url}{g['load_pcr']['ro_api']}{g['load_pcr']['source_id']}"


                    print("temp_url:" + temp_url)

                    #//*** Get active ro Sources
                    response = requests.get(temp_url, headers=headers, verify=False)

                    #//*** Validate Response
                    if response.ok:
                        #//*** Convert response to JSON
                        response_obj = response.json()
                        response.close()

                        pprint(response_obj)

                        print(response_obj.keys())


                        #//******************************************************
                        #//*** Search response_obj to find the active_rundown
                        #//******************************************************

                        #//*** Validate Response
                        if "runorders" in response_obj.keys():

                            runorders = response_obj['runorders']

                            for runorder in runorders:

                                #//**************************************************
                                #//*** Check if the runorder ro_type is RUNORDER
                                #//**************************************************

                                #//*** Validate Key
                                if 'ro_type' in runorder.keys():

                                    if runorder['ro_type'] == 'RUNORDER':
    
                                        #//*** Check for Active Rundown
                                        if runorder['ro_name'] == active_rundown:

                                            #//****************************
                                            #//*** Rundown FOUND get roID
                                            #//****************************

                                            if 'ro_id' in runorder.keys():
                                                ro_id = runorder['ro_id']

                                                print("ro ID Found: " + ro_id)  

                                                temp_url = f"{api_url}{g['load_pcr']['ro_api']}"

                                                response.close()
                                                

                                                parameters = {
                                                        "ro_id" : f"{ro_id}"
                                                }
                                                response = requests.post(temp_url, headers=headers, verify=False, json=parameters)

                                                #//**********************************
                                                #//*** Move Script to Text
                                                #//**********************************

                                                #//*** Validate Response
                                                if response.ok:
                                                    #//*** Convert response to JSON
                                                    response_obj = response.json()
                                                    pprint(response_obj)
                                                    time.sleep(.1)
                                                    handleAction("passthru","CommandScrollPastSlugline",conn)
                    


                else:
                    print("Error Level 2: Can't find 'playingRundownName' in Response ")
                    response.close()
            else:
                    print("Error Level 1: Can't find 'info' in Response ")
                    response.close()



        else:
            print("Invalid PCR value found in: " + input_data)
            print("Check that PCR Values are defined in config.ini. Section [Control Room] ")
    elif action == "JUMP_TO_PCR":
        input_elems = input_data.split(" ")
        
        if len(input_elems) >= 2:
            pcr = input_elems[1]
        else:
            try:
                print("Need to Pass a PCR value after JUMP_TO_PCR")
                print(f"Curent Valid PCRs are: {g['load_pcr'].keys()}")
                return
            except Exception as Argument:
                logger.exception(f"PARAMETER Error in JUMP_TO_PCR. Are PCR values defined in Config.ini?")
                print("PARAMETER Error in JUMP_TO_PCR. Are PCR values defined in Config.ini?")

        cue_type = 'PGM'

        if len(input_elems) >= 3:
            raw_type = input_elems[2]

            if raw_type in g['cue_type']:
                cue_type = raw_type
            else:
                print(f"Unknown Paramter: {raw_type}")
                print(f"Valid Parameters are: {g['cue_type']}")
                print("QUITTING ACTION")
                return
        else:
            print("Defaulting to Overdrive PGM source. Parameter: [PGM,PST] not found")

        #//*** Convert cue_type to the appropriate index value to represent Program or Preview. 
        #//*** PGM = 0, PST = 1
        if cue_type == 'PGM':
            cue_index = 0
        elif cue_type == 'PST':
            cue_index = 1
        else:
            cue_index = 0


        status = {
            'ro_id' : None,
        }

        if pcr in g['load_pcr'].keys():
            print("Valid PCR Found")
            pcr_url = g['load_pcr'][pcr]
        else:
            print(f"f{pcr} NOT found. PCRs are assigned in CONFIG.INI")
            print("QUITTING ACTION")
            return

        #//*** Get the url and Add the Endpoint
        pcr_url = g['load_pcr'][pcr] + g['load_pcr']['fd_shots_endpoint']

        print("pcr_url:")
        print(pcr_url)

        #//********************************************************
        #//*** Get Current Pagenumber and Slug From Overdrive
        #//********************************************************
        try:
            response = requests.get(pcr_url)
        except Exception as Argument:
            logger.exception(f"Cannot Connect to: {pcr_url}")
            print("Cannot Connect to: "+pcr_url)
            return
        response_obj = response.json()
        response.close()
        print("response_obj:")
        if 'shots' in response_obj.keys():
            #print(response_obj['shots'][0])
            status['od_slug'] = response_obj['shots'][cue_index]['slug']
            status['od_page'] = response_obj['shots'][cue_index]['index']

            if status['od_page'] == "NA":
                print("EMPTY PAGE Number: Probably should do some error handling here to avoid Tail-Chasing Later")
                status['od_page'] == "XXX"
        else:
            print('QUITTING JUMP_TO_PCR ACTION: Cannot find Shots in Overdrive Response' )
            return

        #//***************************************************************************************
        #//*** Get Active Show Name from Overdrive 
        #//***  (We are avoiding assumptions by getting the active rundown name fromm Overdrive)
        #//***  (And Cross-Referencing with the Mos Active Shows in the Prompter)
        #//***  (The Goal is to cue the prompter, even if the incorrect show is loaded)
        #//***************************************************************************************

        #//*** Get the url and Add the Endpoint
        pcr_url = g['load_pcr'][pcr] + g['load_pcr']['fd_info_endpoint']

        print("pcr_url:")
        print(pcr_url)
        try:
            response = requests.get(pcr_url)
        except Exception as Argument:
            logger.exception(f"Cannot Connect to {pcr_url}")
            print("Cannot Connect to: "+pcr_url)
            return

        #//*** Validate Response
        if response.ok:
            #//*** Convert response to JSON
            response_obj = response.json()
            response.close()
        else:
            response.close()
            print("JUMP_TO_PCR: ERROR: Trouble getting valid response from Prompter")
            print("QUITTING ACTION")
            return

        #print("response_obj:")
        #print(response_obj)

        try:

            status['od_rundown_name'] = response_obj['info']['playingRundownName']

        except Exception as Argument:
            logger.exception(f"Trouble Parsing PCR Active Show Response: Quitting ACTION")
            print("Trouble Parsing PCR Active Show Response: Quitting ACTION")
            return

        try:

            status['od_client_name'] = response_obj['info']['controllingRcClient']

        except Exception as Argument:
            logger.exception(f"Trouble Parsing PCR client Name in response: Quitting ACTION")
            print("Trouble Parsing PCR client Name in response: Quitting ACTION")
            return


        print("Need to add VALIDATION for an empty Overdrive rundown. What happens if no Show is playing?")

        #//*** Have Valid Rundown Name, Page Number, Story Slug from Overdrive
        #//*** Obtain the RoIDs from Prompter


        #//*** Build Prompter MosID if needed
        if g['load_pcr']['source_id'] == None:
            if not getMOSSourceID():
                print("Trouble getting the MOS Source ID. Skipping Load Action")
                return
        # temp_url = f"{api_url}{g['load_pcr']['ro_api']}{g['load_pcr']['source_id']}"
        temp_url = f"{api_url}{g['load_pcr']['ro_api']}{g['load_pcr']['source_id']}"
        print(f"temp_url: {temp_url}")
        


        print("temp_url:" + temp_url)


        #//*** Get active ro Sources
        response = requests.get(temp_url, headers=headers, verify=False)

        #//*** Validate Response
        if response.ok:
            #//*** Convert response to JSON
            response_obj = response.json()
            response.close()

            pprint(response_obj)

            print(response_obj.keys())

            #//*** Validate Response
            if "runorders" in response_obj.keys():

                runorders = response_obj['runorders']

                for runorder in runorders:

                    #//**************************************************
                    #//*** Check if the runorder ro_type is RUNORDER
                    #//**************************************************

                    #//*** Validate Key
                    if 'ro_type' in runorder.keys():

                        if runorder['ro_type'] == 'RUNORDER':

                            #//*** Check for Active Rundown
                            if runorder['ro_name'] == status['od_rundown_name']:

                                #//****************************
                                #//*** Rundown FOUND Assign roID
                                #//****************************

                                if 'ro_id' in runorder.keys():
                                    status['ro_id'] = runorder['ro_id'] 
                                else: 
                                    print("JUMP_TO_PCR: ERROR: Trouble Parsing Active rundown: Level3") 
                                    return
                    else: 
                        print("JUMP_TO_PCR: ERROR: Trouble Parsing Active rundown: Level2") 
                        return

            else: 
                print("JUMP_TO_PCR: ERROR: Trouble Parsing Active rundown: Level1") 
                return

            if status['ro_id'] == None:
                print("Rundown Not Found: IS it MOS ACTIVE?")
                print("QUITTING ACTION")
                return

        else:
            print("JUMP_TO_PCR: ERROR: Trouble Connecting to Prompter System. QUITTING ACTION")
            return

        #//*** Have: Rundown Name, RoID, Pagenumber, & Slug
        #//*** Object Reference:
        #//*********** status['od_page']
        #//*********** status['od_rundown_name']
        #//*********** status['od_slug']
        #//*********** status['od_roid']

        #//*** Start Querying Dalet
        pprint(status)
        print("ro ID Found: " + status['ro_id'])

        #//*** g['dalet']['server']
        #//*** g['dalet']['database']
        #//*** g['dalet']['username']
        #//*** g['dalet']['password']

        server = g['dalet']['server']
        database = g['dalet']['database']
        username = g['dalet']['username']
        password = g['dalet']['password']

        try:
            #cnxn = pyodbc.connect('Trusted_Connection=yes;DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
            cnxn = pyodbc.connect('Trusted_Connection=yes;DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';')
            cursor = cnxn.cursor()
        except Exception as Argument:
            logger.exception(f"Trouble Connecting to the Daletdase. Server: {server} - database: {database}")
            print("Trouble Connecting to the Daletdase:")
            print("Using the values:")
            print(f"server: {server}")
            print(f"database: {database}")
            print(f"username: {username}")
            print("=======================================")
            print("There could also be firewall rules preventing connectivity.")
            print("QUITTING ACTION")
            return

        ro_id = status['ro_id']
        print(f"Current: {status['od_page']} {status['od_slug']}")
        #//**********************************************************
        #//*** Get the unique Block IDs for the a given rundown Id
        #//**********************************************************
        query = f"""
        select DISTINCT block_id
        from items
        where
            clock_id={ro_id}
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        if len(rows) == 0:
            print("Error getting BlockIDs: Quitting Action")
            return

        #//*** Loop through each block
        for block_id in rows:
            block_id = block_id[0]

            #//**** Get the Rundown Item Id for each Block, & PageNumber
            query = f"""
            select item_id, item_comment
            from items
            where
                block_id={block_id}
                AND item_type=1
            """
            
            cursor.execute(query)

            block_rows = cursor.fetchall()
            
            #//*** Parse each block element (Rundown Row)
            for block_row in block_rows:
                #//*** item_id = rundown_id 
                item_id = block_row[0]
                pagenumber = block_row[1]

                pagenumber = re.findall("<pageNumber t=\"ws\">.+?</pageNumber>", block_row[1])

                if len(pagenumber) > 0:
                    pagenumber = pagenumber[0].replace("<pageNumber t=\"ws\">","").replace("</pageNumber>","")
                else:
                    pagenumber = "XXX"

                #//*** Search for title_id which references the story directly

                query = f"""
                select item_id, title_id
                from spots
                where
                    item_id={item_id}
                """
                
                cursor.execute(query)

                title_id = cursor.fetchall()
                
                #//*** We should add some error handling, but if it doesn't return a single value, this doesn't work
                
                if len(title_id) > 0:
                    title_id = title_id[0][1]

                else:
                    print("Error Gathering the title_id from Dalet")
                    print("QUITTING ACTION")
                    return

                #//*** Get the slug based on the title_id in the titles table
                query = f"""
                select title_id, title
                from titles
                where
                    title_id={title_id}
                    
                """

                cursor.execute(query)

                slug = cursor.fetchall()
                

                if len(slug) != 1:
                    print("Error getting the Slug Value, Got more or less than 1 resonse: QUITTING ACTION")
                
                slug = slug[0][1]
                #//*** Get the associated Story ID from the rundown ID, so we can get the SLUG

                #print(f"{block_id} {item_id} {title_id} {pagenumber} {slug} | {status['od_page']} {status['od_slug']} - {status['od_page'] == pagenumber} -  {status['od_slug'] == slug}")
                

                found = False
                
                if (status['od_page'] == pagenumber) and (status['od_slug'] == slug):
                    print(f"FOUND_BOTH: {block_id} {item_id} {title_id} {pagenumber} {slug} | {status['od_page']} {status['od_slug']} - {status['od_page'] == pagenumber} -  {status['od_slug'] == slug}")
                    found = True
                elif (status['od_page'] == "NA") and (status['od_slug'] == slug):
                    print(f"FOUND_SLUG ONLY: {block_id} {item_id} {title_id} {pagenumber} {slug} | {status['od_page']} {status['od_slug']} - {status['od_page'] == pagenumber} -  {status['od_slug'] == slug}")
                    found = True

                if found:
                    story_id = f"st-{ro_id}:{block_id}:{item_id}"

                    #story_id = "st-52709263:1000266836:8629399"
                    print(story_id)

                    #//*** Build POST Parameter to define Jump to Story
                    parameters = { 
                        "name" : "CommandJumpToStory",
                        "parameter" : story_id
                        
                    }


                    response = requests.post(f"{api_url}commands", headers=headers, verify=False, json = parameters)

                    print("DING")
                    print(response)
                    print(response.url)
                    print(response.headers)
                    print(response.reason)
                    print(response.text)

                    print("DONG")


            




        #//*** Cleanly close Database connection
        cnxn.close()        

        #//***********************
        #//*** END "JUMP_TO_PCR"
        #//***********************
    elif action == "GET_ALL_COMMANDS":

        display_type = 'ALL'

        args = input_data.split(" ")

        if len(args) > 1:
            if args[1] == 'TRUE':
                display_type = 'TRUE'
            elif args[1] == 'FALSE':
                display_type = 'FALSE'



        response = requests.get(f"{api_url}/commands", headers=headers, verify=False)
        
        vals = json.loads(response.text)['commands']

        if display_type == 'TRUE':

            for obj in vals:

                if obj['requires_parameter']:

                    print(f"{obj['requires_parameter']} : {obj['name']}")
                

        elif display_type == 'FALSE':

            for obj in vals:

                if not obj['requires_parameter']:

                    print(f"{obj['requires_parameter']} : {obj['name']}")
        
        else:
            for obj in vals:

                print(f"{obj['requires_parameter']} : {obj['name']}")
        

    elif action == "NEXT_STORY":
        print("NEXT_STORY")
        
        #//*** Build POST Parameter to define Jump to Story
        parameters = { "name" : "CommandJumpNextStory" }

        response1= requests.post(f"{api_url}commands", headers=headers, verify=False, json = parameters)

    elif action == "PREV_STORY":
        #//*** Build POST Parameter to define Jump to Story
        parameters = { "name" : "CommandJumpPrevStory" }

        requests.post(f"{api_url}commands", headers=headers, verify=False, json = parameters)
    elif action == "prompt":
        response = requests.get(f"{api_url}prompt", headers=headers, verify=False)
        print(response.url)
        print(response.text)

    elif action == "getPairing":

        print("Lets get Pairing")
        pair_url = f"{api_url}sysconfig/pairing"
        print(f"{api_url}sysconfig/pairing")

        response = requests.get(pair_url, headers=headers, verify=False)

        print("====================")
        print(response)
        print(response.text)

        response.close()

        response = requests.get(f"{pair_url}", headers=headers, verify=False)

        print("====================")
        print(response)
        print(response.text)

    return


    #//*** END handleAction



    #//*** END HandleInput
    
def capture_keystroke_threaded():
    global keystroke
    lock = threading.Lock()
    loop = True
    while not g["quit"]:
        with lock:
            time.sleep(.1)
            keystroke = keyboard.read_key()
            if keyboard.is_pressed(keystroke):

                if g['active_window_text'] == win32gui.GetWindowText (win32gui.GetForegroundWindow()):
                    print(keystroke)
                    if keystroke == "esc":
                        g["quit"] = True
                    else:
                        docommand()

                        
def load_configfile():
    config = configparser.ConfigParser()
    config.read('config.ini')

    int_vals = ["prompt_port"]
    
    #//*** Add All Main values to G
    for key in config["Main"]:        
        
        value = config["Main"][key]

        if key in int_vals:
            g[key] = int(value)
        else:
            g[key] = str(value)

        #//*** Convert comma separated ports into a list
        if key == "listen_port":

            value = value.split(",")

            ports = []

            for port in value:
                ports.append(int(port))

            g[key] = ports


    #//*** Load PCR FloorDirector Endpoints

    #"PCR2" : "http://10.218.116.11/server/floordirector/api/v1/info?",
    #"PCR3" : "http://10.218.116.111/server/floordirector/api/v1/info?"
    #print(config.sections())
    
    try:
        fd_info_endpoint = config["Floor Director"]["info_endpoint"]
    except Exception as Argument:
        logger.exception("Using default Floor Director Info Endpoint: /server/floordirector/api/v1/info?")
        print("Using default Floor Director Info Endpoint: /server/floordirector/api/v1/info?")
        print("Custom endpoints can be defined in config.ini")
        print("Section: [Floor Director]")
        print("Key: info_endpoint")
        fd_info_endpoint = "/server/floordirector/api/v1/info?"

    try:
        fd_shots_endpoint = config["Floor Director"]["shots_endpoint"]
    except Exception as Argument:
        logger.exception("Using default Floor Director Shots Endpoint: /server/floordirector/api/v1/shots?")
        print("Using default Floor Director Shots Endpoint: /server/floordirector/api/v1/shots?")
        print("Custom endpoints can be defined in config.ini")
        print("Section: [Floor Director]")
        print("Key: shots_endpoint")
        fd_shots_endpoint = "/server/floordirector/api/v1/shots?"

    g['load_pcr']['fd_info_endpoint'] = fd_info_endpoint
    g['load_pcr']['fd_shots_endpoint'] = fd_shots_endpoint
    
    for key in config['Control Room']:
        value = config['Control Room'][key]

        endpoint = f"http://{value}"

        g['load_pcr'][key.upper()] = endpoint

    #//*** Add All Dalet values to g['dalet']
    for key in config["Dalet"]:        
        
        value = config["Dalet"][key]

        #//*** Assign each key value pair
        g['dalet'][key] = value


    #//*** These values associate the Clients with IP addresses, used to denote Primary and Backup Clients
    for key in config['Clients']:

        value = config['Clients'][key]

        key = key.upper()
        #//*** Assign each key value pair
        g['clients'][key] = value
        
    print(f"Clients: {g['clients']}" )
#//*************************************
#//*************************************
#//*************************************
#//**** Startup Code BEGINS HERE
#//*************************************
#//*************************************
#//*************************************

if __name__ == '__main__':

    #//**** START Logging
    logger = logging.getLogger(__name__)
    logger.setLevel('DEBUG')
    #file_handler = logging.FileHandler("prompt.log", mode="a", encoding="utf-8")
    
    #//*** 5mb Rotating Log File with 5 backups. We should catch everything in 25mb
    file_handler = RotatingFileHandler("prompt.log", mode="a", encoding="utf-8", maxBytes=5*1024*1024, backupCount=5)
    formatter = logging.Formatter(
        "{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
        )

    file_handler.setLevel('DEBUG')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    logger.info("System START")
    
    #//**** END Logging

    load_configfile() 

    #//*** Get the Active Window name. Used to Capture Keystrokes only if window is active
    g['active_window_text'] = win32gui.GetWindowText (win32gui.GetForegroundWindow())

    #//*** Launching Listener processes as Threads, in order to gracefully close them on a Quit Command (From the keyboard)

    #//*** Get All Local IP Addresses
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)

        
    name, aliaslist, addresslist = socket.gethostbyname_ex(hostname)
    #print("Hostname:", name)
    #for address in addresslist:
    #    print("IP Address:", address)
    #sys.exit()

    #//*** Start keyboard Listener As a Thread
    keeb = threading.Thread(target = capture_keystroke_threaded)
    keeb.daemon = True
    keeb.start()

    #//*** Loop through each address and start listener
    for address in addresslist:

        #//*** Mount Each Port on each address

        for port in g['listen_port']:
            print(f"Starting Listener: {address}:{port}" )
            #//*** Start RossTalk Listener as thread
            listener = threading.Thread(target = start_listener, args=[address, port])
            listener.daemon = True
            listener.start()

    print(pyodbc.drivers())


    #//*******************************************************************************************************************************
    #//*******************************************************************************************************************************
    #//*** Main Loop Listening for triggered & queued actions. Allows actions to be quend asynchronously and executed linearly.
    #//*******************************************************************************************************************************
    #//*******************************************************************************************************************************
    while True:
        time.sleep(.01)

        

        if len(g['actions']) > 0:

            print(f"Actions: {len(g['actions'])}" )
            
            #//*** Remove First Item from g['actions'] 
            data,conn = g['actions'].pop()

            logger.debug(f"HandleInput:{data}")
            try:
                action = handleInput(data)
            except Exception as Argument:
                logger.exception(f"Trouble with HandleInput:{data}")

            logger.debug(f"handleAction:{data}")

            try:
                handleAction(action,data,conn)
            except Exception as Argument:
                logger.exception(f"Trouble with handleAction:{action} - {data}")


        

        if g["quit"]:
            print("QUITTING")
            sys.exit()

    print("EOL")

    parameters = {
        "code": "code",
        "client_id": "default",
        "client_secret": "winplus",
        "redirect_uri": 'http://172.24.124.148:8080/api/v1/sysdevices',
        "response_type": "code",
        "grant_type": "authorization_code"
    }

    parameters = {
        "username": "default",
        "password": "winplus",
        "grant_type": "password"
    }


