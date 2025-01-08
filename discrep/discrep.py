import csv, requests, json, random,sys, os, re, pprint
import dateutil.parser as dparser

os.system('cls')
print("======================================")
print("======================================")
print("======================================")
print("======================================")
print("======================================")
print("======================================")
print("======================================")
print("======================================")
print("======================================")
ollama = {
    "url_start" : "http://127.0.0.1:11434/api/generate",
    "url_chat" : "http://127.0.0.1:11434/api/chat",
    "model" : "llama3.2",
    "headers" : {"Content-Type" : "application/json"},
    "filename" : "Discrep_issues_2024.CSV",
    "fields" : ['ï»¿"Subject"','From: (Name)','Body'],
    "year" : 2024,
}

cleanups = [
    "Krisann Chasarik \nWriter/Producer | ABC7 KGO-TV Bay Area\n415-954-7926 office | abc7news.com",
    "Krisann Chasarik \nWriter/Producer | ABC7 KGO-TV Bay Area \n415-954-7926 office | abc7news.com",
    "Krisann Chasarik\n\nWriter/Producer | ABC7 KGO-TV Bay Area \n\n415-954-7926 office | abc7news.com",
    "Krisann Chasarik \n\nWriter/Producer | ABC7 KGO-TV Bay Area \n\n415-954-7926 office | abc7news.com",
    "Krisann Chasarik \n\nWriter/Producer | ABC7 KGO-TV Bay Area \n415-954-7926 office | abc7news.com",
    "Krisann Chasarik \n\n\nWriter/Producer | ABC7 KGO-TV Bay Area \n\n415-954-7926 office | abc7news.com",
    "Krisann Chasarik \n\n\nWriter/Producer | ABC7 KGO-TV Bay Area \n415-954-7926 office | abc7news.com",
    "Krisann Chasarik\n\n\tWriter/Producer | ABC7 KGO-TV Bay Area \n\n\t415-954-7926 office | abc7news.com",
    "Krisann Chasarik \n\n\nWriter/Producer | ABC7 KGO-TV Bay Area \n415-954-7926 office | abc7news.com"

    "Andrew Morris \n\n\nNews Producer, KGO-TV | ABC7 Bay Area \n\n925.949.3969 mobile | andrew.a.morris@abc.com | abc7news.com",
    "Andrew Morris\n\nNews Producer, KGO-TV | ABC7 Bay Area \n\n925.949.3969 mobile | andrew.a.morris@abc.com | abc7news.com",
    "Andrew Morris \n\nNews Producer, KGO-TV | ABC7 Bay Area \n\n925.949.3969 mobile | andrew.a.morris@abc.com <mailto:andrew.a.morris@abc.com>  | abc7news.com",
    "Andrew Morris \n\nNews Producer, KGO-TV | ABC7 Bay Area \n925.949.3969 mobile | andrew.a.morris@abc.com | abc7news.com",
    "Andrew Morris\nNews Producer, KGO-TV | ABC7 Bay Area \n925.949.3969 mobile | andrew.a.morris@abc.com | abc7news.com",
    "Andrew Morris \n\n\nNews Producer, KGO-TV | ABC7 Bay Area \n925.949.3969 mobile | andrew.a.morris@abc.com | abc7news.com",
    "Andrew Morris \n\n\nNews Producer, KGO-TV | ABC7 Bay Area \n\n925.949.3969 mobile | andrew.a.morris@abc.com | abc7news.com",

    "Eric Shackelford\nProducer, KGO-TV | ABC7 Bay Area \n\n530.605.6728 mobile | abc7news.com",
    "Eric Shackelford\nProducer, KGO-TV | ABC7 Bay Area \n530.605.6728 mobile | abc7news.com",
    "Eric Shackelford\n\nProducer, KGO-TV | ABC7 Bay Area \n530.605.6728 mobile | abc7news.com",

    "Kate Eby\n\n6 PM Producer, KGO-TV | ABC7 Bay Area\n\nabc7news.com",
    "Kate Eby\n\n\t6 PM Producer, KGO-TV | ABC7 Bay Area\n\n\tabc7news.com",
    "Kate Eby\n6 PM Producer, KGO-TV | ABC7 Bay Area\nabc7news.com",
    
    "Duncan Small\n\nDaily Hire Writer/Producer | ABC7 KGO-TV Bay Area\n\n916.216.7055 mobile | 415.954.7926 desk\n\nabc7news.com",
    "Duncan Small\n\n\nDaily Hire Writer/Producer | ABC7 KGO-TV Bay Area\n\n916.216.7055 mobile | 415.954.7926 desk\n\nabc7news.com",
    "Duncan Small\n\nWriter/Producer | ABC7 KGO-TV Bay Area\n\n916.216.7055 mobile | 415.954.7926 desk\n\nabc7news.com",
    "Duncan Small\n\n\tWriter/Producer | ABC7 KGO-TV Bay Area\n\n\t916.216.7055 mobile | 415.954.7926 desk\n\n\tabc7news.com",
    "Duncan Small\n\nDaily Hire Writer/Producer | ABC7 KGO-TV Bay Area\n916.216.7055 mobile | 415.954.7926 desk\nabc7news.com",
    "Duncan Small\nDaily Hire Writer/Producer | ABC7 KGO-TV Bay Area\n916.216.7055 mobile | 415.954.7926 desk\nabc7news.com",

    "Justin Prochaska \nNews Producer | ABC7 KGO-TV Bay Area\n\n817.723.5826 mobile\n\nabc7news.com",
    "David Fortin \n\nBroadcast Systems Specialist, KGO-TV | ABC7 Bay Area \n415.954.7217 office | abc7news.com",
    "Justin Prochaska \nNews Producer | ABC7 KGO-TV Bay Area\n817.723.5826 mobile\nabc7news.com",
]
subject_cleanups = [
    "5/6am show report","11AM/Midday",
]
replace_turds = { 
    "5/6am" : "5&6am",
    "Fri 12/8/2023" : "Fri 12/18/2023",
    "11AM/Midday Live" : "MDL",
    "5PM/6PM" : "5PM&6PM",
    "5p and 5:30p show report 7/31" : "5p and 5:30p show report",
    "5PM/5:30 Streaming show" : "5PM&5:30 Streaming show",
    "Show:  5PM & 6PM\nDate: 8/7/22" : "Show:  5PM & 6PM\nDate: 1/28/23"
    }

