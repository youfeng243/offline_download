#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  gikieng.li
# @Date    2017-02-23 11:23
import subprocess
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("..")
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice, TagExtractor
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.cmapdb import CMapDB
from pdfminer.layout import LAParams
from pdfminer.image import ImageWriter
from io import BytesIO
import re
short_line_regx =re.compile("^[　]*[\S]{1,20}[　]*$", re.S|re.I)
multi_blank_regx = re.compile("[ ]{4,}")
blank = re.compile("[ ]{3,}")
def remove_invalid_seg(text):
    text = text.decode('utf-8')
    texts = text.split("\n")
    lines = []
    for line in texts:
        line = line.strip()
        if len(line) == 0:
            continue
        else:
            lines.append(line)
            if(short_line_regx.findall(line)):
                #print line , "short line"
                lines.append("\n")
            elif  line[-1] in ["：", "!", "?", "。",".","　"]:
                lines.append("\n")
                #print line, "dot end"
            elif multi_blank_regx.findall(line):
                #print line, "multi blank"
                lines.append("\n")
    return "".join(lines).replace("  ", "\t").replace(" ", "")

def pdf2txt(data, password = '', maxpages = 0, debug = 0):
    # input option
    if hasattr(data, "read"):
        inputs = data
    else:
        inputs = BytesIO()
        inputs.write(data)
    password = password
    pagenos = set()
    maxpages = maxpages
    # output option
    imagewriter = None
    rotation = 0
    stripcontrol = False
    layoutmode = 'normal'
    codec = 'utf-8'
    pageno = 1
    scale = 1
    caching = False
    showpageno = True
    laparams = LAParams()
    PDFDocument.debug = debug
    PDFParser.debug = debug
    CMapDB.debug = debug
    PDFPageInterpreter.debug = debug
    #
    rsrcmgr = PDFResourceManager(caching=caching)
    outtype = "text"
    outfp = BytesIO()
    if outtype == 'text':
        device = TextConverter(rsrcmgr, outfp, codec=codec, laparams=laparams,
                               imagewriter=imagewriter)

    elif outtype == 'xml':
        device = XMLConverter(rsrcmgr, outfp, codec=codec, laparams=laparams,
                              imagewriter=imagewriter,
                              stripcontrol=stripcontrol)
    elif outtype == 'html':
        device = HTMLConverter(rsrcmgr, outfp, codec=codec, scale=scale,
                               layoutmode=layoutmode, laparams=laparams,
                               imagewriter=imagewriter, debug=debug)
    elif outtype == 'tag':
        device = TagExtractor(rsrcmgr, outfp, codec=codec)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for page in PDFPage.get_pages(inputs, pagenos,
                                  maxpages=maxpages, password=password,
                                  caching=caching, check_extractable=False):
        page.rotate = (page.rotate+rotation) % 360
        interpreter.process_page(page)
    device.close()
    text = remove_invalid_seg(outfp.getvalue())
    return text


_jar_path_ = "/".join(__file__.split("/")[:-1]) + "/pdfparser.jar"
def pdffile2textfile(src, desc):
    #用java解析pdf
    cmd = " ".join(["java", "-Dfile.encoding=utf-8", "-jar", _jar_path_, src, desc])
    subp = subprocess.Popen(cmd,
                            shell=True,
                            stdin=file("/dev/null", "w"),
                            stdout=file("/dev/null", "w"),
                            stderr=subprocess.PIPE)
    return subp.communicate()


if __name__ == '__main__':
    if len(sys.argv)  != 2:
        print "please input pdf path!"
        exit(1)
    path = sys.argv[1]
    with open(path) as fp:
        print pdf2txt(fp)
    #sys.exit(main(sys.argv))
