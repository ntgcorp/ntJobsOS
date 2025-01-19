
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
import nlDataFiles

# Test Mode
NT_ENV_TEST_NTD=True

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
def Start():
    sProc="NTD.Start"
    global jData
    sResult=""

# Setup e Argomenti CMDLINE
# -----------------------------------------------------------------------------
    jData=NC_Sys()                                  # Application Object
    sResult=jData.Init("NADATA",
        ini=True,                                   # Ini Presente
        test=True,                                  # Test Mode
        nLive=0,                                    # Secondi di check di LiveApp 0=No
        actions=["PDF.FILL", "CSV2XLS", "XLS2CSV"], # Azioni supportate
        cb=cbActions,                               # CallBack Azioni
        ini_fields=None)

# Run (All in One)
# ---------------------------------------------------------------------------
    if sResult=="":
        sResult=jData.Run()

# Ritorno
    return sResult

# --------------------------------- BODY SINGOLE AZIONI ----------------------

# CallBack Azioni
def cbActions(dictParams):
    sProc="NTD_cbActions"

# Setup per Ritorno
    lResult=["",{},{}]
    sAction=dictParams["ACTION"]
    nlSys.NF_DebugFase(NT_ENV_TEST_NTD, "Start Azione: " + sAction, sProc)

# Azioni dell'App
    if sAction=="PDF.FILL":
        sResult=NTD_PDF_Fill(dictParams)
    elif sAction=="CSV2XLS":
        sResult=NTD_CSV2XLS(dictParams)
    elif sAction=="XLS2CSV":
        sResult=NTD_XLS2CSV(dictParams)
    else:
        sResult="Azione Non trovata " + sAction

# Ritorno a chiamante
    nlSys.NF_DebugFase(NT_ENV_TEST_NTD, "End Azione: " + sAction + ": " + sResult, sProc)
    lResult[0]=sResult
    return lResult

# Azione ntJobs: PDF.FILL - Stessa cartella del file INI
# ------------------------------------------------------------------------------
# Parametri: da jData
# Ritorno: lResult 0=sResult, 1=Files di ritorno (ID=PATH)
# dictParams solo per compatibilità Interfaccia ntJobs ma non usato
# Settings Action PDF.FILL
#  FIELD.KEY:      = Campo chiave
#  FILE.PDF        = Template PDF
#  FILE.CSV        = File CSV
#  FIELDS.CSV      = Campi del file csv divisi da ","
#  FILE.PDF.PREFIX = Prefisso a nome file di output. PREFIX_KEY.PDF (SENZA PATH)
#
def NTD_PDF_Fill(dictParams):
    sProc="NTD.PDF.Fill"
    dictReturnFiles={}

# Setup, Parametri, Verifica
    sResult_v=[""] * 5
    sResult_v[0],sFieldKey=jData.GetParam("FIELD.KEY", "Campo Key del file csv non dichiarato")
    sResult_v[1],sPDF_Template=jData.GetParam("FILE.PDF", "Template PDF non dichiarato")
    sResult_v[2],sCSV_File=jData.GetParam("FILE.CSV", "File Dati CSV non dichiarato")
    sResult_v[3],sFields=jData.GetParamKeys("FIELDS.CSV", "Campi valori non dichiarati divisi da virgola")
    sResult_v[4],sPDF_Prefix=jData.GetParam("FILE.PDF.PREFIX", "Prefisso file PDF di output non dichiarato")
    sResult_v[5],bTrim=nlSys.NF_StrBool(jData.GetParam("FILE.PDF.PREFIX", "Trim True o False"))
    sResult=nlSys.NF_StrJoin(text=sResult_v)
    nlSys.NF_DebugFase(NT_ENV_TEST_NTD, "Start PDF FILL. Check Parameters: " + sResult, sProc)

# Lettura CSV
    if (sResult==""):
# Oggetto CSV
        from ncPDF import NC_Pdf as objCsv
        asFields=nlSys.NF_StrSplitKeys(sFields)
        dictParams={
            "TRIM": bTrim,
            "DELIMITER": sCSV_DELIMITER,
            "FIELDS": asFields,
            "FILE.IN": sCSV_File,
            "FIELD.KEY": sFieldKey}
        sResult=objCSV.Read()
        nlSys.NF_DebugFase(NT_ENV_TEST_NTD, "Load CSV: " + sResult, sProc)

# Lettura File PDF Template con Normalizzazione
    if (sResult==""):
        lResult=nlSys.NF_PathNormal(sPDF_Template)
        sPDF_Template=lResult[5]
        sResult=objPdf.FileRead(sPDF_Template)# Verifica Tabella CSV che ci siano record

    if sResult=="":
        nlSys.NF_DebugFase(NT_ENV_TEST_NTD, "Read PDF Template: " + sPDF_Template, sProc)
        asKeys=jData.objCSV.Keys()
        if nlSys.NF_ArrayLen(asKeys)<1: sResult="Tabella dati CSV per PDF.FILL vuota"

# Ciclo Riempimento da Tabella CSV + Template
# ----------------------------------------------------------------------------------------------
    if sResult=="":
# Oggetto PDF
        from ncPdf import NC_Pdf as objPDF
        nlSys.NF_DebugFase(NT_ENV_TEST_NTD, "Start PDF Merge con dati in CSV", sProc)
