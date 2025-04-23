#
# CLASSE Orchestratore jobs. Gestisce Users e dati correlati
# Fasi:
# ----------------------- inizializzazione ----------------------------
# 1: Init
# 1.1 Start() - Legge INI (INI_Read) + Setup
# 1.3: Assegna USERS, ACTIONS, GROUP
# 1.4: Assegna CONFIG  - A differenza degli altri è un dict non un Table
# 2: Genera lista PATHS/CANALI da ricercare
# 3: Loop che chiama le altre azioni
# ------------------- Lopop dell'Orchestratore -------------------------------
# Get: Cerca jobs nei folders e sposta in Inbox
# Exec: Esegue Jobs in inbox
# End: Trova i job  finiti
# Live: Verifica se ci sono jobs da stoppare
# Return: Ritorno ai chiamanti
# - Billing: Fatturazione attività ai singoli users (da fare)
# - Archive: Ritorna risultati Jobs & Archiviazione del Job da Inbox in Archive
# -----------------------------------------------------------------------------

# Librerie
import nlSys
import os
import signal
import platform
import datetime
from nlDataFiles import NC_CSV
from ncTable import NC_Table
from ncMailSimple import NC_MailSimple
from ncLog import NC_LOG

# Test Mode
NT_ENV_TEST= True
# Wait in secondi
JOBS_WAIT_STD = 5

# ----------------------------- CLASSI ---------------------------
class NC_Jobs:
    """
    ntJobs System Class APP
    ID dictUsers=
    Classe Appliczione ntJobs.App - Obbligatoria sua Presenza
    """
#    jData=None
# Oggetto Mail di ritorno
    objMail=None
# Oggetto Log
    objLog=None
# Risultato ultima elaborazione
    sResult=""
# dictINI config "master" letta da file ntgjobsos.ini 
    dictConfigINI={}
# dictConfigJobsorrent
    dictConfigJobs={}
# dictConfig (o dictINI_jobs), somma di ini ntjobsos.ini + [config] di jobs.ini locale
    dictConfig={}
# File INI jobs.ini letto (che può contenere più jobs) compreso [CONFIG] di login ed altre - Config globale. 
# dictConfigIni+dictConfigJobs
    dictJobs=dict()
# Jobs soggetti a controllo live. Dictionary
#    Key=Path della cartella in inbox dove si trova JOBS.INI
#    Item. Array di 3. 0=LastCheck, 1=SecondsLive, 2=Array di Pid per concluderlo (nel caso jobs.ini contiene più actions, la live vale per tutti)
    dictJobsLive={}
# Job Singolo - Wrapped Azione corrente - Gruppi che possono eseguire questa azione
# Non è possibile scendere a livello di singolo utente la possibilità di eseguire una azione
# dictJob=ParametriSingoloJob, sAction=ID_Azione, sScript=ComandoDaSeguire con ReplaceVars(config), dictAction=ParametriSingolaAzine
# sJob=Path job corrente (che può avere più subjobs in dictjob) - dicrtJob piò avere più actions da eseguire in singolo job
    sJob=""
# Jobs (sezioni .ini) contenuti in file job.ini corrente
    dictJob={}
# Azione Corrente
    sAction=""
# Script Azione Corrente    
    sScript=""
# DA VERIFICARE       
    dictAction={}
# Files associati al Job Corrente
    asFilesJob=list[str]
# Paths da Leggere
    dictPaths={}
# Jobs
    FLD_LASTCHECK=0
# Tabelle di supporto per Tabelle BI/MULTIDIMENSIONALI JobOS, Users, Comandi, Gruppi, Paths da cercare, non CFG
    asUsers=list[str]
    asActions=list[str]
    asGroups=list[str]
    asPaths=list[str]
# Tabelle CSV da leggere - STESSO ORDINE DI JOB_DAT_*
    JOB_DAT_ACT=0   # Data/ntjobs_actions.csv
    JOB_DAT_USR=1   # Data/ntjobs_users.csv
    JOB_DAT_USG=2  # Data/ntjobs_groups.csv
    JOB_DAT_LEN=2  # Range Tabelle JOB_DAT. JOB_DAT_CFG è dopo
# Tabelle Dati Jobs
# Le azioni sono attribuibili solo ai gruppi non agli utenti e un utente può far parte di più gruppi
    asFields_DAT={ JOB_DAT_USR:("USER_ID","USER_PASSWORD","USER_NAME","USER_NOTES","USER_GROUPS","USER_PATHS","USER_MAIL"),
                   JOB_DAT_USG:("GROUP_ID","GROUP_NAME","GROUP_NOTES"),
                   JOB_DAT_ACT:("ACT_ID","ACT_NAME","ACT_GROUPS","ACT_SCRIPT","ACT_ENABLED","ACT_PATH","ACT_TIPS","ACT_HELP","ACT_LIVE")}
    dictFData =  { JOB_DAT_USR:"users", JOB_DAT_USG:"groups", JOB_DAT_ACT:"actions"}    
    asFields_INI=["ADMIN.EMAIL","SMTP.AUTH","SMTP.FROM","SMTP.PASSWORD","SMTP.PORT","SMTP.SERVER","SMTP.SSL","SMTP.TLS","SMTP.USER","NTJOBS.VER"]
# Repository in memoria Tabelle Interne CARICATE DA CSV ESTERNO - CREATO SPAZIO IN ARRAY
    TabData_USR=NC_Table()
    TabData_USG=NC_Table()
    TabData_ACT=NC_Table()
    asUsers=[]
    asActions=[]
    asGroups=[]
