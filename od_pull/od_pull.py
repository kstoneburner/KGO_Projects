# https://www.delftstack.com/howto/python/python-write-to-an-excel-spreadsheet/

import json, requests, xlsxwriter

workbook = xlsxwriter.Workbook("templates.xlsx")
sheet = workbook.add_worksheet("Templates")
shot = workbook.add_worksheet("Shots")



od_ip = "http://10.218.116.11"
endpoint = {
	"masterTemplates" : "/server/rest/api/masterTemplates"
}

tc = {}
templates = []

thelist = requests.get(f"{od_ip}{endpoint['masterTemplates']}")
jsondata = thelist.json()


sheet.write("A3","New Template")
sheet.write("B3","Old Template")
sheet.write("C3","Name")
sheet.write("D3","Transition")
sheet.write("E3","Memory")

shot.write("B3","Template")
shot.write("C3","Name")
shot.write("D3","Transition")
shot.write("E3","Memory")

row = 4
row2 = 4

for element in jsondata:
	
	if element['templateNumber'] not in templates:
		templates.append( element['templateNumber'] )

		shotName = ''

		if "shotName" in element.keys():
			shotName = element['shotName']
		print(f"{element['templateNumber']} {element['name']} {element['dbTemplateTransition']['transition']['name']} [{element['memoryNumber']}] {shotName}")
		sheet.write(f"B{row}",f"{element['templateNumber']}")
		sheet.write(f"C{row}",f"{element['name']}")
		sheet.write(f"D{row}",f"{element['dbTemplateTransition']['transition']['name']}")
		sheet.write(f"E{row}",f"{element['memoryNumber']}")
		sheet.write(f"F{row}",f"{shotName}")
		row+=1
	else:
		#//*** Template Count
		if element['templateNumber'] not in tc.keys():
			tc[element['templateNumber']] = 0

		tc[element['templateNumber']] += 1

		if "shotName" in element.keys():
			shotName = element['shotName']

		print(f"{element['templateNumber']} {element['name']} {element['dbTemplateTransition']['transition']['name']} [{element['memoryNumber']}] {shotName}")
		shot.write(f"B{row2}",f"{element['templateNumber']}")
		shot.write(f"C{row2}",f"{element['name']}")
		shot.write(f"D{row2}",f"{element['dbTemplateTransition']['transition']['name']}")
		shot.write(f"E{row2}",f"{element['memoryNumber']}")
		shot.write(f"F{row2}",f"{shotName}")
		row2+=1


print(jsondata[100].keys())
for key,value in tc.items():
	print(key,value)
	if value == 0:
		print("xxxxx")

#Template Number, Name, Transition, Memory #, Memory Name


workbook.close()