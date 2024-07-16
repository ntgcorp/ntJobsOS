
# ntData - Azioni su File di . Parametro: jobs.ini 
# -----------------------------------------------------------
# Elaborazioni su file di dati, conversioni ed altro
# Sintax: ntData inputFileINI.ini
# Fasi:
# 1=Argomenti
# 2=File_INI in Dictionary - 2b=Verifica_Parametri_INI
# 3=Azione
# 4=Creazione jobs.end in stessa cartella file.ini
# Sintassi di chiamata:
# * AZIONI:
# * PDF.FILL (Compila PDF con CSV di parametri
# [CONFIG]
# ; AZIONE ESEGUITA DAL FRONTEND VIA JOB 
# ACTION=PDF.FILL
# ; Template
# FILE.PDF=Test\Test_ntData_PDF_FILL.pdf
# ; CSV for Fill
# FILE.CSV=Test\Test_ntData_PDF_FILL.csv
# ; FIELDS (NOMI DEI CAMPI ACCETTATI DA AVVALORARE)
# FIELDS.CSV=COGNOME,NOME
# ; NOME DEL CAMPO CHIAVE
# FIELD.KEY=COGNOME
# ; Prefisso Nome PDF Report compilato di ritorno + Valore_Chiave + .pdf
# FILE.PDF.PREFIX=PDF_Report
# ----------------------------------------------------------------------------------------
# Informazioni:
# jData: Application Container
# ------------------------------- Setup ----------------------
import nlSys
from ncJobsApp import NC_Sys
from ncPdf import NC_Pdf

# Test Mode
NT_ENV_TEST_NTD=True

# Global App Container
jData=None

# Global PDF Library
objPdf=NC_Pdf()

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

# Setup e Argomenti CMDLINE
# -----------------------------------------------------------------------------
    jData=NC_Sys("NTDATA")                          # Application Object
    jData.sIniTest="Test\Test_ntData_PDF_FILL.ini"  # Test file
    jData.asActions=["PDF.FILL"]                    # Azioni supportate
    jData.cbActions=NTD_cbActions                   # CallBack Azioni

# Start (Args + Read INI/CSV)
# ---------------------------------------------------------------------------
    if sResult=="": sResult=jData.Start()

# Run (All in One)
# ---------------------------------------------------------------------------
    if sResult=="": sResult=jData.Run()

# Ritorno
    return sResult

# --------------------------------- BODY SINGOLE AZIONI ----------------------

# CallBack Azioni
def NTD_cbActions(dictParams):
    sProc="NTD_cbActions"

# Setup per Ritorno
    lResult=["",{},{}]
    sAction=dictParams["ACTION"]
    nlSys.NF_DebugFase(NT_ENV_TEST_NTD, "Start Azione: " + sAction, sProc)

# Azioni dell'App
    if sAction=="PDF.FILL":
        lResult=NTD_PDF_Fill(dictParams)
        sResult=lResult[0]
    else:
        sResult="Azione Non trovata"

# Ritorno a chiamante
    nlSys.NF_DebugFase(NT_ENV_TEST_NTD, "End Azione: " + sAction + ": " + sResult, sProc)
    lResult[0]=sResult
    return lResult

# Azione ntJobs: PDF.FILL - Stessa cartella del file INI
# ------------------------------------------------------------------------------
# Parametri: da jData
# Ritorno: lResult 0=sResult, 1=Files di ritorno (ID=PATH)
# dictParams solo per compatibilità Interfaccia ntJobs ma non usato
def NTD_PDF_Fill(dictParams):
    global jData, objPdf
    sProc="NTD.PDF.Fill"
    dictReturnFiles={}

# Setup, Parametri, Verifica
    sResult_v=[""] * 3
    sResult_v[0],sFieldKey=jData.GetParam("FIELD.KEY", "Campo Key non dichiarato")
    sResult_v[1],sPDF_Template=jData.GetParam("FILE.PDF", "Template PDF non dichiarato")
    sResult_v[2],sCSV_File=jData.GetParam("FILE.CSV", "File Dati CSV non dichiarato")
    sResult_v[3],asFields=jData.GetParamKeys("FIELDS.CSV", "Campi valori non dichiarati")
    sResult_v[4],sPDF_Prefix=jData.GetParam("FILE.PDF.PREFIX", "Prefisso file PDF di output non dichiarato")
    sResult=nlSys.NF_StrJoin(text=sResult_v)
    nlSys.NF_DebugFase(NT_ENV_TEST_NTD, "Start PDF FILL. Check Parameters: " + sResult, sProc)
    if (sResult==""):
        jData.objCSV.sFieldKey=sFieldKey
        nlSys.NF_DebugFase(NT_ENV_TEST_NTD, "Start PDF Merge con dati in CSV", sProc)
    # Lettura File PDF Template con Normalizzazione
        lResult=nlSys.NF_PathNormal(sPDF_Template)
        sPDF_Template=lResult[5]
        sResult=objPdf.FileRead(sPDF_Template)

# Verifica Tabella CSV che ci siano record
    if sResult=="":
        nlSys.NF_DebugFase(NT_ENV_TEST_NTD, "Read PDF Template: " + sPDF_Template, sProc)
        asKeys=jData.objCSV.Keys()
        if nlSys.NF_ArrayLen(asKeys)<1: sResult="Tabella dati CSV per PDF.FILL vuota"

# Ciclo Riempimento da Tabella CSV + Template
    if sResult=="":
        for sKey in asKeys:
        # Crea FileOut
            sFilename=nlSys.NF_PathMake(jData.sJob_Path, sPDF_Prefix + "_" + sKey,"pdf")
            objPdf.PDF_sFilename=sFilename
        # Estrae Record
            dictRecord=jData.objCSV.Record(sKey)
        # Merge uscita anche se errore
            print(sProc + ", T:" + objPdf.PDF_sModel, "F:" + objPdf.PDF_sFilename)
            sResult=objPdf.FileFill(dictRecord)
            if sResult!="": break
        # Log OK
            nlSys.NF_DebugFase(NT_ENV_TEST_NTD, "Creato PDF: " + sFilename, sProc)
        # Update dictResultFiles
            dictReturnFiles[sKey]=sFilename

# Ritorno
    sResult=nlSys.NF_ErrorProc(sResult,sProc)
    lResult=[sResult, dictReturnFiles]
    return lResult

# --------------------------------- MAIN -------------------------------------
def main():
    NTD_Start()
if __name__ == '__main__':
    main()
