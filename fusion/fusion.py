#"0992f28e-3e51-4945-8088-943040a7ccac" Anchor
#"0e6c1c47-91ca-46ee-8711-5fa5d2b72e71" CO-Anchor
#"4222ad42-aad4-4787-b905-cf378513bf6f" 2SHOT

import json, uuid, copy
import xml.etree.ElementTree as ET 

input_xml_path = "L:\\Vinten\\Fusion\\IGNITE_28102024.xml"
export_json_path = "L:\\Vinten\\Fusion\\Fusion_Converted.json"
explore_json_path = "L:\\Vinten\\exports\\IGNITE 2024-10-23 1428.json"

fusion = {
	"Cameras" : { #//*** Fusion : Vega

		"{dacee744-9b1d-4801-931a-f0b9a9103746}" : "b55c0ede-bd4d-43f7-ab63-e2cffafe9b2c",
		"{80b38f9a-1537-4764-b50c-894e05b2c9e8}" : "afc39ac4-9597-492e-9a72-43a601a9667f",
		"{4196f0be-dfdb-4fbe-8ff8-601a6a266d6c}" : "6f188026-fe09-4d71-9df2-f7ab1e1cd86b",
		"{fdc05602-4ba6-4abc-99fd-7098b992b286}" : "10053e28-753e-40b2-a493-5794aab3fc42",
		"{3c5ae07a-4e03-417c-960d-65d0cf843ace}" : "63ef5508-d0d7-4a84-b9e7-67d59d1f5d94",
		"b55c0ede-bd4d-43f7-ab63-e2cffafe9b2c" : "Camera1",
		"afc39ac4-9597-492e-9a72-43a601a9667f" : "Camera2",
		"6f188026-fe09-4d71-9df2-f7ab1e1cd86b" : "Camera3",
		"10053e28-753e-40b2-a493-5794aab3fc42" : "Canera4",
		"63ef5508-d0d7-4a84-b9e7-67d59d1f5d94" : "Camera5",

	},
	"CamGrid" : { #//*** Holds Counters for the Camera Grid positions
		"{dacee744-9b1d-4801-931a-f0b9a9103746}" : {
			"X" : 0,
			"Y" : 1,
		},
		"{80b38f9a-1537-4764-b50c-894e05b2c9e8}" : {
			"X" : 0,
			"Y" : 1
		},
		"{4196f0be-dfdb-4fbe-8ff8-601a6a266d6c}" : {
			"X" : 0,
			"Y" : 1,
		},
		"{fdc05602-4ba6-4abc-99fd-7098b992b286}" : {
			"X" : 0,
			"Y" : 1,
		},
		"{3c5ae07a-4e03-417c-960d-65d0cf843ace}": {
			"X" : 0,
			"Y" : 1,
		},

		"counter": {
			"X" : 0,
			"Y" : 1,
		},

	},
	"Show" : {
		"Id" : None,
		"UserId" : None,
		"Name" : None,
	},
	"ShotVectors" : { }, #//*** "VectorElementId" : "ShotId"
	"Shots" : {

	}
}


