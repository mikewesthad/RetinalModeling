import os
import pyPdf

def mergePDFs(output_path, filepaths):
    output      = pyPdf.PdfFileWriter()

    filehandles = []
    for filepath in filepaths:
        fh  = file(filepath, "rb")
        pdf = pyPdf.PdfFileReader(fh)
        output.addPage(pdf.getPage(0))
        filehandles.append(fh)
    
    outputStream = file(output_path, "wb")
    output.write(outputStream)
    outputStream.close()
    
    for (fh, filepath) in zip(filehandles, filepaths): 
        fh.close()
        os.remove(filepath)
        

mergePDFs("Retina_0_Decay_Analysis.pdf", ["0_Starburst Output Weights",
                                    "1_Starburst Output Weights",
                                    "2_Starburst Output Weights",
                                    "3_Starburst Output Weights",
                                    "Decay Rate_Summary_Activity",
                                    "Decay Rate_Along Dendrite_Activity",
                                    "Decay Rate_Distal Compartment_Activity"])