# User CURRENT Details - Tutti e quelli più usati - Da Jobs_Login. gli altri in JOBSINI
    sUser_ID=""
    sUser_asGroups=list[str]
# Flag Interni vari
    bExitJOB=False     # Flag di uscita da jobs corrente
    bExitNJOS=False    # Flag di uscita da NTJOBS full
    bMailLogin=False   # Flag Mail Login fatto Flag (deve essere fatto una volta sola)
# Variabili Iniizializzate
    sSys_PathRoot=""   # Path BASE
    sSys_PathInbox=""  # Path INBOX
    sSys_PathArchive=""# Path ARCHIVE
 
# Init - Richiede presenza jData già inizializzata
# ------------------------------------------------------------------------------------------------------------
    def __init__(self):
        pass

# Inizializzazione OGGETTO
    def Init(self) -> str:
        sResult=""
        sProc="JOS.INIT"
# Log Start
        nlSys.NF_DebugFase(NT_ENV_TEST, "Start Log", sProc)
        sLogFile=nlSys.NF_PathMake(nlSys.NF_PathScript("PATH"),"system","log")       
        self.objLog=NC_LOG()        
        sResult=self.objLog.Log("Start Log", log_type="info",log_file=sLogFile,log_cat="info")
# Inizializzazioni - Prima Lettura Init
        nlSys.NF_DebugFase(NT_ENV_TEST, "Start Init", sProc)
        self.sSys_PathRoot=nlSys.NF_PathScript("PATH")
# Lettura INI
        if sResult=="":
            nlSys.NF_DebugFase(NT_ENV_TEST, "Read Config INI", sProc)
            sResult=self.Init_ReadINI()
# Inizializzazioni Dopo lettura INI
        if sResult=="":
            self.sSys_PathArchive=self.Sys_Config("ARCHIVE")
            if self.sSys_PathArchive=="": 
                self.sSys_PathArchive=nlSys.NF_PathMake(self.sSys_PathRoot,"\\Archive")
            self.sSys_PathInbox=self.Sys_Config("INBOX")
            if self.sSys_PathInbox=="": 
                self.sSys_PathInbox=nlSys.NF_PathMake(self.sSys_PathRoot,"\\Inbox")
# Lettura DAT
        if sResult=="":
            sResult=self.Init_ReadDAT()
# Aggiorna Tabelle Interne
        if sResult=="":
            nlSys.NF_DebugFase(NT_ENV_TEST, "Update Cache Config/Data Keys Tables", sProc)
            self.asUsers=self.Sys_Users()
            self.asActions=self.Sys_Actions()
            self.asGroups=self.Sys_Groups()
# Paths Jobs Find Update
            lResult=self.Sys_Paths()
            sResult=lResult[0]
            if sResult=="": 
                self.dictPaths=lResult[1].copy()
# Iniializzazione MAIL ENGINE
        if sResult=="":
            nlSys.NF_DebugFase(NT_ENV_TEST, f"Send ntJobs Init Mail to Admin", sProc)
        #    sResult=self.Init_Mail()

# Uscita
        return nlSys.NF_ErrorProc(sResult, sProc)

# Legge DATI di partenza, config.ini, users.csv, actions.csv
# Rirorna sResult / self.sResult
# inutile forse c'è già Sys_ReadINI
# --------------------------------------------------------------------
    def Init_ReadINI(self) -> str:
        sProc="JOS.INIT.READINI"
        sResult=""
        dictConfigTemp={}
# ConfigFile Name
        sFileConfigName=nlSys.NF_PathMake(self.sSys_PathRoot, self.Sys_PathDati() + "\\Config\\ntjobs_config","ini")        
# Lettura INI
        lResult=nlSys.NF_INI_Read(sFileConfigName)
        sResult=lResult[0]
        if sResult=="": 
# Prende il dictionary "CONFIG" SOLAMENTE
            dictConfigTemp=lResult[1].copy()
            self.dictConfigINI=dictConfigTemp["CONFIG"].copy()
        if nlSys.NF_DictLen(self.dictConfigINI)==0:
            sResult=f"Dictionary Config Read Empty from file {sFileConfigName}"
# Cambio Variabili in Config
        else:
# Assign With Replace dictConfigINI
            dictConfigTemp=self.dictConfigINI.copy()
            dictConfigTemp2=nlSys.NF_DictStrReplaceDict(dictConfigTemp, self.dictConfigINI)
            self.dictConfigINI=dictConfigTemp2.copy()
# Also dictConfig
            sResult=self.Sys_ConfigReset()
            nlSys.NF_DebugFase(NT_ENV_TEST, f"Read INI {sFileConfigName}, Result: {sResult}" +  str(self.dictConfig), sProc)
# Return
        return nlSys.NF_ErrorProc(sResult, sProc)

# Legge DATI di partenza, config.ini, users.csv, actions.csv
# Rirorna sResult / self.sResult
# inutile forse c'è già Sys_ReadINI
# --------------------------------------------------------------------
    def Init_ReadDAT(self) -> str:
        sProc="JOS.INIT.READ.DAT"
        sResult=""
        anIni=self.dictFData.keys()
        objCSV=NC_CSV()
        sFileConfigName=""
        dictParams={}
        dictIniTemp={}

# Lettura Diverse Tab
        for nIni in anIni:
# ConfigFile Name
            sFileConfigName=nlSys.NF_PathMake(self.sSys_PathRoot, self.Sys_PathDati() + "\\Config\\ntjobs_" + self.dictFData[nIni],"csv")        
