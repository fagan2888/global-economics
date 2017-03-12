Script 'pdf_to_tag_p2.py' uses Python 2 and pdfminer module to transform .pdf documents to '.tag' format (html, xml and txt are also possible)

Using pdminer in Python 2 eliminates certain issues previously discovered when using Python 3 and pdfminer.six

This output is more consistent and robust, however, certain issues are stil experienced when working with files with horizontal tables

Examples of output could be found in 'tag_converted_docs' folder
