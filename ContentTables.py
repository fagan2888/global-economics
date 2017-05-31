from bs4 import BeautifulSoup
import re, csv, os


def getTable(filename):
		with open('C:/Users/AYB/ProjPdf/HTMLs/{}'.format(filename), 'rb') as html:
			soup = BeautifulSoup(html,"lxml")
		test = soup(text=re.compile(r'.*_.[0-9]'))
		filename2 = filename.replace('html','txt')
		f = open('C:/Users/AYB/ProjPdf/Tables/{}'.format(filename2), 'w')
		for elem in test:
			f.write(elem)
			f.write('\n')
		f.close()
def rreplace(s,old,new,occurrence):
	li = s.rsplit(old,occurrence)
	return new.join(li)
def get_Htmls(Loc):
    Files = []
    for names in os.listdir(Loc):
        if names.endswith('.html'):
            Files.append(names)
    return Files
def get_Txt(Loc):
    Files = []
    for names in os.listdir(Loc):
        if names.endswith('.txt'):
            Files.append(names)
    return Files
def txttocsv(filenames):	
		F= open("C:/Users/AYB/ProjPdf/Tables/{}".format(filenames),'r')
		C = F.readlines()
		List=[]
		filename2 = filenames.replace('txt','csv')
		for con in C:
			if not con in ['\n','\r\n']:
				con = rreplace(con,"_",";",1)
				con = con.replace("_","")
				CONT= {'topic': con.split(";")[0], 'page': con.split(";")[1].split("\n")[0]}
				List.append(CONT)
		fieldnames = ['topic','page']
		CS = open('C:/Users/AYB/ProjPdf/CsvTables/{}'.format(filename2), 'w', newline='', encoding ='utf-8')
		writer = csv.DictWriter(CS, fieldnames = fieldnames)
		writer.writeheader()
		for T in List:
			writer.writerow(T)
		CS.close()
def main():
	DocList = get_Htmls("/Users/AYB/ProjPdf/HTMLs/")
	DocList2 = get_Txt("/Users/AYB/ProjPdf/Tables/")
	for doc in DocList: 
		getTable(doc)
	for doc2 in DocList2:
		txttocsv(doc2)
if __name__ == '__main__':
	main()