# CSV: Preparazione chiamata CSV READ
            asFields=self.asFields_DAT[nIni]
            sResult=objCSV.Read(file_in=sFileConfigName,fields=self.asFields_DAT[nIni])
# Sostituzione Variabili
            if sResult=="":
                nlSys.NF_DebugFase(NT_ENV_TEST, "Config.CSV Read.End. Starting Replace " + sFileConfigName + ", Rows: " + str(objCSV.nLines), sProc)        
                sResult=nlSys.NF_TableReplaceDict(objCSV.avTable,self.dictConfig)
            if sResult=="":
                self.Sys_TD_Assign(nIni,objCSV.avTable)
                nlSys.NF_DebugFase(NT_ENV_TEST, f"Assigned CSV.Replaced to TabData {nIni}" , sProc)
# Exit in case of Errors
            if sResult != "":
                break
# Uscita
        return nlSys.NF_ErrorProc(sResult, sProc)

# Inizializzazione ambiente mail
# -----------------------------------------------------------------------------
    def Init_Mail(self) -> str:
        sProc="JOS.INIT.MAIL"
        sResult=""
        dictMail={}

    # Esci se già inizializzato
        if self.bMailLogin==True: return ""

    # Inizializzazione oggetto mail
    # Prende da config
        asKeys=["ADMIN.EMAIL","SMTP.USER","SMTP.PASSWORD","SMTP.PORT","SMTP.SERVER","SMTP.SSL","SMTP.FROM","INIT.MAIL"]
        for sKey in asKeys:
            sConfig=self.Sys_Config(sKey)
            if sResult=="":
                dictMail[sKey]=sConfig
            else:
                break
    # Aggiunte
        sAdminEmail=self.Sys_Config("ADMIN.EMAIL")
    # Inizializazione
        if sResult=="":
            self.objMail=NC_MailSimple()
            sResult=self.objMail.Start(sSmtp_User_par=dictMail["SMTP.USER"],
                                       sSmtp_Password_par=dictMail["SMTP.PASSWORD"],
                                       sSmtp_Host_par=dictMail["SMTP.SERVER"],
                                       sSmtp_Port_par=int(dictMail["SMTP.PORT"]),
                                       bSSL_par=nlSys.NF_StrBool(dictMail["SMTP.SSL"]),
                                       bReconnect_par=True)
    # Flag Mail.Init Inizializzazione
        if sResult=="": 
            if self.objMail.bLogin==True:
                self.bMailLogin=True
            if nlSys.NF_StrBool(dictMail["INIT.MAIL"]):
                sResult=self.objMail.Send([sAdminEmail],"Start ntJobsOS",sBody_par="Starting")
    # Uscita
        return nlSys.NF_ErrorProc(sResult, sProc)

# Users/Groups/Actions/Configs. Ritorna NULL o ARRAY USERS/GROUPS/ACTIONS/CONFIGS
# --------------------------------------------------------------------
    def Sys_Users(self) -> list[str]:
        asResult=list[str]
        sProc="JOS.SYS.USERS"
        lResult=self.TabData_USR.GetCol("USER_NAME")
        if lResult=="": asResult=lResult[1]
        return asResult

    def Sys_Groups(self) -> list[str]:
        asResult=list[str]
        sProc="JOS.SYS.GROUPS"        
        lResult=self.TabData_USG.GetCol("GROUP_NAME")
        if lResult=="": asResult=lResult[1]
        return asResult

    def Sys_Actions(self)-> list[str]:
        asResult=list[str]
        sProc="JOS.SYS.ACTIONS"        
        lResult=self.TabData_ACT.GetCol("ACT_NAME")
        if lResult=="": asResult=lResult[1]
        return asResult
    
    def Sys_Configs(self) -> list[str]:
        asResult=list[str]
        sProc="JOB.SYS.CONFIGS"
        asResult=self.dictConfig.keys()
        return asResult
    
# Get KEY from GLOBAL CONFIG *config.ini"
# sType(""=Globale, "j"=singolo file ini)
# -----------------------------------------------------------------------------
    def Sys_Config(self, sKey)  -> str:
        return nlSys.NF_DictGet(self.dictConfig,sKey,"")

# Reset Config da master+jobs. Ritorna vuoto per eventuali usi futuri
# -----------------------------------------------------------------------------
    def Sys_ConfigReset(self)  -> str:
        sProc="JOS.SYS.CONFIG.RESET"
        sResult=""
# Check LEN BASE
        if nlSys.NF_DictLen(self.dictConfigINI)==0:
            sResult="Config INI dictionary empty"
        if sResult=="":
# Check LEN JOBS
# 1: GetdictConfigINI
# 2: Add dictJobs
# 3: Replace All with dictConfig
# 4: Replace ALL with dicConfigJobs
# 5: Assign Temp to dictConfig Again
            if nlSys.NF_DictLen(self.dictConfigJobs) != 0:
                dictTemp=nlSys.NF_DictMerge(self.dictConfigINI,self.dictConfigJobs)
                dictTemp2=nlSys.NF_DictStrReplaceDict(dictTemp, self.dictConfig)
                dictTemp3=nlSys.NF_DictStrReplaceDict(dictTemp2, self.dictConfigJobs)
                self.dictConfig=dictTemp3.copy()
            else:
# Only Get from dictConfigINI
                self.dictConfig=self.dictConfigINI.copy()
# Uscita
        return nlSys.NF_ErrorProc(sResult, sProc)

