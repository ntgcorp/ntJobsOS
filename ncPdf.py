#
# PdfClass - Facilitazione uso
# FileRead, FileWrite, Merge Record o Tabella CSV con Template in FilePdf.Out
#
import nlSys
from PyPDF2 import PdfReader, PdfWriter
from fillpdf import fillpdfs

# Test Mode
NT_ENV_TEST_PDF=True

class NC_Pdf:

# Può essere sia letto che scritto
# Members
    PDF_Filler1=""
    PDF_sModel=""
    PDF_sFilename=""
    PDF_objReader = None
    PDF_objFields=""
    PDF_objWriter=None
    PDF_nPagesRead=0
    PDF_nPagesWrite=0
    PDF_bCompress=False

# Metodi
    def __init__(self):
        pass

# Read PDF File.
# Input: Nome (normalizzato). Ritorno: sResult
# -----------------------------------------------------------------------
    def FileRead(self, sFilename=""):
        sProc="PDF.FileRead"
        sResult=""

        if nlSys.NF_FileExist(sFilename)==False:
            sResult="Non esistente " + sFilename
        else:
            self.PDF_sFilename=sFilename
            self.PDF_sModel=sFilename
            try:
                nStep=1
                self.PDF_objReader = PdfReader(self.PDF_sFilename)
                nStep=2
                self.PDF_nPagesRead = len(self.PDF_objReader.pages)
                nStep=3
                self.PDF_objFields=self.PDF_objReader.get_fields()
            except:
                sResult="Apertura PDF. Step " + str(nStep) + ": " + self.PDF_sFilename
# Ritorno
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        return sResult

# Fill tutte le Pagine di un record dei campi
# ----------------------------------------------------------------------
    def FileFill(self, dictRecord):
        sProc="PDF.File.Fill"
        sResult=""

    # Verifica
        print ("PDF.OBJ. Template: " + self.PDF_sModel + ", Filename " + self.PDF_sFilename)
        sResult=nlSys.NF_StrTests([
            [(self.PDF_sModel==""), "FileTemplate non specificato","V1"],
            [(self.PDF_sFilename==""), "Filename PDF out non specificato","V2"],
            [nlSys.NF_DictLen(dictRecord)<=0, "Record csv per merge non inviato", "V3"],
            [self.PDF_nPagesRead==0,"PDF Template non letto", "V4"]])

    # Get Fields
        if sResult=="":
            try:
                fillpdfs.get_form_fields(self.PDF_sModel)
            except:
                sResult="Recupero campi da template"

# returns a dictionary of fields
# Set the returned dictionary values a save to a variable
# For radio boxes ('Off' = not filled, 'Yes' = filled)
#data_dict = {
#'Text2': 'Name',
#'Text4': 'LastName',
#'box': 'Yes',
#}
    # Fill PDF
        if sResult=="":
            try:
                fillpdfs.write_fillable_pdf(self.PDF_sModel, self.PDF_sFilename, dictRecord)
            except:
                sResult="Riempimento campi in template"

   # Ritorno
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
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
        lResult=nlSys.NF_FileOpen(sFileOut,"wb")
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
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        return sResult
