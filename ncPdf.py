#
# PdfClass - Facilitazione uso
# FileRead, FileWrite, Merge Record o Tabella CSV con Template in FilePdf.Out
#
import nlSys
from PyPDF2 import PdfReader, PdfWriter

class NC_Pdf:

# Può essere sia letto che scritto
# Members
    PDF_sFilename=""
    PDF_objReader = None
    PDF_objFields=""
    PDF_objWriter=None
    PDF_objWriterFile=None
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
# ----------------------------------------------------------------------
    def PageWrite(self, objPage):
        sProc="PDF.Page.Write"
        sResult=""
# Scrive con inizializzazione oggetto
        if self.PDF_objWriter==None: self.PDF_objWriter=PdfWriter
        if self.PDF_bCompress: page.compress_content_streams()  # This is CPU intensive!
        self.PDF_objWriter.add_page(objPage)
        # Incrementa contatore
        self.PDF_nPagesWrite=self.PDF_nPagesWrite+1
# Ritorno
        sResult=ntSys.NF_ErrorProc(sResult, sProc)
        return sResult

# Fill Singola Pagina con Variabili
# ----------------------------------------------------------------------
    def PageFill(self, objPage, nPage, dictRecord):
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

# Fill tutte le Pagine
# ----------------------------------------------------------------------
    def FileFill(self, dictParams):
        sProc="PDF.File.Fill"
        sResult=""

    # Parametri
        sFileIn=ntSys.NF_DictGet(dictParams,"FILE.IN")
        sFileOut=ntSys.NF_DictGet(dictParams,"FILE.OUT")
        dictCSV=ntSys.NF_DictGet(dictParams,"CSV.RECORD")

    # Verifica
        if self.PDF_sFileIn=="" or self.PDF_sFile_Out=="": sResult="FileIn o FileOut non specificati"
        if ntSys.NF_DictLen(dictCSV)<=0: sResult="Tabella csv merge non inviata"
        if self.PDF_nPagesRead==0: sResult="PDF Template non letto"

    # Fill PDF Template
        for nPage in range(0, self.PDF_nPagesRead-1):
        # Record
            try:
                objPage=self.PDF_objReader.page[nPage]
            except:
                sResult="Recupero in fill pagina " + str(nPage)
                break
            if sResult=="": sResult=self.PageFill(objPage,nPage,dictRecord)

    # Salvataggio File
        if sResult: sResult=self.FileSave(sFileOut)

    # Ritorno
        sResult=ntSys.NF_ErrorProc(sResult, sProc)
        return sResult

# Salva PDF
# ----------------------------------------------------------------------
    def FileSave(self, sFileOut):
        sProc="PDF.File.Save"
        sResult=""

    # Verifica
        if sFileOut=="": sResult="PDF File da scrivere non specificato"
        if self.nPDF_PagesWrite<1: sResult="PDF Pagine da scrivere 0"

    # Imposta File Out
        self.sPDF_Filename=sFileOut

    # Scrive File
        lResult=ntSys.NF_FileOpen(sFileOut,"wb")
        sResult=lResult[0]
        if sResult=="":
            self.PDF_ObjWriterFile=lResult[1]
            try:
                self.PDF_ObjWriter.write(self.PDF_ObjWriterFile)
            except:
                sResult="Errore scrittura su file " + sFileOut
    # Chisura File
        if sResult=="": self.PDF_objWriterFile.close

    # Ritorno
        sResult=ntSys.NF_ErrorProc(sResult, sProc)
        return sResult
