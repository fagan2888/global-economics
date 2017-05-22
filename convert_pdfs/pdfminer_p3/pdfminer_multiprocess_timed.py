# PDF to HTML (or TXT or XML- commented out) formats with pdfminer.six
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import HTMLConverter,TextConverter,XMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import io
import csv, re, os, sys
from timeit import default_timer as timer
import datetime as dt
import multiprocessing

def get_files(path1):
    Files = []
    for names in os.listdir(path1):
        if names.endswith('.pdf'): #later add those that end with .PDF
            if names not in redund:
                Files.append(names)
    return Files

def convert(i,doc_list,path1,path2):
    filePDF = doc_list[i]
    print("Working with doc: {}".format(filePDF))
    fileHTML = filePDF.replace('pdf','html')
    pathin = path1 + filePDF
    pathout = path2 + fileHTML

    #Define parameters to the PDF device objet
    manager = PDFResourceManager()
    codec = 'utf-8'
    caching = True
    laparams = LAParams()
    pagenos = set()
    password = ''
    maxpages = 0

    #Bytes IO used for XML and HTML conversions
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

    with open(pathout, "wb") as fileConverted:
        fileConverted.write(convertedPDF)
        fileConverted.close()
           
    print("Done with file: {} numbered: {}".format(fileHTML,i))

    return

if __name__ == "__main__":
    startTotal = timer()
    log = open('Log_{}.txt'.format(str(dt.datetime.today().strftime("%m.%d.%Y"))), 'w')
    path1 = "U:\\tas\\" #inputs directory
    path2 = "U:\\pdfs\\htmls\\" #outputs directory

    doc_list = get_files(path1)

    log.write('All files (.pdf) in original directory: {}\n'.format(doc_list))
    log.write('Total documents (.pdf): {}\n'.format(len(doc_list)))
    print('Total documents (.pdf): {}\n'.format(len(doc_list)))
    
    for i in range(len(doc_list)-1):
        p = multiprocessing.Process(target = convert, args=(i,doc_list,path1,path2,))
        p.start()
        p.join(90)
        if p.is_alive():
            p.terminate()


    endTotal = timer()
    log.write('Total time: {} seconds.\n\n'.format(endTotal - startTotal))
#########Files that didn't convert(from terminal output)
       