# TabData Index: Len    
    def Sys_TD_Len(self, nIndex: int)-> int:
        nResult=0
        if nIndex==self.JOB_DAT_ACT:
            nResult=nlSys.NF_ArrayLen(self.TabData_ACT.avTable)
        elif nIndex==self.JOB_DAT_USG:
            nResult=nlSys.NF_ArrayLen(self.TabData_ACT.avTable)
        elif nIndex==self.JOB_DAT_USR:
            nResult=nlSys.NF_ArrayLen(self.TabData_ACT.avTable)
        return nResult
# TaData: Assign from array
    def Sys_TD_Assign(self, nIndex:int, avTable)-> int: 
        nResult=0
        if nIndex==self.JOB_DAT_ACT:
            self.TabData_ACT.avData=avTable.copy()
        elif nIndex==self.JOB_DAT_USG:
            self.TabData_USG.avData=avTable.copy()
        elif nIndex==self.JOB_DAT_USR:
            self.TabData_USR.avData=avTable.copy()
        else:
            nResult=-1
        return nResult

# Replace config vars in string
# -----------------------------------------------------------------------------
    def Sys_ConfigReplace(self, sText)  -> str: 
        sTextResult=nlSys.NF_StrReplaceDict(sText, self.dictConfig)
        return sTextResult
        
# Replace config vars in string
# -----------------------------------------------------------------------------
    def Sys_ConfigReplaceList(self, asText)  -> str: 
        asTextResult=nlSys.NF_ArrayStrReplaceDict(asText, self.dictConfig)
        return asTextResult

# Get KEY of GLOBAL CONFIG *config.ini"
# -----------------------------------------------------------------------------
    def Sys_ConfigSet(self, sKey, vValue, **kwargs):
        sType=nlSys.NF_DictGet(kwargs,type,"")
        return nlSys.NF_DictReplace(self.dictConfig,sKey,vValue)

# Get Value on Data Setup Talbles
# -----------------------------------------------------------------------------
    def Sys_TableGet(self, nTable, sID: str, sFieldName: str):
        nIndex=0
        return self.avTable[nTable][nIndex]
   
    def Sys_PathDati(self):
        return nlSys.iif(NT_ENV_TEST,"DatiTest","Dati")

# Creazione path da esplorare
# Dato Array di Paths divisi da ",", vengono splittati ed aggiunti ad Array finale, togliendo gli spazi
# Per gestire il ritorno di errori legati al path viene creato un dict ed associato lo user
# Ritorna lResult 0=NoErorr, 1=dictPaths
# ------------------------------------------------------------------------------------------------------
    def Sys_Paths(self) -> list[str]:
        sProc="JOS.SYS.PATHS"
        dictPaths={}
        sResult=""

# Split di tutti i paths e manda su array asResult
        nIndex=0
        for sUser in self.asUsers:
        # Path
            sPath=self.TabData_USR.Get("USER_PATHS",nIndex)
            sUser=self.TabData_USR.Get("USER_ID",nIndex)
            nIndex +=1
        # Split+Norm
            asPaths=sPath.split(",")
            asPaths=nlSys.NF_ArrayNorm(asPaths,"LR")
        # Per Ogni Path Append con ID=USER
            for sPath in asPaths:
                if nlSys.NF_DictExistKey(dictPaths, sPath):
                    sResult=f"Path Duplicate for user {sUser}"
                else:
                    dictPaths[sPath]=sUser
        # Fine
        # Uscita
        return [nlSys.NF_ErrorProc(sResult, sProc),dictPaths.copy()]

# Search: Ricerca tra i path jobs.ini, lo legge  e lo sposta in inbox insieme ai files associati
# Se Trova JOB ma non trova tutti i file con errori effettua un return senza spostamento all'utente
# ------------------------------------------------------------------------------------------
    def Jobs_Search(self)  -> str:
        sProc="JOS.SEARCH"
        sResult=""
        self.sResult=""

    # Paths da cercare
        asPaths=self.dictPaths.keys() 

    # Per tutti i Paths Previsti
        for sPath in asPaths:
        # Prende utente associato al path
            sUser=self.dictPaths[sPath]
        # Lista dei files jobs*.ini
            lResult=self.Jobs_Find(sPath,"J")
            sResult=lResult[0]
        # Per tutti i files JOBS*.INI del path trovato, salvo errore
            if sResult=="":
                asFiles=lResult[1]
                nFiles=nlSys.NF_ArrayLen(asFiles)
            # Se Trovato almeno 1
                if nFiles>0:
            # Legge INI e Sposta File o ritorno MAIL
                    for sFile in asFiles:
                        nlSys.NF_DebugFase(NT_ENV_TEST, f"Search. Finded: {sFile}", sProc)                    
                        sResultGet=self.Jobs_Move(sFile)
                        if sResultGet != "":
                            nlSys.NF_DebugFase(NT_ENV_TEST, f"Error Moving Job {sFile}. {sResultGet}", sProc)                    
                            dictReturn={"USER": sUser, "RESULT": sResultGet, "JOBFILE": sFile, "TYPE": "G"}
                            self.Jobs_Return(dictReturn)
        # Uscita
        return nlSys.NF_ErrorProc(sResult, sProc)

