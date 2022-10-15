# https://pythonbasics.org/tkinter-filedialog/
# https://pythonguides.com/python-tkinter-text-box/
#//*** pyinstaller --onefile caprica_merge.py -n KGO_Caprica_CC_Merge

# Import the required Libraries
from tkinter import *
from tkinter import ttk, filedialog
from tkinter.filedialog import askopenfile
from functools import partial
import json,sys,os,gzip,tarfile,shutil,time

debug_mode = False

# Create an instance of tkinter frame
win = Tk()
win.title("KGO_Caprica_CC_Merge")

class widget_builder():

	def __init__(self):
		self.widget_holder = {}
		self.merge_source_filename = None
		self.merge_target_filename = None

	
	def open_file(self,target):
		name = filedialog.askopenfilename(filetypes=[('Caprica Files', '*.tgz')]) 

		if name:
			if target == "merge_source_filename":
				self.merge_source_filename = name
				self.widget_holder["merge_source_label"]["text"] = name

			if target == "merge_target_filename":
				self.merge_target_filename = name
				self.widget_holder["merge_target_label"]["text"] = name

	def add_widgets(self,input_obj,win=win):

		#//*** Initialize empty options 
		options = {}

		#//*** Build Options if it exists
		if "options" in input_obj.keys():

			options = input_obj["options"]

		#//*** Add Default Text value
		options["text"] = "No Text Specified"

		#//*** Assign default values
		row = -1
		column = -1
		columnspan = -1
		obj_type = None
		hook = None
		action = None
		target = None
		text = None
		width = -1
		
		#//*** Assign values based on input_obj key.
		#//*** Items NOT listed in verify_key list will not be proccessed.
		#//*** This is an explicit whitelist process
		#for verify_key in ["row","column", "type", "hook", "action", "target", "text", "columnspan", "width"]:

		for verify_key in input_obj.keys():

			if verify_key == "row":
				row = input_obj[verify_key]


			if verify_key == "column":
				column = input_obj[verify_key]

			if verify_key == "type":
				obj_type = input_obj[verify_key]

			if verify_key == "hook":
				hook = input_obj["hook"]

			if verify_key == "action":
				action = input_obj["action"]

			if verify_key == "target":
				target = input_obj["target"]

			if verify_key == "text":
				options["text"] = input_obj["text"]

			if verify_key == "columnspan":
				columnspan = input_obj["columnspan"]

			if verify_key == "width":
				width = input_obj["width"]


		if row == -1:
			print("QUITTING widget: Widget missing Row attribute")
			print(input_obj)
			return

		if column == -1 and columnspan == -1:
			print(column,columnspan)
			print("QUITTING widget: Widget missing Column attribute")
			print(input_obj)
			return

		if obj_type == None:
			print("QUITTING widget: Widget missing type attribute")
			print(input_obj)
			return

		#//*** Build Grid Object to handle row, column, columspan values
		grid = { "sticky" : "W"}

		if row != -1:
			grid["row"] = row

		if column != -1:
			grid["column"] = column
		else:
			grid["columnspan"] = columnspan

		#//*** Process the object types: Labels, buttons, etc
		if "type" in input_obj.keys():

			if input_obj["type"] == "label":

				if "text" in input_obj.keys():
					options["text"] = input_obj["text"]

				options["width"] = width


				if hook == None:
					#//*** No Hook, just draw the label
					Label(win,options).grid(grid)
				else:
					#//*** Build Label
					self.widget_holder[hook] = Label(win,options)

					#//*** Draw Label
					self.widget_holder[hook].grid(grid)


			if input_obj["type"] == "button":

				if action == "select_filename":

					options['command'] = self.open_file

				elif action == "export":
					options['command'] = self.export




				if hook == None:
					ttk.Button(win, text=options["text"], width=width, command=options['command']).grid(grid)
				else:
					#//*** Build Hooked Button
					self.widget_holder[hook] = ttk.Button(win, text=options["text"], width=width, command=partial(options['command'],target) )

					#//*** Draw Hooked Button
					self.widget_holder[hook].grid(grid)


		else:
			#//*** No type in keys, kinda can't do anything
			pass

	def draw_response(self,input_text):
		self.widget_holder["response_label"]["text"] = input_text
		win.update()

	def export(self):
		print("Source: ",self.merge_source_filename)
		print("Target:" ,self.merge_target_filename)



		#### Build the Export Folder Path
		if not os.path.exists(export_folder):
			os.mkdir( export_folder)

		#### Build the Temporary Folder Path
		if not os.path.exists(tempFolderName):
			os.mkdir(tempFolderName)

		self.draw_response("Working......")

		#//******************************************
		#//*** Verify Files are selected and Exist
		#//******************************************
		try:
			if not os.path.exists(self.merge_source_filename):
				self.draw_response("Problem Opening Source File")
				return
		except:
			self.draw_response("Please Select a Source File")
			return

		try:
			if not os.path.exists(self.merge_target_filename):
				self.draw_response("Problem Opening Target File")	
				return
		except:
			self.draw_response("Please Select a Target File")
			return


		#//************************************
		#//*** Open the Source File
		#//************************************
		try:
			srcTar = tarfile.open(self.merge_source_filename,"r:gz")
		except:
			self.draw_response("Trouble opening Source file. Is it a Caprica .tgz file?")
			return

		#//************************************
		#//*** Open the Destination File
		#//************************************
		try:
			dstTar = tarfile.open(self.merge_target_filename,"r:gz")
		except:
			self.draw_response( "Trouble opening Destination file. Is it a Caprica .tgz file?")
			return
		
		#//*** Extract the target folder. We'll be keeping most of these
		dstTar.extractall(tempFolderName,dstTar.getmembers())
		
		for item in srcTar.getmembers():
			if "./caprica/data/flash/custct/" in item.name:
				#//*** Only Process xml files
				if ".xml" in item.name:
						#//*** Get the Bank number from the name
						#//*** Get just the filename by splitting by "/"
						#//*** Remove the prepended CC
						#//*** Split by _ and grab the first field
						#//*** Convert to int to type match self.banks
						tar_bank = int(item.name.split("/")[-1].replace("cc","").split("_")[0])
						
						#//*** If zero based index tar_bank matches zero based index in self.banks we keep sync the file
						if tar_bank in self.banks:
							print("Extracting " + item.name + " from source Acuity File to working Folder")
							self.draw_response("Extracting " + item.name + " from source Acuity File to working Folder")
							sourceCC = srcTar.extractfile(item.name)
							print("Writing " + item.name + " to Temporary Files")
							self.draw_response("Writing " + item.name + " to Temporary Files")
							f = open(tempFolderName + "/"+ item.name,"wb")
							f.write(sourceCC.read())
							f.close()
		
		destFilename = export_folder + "merged_"+self.merge_target_filename.split("/")[-1]

		destFilename = os.getcwd() +  "\\merged\\merged_"+self.merge_target_filename.split("/")[-1]

		finalTar = tarfile.open(destFilename,"w:gz")
		
		for root, dirs, files in os.walk(tempFolderName.replace("/","\\")):
		#for root, dirs, files in os.walk(os.getcwd()):
			#for dir_ in dirs:
			#	finalTar.add(os.path.join(root, dir_))
			#	print(os.path.join(root, dir_))
			
			for file in files:
				filename = root.replace(os.getcwd(),"")+"\\"+file
				filename = root.replace(tempFolderName.replace("/","\\"),"")+"\\"+file
				
				finalTar.add(os.path.join(root, file),arcname=filename)
				print("Adding: " + filename)
				self.draw_response("Adding: " + filename)
		finalTar.close()
		
		################################################
		################################################
		#### File Cleanup
		################################################
		################################################
		#### Delete Files in temporary Directory
		################################################
		print("Deleting Temp Files")
		for root, dirs, files in os.walk(tempFolderName + "/"):
			for name in dirs:
				self.draw_response("Delete Temp File:"+name)
				print(name)
		print("Deletng Temp Folder")
		self.draw_response("Deletng Temp Folder")
		shutil.rmtree(tempFolderName)
		print(tempFolderName)
		self.draw_response("Merged file saved to:\n"+destFilename)


