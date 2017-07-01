import re, csv, os
import json


def get_Txt(Loc):
    Files = []
    for names in os.listdir(Loc):
        if names.endswith('.txt'):
            Files.append(names)
    return Files

def createJson():
	DocList = get_Txt("Tables of content repository path")
	data = []
	for doc in DocList:
		List=[]
		f = open("Tables of content repository path/{}".format(doc), 'r',encoding ='utf-8')
		C = f.readlines()
		for con in C:
			if "APPRAISAL" in con:
				break
			elif not con in ['\n','\r\n']:
				con = con.split("_")[0]
				List.append(con)
		key = doc.split(".txt")[0]
		data.append({key : List})
		json_data = json.dumps(data)
	fil = open('repository path/Json.txt','w')
	fil.write(json_data)
	fil.close
def main():
	createJson()
				
if __name__ == '__main__':
	main()
