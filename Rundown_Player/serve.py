from flask import Flask, render_template, request, send_file
import pyodbc,socket,os,datetime,json,re
from datetime import date, timedelta
import pandas as pd
import numpy as np 
app = Flask(__name__)


regex = {
    "pageNumber" : { 
        "findall" : '<pageNumber t="ws">.+?</pageNumber>',
        "replace1" : '<pageNumber t="ws">',
        "replace2" : '</pageNumber>',

    },

    "story" : { 
        "findall" : '<Story .+?>',

    },
    "embedded" : {
        "findall" : '<EmbeddedObject.+?</EmbeddedObject>'
    },
    "ObjectId" : {
        "findall" : 'ObjectId.l=".+?"',
        "replace1" : 'ObjectId.l=',
        "replace2" : '"',
    },
    
}

rundown_names = ["5PM Weekday"]
rundown_target = rundown_names[0]
config_filename = "rp.config"
config = {}
playout_paths = ["\\\\om-casf-dlbr06\\MEDIA"]

def get_db_connection():
    h_name = socket.gethostname()
    HOST = socket.gethostbyname(h_name)
    PORTS = [10522]

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


    cnxn = pyodbc.connect('Trusted_Connection=yes;DRIVER={SQL Server};SERVER='+config['server']+';DATABASE='+config['database']+';UID=user;PWD=password')
    print("!!!!!!")
    return cnxn

def get_rundowns(date_range,cnxn):
    cursor = cnxn.cursor()

    query = f"""
    SELECT *
    FROM resourceReservations 
    WHERE startTime BETWEEN {date_range}
    AND stationId = '1132'
    
    """
    #
    #AND content LIKE '%{rundown_target}%'
    #ORDER BY startTime
     
    #//*** Get List of Rundowns Matching date Range and Rundown Name
    cursor.execute(query)
    results = cursor.fetchall()

    #//**** Initialize the Rundown Player Object
    #//*** Houses all the data associated with the rundown Values
    rp = {
    
        "data_fields" : ["clockId","content","startTime","endTime"],
        "data_index" : {},
        "data" : {},
        "name_replace_1" : '<name t="ws">CLOCK ',
        "name_replace_2" : '</name>',
        "name":"XXX PLACEHOLDER XXX",
        "id" : None,
        "blocks" : [],
        "storyOrder" : [],
        "stories" : {},
        "pageNumber" : "_",

        "rundowns" : [],
        }
    


    #//*** Get the Column Names From the Cursor
    metas = cursor.columns(table='resourceReservations') 
    
    #//*** Build Column Indexes and Store in rp, Rundown
    for x,meta in enumerate(metas):   
        if meta[3] in rp["data_fields"]:
            rp["data_index"][meta[3]] = x


    #//*** Currently assuming there is only one Rundown with this name, We should account for multiple.
    rundowns = []
    for result in results:
        #result = result[0]
        rundown = { "error" : [], }
        
        for field,index in rp["data_index"].items():
            rundown[field] = result[index]

            
        #//*** Extract Rundown Name From Content Field
        content = rundown["content"]

        try:
            content = re.findall('<name t="ws">.+</name>',content)[0]

        except:
            msg = "build_rundown_info: EC 1: Problem with regex: quitting"
            print(msg)
            rundown["error"].append(msg)
            continue
            
        

        #//*** Get Rundown Name From Content. Must Strip XML fields from Content
        rundown["name"] = content.replace(rp["name_replace_1"],"").replace(rp["name_replace_2"],"")

        rundown["id"] = rundown["clockId"]

        del rundown['content']
        rundowns.append(rundown)


        #print(rundown)
        #print("===========")


    return rundowns
    