hard_pass = [
    "4:30 Cut in discrepany report",
]

raw_rows = []

rows = []


#If there are separate issues, list them separately. The Header includes the Producer, Director, Closed Captioning, and Date

i=0
with open(ollama['filename'], errors='ignore') as csvfile:

    reader = csv.DictReader(csvfile)


    #print(xmax)
    #for x in range(5):
    #    print(f"{x} : {random.randint(1,845)}")

    for raw_row in reader:
        
        row = {}

        for field in ollama['fields']:
        
            if field == 'ï»¿"Subject"':
                row["Subject"] = raw_row[field]

            elif field == 'From: (Name)':
                row["From"] = raw_row[field]

            else:
                row[field] = raw_row[field]

        #//*** Skip Items that Are replies. "________________________________" is a good stand in for a reply
        if "________________________________" in row["Body"]:
            continue

        #//*** From and To are tell tale responses
        if "From:" in row['Body'] and "To: #KGO-TV DL-News Show Report" in row['Body']:
            continue

        
        if row['Subject'] in hard_pass:
            continue



        #//*** Declaritive Cleanup, Which is the easy email signatures.

        for find in cleanups:
            if find in row["Body"]:
                row["Body"] = row["Body"].replace(find,"") 

        #if "abc7news.com" in row["Body"]:
        #    print(row["Body"].encode('utf-8'))

        #//*** Producer is Easy
        row['producer'] = row['From']

        #//*** Build the Date & Show

        row['date'] = None

        #//*** Start with the Subject

        clean_subject = row["Subject"]

        for find in subject_cleanups:
            if find in clean_subject:
                clean_subject = clean_subject.replace(find,"")
                #print("cleaning: " + clean_subject + ":" + row["Subject"] + ":" + find)


        #//*** If there's a / in the subject, try Guessing the Date
        if "/" in clean_subject:
        
            try:

                #//*** This version is date only. Keeping for Reference
                #this_date = dparser.parse(row["Subject"],fuzzy=True).date()


                this_date = dparser.parse(clean_subject,fuzzy=True, tzname="PDT")

                #//*** Replace the Date with the year we are working on. 
                #//*** The dparser assumes the current year
                if this_date.year != ollama['year']:
                    this_date = this_date.replace(year=ollama['year'])

                #print(f'{this_date} : {row["Subject"]}')
                row['date'] = this_date
            except:
                #print("Skipping:" + clean_subject)
                pass
        
        #//*** Let's Try to find the Date in the Body
        if row['date'] == None:
            clean_body = row['Body']

            for turd in replace_turds.keys():
                if turd in clean_body:
                    clean_body = clean_body.replace(turd, replace_turds[turd])
                    #print("Clean TURD")
                    #print(clean_body)
            """
            if "5PM & 6PM News Show Report" in row['Subject']:
                print("======")
                print(clean_body.encode('utf-8'))
                print("=======")
                print("Fri 12/8/2023 5:55 AM" in clean_body)
                print(replace_turds)
                print("=======")
            """
            for line in clean_body.replace("\n\n","\n").split("\n")[:5]:

                if "date:" in line.lower() or "/" in line:
                    try:

                        #//*** This version is date only. Keeping for Reference
                        #this_date = dparser.parse(row["Subject"],fuzzy=True).date()
                        
                        this_date = dparser.parse(line.lower(),fuzzy=True)



                        #//*** Replace the Date with the year we are working on. 
                        #//*** The dparser assumes the current year
                        if this_date.year != ollama['year']:
                            this_date = this_date.replace(year=ollama['year'])
                        
                        """
                        if "11AM/Midday Live Discrepancy Report" in row['Subject']:
                            print("XXXXX")
                            print(f'Found: {this_date} : {line}')
                            #print(row['Body'])
                            print(clean_body)
                        """
                        row['date'] = this_date
                        break
                    except:
                        pass
        #//*** If it's Still None, We're not done
        if row['date'] == None:
            for line in row['Body'].replace("\n\n","\n").split("\n")[:3]:
                for month in ['january','february','march','april','may','june','july','august','september','october','november','december']:
                    if month in line.lower():
                        try:

                            #//*** This version is date only. Keeping for Reference
                            #this_date = dparser.parse(row["Subject"],fuzzy=True).date()
                            
                            this_date = dparser.parse(line,fuzzy=True)

                            #//*** Replace the Date with the year we are working on. 
                            #//*** The dparser assumes the current year
                            if this_date.year != ollama['year']:
                                this_date = this_date.replace(year=ollama['year'])

                            #print(f'Found: {this_date} : {line}')
                            row['date'] = this_date
                            break
                        except:
                            print(f"======\nSkipping:\n======\n{ row['Body']}")
                            pass
                    #if row['date'] != None:
                    #    print("Second Break")
                    #    break

        #//*** If Date Still Not Found, skip the report
        #//*** It's likely a reply to another message, or a poorly formatted report.
        if row['date'] == None:
            continue
            #print("==========")
            #print(row['Body'])

        #print("=========")
        #print(f"{row['date']} - {row['Subject']}")

        row['director'] = None
        #//*** Get the Director
        clean_body = row['Body']
        for line in clean_body.replace("\n\n","\n").split("\n")[:8]:
            #//*** This is the easiest case.
            if 'director' in line.lower() and ":" in line:
                row['director'] = line.split(":")[1]
                if row['director'][0] == " ":
                    row['director'] = row['director'][1:].replace("â€","").replace(",","")
                break

            if 'director' in line.lower():
                words = line.split(" ")
                found = False
                
                while not found or len(words) > 0:
                    if 'director' in words[0].lower():
                        found = True
                        

                    if not found:
                        words.pop(0)
                        continue
                    else:
                        words.pop(0)
                        break

                row['director'] = " ".join(words).replace("â€","").replace(",","")
                break

            if line == "Jerry Sandy":
                row['director'] = "Jerry Sandy"

        #//*** These are poor emails, toss them
        if row['director'] == None:
            #print(clean_body.replace("\n\n","\n").split("\n")[:10])
            continue

        #//*** Cleanup the Body for the LLM
        #print("=========")
        row['clean_body'] = row['Body']

        row['clean_body'] = row['clean_body'].replace("\t","")
        row['clean_body'] = row['clean_body'].replace("â€‚","")
        
        #if 'narrative' in row['Body'].lower():
        #    narrative_split = row['Body'].split()

        narrative_split = re.split(r"narrative", row['clean_body'], flags=re.IGNORECASE)

        if len(narrative_split) > 1:
            row['clean_body'] = " ".join(narrative_split[1:])




            #print(row['clean_body'].encode("utf-8"))
        else:
            #//*** Work on the Non-Narrative Discrepancy reports
            narrative_split = re.split(r"Closed.Captioning(.+)Good", row['clean_body'], flags=re.IGNORECASE)

            if row['Subject'] == "5a report 4/2":
                narrative_split = []
  
            if len(narrative_split) > 1:
                row['clean_body'] = " ".join(narrative_split[2:])

            else:
                #//*** Keep Cleaning!
                narrative_split = re.split(r"Director(.+\W)", row['clean_body'], flags=re.IGNORECASE)




                if len(narrative_split) > 2:
                    row['clean_body'] = "director".join(narrative_split[2:])

                else:
                    print("==================")
                    print("DIRTY CLEAN BODY")                    
                    print("==================")
                    print(row)
                    print("==================")
                    print("==================")

                if "5a report 4/2" in row['Subject']:
                    row['clean_body'] = row['clean_body'].replace("Closed Captioning: Verified Good","")

        while "\n\n" in row['clean_body']:
            row['clean_body'] = row['clean_body'].replace("\n\n","\n") 

        while "\n \n" in row['clean_body']:
            row['clean_body'] = row['clean_body'].replace("\n \n","\n") 



        #print("=====")
        #print(row['clean_body'].encode('utf-8'))

        empty_reports = [
            "Midday Live Show Report 2/6",
            'Show Report 4/17 Midday Live',
            'Show Report Midday 4/16',
            '5a report 3/19',
            '6pm discrep',
            '5p & 530p show report 10/27',
            '3PM Getting Answers discrepancy report',
            '5p & 530p show report 6/13',
            '5A REPORT 11/6',


        ]
        if row['Subject'] in empty_reports:
            row['clean_body'] = "\nClean Show [Assumed]\n"

        if row['clean_body'] == "\n":

            print("XXXXXXX")
            print("XXXXXXX")
            print("XXXXXXX")
            print("XXXXXXX")
            print(row)

        print("=====")
        print(row['clean_body'].encode('utf-8'))

        rows.append(row)