# Merge
        for sKey in asKeys:
        # Crea FileOut
            sFilename=nlSys.NF_PathMake(jData.sJob_Path, sPDF_Prefix + "_" + sKey,"pdf")
            objPdf.PDF_sFilename=sFilename
        # Estrae Record
            dictRecord=objCSV.Record(sKey)
        # Merge uscita anche se errore
            print(sProc + ", T:" + objPdf.PDF_sModel, "F:" + objPdf.PDF_sFilename)
            sResult=objPdf.FileFill(dictRecord)
            if sResult!="":
                break
        # Log OK
            nlSys.NF_DebugFase(NT_ENV_TEST_NTD, "Creato PDF: " + sFilename, sProc)
        # Update dictResultFiles
            jData.dictReturnFiles[sKey]=sFilename

# Ritorno
    return nlSys.NF_ErrorProc(sResult,sProc)

# Remapping sFileIn, sFileOut
# Return 3 parameters. sResult, New FileIn, New FileOut
def NF_PathRemapInOut(sFileIn,sFileOut,sExtOut):
    sResult=""
    sProc="PathRemapInOut"

# Check FileIn Exist
    sResult,sFileIn=nlSys.NF_FileExistMap(sFileIn)

# FileOut create
    if sResult=="":
        if sFileOut=="" or sFileOut=="#":
            sPath,sFile,sExt=nlSys.NF_PathScompose(sFileIn)
            nlSys.NF_DebugFase(True, "FileIn. Path: " + sPath + ", File: " + sFile + ", Ext: " + sExt, sProc)
            sFileOut=sPath + sFile + "." + sExtOut
            nlSys.NF_DebugFase(True, "FileOut " + sFileOut, sProc)

# Fine
    sResult=nlSys.NF_ErrorProc(sResult, sProc)
    return sResult,sFileIn,sFileOut

# Command CSV2XLS
# ------------------------------------------------------------------------------------------------------------
# Parametri:
# FILE.IN   = Nome file di imput csv
# FILE.OUT  = Nome file di output xls
# SHEET     = Sheet Da Esportare
def NTD_CSV2XLS(*args):
    sProc="CMD_CSV2XLS"
    sResult=""
    sFileIn=""
    sFileOut=""
    sSheetName=""
    nArgs=len(args)

# Parameters
    sFileIn=jData.GetParam("FILE.IN", "File in non dichiarato")
    sFileOut=jData.GetParam("FILE.OUT", "File out non dichiarato")
    sSheetName=jData.GetParam("SHEET", "Sheet non dichiarato")
    nlSys.NF_DebugFase(True, "Parameters. Arg0: " + sFileIn + ",  Arg1: " + sFileOut + ", Arg2: " + sSheetName, sProc)

# Remapping in e out (da non specificare o "#" se da remapping
    sResult,sFileIn,sFileOut=NF_PathRemapInOut(sFileIn,sFileOut,"xlsx")

# Debug Message
    if sResult=="":
# Create Panda objct + Read CSV
        import ncPanda
        objPanda=ncPanda.NC_PANDA_XLS()
        nlSys.NF_DebugFase(True, "Read & Write. IN " + sFileIn + ",  OUT " + sFileOut + ", Sheet: " + sSheetName, sProc)
        sResult=objPanda.read_from_csv(sFileIn)
# Save to XLS
    if sResult=="":
        nlSys.NF_DebugFase(True, "Write XLS", sProc)
        sResult=objPanda.write_to_xls(sFileOut,sSheetName)
# Fine
    return nlSys.NF_ErrorProc(sResult, sProc)

# Comando XLS2CSV
# ------------------------------------------------------------------------------------------------------------
# Parametri:
# FILE.IN   = Nome file di imput xls
# FILE.OUT  = Nome file di output csv
# SHEET     = Sheet Da Importare
def NTD_XLS2CSV(dictParams):
    sProc="CMD_XLS2SCSV"
    sResult=""
    sFileIn=""
    sFileOut=""
    sSheetName=""
    nArgs=len(args)

# Parameters
    sFileIn=jData.GetParam("FILE.IN", "File in non dichiarato")
    sFileOut=jData.GetParam("FILE.OUT", "File out non dichiarato")
    sSheetName=jData.GetParam("SHEET", "Sheet non dichiarato")
    nlSys.NF_DebugFase(True, "Parameters. Arg0: " + sFileIn + ",  Arg1: " + sFileOut + ", Arg2: " + sSheetName, sProc)

# Remapping in e out (da non specificare o "#" se da remapping
    sResult,sFileIn,sFileOut=NF_PathRemapInOut(sFileIn,sFileOut,"csv")

    if sResult=="":
# Create Panda objct + Read CSV
        import ncPanda
        objPanda=ncPanda.NC_PANDA_XLS()
        nlSys.NF_DebugFase(True, "Read & Write. IN " + sFileIn + ",  OUT " + sFileOut + ", Sheet: " + sSheetName, sProc)
        sResult=objPanda.read_from_xls(sFileIn, sSheetName)
    if sResult=="":
        sResult,nRows,nCols=objPanda.df_size()
        nlSys.NF_DebugFase(True, "Size DF " + str(nRows) + ", Cols: " + str(nCols),sProc)
# Save to XLS
    if sResult=="":
        nlSys.NF_DebugFase(True, "Write CSV", sProc)
        sResult=objPanda.write_to_csv(sFileOut)
# Fine
    return nlSys.NF_ErrorProc(sResult, sProc)

# --------------------------------- MAIN -------------------------------------
def main():
    Start()
if __name__ == '__main__':
    main()