# Legge INI di un file jobs.ini ---- DEVONO ESSERE ESEGUITI SUBITO DOPO LETTI
# perché lo spazio "config"  è unico per .ini e viene ripristinato ogni volta
# -----------------------------------------------------------------------------
    def Jobs_Read(self, sFileJob: str) -> str:
        sProc="JOS.READ"
        sResult=""

    # Legge INI
    # Ritorna lResult 0=Ritorno, 1=IniDict, dove Trim/UCASE.KEY e valori "trimmati"
        nlSys.NF_DebugFase(NT_ENV_TEST, f"Read JOBS.INI: {sFileJob}", sProc)    
        lResult=nlSys.NF_INI_Read(sFileJob)
        sResult=lResult[0]
        asFilesJob=list[str]

    # Crea Lista di files associati
        nlSys.NF_DebugFase(NT_ENV_TEST, "Read Files joined", sProc)    
        if (sResult==""):
            self.dictJobs=lResult[1]
            self.asFilesJob=list[str]
            asKeys=nlSys.NF_DictKeys(self.dictJobs)
            for sKey in asKeys:
            # Se lo trova, lo estra, lo Normalizza e lo aggiunge{ ai file Extra
                if nlSys.NF_StrSearch("FILE.",sKey,-1):
                    asFileExtra=self.dictJobs[sKey]
                    lResult=nlSys.NF_PathNormal(asFileExtra)
                    sFileExtra=lResult[1]
                    asFilesJob.append(sFileExtra)
            # Aggiunge File Jobs
            self.asFilesJob.Append(sFileJob)

    # Reset Config con nuovo INI letto master+read
        if sResult=="":
            nlSys.NF_DebugFase(NT_ENV_TEST, f"Files Associated with {sFileJob}: {asFilesJob}", sProc)        
            sResult=self.Sys_ConfigReset()

    # Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)

# Sposta i files di un job in cartella Inbox\JOB_ID
# dictJob.JOBFILE: Cartella da spostare dove ci deve essere almeno un file jobs.ini ma ci sono anche più jobs
# Nella stessa cartella ci devono essere tutti i file associati
# Importante ci siano anche i files associati o il processo viene bloccato
# -----------------------------------------------------------------------------
    def Jobs_Move(self, dictJob:dict)  -> str:
        sProc="JOS.MOVE"
        sResult=""
        sPathJob_out=""
    # Estrae
        sPath=dictJob["JOBFILE"]
        if nlSys.NF_NullToStr(sPath)=="": sResult="job.ini non specificato"
    # Estrae Job. Toglie "_" che identifica finito
        lResult=nlSys.NF_PathScompose(sPath)
        sJobID_in=lResult[1]
        sJobPath_in=lResult[1]
    # Lista files da spostare
        if sResult=="":
            nlSys.NF_DebugFase(NT_ENV_TEST, "Create List JobsFiles to move to Inbox", sProc)    
            asFiles=[sPath]
            for sKey in nlSys.NF_DictKeys(dictJob):
                if nlSys.NF_StrSearch(-1,sKey,"FILE."):
                    sFileToMove=nlSys.NF_PathMake(sJobPath_in,dictJob[sKey],"")
                    asFiles.append(sFileToMove)
    # Verifica esistenza, se non esistono tutti NON PROSEGUE
            for sFile in asFiles:
                if nlSys.NF_FileExist(sFile)==False: sResult=nlSys.NF_StrAppendExt(sResult, "not.exist=" + sFile, ",")
    # Creazione Folder + Spostamento files
            if sResult=="":
                sJobID_out=nlSys.NF_TS_Now()
                sPathJob_out=nlSys.NF_PathMake(self.sSys_PathInbox,sJobID_out)
                sResult=os.makedir(sPathJob_out)
                nlSys.NF_DebugFase(NT_ENV_TEST, f"Created Path {self.sPathJob_out}", sProc)    
            # Se creato folder, sposta file
            if sResult=="":
                nlSys.NF_DebugFase(NT_ENV_TEST, f"Move Files to path {self.sPathJob_out}", sProc)    
                for sFile in asFiles:
                    lResult=nlSys.NF_PathScompose(sFile)
                    sFileOut=nlSys.NF_PathMake(self.sSys_PathInbox, lResult[1], lResult[2])
                    sResult=nlSys.NF_StrAppendExt(sResult, nlSys.NF_FileMove(sFile,sPathJob_out))
    # Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)

# Exec Action
# 1: Cerca in Inbox se ci sono jobs da eseguire
# 2: Per quelli trovati legge jobs.ini nella cartella. SOLO se TROVA JOBS.INI esegue
# 2.1: Ripristina CONFIG a .ini di default
# 2.2: Read jobs.ini e config letto merge con quello dj ntjobsos
# 2,3: Effettua Login utente
# 2.4: Esegue processo con wait o no.
# -----------------------------------------------------------------------------
    def Jobs_Exec(self)  -> str:
        sProc="JOS.EXEC"
        sResult=""

    # Ricerca
        lResult=self.Jobs_Find("J")
        sResult=lResult[0]
        if sResult=="":

    # Esecuzione
        # Per ogni cartella...
            asFind=lResult[1]
            for sFind in asFind:
        # Legge Job.INI
                sResult=self.Jobs_Read(sFind)
        # Verifica dictJobs
                if sResult=="":
                    sResult=self.Jobs_Login(self)
        # Esecuzione
                if sResult=="":
                    sResult=self.Jobs_Exec_Run(self)

    # Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)

# Verifica dictJobs (Login Utente)
# Estrae Dati utente corrente
# -----------------------------------------------------------------------------
    def Jobs_Login(self)  -> str:
        sProc="JOS.LOGIN"
        sResult=""

# Parametri
        sUser=self.Sys_Config("USER")
        sPassword=self.Sys_Config("PASSWORD")

