#!/Users/dariaulybina/anaconda/envs/python2/bin/python
##THIS SCRIPT USES PYTHON 2 

import sys, os, csv, re
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice, TagExtractor
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.cmapdb import CMapDB
from pdfminer.layout import LAParams
from pdfminer.image import ImageWriter


def list_files(dirin):
	pdf_list = [file for file in os.listdir(dirin) if file.endswith('.pdf')]
	return pdf_list

def main():

	dirout = '/Users/dariaulybina/Desktop/georgetown/global-economics/convert_pdfs/pdfminer_p2/tag_converted_docs/'
	dirin = '/Users/dariaulybina/Desktop/georgetown/global-economics/scrape_articles/pdfs_downloaded/'
	layoutmode = 'normal'
	codec = 'utf-8'
	laparams = LAParams()
	caching = True
	stripcontrol = True

	pdf_list = list_files(dirin)

	print pdf_list

	for fn in pdf_list:
		fname = os.path.join(dirin,fn)
		print fname 
		file_out = fn.replace('.pdf','.tag')
		outfile = os.path.join(dirout,file_out)
		#print(outfile)
		outfp = file(outfile, 'w')
		fp = file(fname, 'rb')
		rsrcmgr = PDFResourceManager(caching=caching)
		#device = TextConverter(rsrcmgr, outfp, codec=codec, laparams=laparams)
		#device = XMLConverter(rsrcmgr, outfp, codec=codec, laparams=laparams)
		#device = HTMLConverter(rsrcmgr, outfp, codec=codec,layoutmode=layoutmode, laparams=laparams)
		device = TagExtractor(rsrcmgr, outfp, codec=codec)
		interpreter = PDFPageInterpreter(rsrcmgr, device)
		for page in PDFPage.get_pages(fp):
			interpreter.process_page(page)
		fp.close()
		device.close()
		outfp.close()
		print 'Document done'
	print 'Finished all documents'

if __name__ == "__main__":
	print main()
