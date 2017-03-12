# PDF to HTML (or TXT or XML- commented out) formats with pdfminer.six
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import HTMLConverter,TextConverter,XMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import io
import csv, re, os, sys
from timeit import default_timer as timer
import datetime as dt

def convert(case,pathin, fileHTML):

    #Define parameters to the PDF device objet   
    manager = PDFResourceManager() 
    codec = 'utf-8'
    caching = True
    laparams = LAParams()
    pagenos = set()
    password = ''
    maxpages = 0

    if case == 'text' :
        #Cast to StringIO Object
        output = io.StringIO()
        converter = TextConverter(manager, output, codec=codec, laparams=LAParams())

    if case == 'HTML' :
        #Cast to ByteIO Object for HTML or XML
        output = io.BytesIO()
        converter = HTMLConverter(manager, output, codec=codec, laparams=LAParams())

    #Create PDF interpreter object
    interpreter = PDFPageInterpreter(manager, converter)   
    infile = open(pathin, 'rb')


    #Process each page contained in the document
    for page in PDFPage.get_pages(infile, pagenos,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    convertedPDF = output.getvalue()

    infile.close()
    converter.close()
    output.close()
    
    return convertedPDF

if __name__ == "__main__":
    path1 = "/Users/dariaulybina/Desktop/georgetown/global-economics/convert_pdfs/pdfminer_p3/" #pdf inputs directory
    path2 = "/Users/dariaulybina/Desktop/georgetown/global-economics/convert_pdfs/pdfminer_p3/" #outputs directory

    #Read the list of documents to convert and make a list (make sure those documents exist in input directory)
    #data = list(csv.DictReader(open("U:\\....\\doc_list.csv", "r", encoding="UTF-8", errors="ignore"))
    #doc_list = []
    #for row in data:
        #doc = row['FILE'].strip()
        #docs = doc + '.pdf'
        #doc_list.append(docs)

    #Example file that works (example that doesn't -doc-_cr1606.pdf)
    doc_list = ['-doc-cr1701.pdf']

    #Declare case to be converted to (#if you want txt - put 'text')
    case = "HTML" 
    for filePDF in doc_list:
        print("Working with doc: {}".format(filePDF))
        fileHTML = filePDF.replace('pdf','html')
        pathin = path1 + filePDF
        pathout = path2 + fileHTML

        convertedPDF = convert(case, pathin, fileHTML)
        with open(pathout, "wb") as fileConverted:
            fileConverted.write(convertedPDF)
            fileConverted.close()

        #print(convertedPDF)
        print("Done with file {}".format(fileHTML))

        
        
 



   
       