ignore_prompt = ""
ignore_prompt += "Certain elements in the email describe the specific element in a show. These elemenst should be ignored."
ignore_prompt += "Here are example of elements to ignore:\n"
ignore_prompt += "B3- 5P COLD COW PALACE PKG:,Preshow page 5:,F11 ALLIES HIGHER GROUND:"
ignore_prompt += ""
ignore_prompt += ""


examples_dict = {
    "CG/TYPO" : [
        'typo in CG',
        'Cold open had a generic banner; I thought I had saved it but evidently I did not.'
    ],
    "CG/TECHNICAL" : [
        "The A block tease cg did not load","bc of xpression preview issues we cannot fix",
        "Baseline did not air. Overdrive skipped over it",
    ],
    "CLEAN" : [
        "Clean Show [Assumed]",
        "GNSP"
    ],

    
}



base_prompt = ""
base_prompt += "I have questions about the a report which I will describe later. It is a report that describes any issues that occurred during a show.\n"
#base_prompt += "If a report includes clean show or GNSP. Then it is a clean show. Otherwise, a show is not clean\nAny show with stated issues is not clean.\n"
#base_prompt += "A show may also have one or more issues.\n"
#base_prompt += "Are any of the issues are resolved?\n"
#base_prompt += "Here are my questions to ask regarding each email.\n"
#base_prompt += "Describe the problem indicated in each issue.\n"
#base_prompt += "Are any of the issues are resolved? YES/NO/Unknown\n"
#base_prompt += "Who or what is responsible for the issue? PERSON,EQUIPMENT,OTHER,CLEAN,TYPO \n"
#base_prompt += "If clean show or GNSP are indicated indicates there are no issues to report. Return CLEAN as a summary\n"
#base_prompt += "Is it a clean show? TRUE/FALSE\n"

