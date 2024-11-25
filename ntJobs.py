# Lancio naJobs Componenti per eseguire ntJobsOS o singoli comandi senza necessità
# di una App ntJobs controllata da ntJobsOs
# 20240927: Diventa ntJobs.py ed è hub di lancio sia di ntJobsOS sia di singoli comandi tramite file .ini come parametro
# e file di supporto nella stessa cartella del file .ini
# 20240808: Piccola sistemazione - Eliminazione nlJobCmd - Tutto in questo file
# 20240616: Conversione totale
# 20240607: Aggiunge xls2csv e csv2xls da completare
# ------------------------------------------------------------------------------
import nlSys, nlExt
import os
from ncJobsApp import NC_Sys

# Global App Container
jData=None

# Test Mode
NT_ENV_TEST_APP=True

# Start App
# -----------------------------------------------------------------------------
def Start():
    sProc="JOBS.Start"
    sResult=""
    #bDebug=True
    #nArgs=0
    #dictArgs={}
    #lResult=nlSys.NF_TS_ToStr("")
    #print("Time:" + str(lResult))

# Setup e Argomenti CMDLINE
# -----------------------------------------------------------------------------
    jData=NC_Sys()                                  # Application Object
    sResult=jData.Init("NTJOBS",
        ini=True,                                   # Ini Presente
        test=True,                                  # Test Mode
        nLive=0,                                    # Secondi di check di LiveApp 0=No
        cb=cbActions)                               # CallBack Azioni    

# Run (All in One)
# ---------------------------------------------------------------------------
    if sResult=="":
        sResult=jData.Run()

# Fine
    return nlSys.NF_ErrorProc(sResult,sProc)

 # CallBack Azioni
def cbActions(dictParams):
    sProc="NTJOBS.CB.ACTIONS"
    sResult=""

# Setup per Ritorno
    lResult=["",{},{}]
    sAction=dictParams["ACTION"]
    nlSys.NF_DebugFase(NT_ENV_TEST_APP, "Start Azione: " + sAction, sProc)

# Azioni NJOS
    if sAction=="NJOS.START":
        sResult=cmdNJOS_Start(dictParams)
    elif sAction=="NJOS.END":
        sResult="To do " + sAction
    elif sAction=="NJOS.RESTART":
        sResult="To do " + sAction
# Azioni FILE XLS
    elif sAction=="CSV2XLS":
        sResult=cmdXSL_FromCSV(dictParams)
    elif sAction=="XLS2CSV":
        sResult=cmdXLS_ToCSV(dictParams)
    elif sAction=="XLS.MERGE":
        sResult=cmdXLS_Merge(dictParams)
    elif sAction=="XLS.SPLIT":
        sResult=cmdXLS_Split(dictParams)
# Azioni FILE PDF
    elif sAction=="PDF.FILL":
        sResult=NTD_PDF_Fill(dictParams)
# Azioni VARIE
    elif sAction=="PATH.MIRROR":
        sResult=cmdPATH_Mirror(dictParams)
    elif sAction=="TEST":
        sResult=cmdTest(dictParams)
    else:
        sResult="Comando non riconosciuto " + sAction

# Ritorno
    sResult=nlSys.NF_ErrorProc(sResult,sProc)
    lResult=[sResult]
    return lResult

# --------------------------------- AZIONI -------------------------------------

def cmdNJOS_Start():
# CMD.NJOS
    sProc="CMD.NJOS.START"
    import ncJobsOS as objJobOS
    nlSys.NF_DebugFase(jData.bTest,"NJOS Start",sProc)
    sResult=objJobOS.Init()

# LOOP
    if sResult=="":
        while objJobOS.bExitFull==False:
            nlSys.NF_DebugFase(jData.bTest,"NJOS Loop",sProc)
            sResult=objJobOS.Loop()

# EXIT PER Errore
    if sResult != "":
        objJobOS.bExitFull=True

