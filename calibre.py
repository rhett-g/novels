"""This is general purpose utility file to create epubs given chapter titles
and chapter text in html format"""
from collections import namedtuple

chapter_info = namedtuple('chapter_info', 'url title html')


def create_toc(chapters):
    """Calibre requires that we have a TOC for multi-chapter html input"""
    toc_file = open("tmp/TOC.html", "w")
    indent = "  "
    toc_file.write("<html>\n")
    toc_file.write(indent*2+"<body>\n")
    toc_file.write(indent*3+"<h1>Table of Contents</h1>\n")
    toc_file.write(indent*3+"<p style='text-indent:0pt'>\n")
    for chapter in chapters:
        toc_file.write(indent*4+"<a href='"+chapter.title+".html'>"+chapter.title+"</a><br/>\n")
    toc_file.write(indent*3+"</p>\n")
    toc_file.write(indent*2+"</body>\n")
    toc_file.write("</html>\n")
    toc_file.close()