base_prompt += "A report can be classified as one of the following categories: CG/TYPO, CG/TECHNICAL, CLEAN, OTHER.\n"
base_prompt += "Examples:\n"
#base_prompt += '- CLEAN: "Clean Show [Assumed]","GNSP"\n'
base_prompt += "\n"
base_prompt += 'Based on these categories, classify this report. :'

#base_prompt += ignore_prompt + "\n"

sys.exit()

random_indexes = [];
samples = 5
for x in range(0,20):
    #rand_val = random.randint(0,len(rows))
    #print(f"{x} : {rand_val}")
    #random_indexes.append(rand_val)
    random_indexes.append(x)


url = ollama['url_start']

#//*** Let's Initialize with an Empty Request. Then Use Chat for subsequent requests
data = {
    "model" : ollama['model'],
    "stream" : False,
    "prompt" : "",
    "keep_alive": 20, #//*** Keep Alive for 20 Seconds After this Request
}

response = requests.post(ollama['url_start'], headers=ollama['headers'], data=json.dumps(data))
print("=== INITIALIZING ollama ===")
print(response.text)
print("===========================")

data = {
    "model" : ollama['model'],
    "stream" : False,
    'messages': [
        {
            "role" : "user",
            "content" : f'{base_prompt}'
        }
    ],
    "keep_alive": 20, #//*** Keep Alive for 20 Seconds After this Request
}
print(base_prompt)
response = requests.post(ollama['url_chat'], headers=ollama['headers'], data=json.dumps(data))
print("=== INITIALIZING chat ===")
print(response.text)
print("===========================")