# Verifica utente dal db config in memoria
        if nlSys.NF_ArrayFind(self.asUsers,sUser)==-1: sResult="User not found " + sUser
        if sResult=="":
            sPwd2=self.Jobs_TabData(self.JOB_DAT_CFG, "USER", sUser, "PASSWORD")
            if sPwd2 != sPassword: sResult="User " + sUser + " password invalid"
# Login Effettivo
        if sResult=="":
            self.sUser_ID=sUser
            self.sUser_asGroups=self.Jobs_TabData(self.JOB_DAT_CFG, "USER", sUser, "GROUPS")
# Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)

# Logout Utente - Reset Variables self.sUser_
# -----------------------------------------------------------------------------
    def Jobs_Logout(self)  -> str:
        self.sUser_ID=""
        self.sUser_asGroups=[]

# Estrae Azione corrente e verifica che sia eseguibile da utente corrente
# -----------------------------------------------------------------------------
    def Jobs_Exec_Get_Act(self)  -> str:
        sProc="JOS.EXEC.GET.ACT"
        sResult=""

# Estrae dati azione corrente
        sResult=self.Act_Get(self)
        self.sAction=nlSys.NF_DictGet(self.dictJob["ACTION"],"")

# Cerca sua esistenza
        if nlSys.NF_ArrayFind(self.asActions,self.sAction)==-1:
            sResult="Action richiesto non previsto: " + self.sAction

# Verifica Action in gruppi utente consentiti
        if sResult=="":
            sACT_Groups=self.Jobs_TabData(self.JOB_DAT_CFG, "ACTIONS", self.sAction, "GROUPS")
            nFind=nlSys.NF_ArrayFind(self.User_asGroups, self.sUser_ID)
# Uscita
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        return sResult

# Exec.Run: Esecuzione job
# -----------------------------------------------------------------------------        
    def Jobs_Exec_Run(self) -> str:
        sProc="JOS.EXEC.RUN"
        sResult=""

# Esecuzione
        nlSys.NF_DebugFase(NT_ENV_TEST, "Exec " + self.sScript, sProc)    
        sResult=nlSys.NF_Exec(self.sScript)

    # Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)

# Exec.Quit: Check Fine jobs.ini corrente
# -----------------------------------------------------------------------------------------------------
    def Jobs_Exec_Quit(self)  -> str:
        sProc="JOS.EXEC.Quit"
        sResult=""

    # Cerca se esiste ma lo cancela anche per sicurezza
    # Se errore in cancellazione ritorna errore
        sFileJobEnd=nlSys.NF_PathMake(self.jData.sSys_Path,"jobs","end")
        if nlSys.NF_FileExist(self.sFileJobend):
            self.sResult=nlSys.NF_FileDelete(self.sFileJobend)
    # Ritorno
        return sResult

# Cerca Cartella con caratteristiche - Ritorna lResult. Se 0=ERROR, 1=Lista path jobs da arhiviare
# Type="A"= DaArchiviare, "J": Da Eseguire, "": Da Spostare in una cartella sPath
# Se Type="A"[da archiviare]="___" o "J"[da eseguire], E=[Finiti]="_", R="__" da fare Return, non viene considerato sPath ma sSysPath_Inbox
# I Path contenenti jobs cominciano per jobs*, quelli da arhiviare iniziano per _jobs*
# sType="", cerca files, in caso A o J cerca "folders"
# ----------------------------------------------------------------------------------------------------
    def Jobs_Find(self, sPath="", sType="J"):
        sProc="JOBS.FIND"
        asResult=list[str]
        sType=sType.upper()
        sPathToFind=""
        sTypeSearxh=""
        asPaths=[]

    # Calcola folder di base su inbox che inizia per jobs
    # R, A, E, J, ""(Find)        
        if sType=="":
            sPathToFind=nlSys.NF_PathMake(sPath,"jobs*","")
            sTypeSearch="DN"
        elif sType=="J":
            sPathToFind=nlSys.NF_PathMake(sPath,"jobs*","")
            sTypeSearch="DN"
        elif sType=="R":
            sPathToFind=nlSys.NF_PathMake(sPath,"__jobs*","")
            sTypeSearch="DN"
        elif sType=="E":
            sPathToFind=nlSys.NF_PathMake(sPath,"_jobs*","")
            sTypeSearch="DN"        
        elif sType=="A":
            sPathToFind=nlSys.NF_PathMake(sPath,"___jobs*","")
            sTypeSearch="DN"
        else:
            sResult=f"Type not corrent: {sType}" 
    # Ricerca valida sia per J che per A
        if sResult=="":
            sResult,asPaths=nlSys.NF_PathFind(sPathToFind,sTypeSearch)
        else:
            sResult,nlSys.NF_ErrorProc(sResult, sProc)
    # Uscita
        return sResult, asPaths

# Crea Cartella in Inbox temp jobs con jobs.ini al suo interno con dictINIs (con config ed altre azioni)
# Parametri: sResult=Ritorno da scrivere nel job
# ----------------------------------------------------------------------------
    def Jobs_Temp(self,dictINIs) -> str:
        sProc="JOBS.TEMP"
        sResult=""
        sPathTemp=""

        lResult=nlSys.PathTemp(self.Sys_PathInbox,"D")
        sResult=lResult[0]
        if sResult=="":
            sPathTemp=lResult[1]
            sFileName=nlSys.NF_PathMake(sPathTemp,"jobs","ini")
            sResult=nlSys.NF_INI_Write(sFileName,self.dictINI)
    # Uscita
        return nlSys.NF_ErrorProc(sResult, sProc)

