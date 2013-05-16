# -*- coding: utf-8 -*-
"""
Created on Wed May 15 13:18:58 2013

@author: teacher
"""

from fpdf import FPDF

with open("BatchPRocessingStarburstLayerV2.py") as f:
    lines = f.readlines()


parameter1 = 100
parameter2 = 200
parameter3 = 300
sac_width = 300


pdf = FPDF(orientation = 'P', unit = 'pt', format = 'Letter')
pdf.add_page()
pdf.set_font('Arial', 'B', 12)
print 'pre-image', pdf.get_x(), pdf.get_y()
pdf.image('sac.jpg', 20, 10, sac_width)
pdf.image('sac.jpg', 20 + sac_width, 10, sac_width)
print 'post-image', pdf.get_x(), pdf.get_y()
pdf.set_xy(40, sac_width)
print 'post set', pdf.get_x(), pdf.get_y()
pdf.ln(h=20)
print 'post ln', pdf.get_x(), pdf.get_y()
pdf.cell(0, 0, 'Parameters')
print 'post-par', pdf.get_x(), pdf.get_y()
pdf.ln(h=12)
print 'post ln', pdf.get_x(), pdf.get_y()
pdf.set_font('Arial', size=12)
#for k,v in list(locals().iteritems()):
#    if k[0] == 'p':
#        print 'pre-parX', pdf.get_x(), pdf.get_y()
#        pdf.cell(0, 0, '{0} = {1}'.format(k, v))
#        pdf.ln(h=20)
left_margin = pdf.get_x()
parameters_y = pdf.get_y()
center = 300
tab = left_margin
cell_x = 0
cell_y = 0
print_line = False
for line in lines:
    #line = line.strip()
    if line[:7] == "# Build":    
        tab = center
        pdf.set_y(parameters_y+12)
    if line == "'print_stop'\n":
        print_line = False
    if print_line:
        pdf.set_xy(tab, pdf.get_y()+12)
        pdf.cell(cell_x, cell_y, line)
        print line, pdf.get_x(), pdf.get_y() 
    if line == "'print_start'\n":
        print_line = True
        pdf.set_xy(pdf.get_x(), pdf.get_y()+12)
pdf.output('parameters.pdf', 'F')