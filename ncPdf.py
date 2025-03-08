#
# PdfClass - Facilitazione uso
# FileRead, FileWrite, Merge Record o Tabella CSV con Template in FilePdf.Out
#
import nlSys
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2 import PdfFileWriter

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

# Scrive Singola Pagina
# ----------------------------------------------------------------------
    def PageWrite(self, objPage):
        sProc="PDF.Page.Write"
        sResult=""
# Scrive con inizializzazione oggetto
        if self.PDF_objWriter==None: self.PDF_objWriter=PdfWriter
        #if self.PDF_bCompress: self.page.compress_content_streams()  # This is CPU intensive!
        self.PDF_objWriter.add_page(objPage)
        # Incrementa contatore
        self.PDF_nPagesWrite=self.PDF_nPagesWrite+1
# Ritorno
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
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
            sResult="PDF PageFill errore pagina " + str(nPage)

    # Ritorno
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        return sResult

# Fill tutte le Pagine di un record dei campi
# ----------------------------------------------------------------------
    def FileFill(self, dictRecord):
        sProc="PDF.File.Fill"
        sResult=""

    # Verifica
        print ("PDF.OBJ. Template: " + self.PDF_sModel+ ", Filename " + self.PDF_sFilename)
        sResult=nlSys.NF_StrTests([
            [(self.PDF_sModel==""), "FileTemplate non specificato","V1"],
            [(self.PDF_sFilename==""), "Filename PDF out non specificato","V2"],
            [nlSys.NF_DictLen(dictRecord)<=0, "Record csv per merge non inviato", "V3"],
            [self.PDF_nPagesRead==0,"PDF Template non letto", "V4"]])



    # Fill PDF Template
        if sResult=="":
            nlSys.NF_DebugFase(NT_ENV_TEST_PDF, "Fill PDF Start pagine: " + str(self.PDF_nPagesRead) , sProc)
            for nPage in range(1, self.PDF_nPagesRead):
        # 1: ID Page
                try:
                    objPage=self.PDF_objReader.pages[nPage]
                except:
                    sResult="Recupero in fill pagina " + str(nPage)
                    break
        # 2: Aggiunge Pagina
                if sResult=="": sResult=self.PageWrite(objPage)
        # 3: Merge Page
                if sResult=="": sResult=self.PageFill(objPage,nPage,dictRecord)

    # Salvataggio File
        if sResult=="":
            nlSys.NF_DebugFase(NT_ENV_TEST_PDF, "Fill PDF Template per " + str(self.PDF_nPagesRead) + ", Risultato: " + sResult, sProc)
            sResult=self.FileSave(self.PDF_sFilename)

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
