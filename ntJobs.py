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
import nlDataFiles

# Test Mode
NT_ENV_TEST_APP=True

# Start App
# -----------------------------------------------------------------------------
def Start():
    sProc="JOBS.Start"
    sResult=""
    bDebug=True
    nArgs=0
    dictArgs={}
    lResult=nlSys.NF_TS_ToStr("")
    print("Time:" + str(lResult))
    sTS_Start=lResult[1]

# CurrentDir = ScriptDir.
# Dichiarare TIMESTAMP.START e TIMESTART.END
    sCurDir=nlSys.NF_PathScript("PATH")
    print("ntJobs Start. \nCurrent Dir: " + sCurDir + "\nTime.Start: " + sTS_Start)
    os.chdir(sCurDir)

# Prende Argomenti
    nlSys.NF_DebugFase(bDebug,"Check Argomenti", sProc)
    lResult=nlSys.NF_Args([])
    sResult=lResult[0]
    if (sResult==""):
        dictArgsTemp=lResult[1]

# Conversione args ntjobs (lettura ini o trasformazione in dict parametri)
    if (sResult==""):
        nlSys.NF_DebugFase(bDebug,"Conversione Argomenti", sProc)
        lResult=NF_ArgsJobs(dictArgsTemp)
        sResult=lResult[0]
        if sResult=="":
            dictArgs=lResult[1]

# Altro check e prende comando
    if sResult=="":
        nArgs=nlSys.NF_DictLen(dictArgs)
        nlSys.NF_DebugFase(bDebug,"Argomenti: " + str(nArgs)  + ", valori: " + str(dictArgs), sProc)
        if nArgs<1:
            sResult="naJobs Argomenti: comando, ...Altri parametri"
        else:
            sAction=dictArgs['ACTION'].upper()
            dictArgs.update({'ACTION':sAction})

# Comandi. caricando moduli utilizzati
# -----------------------------------------------------------------------------
    if sResult=="":
        nlSys.NF_DebugFase(bDebug,"Post Parsing Args. , ACTION: " + sAction + ", Args: " + str(dictArgs),sProc)
        lResult=cbActions(dictArgs)
        sResult=lResult[0]

# Fine
    return nlSys.NF_ErrorProc(sResult,sProc)

 # CallBack Azioni
def cbActions(dictParams):
    sProc="JANOSBS.CB.ACTIONS"
    sResult=""

# Setup per Ritorno
    lResult=["",{},{}]
    sAction=dictParams["ACTION"]
    nlSys.NF_DebugFase(NT_ENV_TEST_APP, "Start Azione: " + sAction, sProc)

    if sAction=="NJOS.START":
        sResult=cmdNJOS_Start(dictParams)
    elif sAction=="XLS.MERGE":
        sResult=cmdXLS_Merge(dictParams)
    elif sAction=="XLS.SPLIT":
        sResult=cmdXLS_Split(dictParams)
    elif sAction=="NJOS.END":
        sResult="To do " + sAction
    elif sAction=="NJOS.RESTART":
        sResult="To do " + sAction
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
    nlSys.NF_DebugFase(bDebug,"NJOS Start",sProc)
    sResult=objJobOS.Init()

# LOOP
    if sResult=="":
        while objJobOS.bExitFull==False:
            nlSys.NF_DebugFase(bDebug,"NJOS Loop",sProc)
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
        sPathOut=nlSys.NF_DictGet(dictParams,"OUT.PATH,"")
        for sFile in asFiles:
            sFileIn=nlSys.NF_PathMake(sPathIn,sFile,"")
            sTemp=nlSys.NF_FileCopy(sFile,sPathOut,replace=True, outpath=True)
            if sTemp != "": sResult=sResult + ": " + sTemp
            nlSys.NF_DebugFase(NT_ENV_TEST_APP, f"Copy {sFileIn} to {sPathOut}", sProc)

# FINE
    return nlSys.NF_ErrorProc(sResult,sProc)

# --------------------------------- INTERNAL -------------------------------------

# Interpreta Args come ntJobs con action e -parametro oppure se unico e finisce per .ini lo legge tutto e interpreta
def NF_ArgsJobs(dictArgs):
    sProc="ARGS.JOBS"
    sResult=""
    dictResult={}
    sType="A"   # A=Argomenti, I=FileIni
    sAction=""
    sArgs=""

# Determina tipologia arg o ini
    nLen=nlSys.NF_DictLen(dictArgs)
    if nLen==1:
        sArgs=str(dictArgs[0])
        #sArgs=sArgs.lower
        print("Args: " + sArgs)
        if sArgs.endswith("ini"): sType="I"
    nlSys.NF_DebugFase(NT_ENV_TEST_APP, "Args.Num:" + str(nLen) + ", sType: " + sType, sProc)

# Caso "I": Deve essere con [CONFIG]
    if sType=="I":
        lResult=nlDatafiles.NF_INI_Read(sArg)
        if sResult=="":
            dictTemp=dict(lResult[1]).copy()
            dictResult=dictTemp["CONFIG"].copy()

# Caso "A" (tutti devono essere nella forma -key value, quelli senza key davanti vengono scartati)
    else:
        sKey=""
        sValue=""
        nIndex=0
        avKeys=dictArgs.keys()
        for key in avKeys:
            value=str(dictArgs[key])
# Il primo è il comando
            if nIndex==0:
                dictResult["ACTION"]=value
                sAction=value
# Si aspetta comandi inizianti per "-"
            elif value.startswith("-"):
                sKey=value[1:]
                sValue=""
# Deve essere il valore
            else:
                if sKey != "":
                    sValue=str(value).strip()
                    dictResult[sKey]=sValue
                    sKey=""
# Indice di args
            nIndex = nIndex + 1

    nlSys.NF_DebugFase(NT_ENV_TEST_APP, "ntJob Args: " + sType + ", ACTION: " + sAction + ", Params: " +  str(dictResult), sProc)
    lResult=[sResult, dictResult]
    return lResult

# --------------------------------- MAIN -------------------------------------
def main():

    sResult=Start()
    if sResult != "":
        import sys
        sys.exit(sResult)

# Python Start
if __name__ == '__main__': main()