# Archiviazione Jobs Finiti
# Ritorno: sResult
# -----------------------------------------------------------------------------
    def Jobs_Archive(self) -> str:
        sProc="JOBS.ARC"
        sResult=""
    # DA VERIFICARE
        sPathInbox=self.sSys_PathInbox
        sPathArchive=self.sSys_PathArchive
    # Muove Files
        sResult=nlSys.NF_FolderMove(sPathInbox, sPathArchive)
    # Uscita
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        self.sResult=sResult
        return sResult

# Estrae Dato da Tabelle  JOB_DAT_ACT=1   JOB_DAT_USR=2  JOB_DAT_USG=3
# Input: ID_Tabella, Campo Chiave, Valore Ch
# Return: 2 values. sResult e Dato Estratto
# -----------------------------------------------------------------------------
    def Jobs_TabData(self, nID_TAB, sKey, sKeyValue, sField):
        sProc="JOBS.TABDATA"
        sResult=""

# Cerca Key (non previsto JOB_DAT_CFG)
        if nID_TAB==self.JOB_DAT_ACT:
            avFields=self.asActions
        elif nID_TAB==self.JOB_DAT_USR:
            avFields=self.asUsers
        elif nID_TAB==self.JOB_DAT_USG:
            avFields=self.asGroups
        else:
            sResult="nID not found"
# Estrae Dato da Tabella/Field
        nIndexField=nlSys.NF_ArrayFind(avFields, sKey)
        vDato=nlSys.NF_ArrayFind(self.avTable[nID_TAB][nIndexField])

# Ritorno
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        return sResult,vDato
    
# Archive
# Cerca tutti i JOBS da Archiviare e li sposta in zona Archivio
# --------------------------------------------------------------
    def Jobs_Archive(self) -> str:
        sProc="JOS.ARCHIVE"
        sResult=""
        sJobEnd=""
    # Ricerca JOBS DA ARCHIVIARE
        lResult=self.Jobs_Find("A")
        sResult=lResult[0]
        if sResult=="":
    # Spostamento (Archiviazione) + Archiviazione
            # Per ogni cartella...
            asFind=lResult[1]
            for sFind in asFind:
            # Legge Job
                sResult=self.Jobs_Red(sFind)
            # Email di ritorno
            # ---------- da togliere ------------------
                sResult=self.Arc_Return(self.dictJob)
            # Archiviazione
                if sResult=="": sResult=self.Arc_Archive(sResult)
    # Uscita
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        self.sResult=sResult
        return sResult

# Sottofunzione di Job.End, cerca jobs.end. se lo trova
# Se lo trova, rinomina la cartella con "_" davanti per indicare da archiviare
# -------------- FORSE A INTEGREARE IN ARCHIVE ----------------------------------------
    def Jobs_End_Archive(self, sPathInboxJ) -> str:
        sProc="JOS.END.ARC"
        sResult=""

    # Ricerca jobs.end
        lResult=nlSys.NF_PathNormal(sPathInboxJ)
        if sResult=="":
            sPathInboxA=nlSys.NF_PathMake("_" + lResult[1])
            sResult=nlSys.NF_FileRename(sPathInboxJ,sPathInboxA)

    # Uscita
        return nlSys.NF_ErrorProc(sResult, sProc)

# Kill Job corrente ma scrive anche jobs.end
    def Jobs_Kill(self, sJob) -> str:
        sProc="JOS.KILL"
        sResult=""
    # Scrive jobs.end
        sFileJobEnd=nlSys.NF_PathMake(sJob,"jobs","end")
        sResult=nlSys.NF_FileWrite(sFileJobEnd,"End")
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        return sResult

# AZIONE: Ciclo Search - Exec - Return - Archive
# WAIT_STD ongni diversi moltiplicatori tra Search - Find - Archive 
# -----------------------------------------------------
    def Jobs_Loop(self) -> str:
        sProc="JOS.LOOP"
        sResult=""

# Log
        sResult=self.objLog.Log("NJOS Start: " +  sResult, cat="NJOS")


# Prende Limite Contatori e Inizializza. Moltiplicatori SEARCH, FIND, ARCHIVE
        nMX_Search=self.Sys_Config("MX_SEARCH")
        nMX_Search=nlSys.iif(nMX_Search==0,5,nMX_Search)
        nCounter_Search=nMX_Search

        nMX_Archive=self.Sys_Config("MX_ARCHIVE")
        nMX_Archive=nlSys.iif(nMX_Archive==0,5,nMX_Archive)
        nCounter_Archive=nMX_Archive

# Inizio Loop
        while self.bExitNJOS==False:

# Prende Jobs Nuovi Nelle Cloud e copia in INBOX su cartelle dedicate al JOB
            if nCounter_Search==0:
                sResult=self.Jobs_Search()
                if sResult != "":
                    self.bExit=True
                    break
                nCounter=Search=nMX_Search
            else:
                nCounter_Search =- 1

# Esegue Processi in INBOX accumulati
            sResult=self.Jobs_Exec()
            if sResult != "":
                self.bExit=True
                break

# Verifica se ci sono processi conclusi
            sResult=self.Jobs_End()
            if sResult != "":
                self.bExit=True
                break

# Return
            sResult=self.Jobs_Return()
            if sResult != "":
                bExit=True
                break

# Archiviazione
            if nCounter_Archive==0:
                sResult=self.Jobs_Archive()
                if sResult != "":
                    bExit=True
                    break
                nCounter_Archive=nMX_Archive
            else:
                nCounter_Archive =- 1
 
# Uscita forzata da NTJOBOS
            sResult=self.Jobs_Exit()
            if (sResult=="") or self.bExitNJOS:
                bExit=True
                break