# FINE
    return nlSys.NF_ErrorProc(sResult,sProc)

def cmdNJOS_Shutdown(dictParams={}):
    sProc="CMD.SHUTDOWN"
    sResult=""

# FINE
    return nlSys.NF_ErrorProc(sResult,sProc)

def cmdNJOS_End(dictParams={}):
    sProc="CMD.NJOS.END"
    sResult=""

# FINE
    return nlSys.NF_ErrorProc(sResult,sProc)

def cmdNJOS_Restart(dictParams={}):
    sProc="CMD.NJOS.RESTART"
    sResult=""

# FINE
    return nlSys.NF_ErrorProc(sResult,sProc)

def cmdXLS_Merge(dictParams={}):
    sProc="CMD.XLS.MERGE"
    sResult=""

# FINE
    return nlSys.NF_ErrorProc(sResult,sProc)

def cmdXLS_Split(dictParams={}):
    sProc="CMD.XLS.SPLIT"
    sResult=""

# FINE
    return nlSys.NF_ErrorProc(sResult,sProc)

def cmdXLS_ToCsv(dictParams={}):
    sProc="CMD.TO.CSV"
    sResult=""

# FINE
    return nlSys.NF_ErrorProc(sResult,sProc)

def cmdXLS_FromCsv(dictParams={}):
    sProc="CMD.FROM.CSV"
    sResult=""

# FINE
    return nlSys.NF_ErrorProc(sResult,sProc)

def cmdTest(dictParams={}):
    sProc="CMD.TEST"
    sResult=""

    print("Test command")

    for key in dictParams.keys():
        value=dictParams[key]
        print("Param: " + key + ", Value: " + value)

# FINE
    return nlSys.NF_ErrorProc(sResult,sProc)

def cmdPATH_Mirror(dictParams):
    sProc="CMD.PATH.MIRROR"
    sResult=""

# Verifica Folder IN e Folder Out
    asFiles=nlSys.NF_DictGet(dictParams,"FILES",None)
    sResult=nlSys.NF_ParamVerify(dictParams, {"dexist": ("IN.PATH","OUT.PATH"),"fexist": asFiles})

# Mirror
    if sResult=="":
        nlSys.NF_DebugFase(NT_ENV_TEST_APP, "Mirror", sProc)
        sPathIn=nlSys.NF_DictGet(dictParams,"IN.PATH","")
        sPathOut=nlSys.NF_DictGet(dictParams,"OUT.PATH","")
        for sFile in asFiles:
            sFileIn=nlSys.NF_PathMake(sPathIn,sFile,"")
            sTemp=nlSys.NF_FileCopy(sFile,sPathOut,replace=True, outpath=True)
            if sTemp != "": sResult=sResult + ": " + sTemp
            nlSys.NF_DebugFase(NT_ENV_TEST_APP, f"Copy {sFileIn} to {sPathOut}", sProc)

# FINE
    return nlSys.NF_ErrorProc(sResult,sProc)

# Command CSV2XLS
# ------------------------------------------------------------------------------------------------------------
# Parametri:
# FILE.IN   = Nome file di imput csv
# FILE.OUT  = Nome file di output xls
# SHEET     = Sheet Da Esportare
def cmdXLS_FromCSV(*args):
    sProc="CMD_CSV2XLS"
    sResult=""
    sFileIn=""
    sFileOut=""
    sSheetName=""
    nArgs=len(args)

# library
    import nlDataFiles

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
def cmdXLS_ToCSV(dictParams):
    sProc="CMD_XLS2SCSV"
    sResult=""
    sFileIn=""
    sFileOut=""
    sSheetName=""
    nArgs=len(args)

# library
    import nlDataFiles

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

# --------------------------------- INTERNAL -------------------------------------


# --------------------------------- MAIN -------------------------------------
def main():

    sResult=Start()
    if sResult != "":
        import sys
        sys.exit(sResult)

# Python Start
if __name__ == '__main__': main()