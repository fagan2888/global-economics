from bs4 import BeautifulSoup
import re, csv


def getTable(filename):
		with open('C:/Users/AYB/ConTable/{}.html'.format(filename), 'rb') as html:
			soup = BeautifulSoup(html,"lxml")
		test = soup(text=re.compile(r'.*_.[0-9]'))
		f = open('{}.txt'.format(filename), 'w')
		for elem in test:
			f.write(elem)
			f.write('\n')
		f.close()
def rreplace(s,old,new,occurrence):
	li = s.rsplit(old,occurrence)
	return new.join(li)

def txttocsv(filenames):	
		F= open("{}.txt".format(filenames),'r')
		C = F.readlines()
		List=[]
		for con in C:
			if not con in ['\n','\r\n']:
				con = rreplace(con,"_",";",1)
				con = con.replace("_","")
				CONT= {'topic': con.split(";")[0], 'page': con.split(";")[1].split("\n")[0]}
				List.append(CONT)
		fieldnames = ['topic','page']
		CS = open('{}.csv'.format(filenames), 'w', newline='', encoding ='utf-8')
		writer = csv.DictWriter(CS, fieldnames = fieldnames)
		writer.writeheader()
		for T in List:
			writer.writerow(T)
		CS.close()
def main():
	DocList = ["-doc-cr1742","-doc-cr1750","-doc-cr1753"]
	#for doc in DocList:
		#getTable(doc)
	for doc in DocList:
		txttocsv(doc)
if __name__ == '__main__':
	main()

