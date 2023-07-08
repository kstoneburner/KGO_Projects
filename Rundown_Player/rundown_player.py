import re
import pandas as pd
import numpy as np 

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

def build_rundown_info(rundown_target,date_range,config,cnxn):

    cursor = cnxn.cursor()

    print("=======")
    print("== 1 ==")
    print("=======")

    #Get Current Rundown IDs from resourceReservations, ClockID and Name in Content

    #//*** Get Rundown ID of Shows based on Rundown Name which needs to be a Unique and Exact Match. There can be trouble if there are multiple Rundowns wit the same name. 
    #//*** We Should Probably take that into account when welaunch the Final Product


    query = f"""
    SELECT *
    FROM resourceReservations 
    WHERE startTime BETWEEN {date_range}
    AND content LIKE '%{rundown_target}%'
    """
    #WHERE stationId = '1132'

     
    #//*** Get List of Rundowns Matching date Range and Rundown Name
    cursor.execute(query)
    results = cursor.fetchall()

    #//**** Initialize the Rundown Player Object
    #//*** Houses all the data associated with the rundown Values
    rp = {
    
        "data_fields" : ["clockId","content","startTime"],
        "data_index" : {},
        "data" : {},
        "name_replace_1" : '<name t="ws">CLOCK ',
        "name_replace_2" : '</name>',
        "name":"XXX PLACEHOLDER XXX",
        "id" : None,
        "blocks" : [],
        "storyOrder" : [],
        "stories" : {},
        "pageNumber" : "_"
        }
    


    #//*** Get the Column Names From the Cursor
    metas = cursor.columns(table='resourceReservations') 

    #//*** Build Column Indexes and Store in rp, Rundown
    for x,meta in enumerate(metas):    
        if meta[3] in rp["data_fields"]:
            rp["data_index"][meta[3]] = x

    #print(rp["data_index"])


    #//*** Currently assuming there is only one Rundown with this name, We should account for multiple.

    if len(results) == 1:
        result = results[0]      
    else:
        result = None
        handleError(f"EC 1: Returned Multiple Rundowns with name {rundown_target}. Expected Answer is 1.\nNeed Code to deal with edge case. Expect a Crash after this.")

    for field,index in rp["data_index"].items():
        rp["data"][field] = result[index]

    #for key,value in rp["data"].items():
    #    print(key,value)

    content = rp["data"]["content"]

    try:
        content = re.findall('<name t="ws">.+</name>',content)[0]
    except:
        print("build_rundown_info: EC 1: Problem with regex: quitting")
        return None
        

    #//*** Get Rundown Name From Content. Must Strip XML fields from Content
    rp["name"] = content.replace(rp["name_replace_1"],"").replace(rp["name_replace_2"],"")

    rp["id"] = rp["data"]["clockId"]

    #print(rp["id"],rp["name"])



    #//*** Get Ordered Scripts from Items by clock_id (rundown id). Breaks will be associated will Specific Clip Names and Handled with the VLC player 
    #//*** Get Script IDs from items clock_id

    #//item_type 1 = Scripts
    #//item_type 3 = Blank Line
    #//item_type 5 = Block

    #//*** Get Blocks --- block_id is Parent Block ID.
    #//*** item_id will be used to get the Block ID
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
    print("Blocks:",rp['blocks'])

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


        print("==========")
        print(block)
        print("==========")
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
                print("LAST STORY")

            #//*** Extract Pagenumber if it exists
            if "<pageNumber" in story['item_comment']:
                pageNumber = re.findall(regex["pageNumber"]['findall'],story['item_comment'])

                #//*** This should always be one, but it's best not assume.
                #//*** On error, it'll just use the default value
                if len(pageNumber) == 1:
                    #//*** Convert to String and Strip XML
                    story['pageNumber'] = pageNumber[0].replace(regex['pageNumber']['replace1'],"").replace(regex['pageNumber']['replace2'],"")

            
            #//*** Use the block based item_id to get the title_id for the story content
            print("Get StoryID For: ", story['pageNumber'],"-",story['item_id'])
            

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

                print(story)


                rp['storyOrder'].append(story['title_id'])
                rp['stories'][story['title_id']] = story

                

            



            print("-------------------------------------")
            


        print("=======")
        print("== 2 ==")
        print("=======")

    return rp