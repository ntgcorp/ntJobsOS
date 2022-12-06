#
# Interface for ntJobsOS FrontEnd Application
# JOBS_Start_Read: Legge INI di Configurazione
# JOBS_End_Write: Scrive INI di Fine attività
# JOBS_ARGS: Recupero parametri secondo varie opzioni permesse nel lancio FrontEnd ntJobsOS
#
import ntSys, ntDataFiles
import argparse

NT_ENV_TEST_JIO=True

# Sezione Legge file INI + Parametri di default
# Ritorno lResult. 0=Stato, 1=dictINI se trovato o None
# Parametri:
#    FILE.INI=File da leggere
#    FIELDS.TYPE: dict. Campi accettati come valore hanno il tipo "Number o Boolean o Integer"
#    ACTIONS: Array Stringa azioni accettate
# -------------------------------------------------------
def JOBS_Start_Read(dictParams):
    sProc="Jobs.Start_Read"
    sResult=""
    dictINI=dict()
    
# Parametri - Prende e Verifica
# -------------------------------------------------------
# File da leggere
    sFileConfig=dictParams["FILE.INI"]
# Campi Accettati e Conversione
    dictFields=dictParams["FIELDS"]
# Azioni Accettate
    asActions=dictParams["ACTIONS"]
# Prende File INI o Errore    
    lResult=ntSys.NF_PathNormal(sFileConfig)
    sResult=lResult[0]
    if sResult=="": sFileConfig=lResult[5]

# Legge INI 
    if sResult=="":
        ntSys.NF_DebugFase(NT_ENV_TEST_JIO, "Lettura file INI:" + sFileConfig, sProc)
        lResult=ntDataFiles.NF_INI_Read(sFileConfig)    
        sResult=lResult[0]
        
# Prende sezione CONFIG
    if sResult=="":        
    # Verifica che ci sia Config
        dictSections=lResult[1]
        if ntSys.NF_DictExistKey(dictSections,"CONFIG"):
            dictINI=dictSections["CONFIG"]
            if ntSys.NF_DictLen(dictINI)<1: sResult="assente sezione config"
        else:
            sResult="Sezione CONFIG non esistente"

# Conversioni di Tipi e Verifica che ci siano i parametri "obbligatori"
    if sResult=="":
        dictINI=ntSys.NF_DictConvert(dictINI, dictFields)
        if len(dictINI)==0: sResult="Conversione KEYS in dict"
        
# Verifica Azione
    if sResult=="":
        sAction=dictINI["ACTION"]
        if ntSys.NF_ArrayLen(asActions)>-1:
            if ntSys.NF_ArrayFind(asActions,sAction)==-1:
                sResult="Azione non prevista: " + sAction

# Completment:
    ntSys.NF_DebugFase(NT_ENV_TEST_JIO, "Letto file INI. Eventuali errori: " + sResult, sProc)
    
# Ritorno
    sResult=ntSys.NF_ErrorProc(sResult,sProc)
    return sResult

# Arguments
# Parametri
# INI.YES: Obbligatorio File INI
# CSV.YES: Obbligatorio File CSV (allora anche INI deve essere True)
# TEST.YES: Previsti file di test, allora ci deve essere anche TEST.INI e TEST.CSV se bINI e bCSV
# Ritorno lResult. 0=sFileINI, 1=sFileCSV
# -------------------------------------------------------
def JOBS_Args(dictParams):
    sProc="JOBS_ARGS"
    sResult=""
        
# CSV/INI Obbligatorio o Facoltativo 
    bCSV=ntSys.NF_DictGet(dictParams,"CSV.YES", False)
    bINI=ntSys.NF_DictGet(dictParams,"INI.YES", True)
    if bCSV: bINI=True
    bTest=ntSys.NF_DictGet(dictParams,"TEST.YES", True)
    sFileTest_INI=ntSys.NF_DictGet(dictParams,"TEST.INI", "")
    sFileTest_CSV=ntSys.NF_DictGet(dictParams,"TEST.CSV", "")
    
# Controlli
# Se da TEST
    if bTest:
        if bINI and sFileTest_INI=="": sResult="Non previsto file TEST.INI"
        if bCSV and sFileTest_CSV=="": sResult="Non previsto file TEST.CSV"
        if bINI: sFileINI=sFileTest_INI
        if bCSV: sFileCSV=sFileTest_CSV
        if bINI or bCSV: ntSys.NF_DebugFase(bTest, "Utilizzo INI/CSV Demo. INI: " + sFileINI + ", CSV:" + sFileCSV, sProc)
    else:
# Prende ARGS REALI
        if bINI or bCSV:
            parser = argparse.ArgumentParser()
            if bINI: parser.add_argument("sFileINI", help="InputFileConfig.INI ")
            if bCSV: parser.add_argument("sFileCSV", "--verbose", help="InputFile.CSV")
            args = parser.parse_args()
            if args.count>0 and bINI: sFileINI=args.sFileINI
            if args.count>1 and bCSV: sFileCSV=args.sFileCSV
            ntSys.NF_DebugFase(bTest, "Utilizzo INI/CSV da CMDLINE: " + sFileINI + ", CSV: " + sFileCSV, sProc)
    
# Verifica Parametri
    if bINI and sFileINI=="" and sResult=="": sResult="Non specificato parametro File INI"
    if bCSV and sFileCSV=="" and sResult=="": sResult="Non specificato File CSV"
    
# Ritorno
    sResult=ntSys.NF_ErrorProc(sResult,sProc)
    lResult=[sResult,sFileINI,sFileCSV]
    return lResult
        
# Crea file JOBS.END nella stessa cartella file JOBS.INI
# Parametri:
# JOB.PATH: Cartella del JOB.
# RETURN.TYPE: RETURN.TYPE=E=Errore/W=Working/Nulla=OK
# RETURN.VALUE=Messaggio di ritorno
# TS.START
# Ritorno sResult
def JOBS_END_Write(dictReturn):
    sProc="JOBS_ARGS"
    sResult=""
    
# Setup
    sTS_END=ntSys.NF_TS_ToStr()
# Parametri
    sRetType=ntSys.NF_DictGet(dictReturn, "RETURN.TYPE", "")
    sTS_START=ntSys.NF_DictGet(dictReturn, "TS.START", "")
    sRetValue=ntSys.NF_DictGet(dictReturn, "RETURN.VALUE", "")
    sJobPath=ntSys.NF_DictGet(dictReturn, "JOB.PATH", "")
# Preparazione
    sFileEnd=ntSys.NF_PathMake(sJobPath, "jobs", "end")
    dictReturn={
        "RETURN.TYPE":  sRetType,
        "RETURN.VALUE": sRetValue,
        "TS.START": sTS_START,
        "TS.END": sTS_END
    }
    
# Scrive
    sResult=ntDataFiles.NF_INI_Write(sFileEnd,"w")
    
# Completment:
    ntSys.NF_DebugFase(NT_ENV_TEST_JIO, "Scrito FILE.END. Eventuali errori: " + sResult, sProc)
    
# Ritorno
    sResult=ntSys.NF_ErrorProc(sResult,sProc)
    return sResult