def get_video_from_rundown(rundown_id,rundown_name):
    cnxn = get_db_connection()
    cursor = cnxn.cursor()
    print(rundown_name)
    rp = {

    "id" : rundown_id,
    "name" : rundown_name,
    "blocks" : [],
    "storyOrder" : [],
    "stories" : {},

    }
    query = f"""
    SELECT block_id, item_id, item_order, item_comment
    FROM items 
    WHERE clock_id = '{rp["id"]}'
    AND item_type = 5
    ORDER BY item_order

    """
    
    cursor.execute(query)
    
    results1 = cursor.fetchall()
    
    for result1 in results1:
        

        block_item_id = result1[1]
        block_comment = result1[3]

        #print(block_item_id,":",block_comment)

        #//*** Skip Floated Blocks
        if "hold.l" in block_comment:
            print("FLOAT BLOCK")
            continue
        
        #//*** Get Child Block ID
        query = f"""
        SELECT child_block_id
        FROM block_item 
        WHERE item_id = '{block_item_id}'
        """

        cursor.execute(query)
        results2 = cursor.fetchall()
        
        if len(results2) == 1:
            #//*** First Row, First Item add to
            print(results2[0][0])
            rp['blocks'].append(results2[0][0])
        else:
            print

    #//*** Active (unfloated) Blocks built
    #print("Blocks:",rp['blocks'])

    #//*** Loop through each block to acquire Story Information
    #//*** Get Block Level Story ID which will acquire the Story ID
    for block in rp['blocks']:

        query = f"""
        SELECT *
        FROM items 
        WHERE clock_id = '{rp["id"]}'
        AND item_type = 1
        AND block_id = {block}
        ORDER BY item_order

        """

        cursor.execute(query)
        block_results = cursor.fetchall()


        #print("==========")
        #print(block)
        #print("==========")
        for block_result in block_results:


            #//*********************************************************************************************
            story = {
                "fields" : ["block_id", "item_id", "item_order", "item_comment"],
                "field_index" : {},
                "last_story" : False,
                "mos" : [],
                "title" : "_",
                "pageNumber" : "_",
            }
            #//*********************************************************************************************
            #print("Reset Story <-----------------------")

            #//*** Get the Column Names From the Cursor
            metas = cursor.columns(table='items') 

            #//*** Build Column Indexes and Store in story rundown
            #//*** Automatically indexes the columns in story["fields"]
            #//*** Avoids hardcoding column indexes. Everything should be fixed, but this method should be more reliable

            for x,meta in enumerate(metas):   
                if meta[3] in story["fields"]:
                    story["field_index"][meta[3]] = x


            #//*** Hunting for Each Story in Block
            #//*** Use story["field_index"] to add block_results to story
            for key,value in story["field_index"].items():
                story[key] = block_result[value]
                
            
            #//*** hold.1
            #//*** Check for floated Story
            #//*** Extract the <story ... > tag
            text = re.findall(regex["story"]["findall"],story["item_comment"])
            
            #//*** Double check good regex. We should. But It's always a good idea to check
            #//*** Otherwise skip the story
            if len(text) == 1:
                text = text[0]
                if "hold.l" in text:
                    print("FLOAT STORY - SKIPPING")
                    continue
            else:
                print("Regex Problem in trying to parse Story Tag\n",story["item_comment"])
                continue

            #//*** Check for Spot hold indicating Last Element in a Block
            if "<Spot hold.l=" in story['item_comment']:
                story['last_story'] = True
                #print("LAST STORY")

            #//*** Extract Pagenumber if it exists
            if "<pageNumber" in story['item_comment']:
                pageNumber = re.findall(regex["pageNumber"]['findall'],story['item_comment'])

                #//*** This should always be one, but it's best not assume.
                #//*** On error, it'll just use the default value
                if len(pageNumber) == 1:
                    #//*** Convert to String and Strip XML
                    story['pageNumber'] = pageNumber[0].replace(regex['pageNumber']['replace1'],"").replace(regex['pageNumber']['replace2'],"")

            
            #//*** Use the block based item_id to get the title_id for the story content
            #print("Get StoryID For: ", story['pageNumber'],"-",story['item_id'])
     

            #//*********************************************************************************************
            #//*********************************************************************************************
            #//*********************************************************************************************
            #//*********************************************************************************************


            query = f"""
            SELECT title_id
            FROM spots 
            WHERE item_id = '{story["item_id"]}'
            """

            cursor.execute(query)
            title_id_results = cursor.fetchall()



            if len(title_id_results) == 1:
                
                try:
                    story['title_id'] = title_id_results[0][0]
                except:
                    print("PROBLEM Assigning title_id SKIPPING STORY")    
                    continue
            else:
                print("PROBLEM getting title_id SKIPPING STORY")
                continue

            #for key,value in story.items():
            #    print(key,":",value)

            #//*********************************************************************************************
            #//*********************************************************************************************
            #//*** use title_id to get StoryXml from StoryContent
            #//*** Finally down to the Story MEAT!
            #//*********************************************************************************************
            #//*********************************************************************************************

            query = f"""
            SELECT StoryXml
            FROM StoryContent
            WHERE TitleId = '{story['title_id']}'
            """

            cursor.execute(query)
            story_results = cursor.fetchall()
            
            if len(story_results) == 1:
                story_results = story_results[0][0]
            else:
                print("PROBLEM getting StoryXML. Skipping STORY")
                continue


            story['script'] = story_results

            #//*** Get the embedded Objects (MOS) Objects from the Script
            #//*** And Loop through them
            for mos in  re.findall(regex['embedded']['findall'],story_results):

                #//*** Video Objects have a Duration
                if "duration.tc=" not in mos:
                    continue

                #//*** SHould be here, but again it's good to check.
                if "ObjectId.l=" in mos:
                    #//*** Extract Mos Object ID from the regex response.
                    story['mos'].append(re.findall(regex['ObjectId']['findall'],mos)[0].replace(regex['ObjectId']['replace1'],"").replace(regex['ObjectId']['replace2'],""))
            
            

            #//*********************************************************************************************
            #//*********************************************************************************************
            #//**** Get Story Title (slug) from titles by Story ID
            #//*********************************************************************************************
            #//*********************************************************************************************

            if len(story['mos']) > 0:
                #//**** Only get Title if the story has video
                query = f"""
                SELECT title
                FROM titles
                WHERE title_id = '{story['title_id']}'
                """
                
                cursor.execute(query)
                title_results = cursor.fetchall()

                #//*** Again should always be 1, but we are checking anyways. Good Hygenie here!
                if len(title_results) == 1:
                    story['title'] = title_results[0][0] 

                #//***********************************************
                #//**** Story Processing Done
                #//**** Add Story to RP if there is video 
                #//***********************************************

                #print(story)


                rp['storyOrder'].append(story['title_id'])
                rp['stories'][story['title_id']] = story

                

            



            #print("-------------------------------------")

    #for key,value in rp.items():
    #    print(key,value)

    cnxn.close()

    return rp



