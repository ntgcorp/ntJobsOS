
# ntData - Azioni su File di dati
# -----------------------------------------------------------
# Elaborazioni su file di dati, conversioni ed altro
# Sintax: ntData inputFileINI.ini
# Fasi:
# 1=Argomenti
# 2=File_INI in Dictionary - 2b=Verifica_Parametri_INI
# 3=Azione
# 4=Creazione jobs.end in stessa cartella file.ini
# ------------------------------- Setup ----------------------
import nlSys, nlDataFiles, ncJobs
from ncJobs import NC_Sys
from nlDataFiles import NC_CSV
from ncPdf import NC_Pdf

# Test Mode
NT_ENV_TEST_DATA=True

# Global App Container
jData=None

# Partenza
# Ritorno sResult
# 1: Setup interno
# 2: Argomenti di lancio
# 3: Lettura INI Setup
# 4: Lettura CSV Dati
# 5: Esecuzione Azione scelta
# 6: Return Execution Job
# -------------------------------------------------------
def NTD_Start():
    sProc="NTD.Start"
    global jData
    sResult=""

# Application Object
    jData=NC_Sys("NTDATA")

# Setup e Argomenti CMDLINE
# -----------------------------------------------------------------------------
    jData.bINI=True
    jData.bTest=True
    jData.sIniTest="Test\Test_ntData_PDF_FILL.ini"
    jData.asActions=["PDF.FILL"]

# Argomenti
# -----------------------------------------------------------------------------
    sResult=jData.Args()

# Parametri: Lettura INI JOB
# ----------------------------------------------------------------------------
    if sResult=="": sResult=jData.ReadINI()
    if sResult=="": ntSys.NF_DebugFase(NT_ENV_TEST_DATA, "INI CONFIG. Keys " + ntSys.NF_DictStr(jData.dictINI), sProc)

# Parametri: Lettura CSV se presende
# ---------------------------------------------------------------------------
    if sResult=="": sResult=jData.ReadCSV()
    if sResult=="":
        ntSys.NF_DebugFase(NT_ENV_TEST_DATA, "Lettura file CSV. Risultato: " + sResult, sProc)

# Esecuzione Azioni
# ------------------------------------------------------------------------------
# GESTIONE SINGOLE AZIONI
    if sResult=="":
    # Ciclo Azioni
        for sAction in jData.asActions:
        # Start Azione X
            ntSys.NF_DebugFase(NT_ENV_TEST_DATA, "Azione:" + sAction, sProc)
    # ---------- AZIONI PREVISTE [DA CAMBIARE SOLO QUESTA PARTE X N.AZIONI ---------------
        # AZIONE PDF.FILL
            if sAction=="PDF.FILL":
                lResult=NTD_PDF_Fill()
                sResultAction=lResult[0]
    # ----------- AZIONE ERRATA ----------------
            else:
                sResultAction="Azione JOB non prevista: " + sAction
    # ----------- RITORNO AZIONE ----------------
            self.sResult=sResultAction
            # Prende Files
            if sResultAction=="": self.dictReturnFiles=lResult[1]
            # Scrive Ritorno
            sResult=jData.EndJob()
            sResult=ntJobsApp.ReturnCalcWrite(sResult,jData,dictReturnFiles)
    # Conclusione
    ntSys.NF_AssertPrint(sResult!="","Errore calcolo/scrittura ritorno JOB: " + sResult, "Fine Job: " + jData.sTS_End)

# Ritorno
    return sResult

# ------------------ BODY SINGOLE AZIONI ----------------------

# Azione: PDF.FILL - Stessa cartella del file INI
# ------------------------------------------------------------------------------
# Usa NTD_dictINI, NTD_dictCSV
# Ritorno lResult 0=sResult, 1=dictFilecreato (FIELD.KEY=FILE.Creato), FIELD.KEY senza spazi
def NTD_PDF_Fill():
    global NTD_dictINI, NTD_dictCSV
    sProc="Data.PDF.Fill"
    dictReturnFiles={}

# Setup
    from ntPdfClass import NC_PDF
    sFieldKey=ntSys.NF_DictGet(NTD_dictINI,"FIELD.KEY","")
    sPDF_Template=ntSys.NF_DictGet(NTD_dictINI,"FILE.PDF","")
    objPDF=NC_PDF()

# Lettura File PDF Template con Normalizzazione
    lResult=ntSys.NF_PathNormal(sPDF_Template)
    if sResult=="":
        sPDF_Template=lResult[5]
        sResult=self.FileRead(sPDF_Template)

# Verifica Tabella CSV che ci siano record
    if sResult=="":
        asKeys=ntSys.NF_DictKeys(NTD_dictCSV)
        if ntSys.NF_Arraylen(asKeys)<1: sResult="Tabella dati per fill PDF vuota"

# Ciclo Riempimento da Tabella CSV + Template
    if sResult=="":
        for sKey in asKeys:
        # ReImpostato
            self.sFilename=sPDF_Template
        # Crea FileOut
            sPDF_FileOut=ntSys.NF_PathMake(jData.self.sJob_Path,sKey,"pdf")
        # Estrae Record
            dictRecord=NTD_dictCSV[sKey]
        # Merge uscita anche se un errore
            dictParams={
                "OUT.FILE": sPDF_FileOut,
                "CSV.RECORD": dictRecord}
            sResult=objPDF.FileFill(dictParams)
            if sResult!="": break
        # Update dictResultFiles
            dictReturnFiles[sKey]=sPDF_FileOut

# Ritorno
    sResult=ntSys.NF_ErrorProc(sResult,sProc)
    lResult=[sResult, dictReturnFiles.copy()]
    return lResult

# --------------------------------- MAIN -------------------------------------
def main():
    NTD_Start()
if __name__ == '__main__':
    main()