#base_prompt = "please classify this report:\n"

for i,row in enumerate(rows):
    
    if i in random_indexes:

    
        #print(row["Body"])
        data = {
            "model" : ollama['model'],
            'messages': [
                {
                    "role" : "user",
                    "content" : f'{base_prompt}\n"{row["clean_body"]}"'
                }
            ],

            "stream" : False,
            "keep_alive": 20, #//*** Keep Alive for 20 Seconds After this Request
            "format": {
                "type": "object",
                    "properties": {
                        "classify": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                        },
                        "reasoning": {
                            "type": "array",
                                "items": {
                                    "type": "string",
                                },
                        },
                        #"clean": {
                        #    "type": "boolean"
                        #},
            },
            "required": [
                "classify",
                "reasoning",
                "resolved",
                #"clean",

                ]
            },
        }

        
        #del data['format']

        #//*** The First prompt is generated differently


        response = requests.post(ollama['url_chat'], headers=ollama['headers'], data=json.dumps(data))
        print("====================")
        print("Discrepancy Report:")
        print("====================")
        print(row['clean_body'])
        
        #print (json.loads(response.text)['response'])
        print(f"{i}: ====================")
        print(f"{i}: Ollama LLM Response:")
        print(f"{i}: ====================")
        pprint.pprint (json.loads(response.text)['message']['content'])
        print("=================")

        #del data['format']
        #response = requests.post(ollama['url_chat'], headers=ollama['headers'], data=json.dumps(data))
        #print (json.loads(response.text)['message']['content'])
        #print("=================")
        
        #print("=======")

    #print(f"{i}: {row['From: (Name)']} \n {raw_text}")
    #print(f"{i}: {row['Body']}")