@app.route('/')
def index():
    
    cnxn = get_db_connection()
    
    

    print(cnxn)

    offset_days = 0
    #//*** Today's date range starts with today's date beginning at 00:00:00 and Tomorrow's Date at 00:00:00
    todayStart = str(date.today() + timedelta(days=offset_days))
    todayEnd = str(date.today() + timedelta(days=offset_days+1))
    date_range = f"'{todayStart}T00:00:00' AND '{todayEnd}T00:00:00'"


    rundowns = get_rundowns(date_range,cnxn)

    cnxn.close()
    return render_template('index.html', rundowns=rundowns,today=str(date.today()))
    

#@app.route('/rundown/<rundown_id>')
#def rundown_video(rundown_id):
    #cnxn = get_db_connection()
#    print("Handling Rundown ID:")

#   return "Hello Wrodl"


@app.route('/rundown', methods=['GET'])
def rundown_video():
    args = request.args
    rundown_id = args['rundown_id']
    rundown_name = args['rundown_name']

    print(args)


    
    results = get_video_from_rundown(rundown_id,rundown_name)
    
    #return results    

    return render_template('rundown.html', rp=results)


@app.route('/video', methods=['GET'])    
def get_video_clip():
    args = request.args
    video_id = args['video_id']

    filepath = playout_paths[0] + "\\" + video_id + ".mxf"

    os.path.exists(filepath)


    #return f"{video_id} {str(file_exists)} {filepath}"
    return send_file(filepath)

app.run()