#//*************************************
#//*** End widget_builder class
#//*************************************

if __name__ == '__main__':

	config_filename = "settings.config"
	export_folder = "merged/"
	banks = []
	tempFolderName = "exaction_temp/"

	tempFolderName = "./" + export_folder + tempFolderName



	# Set the geometry of tkinter frame
	win.geometry("900x300")

	#//*** Initialize Widget Builder Object
	wb = widget_builder()

	#//*** Load Widget Parameters from JSON
	#//*** Everything loads from an object making it easy to add widgets to the GUI
	with open("widgets.json", "r") as f:
		widgets = json.loads(f.read())

	#//*** Process settings.config file
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

	                #print(f">{key}<")
	                #print(f">{value}<")

	                if key == "HOST":
	                    HOST = value

	                if key == "banks":
	                    banks = []
	                    for x in value.split(","):
	                        try:
	                            banks.append( int(x.strip()) )
	                        except:
	                            pass
	else:
		print("Configuration File Missing: player.config")
		print("Quitting")
		sys.exit()

	bank_msg = "Merging Custom Control Bank(s): "
	for bank in banks:
		bank_msg += f"{bank},"

	bank_msg = bank_msg[:-1]
	#//*** Convert banks to Zero based indexes
	for x in range(len(banks)):
		banks[x] = int(banks[x])-1
	

	#//*** Assign zero based banks to wb class
	wb.banks = banks

	#//*** Load each widget into the gui
	for widget in widgets:
		wb.add_widgets(widget)

	wb.widget_holder["bank_label"]["text"] = bank_msg		
	#//*** Automatically assign source and target files if in debug mode
	if debug_mode:
		filename = "WLS_CAPRICA NEW GFX 7-13-22.tgz"
		wb.merge_source_filename = filename
		wb.widget_holder["merge_source_label"]["text"] = filename


		filename = "KGO_PCR3_Launch_Candidate_9.tgz"
		wb.merge_target_filename = filename
		wb.widget_holder["merge_target_label"]["text"] = filename


	#//*** Run the GUI
	win.mainloop()