def buildFusion(input_filename):
	# writing to csv file 

	def getETValue(input_string, input_element):

		#//*** Combs the top level of the input_element looking for the input_tring
		for elem in input_element:

			try:

				#//*** If Found Return the Return children or the Text Value
				if input_string == elem.tag:

					#//*** Check for Single Element. 
					if len(list(elem)) == 0:
						return elem.text
					else:
						return list(elem)
			except:
				print("Trouble with Elem")
				print(elem)
				print(elem.text)


		#//*** Return None if not Found
		return None


	tree = ET.parse(input_filename) 

	# get root element 
	root = tree.getroot() 

	q = {}

					
	for child in root:

		print(child.tag )
		
		if child.tag == "Show":
			for showElem in child:
				if showElem.tag == "Id":
					fusion['Show']["Id"] = showElem.text
				if showElem.tag == "UserId":
					fusion['Show']["UserId"] = showElem.text
				if showElem.tag == "Name":
					fusion['Show']["Name"] = showElem.text
		if child.tag == "Shots":
			shots = child
			for shot in shots:
				
				shot_obj = {
					"Id" : None,
					"Name" : None,
					"DeviceId" : None, #//*** Camera ID
					"GridPosition" : { #//*** Radamec Values
						"RowIndex" : None,
						"ColumnIndex" : None,
						"X" : None,
						"Y" : None,
					}
				}
				
				shot_obj["Id"] = getETValue("Id", shot)
				shot_obj["Name"] = getETValue("Name", shot)
				DeviceId = getETValue("DeviceId", shot) #//*** Camera Shot ID
				shot_obj["DeviceId"] = DeviceId

				#//*** Skip Camera shots that Don't use camera1 - camera5
				if DeviceId not in fusion["Cameras"].keys():
					#print(f"Skipping Old Camera Shot: {shot_obj['Name']}" )
					continue

				grids = getETValue("GridPositions",shot)

				#//*** Grids should return two elements. Hunt for Grid Typr GPC
				for grid in grids:
					if getETValue("GridType",grid) == "Radamec":
						shot_obj["GridPosition"]["RowIndex"] = getETValue("RowIndex",grid)
						shot_obj["GridPosition"]["ColumnIndex"] = getETValue("ColumnIndex",grid)

						shot_obj["GridPosition"]["RowIndex"] = int(shot_obj["GridPosition"]["RowIndex"]) + 1
						shot_obj["GridPosition"]["ColumnIndex"] = int(getETValue("ColumnIndex",grid)) + 1

						#//*** Build Ficticious Camera grid Value.
						fusion['CamGrid']['counter']["X"]+=1

						
						#//*** If X is greater than 10, reset to 1 and increment Y. This expands the "Grid"

						xcounter_limit = 1000

#						if fusion['CamGrid'][DeviceId]["X"] > 10:
#							fusion['CamGrid'][DeviceId]["X"] = 1
#							fusion['CamGrid'][DeviceId]["Y"] += 1

						#//*** Assign CamGrid Values
#						shot_obj["GridPosition"]["X"] = fusion['CamGrid'][DeviceId]["X"]
#						shot_obj["GridPosition"]["Y"] = fusion['CamGrid'][DeviceId]["Y"]

						#//*** If X is greater than 10, reset to 1 and increment Y. This expands the "Grid"
						#if fusion['CamGrid']['counter']["X"] > xcounter_limit:
						#	fusion['CamGrid']['counter']["X"] = 1
						#	fusion['CamGrid']['counter']["Y"] += 1

						#//*** Assign CamGrid Values
						shot_obj["GridPosition"]["X"] = fusion['CamGrid']['counter']["X"]
						shot_obj["GridPosition"]["Y"] = fusion['CamGrid']['counter']["Y"]
						shot_obj["GridPosition"]["RowIndex"] = shot_obj["GridPosition"]["RowIndex"]
						shot_obj["GridPosition"]["ColumnIndex"] = shot_obj["GridPosition"]["ColumnIndex"]


				x = shot_obj["GridPosition"]["ColumnIndex"]
				y = shot_obj["GridPosition"]["RowIndex"]
				if x not in q.keys():
					q[x] = { y : {} }
					#print(f"{x} {y} : {q}" )
				else:
					if y not in q[x].keys():
						q[x][y] = {}
						#print(f"{x} {y}: { q[x].keys()} Adding")
					else:
						print(f"{x} {y}: Duplicate")
						continue


				#//*** Save the  shot_obj to the Fusion Shot Dictionary
				fusion['Shots'][shot_obj["Id"]] = shot_obj


		if child.tag == "StateVectorMaps":
			
			#//*** Loop through State VectorMaps to get the VectorElementId for each shot
			for VectorMap in list(child):
				
				ShotId = getETValue("ShotId",VectorMap)
				VectorElementId = getETValue("VectorElementId", VectorMap)
				try:
					fusion["Shots"][ShotId]["VectorElementId"] = VectorElementId
					fusion["ShotVectors"][VectorElementId] = ShotId
				except:
					continue
		
		if child.tag == "StateVectors":

			for Vector in list(child):

				ElementId = getETValue("ElementId",Vector)

				#//*** The Camera elements are String embedded XML values.
				#//*** Gotta dig a bit to get them properly converted

				StateVector = Vector.findall("./StateVector")[0]
				StateVector = ET.ElementTree(ET.fromstring(StateVector.text))
				StateVector = StateVector.getroot()

				#//*** XML Field Values are now accessible

				try:
					#//*** Get ShotId
					ShotId = fusion['ShotVectors'][ElementId]
				except:
					continue

				for x in ['Pan','Tilt','Zoom','Focus','X','Y','Elevation']:
					fusion['Shots'][ShotId][x] = getETValue(x,StateVector)


