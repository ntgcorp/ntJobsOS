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

# Test Mode
NT_ENV_TEST_JOBSA=True

# Start App
# -----------------------------------------------------------------------------
def Start():
    sProc="JOBS.Start"
    sResult=""
    bDebug=True
    nArgs=0
    dictArgs={}
    sTS_Start=NF_TimeStrHHMMSS()

# CurrentDir = ScriptDir.
# Dichiarare TIMESTAMP.START e TIMESTART.END
    sCurDir=nlSys.NF_PathScript("PATH")
    print("ntJobs Start. \nCurrent Dir: " + sCurDir + "\nTime.Start: " + sTS_Start)
    os.chdir(sCurDir)

# Prende Argomenti
#    nlSys.NF_DebugFase(bDebug,"", sProc)
#    lResult=nlSys.NF_Args([])
#    sResult=lResult[0]
#    if (sResult==""):
#        dictArgs=lResult[1]
#        nArgs=nlSys.NF_DictLen(dictArgs)
#    else:
#        sResult=nlSys.NF_ErrorProc(sResult,sProc)
#        return sResult

# Altro check e prende comando
#   nlSys.NF_DebugFase(bDebug,"Argomenti: " + str(nArgs)  + ", valori: " + str(dictArgs), sProc)
#    if nArgs<1:
#        sResult="naJobs Argomenti: comando, ...Altri parametri"
#    else:
#        sCmd=dictArgs[0].upper()
#        dictArgs.update({'cmd':sCmd})

# Comandi. caricando moduli utilizzati
# -----------------------------------------------------------------------------
 #  nlSys.NF_DebugFase(bDebug,"Post Parsing Args. , cmd: " + sCmd + ", Args: " + str(dictArgs),sProc)

 # CallBack Azioni
def cbActions(dictParams):
    sProc="JANOSBS.CB.ACTIONS"
    sResult=""

# Setup per Ritorno
    lResult=["",{},{}]
    sAction=dictParams["ACTION"]
    nlSys.NF_DebugFase(NT_ENV_TEST_APP, "Start Azione: " + sAction, sProc)

    if sAction=="NJOS.START":
        sResult=cmdNJOS()
    elif sAction=="XLS.MERGE":
        sResult=cmdXLS_Merge()
    elif sAction=="XLS.SPLIT":
        sResult=cmdXLS_Split()
    elif sAction=="NJOS.END":
        sResult=cmdXLS_Split()
    elif sAction=="NJOS.RESTART":
        sResult=cmdXLS_Split()
    elif sAction=="NJOS.SHUTDOWN":
        sResult=cmdXLS_Split()
    else:
        sResult="Comando non riconosciuto " + Action


# Ritorno
    sResult=nlSys.NF_ErrorProc(sResult,sProc)
    lResult=[sResult]
    return lResult

# --------------------------------- AZIONI -------------------------------------

def cmdNJOS_Start():
# CMD.NJOS
    sProc="CMD.NJOS.START"
    import ncJobsOS as objJobOS
    nlSys.NF_DebugFase(bDebug,"NJOS Start",sProc)
    sResult=objJobOS.Init()

# LOOP
    if sResult=="":
        do while objJobOS.bExitFull==False:
            nlSys.NF_DebugFase(bDebug,"NJOS Loop",sProc)
            sResult=objJobOS.Loop()

# EXIT PER Errore
    if sResult != "":
        objJobOS.bExitFull=True

# FINE
    return nlSys.NF_ErrorProc(sResult,sProc)

def cmdNJOS_Shutdown():
    sProc="CMD.SHUTDOWN"
    sResult=""

# FINE
    return nlSys.NF_ErrorProc(sResult,sProc)

def cmdNJOS_End():
    sProc="CMD.NJOS.END"
    sResult=""

# FINE
    return nlSys.NF_ErrorProc(sResult,sProc)

def cmdNJOS_Restart():
    sProc="CMD.NJOS.RESTART"
    sResult=""

# FINE
    return nlSys.NF_ErrorProc(sResult,sProc)

def cmdXLS_Merge():
    sProc="CMD.XLS.MERGE"
    sResult=""

# FINE
    return nlSys.NF_ErrorProc(sResult,sProc)

def cmdXLS_Split():
    sProc="CMD.XLS.SPLIT"
    sResult=""

# FINE
    return nlSys.NF_ErrorProc(sResult,sProc)

def cmdPATH_Mirror():
    sProc="CMD.PATH.MIRROR"
    sResult=""
    global jData

# Verifica Folder IN e Folder Out
    asFiles=nlSys.NF_DictGet(jData.dictINI,"FILES",None)
    sResult=nlSys.NF_ParamVerify(jData.dictINI, {"dexist": ("IN.GITDIR","OUT.GITDIR"),"fexist": asFiles})

# Mirror
    if sResult=="":
        nlSys.NF_DebugFase(NT_ENV_TEST_APP, "Mirror", sProc)
        sPathIn=nlSys.NF_DictGet(jData.dIctIni,"IN.GITDIR","")
        sPathOut=nlSys.NF_DictGet(jData.dIctIni,"OUT.GITDIR","")
        for sFile in asFiles:
            sFileIn=nlSys.NF_PathMake(sPathIn,sFile,"")
            sTemp=nlSys.NF_FileCopy(sFile,sPathOut,replace=True, outpath=True)
            if sTemp != "": sResult=sResult + ": " + sTemp
            nlSys.NF_DebugFase(NT_ENV_TEST_APP, f"Copy {sFileIn} to {sPathOut}", sProc)

# FINE
    return nlSys.NF_ErrorProc(sResult,sProc)

# --------------------------------- MAIN -------------------------------------
def main():

    sResult=Start()
    if sResult != "":
        import sys
        sys.exit(sResult)

# Python Start
if __name__ == '__main__': main()