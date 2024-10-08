import pandas as pd
import os,shutil,sys
#//*** python -m PyInstaller --onefile placeholder.py -n Temp_Picon_Builder

incremental = False


os.system("cls")

excel_filename = "placeholder.xlsx"
ef = pd.ExcelFile(excel_filename)
print(ef.sheet_names)

local_path = os.getcwd()
magic_path = f"{local_path}\\ImageMagick\\magick.exe"
magic_path = f"magick.exe"
column_names = ["Text","Filename","Folder"]
export_root = f"{local_path}\\export"


magic_options = "-size 80x60 xc:black -fill white -pointsize 15 -gravity center -draw \"text 0,0 '123456789'\" c:\\users\\stonk013\\KGO_projects\\icon_placeholder\\export\\test_15.png"
magic_options = "-size 80x60 xc:black -fill white -pointsize 20 -gravity center -draw \"text 0,0 '1234567'\" c:\\users\\stonk013\\KGO_projects\\icon_placeholder\\export\\test_20.png"
magic_options = "-size 80x60 xc:black -fill white  -trim -gravity center -extent 80x60 -draw \"text 0,0 '12345'\" c:\\users\\stonk013\\KGO_projects\\icon_placeholder\\export\\test_25.png"
magic_options = "-size 80x60 xc:black base_black.png"

magic_options = "-size 80x60 xc:black -fill black -stroke red -gravity center caption:'Hello!' -composite z_result.png"
magic_options = "convert base_black.png  -size 80x60! -gravity center  caption:'Hello_World' -trim  -resize 80x60! -composite z_result.png"
magic_options = f"convert  -size 80x60 -fill white -gravity center  -border  0x10 -background black label:\"L:\\nAnc1\" -trim +repage -resize 80x60!! {export_root}\\x.png"
#magic_options = "-size 80x60 xc:black -fill white -pointsize 25 -gravity center -draw \"text 0,0 '123456'\" c:\\users\\stonk013\\KGO_projects\\icon_placeholder\\export\\test_30.png"
#magic_options = "-size 80x60 xc:skyblue -fill white -stroke yellow -pointsize 50 -gravity center -draw \"text 0,0 'Hello'\" test.png"

for x in sys.argv:
	if x == "--incremental":
		incremental = True



#os.system(f"{magic_path} {magic_options}")
#sys.exit()
if not incremental:
	if os.path.exists(export_root):
		print("Deleting Export Directory")
		shutil.rmtree(export_root)

	print("Creating New Export Directory")
	os.mkdir(export_root)

#//*** Parse Each Sheet in the Excel File
file_list = []
for sheet_name in ef.sheet_names:
	print(sheet_name)
	df = pd.read_excel("placeholder.xlsx",sheet_name = sheet_name, header =0)
	print(df)
	print(df.columns)

	#//*** Validate Column Names
	for index,value in enumerate(df.columns):
		if not value == column_names[index]:
			print(f"Columns don't Match!\nError:\n Excel Columns: {list(df.columns)} doesn't match {column_names}")
			print("Quitting!")
			sys.exit()

	#//***Columns are good.
	#//*** Parse Each row
	for i in df.index:
		row = df.iloc[i]

		text = row['Text']
		filename =  row['Filename']
		folder = row['Folder']
		
		try:
			#//*** Validate Filename
			if ".png" not in filename.lower():
				print("Invalid Filename, must contain .png\nskipping:",filename)
				continue
		except:
			print("Invalid Filename, must contain .png\nQuitting:",filename)
			break
		#//*** Build Folder if needed
		#//*** Rebuild Full Path for Safety
		try:
			tfolder = folder.split("\\")
			folders = []

			for xf in tfolder:
				if len(xf) > 0:
					folders.append(xf)
			folder_path = ""
			for x in folders:
				folder_path += f"\\{x}"
		except:
			folders = []
			folder_path = ""

		
		running_foldername = ""
		for fname in folders:
			if len(folder_path) == 0:
				continue
			running_foldername += f"\\{fname}"
			#print("Running Folder Name:", running_foldername)
			if not os.path.isdir(export_root+running_foldername):
				print("Making Directory:",export_root+running_foldername)
				os.mkdir(export_root+running_foldername)
			#else:
			#	print("Directory Exists:",export_root+running_foldername)

		whole_filename = export_root+running_foldername+"\\"+filename
		#whole_filename = ".\\export"+running_foldername+"\\"+filename
		#{export_root}\\x.png
		
		#print(magic_options)
		file_list.append(running_foldername+"\\"+filename)
		
		if incremental and os.path.exists(whole_filename):
			print("Skipping: "+whole_filename)
			continue

		magic_options = f"convert  -size 80x60 -fill white -gravity center  -border  0x10 -background black label:\"{text}\" -trim +repage -resize 80x60!! \"{whole_filename}\""
		print("Making File:",whole_filename)
		
		os.system(f"{magic_path} {magic_options}")
		
		#print("Text:",text)
		#print("Path:",folder,"\\",filename)
		#print("local Path", local_path)
		#print("Folder_path", folder_path)

whole_text = ""
for f in file_list:
	whole_text += f+"\n"

with open(export_root+"\\Icon_filepaths.txt", "w") as text_file:
    text_file.write(whole_text)


	
	


