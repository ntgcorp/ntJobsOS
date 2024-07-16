# Lancio naJobs App per eseguire ntJobsOS o singoli comandi
# 20240616: Conversione totale
# 20240607: Aggiunge xls2csv e csv2xls da completare
# ------------------------------------------------------------------------------
import nlSys
import os

# Test Mode
NT_ENV_TEST_JOBSA=True


# Start App
# -----------------------------------------------------------------------------
def Start():
    sProc="JOBS.Start"
    sResult=""
    sCmd=""
    bDebug=True
    nArgs=0
    dictArgs={}

# CurrentDir = ScriptDir
    sCurDir=nlSys.NF_PathScript("PATH")
    print("Current Dir: " + sCurDir)
    os.chdir(sCurDir)

# Prende Argomenti
    nlSys.NF_DebugFase(bDebug,"", sProc)
    lResult=nlSys.NF_Args([])
    sResult=lResult[0]
    if (sResult==""):
        dictArgs=lResult[1]
        nArgs=nlSys.NF_DictLen(dictArgs)
    else:
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        return sResult

# Altro check e prende comando
    nlSys.NF_DebugFase(bDebug,"Argomenti: " + str(nArgs)  + ", valori: " + str(dictArgs), sProc)
    if nArgs<1:
        sResult="naJobs Argomenti: comando, ...Altri parametri"
    else:
        sCmd=dictArgs[0].upper()
        dictArgs.update({'cmd':sCmd})

# Comandi. caricando moduli utilizzati
# -----------------------------------------------------------------------------
    nlSys.NF_DebugFase(bDebug,"Post Parsing Args. , cmd: " + sCmd + ", Args: " + str(dictArgs),sProc)
    if sCmd=="NJOS":
# CMD.NJOS
        import nlJobsOS as objJobOS
        nlSys.NF_DebugFase(bDebug,"NJOS Start",sProc)
        sResult=objJobOS.Start()
        nlSys.NF_DebugFase(bDebug,"NJOS Loop",sProc)
        if sResult=="": sResult=objJobOS.Loop()
# CMD.XLS2CSV
    elif sCmd=="XLS2CSV":
        import nlJobsCmd as objCmd
        sFileIn=nlSys.NF_DictGet(dictArgs,1,"")
        sFileOut=nlSys.NF_DictGet(dictArgs,2,"")
        nlSys.NF_DebugFase(bDebug,"XLS2CSV, Args: " + str(dictArgs),sProc)
        sResult=objCmd.cmd_XLS2CSV(sFileIn, sFileOut)
# CMD.CSV2XLS
    elif sCmd=="CSV2XLS":
        import nlJobsCmd as objCmd
        sFileIn=nlSys.NF_DictGet(dictArgs,1,"")
        sFileOut=nlSys.NF_DictGet(dictArgs,2,"")
        nlSys.NF_DebugFase(bDebug,"CSV2XLS, Args: " + str(dictArgs),sProc)
        sResult=objCmd.cmd_CSV2XLS(sFileIn, sFileOut)
# Errore
    else:
        sResult="Comando non riconosciuto " + sCmd

# Ritorno
    nlSys.NF_DebugFase(bDebug,"End: " + sResult,sProc)
    return sResult

# --------------------------------- MAIN -------------------------------------
def main():
    sResult=Start()
    if sResult != "":
        import sys
        sys.exit(sResult)

# Python Start
if __name__ == '__main__': main()