def buildVega():
	vega = {
	    "ShowConfig": {
        "Id": "914d3f95-e474-4fef-8a21-2cd45e2ec871", #//*** ShowId manually, Updated To an Exported Fusion File
        "OwnerId": "e3126ba4-a273-496f-89f7-e7b36583e16f",
        "Name": "FUSION", #//**** Manually Updated
        "SetId": "21c9abd0-028f-4857-80d5-a176f0ac8bce",
        "NumberOfColumns": 12,
        #"ShowPermissions": [
	    #        {
	    #            "ShowId": "00000000-0000-0000-0000-000000000000",
	    #            "UserGroupType": 0,
	    #            "UserGroupId": "e3126ba4-a273-496f-89f7-e7b36583e16f",
	    #            "Permission": 0
	    #        }
        # 	]
        "ShowPermissions": [ ]
    	},
    	"ShotConfigs": [ ],

    	"ModuleData":
	    {
	        "GridModule":
	        {
	            "$type": "Common.Api.ControlSystemService.GridItemConfig[], Common.Api.ControlSystemService",
	            "$values": [ ]
	        }

	    }

	} #//*** END Intialize Vega

	ShotConfig_template = {
            "Plan": {
                "$type": "Common.Api.ControlSystemService.SinglePointShotPlan, Common.Api.ControlSystemService",
                "AxisPositions": [

                ],
                "CameraId": None,
                "Index": 0,
                "TransitionTime": "00:00:02"
            },
            "Id": None,
            "Name": None
        }

	GridModule_template = {
		"$type": "Common.Api.ControlSystemService.SingleShotGridItemConfig, Common.Api.ControlSystemService",
		#"Thumbnail": "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KKSgAooooELRSUUDFopKKBhRRSUAFFFFABSZoopgGaM0UlABRRRQAUUmaKACikooGFFFJQAUlFFABSUUUDCmSfcb6U6mP9xvpQBLH/q1+gp9Rx/6tfoKfUje4tLSUUEi0tJRTELRSUtAC0UlLQAtFJRQAtKKbS0ALS0lFAC0lFFAhaKSloGLRmkozQAtFJRQAtFJmjNIBaKTNFAC0UlFAhaM0lFAxaKSigBaSiigApaSigBaKSigBaSiigANJRRQAUUUUCCikopjFopKKAFpDRRQISiiigBaSijNAwpaTNFABSUUUAFFFFABSUUUAFFFJTAKKKSgYUUUUAFJRmigAoopKBhSUUUgCkoopgFNf7jfSlpr/cb6UDHxn92v0FPBqKP7i/Sng1IPcfmikzS0CFpabS0xC0UlLQIWikooAWlpKKAFopKKAHZozSUUALRSUUCFpc0lFAxaKKKACiiigAoopKQC0UlLQAUUUUAFFFFABRSUtAgooooAKM0UUDClpKKBhRRRQAUlFFAgopKKBC0UlFMBaSiigYUUUUAGaSiigAopKKAFopKKACiiigAopKKACiikoGLRRSZpgLSZoooAKSikoAWkoooGFJRRQAUUlFABSUUUDCmv9xvpS01/uN9KQwjPyL9KkBqJD8i/Sng0hvceDTgaYDS5pkj6KTNFBItLSUUCFpc02loGLRmkooELRRRQAtGaSigB1FJRQAtFFFAC0UlFAC0UlFAC0UlFAC0UUUgCiiigAooooAKKSloAKKKKACiiigAooooGGaKKSgBaSiigQUUlFAC0UlFMAooooAKKKKACkpaSgAoopKAFopKKADNFFJQMWkzRRQAUUUUAFFFJTAKKKSgYUUUlAC0lFFABRSUUDCkoooAKSikNIAJpr/cb6UpNMf7p+lA0CH5B9KeDUafdH0p4NIp7jwacDTBSg0yWPzS5poNLQSOozSUUCHUUlFAC0tJRQAtFJRQIdRSUUALS0lFAC0UlFAxaXNJRQAuaKSjNAhaM0lFAC0UUUgCiiigBaSiigAoopKAFopKKBi0UlFAC0UlFAC0UlFABRSUUCFpKKKACiiimAUUUUAFFJRQAtFJRQAUlFFABRRRQMKKKKACikozQAUUUlAxaSiigAopKKACikopgFFFJQMWkopKACiikNAAaTNFNzSGKaY5+U/SlzTX+6fpQ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",
		"Thumbnail": "",
		"Id": None, #//*** use Element ID
		"Positions":
	[
		{
			"Name":
			{
				"$type": "Common.Api.ControlSystemService.CameraGridViewName, Common.Api.ControlSystemService",
				"CameraId": None,
			},
			"X": None,
			"Y": None
		},
		{
			"Name":
				{
					"$type": "Common.Api.ControlSystemService.GlobalGridViewName, Common.Api.ControlSystemService"
				},
				"X": None,
				"Y": None
		}
	],
	"Reference":
		{
			"TargetId": None,
			"ItemTypeName": "shot"
		}
	}

	#//*** Loop through each shot in fusion

	counter = 1
	for ShotId,shot in fusion['Shots'].items():
		
		#if shot['Name'] == "ANCHOR":
		#	print(ShotId)	
		#	print(shot)

		shotconfig = copy.deepcopy(ShotConfig_template)

		#//*** Build Shotconfig
		shotconfig["Plan"]["AxisPositions"] = [
		{
			    "Type": 4, #//*** PAN
			    "Value": shot['Pan']
			},
			{
			    "Type": 8,  #//*** Tilt
			    "Value": shot["Tilt"]
			},
			{
			    "Type": 16,  #//*** Zoom
			    "Value": shot["Zoom"]
			},
			{
			    "Type": 32,  #//*** Focus
			    "Value": shot["Focus"]
			},
			{
			    "Type": 64, #//*** Elevation
			    "Value": shot["Elevation"]
			},
			{
			    "Type": 1, #//*** X
			    "Value": shot["X"] 
			},
			{
			    "Type": 2,  #//*** Y
			    "Value": shot["Y"]
			}
		]
		
		#//*** Get Vega CameraID
		CameraId = fusion["Cameras"][shot["DeviceId"]]

		#//*** Assign Camera Id
		shotconfig["Plan"]["CameraId"] = CameraId
		shotconfig["Id"] = ShotId[1:-1] #//*** Trim the { } from the string
		shotconfig["Name"] = shot['Name']

		#print(ShotConfig_template)

		vega["ShotConfigs"].append(shotconfig)

		#//*** Build Grid Module
		gridmodule = copy.deepcopy(GridModule_template)
		#//*** Generate Random GUID if grid Temmplate Id
		gridmodule["Id"] = str(uuid.uuid4())
		gridmodule["Positions"][0]['Name']['CameraId'] = CameraId
		gridmodule["Positions"][0]['X'] = shot['GridPosition']['X']
		gridmodule["Positions"][0]['Y'] = shot['GridPosition']['Y']
		
		gridmodule["Positions"][1]['Y'] = shot['GridPosition']['RowIndex']
		gridmodule["Positions"][1]['X'] = shot['GridPosition']['ColumnIndex']
		gridmodule['Reference']["TargetId"] = ShotId[1:-1]
		vega['ModuleData']['GridModule']['$values'].append(gridmodule)
		#print(vega['ModuleData']['GridModule']['$values'])
		
		if counter > 600:
			break
		else:
			counter +=1 

	return vega

def main(): 
	buildFusion(input_xml_path)

	vega = buildVega()

	#print(fusion["Shots"]["{0288102a-78cf-4f0b-8f2c-f8af5800b554}"])
	#print(fusion)
	json_string = json.dumps(vega)

	# Writing to file
	with open(export_json_path, "w") as f:
	    # Writing data to a file
	    f.write(json_string)
	    

	with open(export_json_path, "r") as f:
		e = f.read()

		e = json.loads(e)

					

			#	if pos['Positions'][1]['Y'] not in q[pos['Positions'][1]['X']].keys():
			#		q[pos['Positions'][1]['X']][q[pos['Positions'][1]['Y']]] = {}
			#		print(f"{pos['Positions'][1]['X']} {pos['Positions'][1]['Y']} ")
			#	else:
			#		print("duplicate")


			#print(pos['Positions'][0])
			#print(pos['Positions'][0]["X"])
			#print(pos['Positions'][0]["Y"])
			


	
      
if __name__ == "__main__": 
  
    # calling main function 
    main() 