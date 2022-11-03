#
# PdfClass
#
import ntSys
from PyPDF2 import PdfReader, PdfWriter

class NC_Pdf:
    
# Members
    PDF_sFilename=""    
    PDF_objReader = None
    PDF_objFields=""
    PDF_objWriter=None
    PDF_nPagesRead=0
    PDF_nPagesWrite=0
    PDF_bCompress=False

# Metodi
    def __init__(self, sFilename=""):
        pass
        
# Read PDF File.
# Input: Nome (normalizzato). Ritorno: sResult
# -----------------------------------------------------------------------
    def FileRead(self, sFilename=""):
        sProc="PDF.FileRead"
        sResult=""
        
        if ntSys.ntFileExists(sFilename)==False:
            sResult="Non esistente " + sFilename
        else:
            self.PDF_sFilename=sFilename
            try:
                self.PDF_objReader = PdfReader(self.PDF_sFilename)
                self.PDF_nPagesRead = len(PDF_obj.pages)
                self.PDF_objFields=PdfReader.get_fields()
            except:
                sResult="Apertura PDF " + sFilename                    
# Ritorno
        sResult=ntSys.NF_ErrorProc(sResult, sProc)
        return sResult

# Scrive Singola Pagina
    def PDF_PageWrite(objPage):
        sProc="PDF.Page.Write"
        sResult=""        
# Scrive con inizializzaione oggetto        
        if self.PDF_objWriter==None:
            self.PDF_objWriter=PdfWriter
        if self.PDF_bCompress: page.compress_content_streams()  # This is CPU intensive!
        self.PDF_objWriter.add_page(objPage)
        # Incrementa contatore
        self.PDF_nPageWrite=PDF_nPageWrite+1
        
# Ritorno
        sResult=ntSys.NF_ErrorProc(sResult, sProc)
        return sResult
    
# Fill Singola Pagina con Variabili
    def PDF_PageFill(objPage, nPage, dictRecord):
        sProc="PDF.Page.Fill"
        sResult=""
        
    # Merge Page + Fields
        try:
            self.PDF_ObjWriter.update_page_form_field_values(objPage, dictRecord)
        except:
            sResult="PDF errore pagina " + str(nPage)
            
    # Ritorno
        sResult=ntSys.NF_ErrorProc(sResult, sProc)
        return sResult
    
# Salva PDF
    def PDF_FileSave(sFileOut):
        sProc="PDF.File.Save"
        sResult=""
    
    # Verifica
        if sFileOut=="": sResult=="PDF File da scrivere non specificato"
        if self.nPDF_PagesWrite<1: sResult "PDF Pagine da scrivere 0"
        
    # Scrive
    # write "output" to PyPDF2-output.pdf
        lResult=ntSys.NF_FileOpen(sFileOut,"wb")
        sResult=lResult[0]
        if sResult=="":
            DA COMPLETARE
    with open("filled-out.pdf", "wb") as output_stream:
    writer.write(output_stream)
        
    # Ritorno
        sResult=ntSys.NF_ErrorProc(sResult, sProc)
        return sResult        
        