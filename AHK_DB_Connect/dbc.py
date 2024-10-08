import sys
import pyodbc,json,re,socket, pyperclip
#import time

#//*** pyinstaller --onefile dbc.py -n kgo_dalet_AHK_Connect.exe

itemID = None
titleID = None

#print(sys.argv)


for x in sys.argv:

	if "ItemId" in x:
		print (x)
		
		x = x.split(":")

		x[0] = x[0].split("=")[-1]

		itemID = x[2]

		lastnum = False

		try:
			int(itemID[-1])
			lastnum = True
		except:
			pass

		while not lastnum:
			#//*** Trim Last character
			itemID = itemID[:-1]

			#print("Loop:",itemID)
			try:
				int(itemID[-1])
				lastnum = True
			except:
				pass




		#print("itemID",itemID)
		#print(int(itemID[-1]))


	if "Id=" in x and "Parent" not in x:
		for rawid in x.split(" "):
			if "Id=" in rawid:
				titleID = rawid.replace("Id=","")

#print("itemID",itemID)
#print("titleID",titleID)

if itemID == None:
	print("itemID Not Found in ", sys.argv)
	
	sys.exit()

if titleID == None:
	print("TitleID Not Found in ", sys.argv)
	
	sys.exit()



server = 'OM-CASF-DLSQL' 
database = 'DaletDB' 

with open('./ignore_folder/misc.json') as f:
    data = json.loads(f.read())

username = data["user"] 
password = data["password"]
del data

cnxn = pyodbc.connect('Trusted_Connection=yes;DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

#print(username + ":" + password)
#print(server + ":" + database)


query = f"""
            SELECT *
            FROM items
            WHERE item_id='{itemID}'
            """

cursor.execute(query)
result = cursor.fetchall()


response = {
	"format" : None,
	"graphics" : None,
	"anc" : None,
	"stage" : None,
	"cam" : None
 }

for row in result:

	for raw in row:
		
		if "<Story" in str(raw):
			#print(raw)
			
			for x in raw.split("><"):
				if "custom" in x:
					print(x)
					#//*** Get Text From Field
					q = re.findall(">.+?<",x)
					if len(q) == 1:
						q = q[0][1:][:-1]
					else:
						q = ""
					
					if "custom10" in x:
						#print("Stage:",q)
						response["stage"] = q

					if "custom8" in x:
						#print("cam:",q)
						response["cam"] = q



#TitleDataDictString -- TitleId

query = f"""
            SELECT *
            FROM TitleDataDictString
            WHERE TitleId='{titleID}'
            """

cursor.execute(query)
result = cursor.fetchall()

for row in result:
	if row[0] == 1173:
		response["format"] = row[3]
	if row[0] == 1215:
		response["graphics"] = row[3]
	if row[0] == 1216:
		response["anc"] = row[3]

print(response)

msg = f"response:rundown_story_items,format:{response['format']},graphics:{response['graphics']},anc:{response['anc']},stage:{response['stage']},cam:{response['cam']}"

pyperclip.copy(msg)


#///*** Dictionary Datafield Values: DataField_Id = rundown Column
#1173 - Format
#1216 - Graphics
#1215 - Ancs


query = f"""
            SELECT *
            FROM DataFields
            WHERE DataField_Id='1173'
            """
#cursor.execute(query)
#result = cursor.fetchall()

#for x in result:
#	print(x)

query = f"""
            SELECT *
            FROM DataFields
            WHERE DataField_Id='1215'
            """
#cursor.execute(query)
#result = cursor.fetchall()

#for x in result:
#	print(x)