# Uscita da motore ntJobs  - forse
            sResult=self.Jobs_Quit()
            if sResult != "":
                bExit=True
                break

# Wait
            nlSys.NF_Wait(JOBS_WAIT_STD)

# Uscita
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        return sResult

# AZIONE: Quit jobs.ini corrente - Forzato
# ID di job corrente = uso path esecuzione
# -----------------------------------------------------
    def Jobs_Quit(self) -> str:
        sProc="JOS.QUIT"
        sResult=""
# Log
        sResult=self.objLog.Log("NJOS Quit Job.ini Forced: " + self.sJob, cat="NJOS")
# Scrive File Quit        
        sFileJobQuit=nlSys.NF_PathMake(self.jData.sJob,"jobs","end")
        sResult=nlSys.NF_FileWrite(sFileJobQuit,"Quit")
# Uscita
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        self.sResult=sResult
        return sResult

# AZIONE: Restart ----- NON IMPLEMENTATA IN LOOP PER ORA
# -----------------------------------------------------
    def Jobs_Restart(self) -> str: 
        sProc="JOS.RESTART"
        sResult=""
# Log
        sResult=self.objLog.Log("NJOS Restart: " +  sResult, cat="NJOS")
# Scrive File Restart per batch che lo esegue
        sFileJobRestart=nlSys.NF_PathMake(self.jData.sSys_Path,"jobs","restart")
        sResult=nlSys.NF_FileWrite(sFileJobRestart,"Restart")
# Scrive File Quit
        if sResult=="": 
            nlSys.NF_DebugFase(NT_ENV_TEST, "Scrive File Restart", sProc)    
            sResult=self.act_Quit()
# Uscita
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        self.sResult=sResult
        return sResult

# Ritorno MAIL, FILE risultanti e jobs.end
# Cerca tutti i jobs dichiarati come end (_ + jobs.end dentro)
# -----------------------------------------------------------------------------
    def Jobs_Return(self)  -> str:
        sProc="JOS.RETURN"
        sResult=""

    # Parametri    
        sUser=self.dictReturn["USER"]
        sType=self.dictReturn["TYPE"]
        sJobID=self.dictReturn["JOBID"]
        sPath=self.dictReturn["JOBFILE"]
        sReturn=self.dictReturn["RESULT"]
        nlSys.NF_DebugFase(NT_ENV_TEST, "Return data ", sProc)
    # Recupero Mail
        sUser_Mail=""
    # Creazione Soggetto e Body
        if sType=="A":
            sSubject="Completamento Job: " + sJobID
            sBody = sSubject + ", archiviato job."
        else:
            sSubject="Errore lettura job in file " + sPath
            sBody = sSubject + "\n" + sReturn
    # Invia Mail di Ritorno
        nlSys.NF_DebugFase(NT_ENV_TEST, f"Invio mail {sSubject}" , sProc)    
        sResult=self.objMail.Send([sUser_Mail],sSubject,sBody)
    # Uscita
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        self.sResult=sResult
        return sResult

# End Action
# 1: Cerca in Inbox se ci sono jobs terminati
# 2: Se trova jobs.end rinomina cartella con "_" davanti per indicare che è da archiviare
# -------------------------------------------------------------------------------------------------------
    def Jobs_End(self) -> str:
        sProc="JOS.END"
        sResult=""

# Prende Inbox Path e ed
        nlSys.NF_DebugFase(NT_ENV_TEST, "Ricerca JOBS.END", sProc)    
        lResult=self.Jobs_Find("E")
        sResult=lResult[0]
        asPathInboxJ=[]
# Cancellazione e Rinomina
        if sResult=="":
            nlSys.NF_DebugFase(NT_ENV_TEST, "Cancellazione e Rinomina JOBS.END", sProc)    
            asPathInboxJ=lResult[1]
            for sPathInBoxJ in asPathInboxJ:
                sResult=nlSys.NF_StrAppendExt(sResult,self.End_Archive(asPathInboxJ))
# Uscita
        return nlSys.NF_ErrorProc(sResult, sProc)

# Exec Live
# 1: Cerca in Inbox se ci sono jobs da eseguire
# 2: Se trova jobs.end rinomina cartella con "_" davanti per indicare che è da archiviare
# -------------------------------------------------------------------------------------------------------
    def Jobs_Live(self) -> str:
        sProc="JOS.LIVE"
        sResult=""

# Tutti i jobs che hanno un checklive memorizzato ogni x secondi
# dictJobsLive(id=folder, 0=ogni x secondi, 1=ultimo check vDateTimeNow)
        asJobs=self.dictJobsLive.keys()
# Ciclo di ricerca e kill
        for sJob in asJobs:
        # Estrae Dati di check
            dictLive=self.dictJobsLive[sJob]
            vLastCheck=self.dictLive["LAST"]
            nSeconds=self.dictLive["SEC"]
            avPid=self.dictLive["PID"]
        # Confronto
            vNow=datetime.now
            vPassed=vLastCheck+nSeconds
            if vNow>vPassed:
                for vPid in avPid:
                    sResult=nlSys.NF_StrAppendExt(sResult,nlSys.NF_Kill(vPid),"!")
                if sResult=="":
                    sResult=self.Jobs_End(sJob)
                if sResult=="":
                    sResult=self.objLog.Log("Kill for not live check  " + str(nSeconds) + ": " + sJob)
        # Salva ultimo Check
            self.dictJobsLive[sJob][self.FLD_LASTCHECK]=vNow
# Uscita
        return nlSys.NF_ErrorProc(sResult, sProc)