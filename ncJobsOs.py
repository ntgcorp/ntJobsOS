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
from ncMail import NC_Mail
from ncLog import NC_LOG

# Test Mode
NT_ENV_TEST_JOS = True
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
    asFilesJob=[]
# Paths da Leggere
    dictPaths=dict()
# Jobs
    FLD_LASTCHECK=0
# Tabelle di supporto per Tabelle BI/MULTIDIMENSIONALI JobOS, Users, Comandi, Gruppi, Paths da cercare, non CFG
    asUsers=[]
    asActions=[]
    asGroups=[]
    asPaths=[]
# Tabelle CSV da leggere - STESSO ORDINE DI JOB_DAT_*
    JOB_DAT_CFG=0   # Data/ntjobs_config.ini
    JOB_DAT_ACT=1   # Data/ntjobs_actions.csv
    JOB_DAT_USR=2   # Data/ntjobs_users.csv
    JOB_DAT_USG=3   # Data/ntjobs_groups.csv
# Nomi File esterni
    dictFData={JOB_DAT_CFG:"config", JOB_DAT_ACT:"actions", JOB_DAT_USR:"users", JOB_DAT_USG:"groups"}
# Tabelle Dati Jobs
    asJobsFields={ JOB_DAT_USR:("USER_ID","USER_PASSWORD","USER_NAME","USER_NOTES","USER_GROUPS","USER_PATHS","USER_MAIL","USER_ACTIONS"),
                   JOB_DAT_USG:("GROUP_ID","GROUP_NAME","GROUP_NOTES"),
                   JOB_DAT_ACT:("ACT_ID","ACT_NAME","ACT_GROUPS","ACT_SCRIPT","ACT_ENABLED","ACT_PATH","ACT_ORDER","ACT_TIPS","ACT_HELP","ACT_LIVE"),
                   JOB_DAT_CFG:("ADMIN.EMAIL","SMTP.AUTH","SMTP.FROM","SMTP.PASSWORD","SMTP.PORT","SMTP.SERVER","SMTP.SSL","SMTP.TLS","SMTP.USER","NTJOBS.VER")}
# Repository in memoria Tabelle Interne CARICATE DA CSV ESTERNO - CREATO SPAZIO IN ARRAY
    TabData=["","","",""]
# User CURRENT Details - Tutti e quelli più usati - Da Jobs_Login. gli altri in JOBSINI
    sUser_ID=""
    sUser_asGroups=[]
# Flag Interni vari
    bExitJOB=False     # Flag di uscita da jobs corrente
    bExitNJOS=False    # Flag di uscita da NTJOBS full
    bMailLogin=True    # Flag Mail Login fatto Flag (deve essere fatto una volta sola)
# Variabili Iniizializzate
    sSys_PathRoot=""   # Path BASE 

# Init - Richiede presenza jData già inizializzata
# ------------------------------------------------------------------------------------------------------------
    def __init__(self):
        pass

# Inizializzazione OGGETTO
    def Init(self):
        sResult=""
        sProc="JOS.INIT"
# Log Start
        nlSys.NF_DebugFase(NT_ENV_TEST_JOS, "Start Log", sProc)
        sLogFile=nlSys.NF_PathMake(nlSys.NF_PathScript("PATH"),"system","log")       
        self.objLog=NC_LOG()        
        sResult=self.objLog.Log("Start Log", log_type="info",log_file=sLogFile,log_cat="info")
# Inizializzazioni
        nlSys.NF_DebugFase(NT_ENV_TEST_JOS, "Start Init", sProc)
        self.sSysPathRoot=nlSys.NF_PathScript("PATH")
# Lettura INI
        if sResult=="":
            for nConfig in self.dictFData.keys():
                nlSys.NF_DebugFase(NT_ENV_TEST_JOS, "Read Config " + self.dictFData[nConfig], sProc)
                sTemp=self.Sys_ReadINI(nConfig)
                if sTemp=="":
                    sResult = sResult + nlSys.iif(sResult != "",",","") + "Read Config Error " + self.dictFData[nConfig] + ": " + sTemp
# Iniializzazione MAIL ENGINE
        if sResult=="":
            nlSys.NF_DebugFase(NT_ENV_TEST_JOS, "Send Mail", sProc)
            sResult=self.Init_Mail()
# Uscita
        return nlSys.NF_ErrorProc(sResult, sProc)

# Legge DATI di partenza, config.ini, users.csv, actions.csv
# Rirorna sResult / self.sResult
# inutile forse c'è già Sys_ReadINI
# --------------------------------------------------------------------
    def Init_ReadINI(self):
        sProc="JOS.INIT.READINI"
        sResult=""
        anIni=self.dictFData.keys()
        objCSV=NC_CSV()
        sFileConfigName=""
        dictParams={}
        dictIniTemp={}
# Lettura DATI INI o CSV
#  Legge Parametri
#self.bTrim=nlSys.NF_DictGet(dictParams,"TRIM",False)
#self.sDelimiter=nlSys.NF_DictGet(dictParams,"DELIMITER",sCSV_DELIMITER)
#self.asFields=nlSys.NF_DictGet(dictParams,"FIELDS",[])
#self.sFileCSV=nlSys.NF_DictGet(dictParams,"FILE.IN","")
#self.sFieldKey=nlSys.NF_DictGet(dictParams,"FIELD.KEY","")
        for nIni in anIni:
        # Comportamento Diverso a seconda tipo. CSV princpale o INI
        # Lettura CSV e associazione Tabella letta a quella di riferimento 
        # usr/groups/actions
            if self.Sys_ConfigFileType(nIni)=="csv":
        # NomeFile Config e Normalizzazione
                sFileConfigName=self.Sys_ConfigFileName(nIni)
        # Preparazione chiamata CSV READ
                dictParams["FILE.IN"]=sFileConfigName
                asFields=self.asJobsFields[nIni]
                dictParams["FIELDS"]=asFields
                dictParams["FIELD.KEY"]=asFields[0]
                sResult,dictCSV=nlSys.NF_Return2(objCSV.Read(sFileConfigName,dictParams))
                if sResult=="":
                    self.TabData[nIni]=dictCSV.copy()
            else:
                sResult,dictIniTemp=nlSys.NF_Return2(nlSys.NF_INI_Read(sFileConfigName))
                if sResult=="": self.dictConfigINI=dictIniTemp.copy()
# Aggiorna Tabelle Interne
        if sResult=="":
            self.asUsers=self.Sys_Users()
            self.asActions=self.Sys_Actions()
            self.asGroups=self.Sys_Groups()
            self.asConfigs=self.Sys_Configs()
# Uscita
        return nlSys.NF_ErrorProc(sResult, sProc)

# Inizializzazione ambiente mail
# -----------------------------------------------------------------------------
    def Init_Mail(self):
        sProc="JOS.INIT.MAIL"
        sResult=""
        dictMail=[]

    # Esci se già inizializzato
        if self.bMailLogin==True: return ""

    # Inizializzazione oggetto mail
    # Prende da config
        asKeys=["SMTP.FROM","SMTP.USER","SMTP"]
        for sKey in asKeys:
            sResult,sConfig=self.Config(sKey)
            if sResult=="":
                dictMail[sKey]=sConfig
            else:
                break
    # Inizializazioneg
        if sResult=="":
            self.objMail=NC_Mail(dictMail)
            sResult=self.objMail.sResult

    # Flag Mail.Init Inizializzazione
        if sResult=="": self.bMailLogin=True

    # Uscita
        return nlSys.NF_ErrorProc(sResult, sProc)

# Users/Groups/Actions/Configs. Ritorna NULL o ARRAY USERS/GROUPS/ACTIONS/CONFIGS
# --------------------------------------------------------------------
    def Sys_Users(self):
        asResult=[]
        sProc="JOS.SYS.USERS"
        lResult=self.TabData[self.JOB_DAT_USR].GetCol("USER_NAME")
        if lResult=="": asResult=lResult[1]
        return asResult

    def Sys_Groups(self):
        asResult=[]
        sProc="JOS.SYS.GROUPS"        
        lResult=self.TabData[self.JOB_DAT_USG].GetCol("GROUP_NAME")
        if lResult=="": asResult=lResult[1]
        return asResult

    def Sys_Actions(self):
        asResult=[]
        sProc="JOS.SYS.ACTIONS"        
        lResult=self.TabData[self.JOB_DAT_ACT].GetCol("ACT_NAME")
        if lResult=="": asResult=lResult[1]
        return asResult
    
    def Sys_Configs(self):
        asResult=[]
        sProc="JOB.SYS.CONFIGS"
        asResult=self.dictINI.keys().copy()
        asResult=nlSys.NF_ArrayAppend(self.dictJobs.keys())
        return asResult

    def Sys_ConfigFileName(self, nConfig):
        sResult=self.dictFData[nConfig]
        sPath=self.sSys_PathRoot & "/DatiTest"
        sResult=nlSys.NF_PathMake(sPath, sResult, self.Sys_ConfigFileType(nConfig))
        
    def Sys_ConfigFileType(self, nConfig):
        return nlSys.iif(nConfig==self.JOB_DAT_CFG,"ini","cfg")

# Get KEY from GLOBAL CONFIG *config.ini"
# sType(""=Globale, "j"=singolo file ini)
# -----------------------------------------------------------------------------
    def Sys_Config(self, sKey, **kwargs):
        sResult=""
        sProc="JOBS.SYS.CONFIG"
# Opzione Tipo di config
        sType=nlSys.NF_DictGet(kwargs,"type","")
# Estrae Config j=globale, ""=IniCorrente        
        if sType=="":
            vResult=nlSys.NF_DictGet(self.dictINI,sKey,"")
        elif sType=="j":
            vResult=nlSys.NF_DictGet(self.dictConfig,sKey,"")
        else:
            vResult=""
# Uscita
        return nlSys.NF_ErrorProc(sResult, sProc), vResult

# Reset Config da master+jobs. Ritorna vuoto per eventuali usi futuri
    def Sys_ConfigReset(self):
        sProc="JOS.SYS.CONFIG.RESET"
        sResult=""
        if nlSys.NF_DictExistKey(self.dictJobs,"CONFIG"):
            dictConfigJob=self.dictJobs["CONFIG"]
        self.dictConfig=nlSys.NF_DictMerge(self.dictINI,self.dictConfigJob)
        return sResult

# Replace config vars in string
# -----------------------------------------------------------------------------
    def Sys_ConfigReplace(self, sText): 
        sResult=nlSys.NF_StrReplaceDict(sText, self.dictConfig)
        return sResult

# Get KEY of GLOBAL CONFIG *config.ini"
# -----------------------------------------------------------------------------
    def Sys_ConfigSet(self, sKey, vValue, **kwargs):
        sType=nlSys.NF_DictGet(kwargs,type,"")
        return nlSys.NF_DictReplace(self.dictConfig,sKey,vValue)
    


# Creazione path da esplorare
# Dato Array di Paths divisi da ",", vengono splittati ed aggiunti ad Array finale, togliendo gli spazi
# Per gestire il ritorno di errori legati al path viene creato un dict ed associato lo user
# ------------------------------------------------------------------------------------------------------
    def Sys_Paths(self):
        sProc="JOS.SYS.PATHS"
        asPaths=self.TabData[self.JOB_DAT_USR].GetCol("USER_PATHS")
        if nlSys.NF_ArrayEmpty(asPaths): return asPaths

    # Split di tutti i paths e manda su array asResult
        for sTemp in asPaths:
        # Split+Norm
            asPaths=sTemp.split(",")
            asPaths=nlSys.NF_ArrayNorm(asPaths,"LR")
        # Cerca Usser
            nKey=self.TabData[self.JOB_DAT_USR].Index("USER_PATHS",sTemp)
            if nKey > 0:
                sUser=self.TabData[self.JOB_DAT_USR].GetValue(nKey, "USER_ID")
        # Per Ogni Path attribuisce user come valore
            for sPath in asPaths:
                self.dictPaths[sPath]=sUser
# Legge gli INI di configuazione con chiave numerica di tabella FDATA
    def Sys_ReadINI(self,nKey):
        sProc="JOS.SYS.READINI"
        sResult=""
        objCSV=NC_CSV()
# File da leggere e verifica sua esistenza
        sFile=""
# Verifica
        anConfig=self.dictFData.keys()
        if not nKey in anConfig:
            sResult="Key out of range: " + str(nKey)
# Crea Nome file da leggere con estensiione e path
        if sResult=="":
            sFile=self.dictFData[nKey] + "." + nlSys.iif(nKey==self.JOB_DAT_CFG,"ini","csv")
            sFile=nlSys.iif(NT_ENV_TEST_JOS,"DatiTest","Data") + "\\Config\\ntjobs_" + sFile 
            sFile=self.sSysPathRoot + sFile
# Verifica se esiste
            sResult=nlSys.NF_FileExistErr(sFile)
# Lettura INI o CSV =dict Interno
        if sResult=="":
            if nKey==self.JOB_DAT_CFG:
                nlSys.NF_DebugFase(NT_ENV_TEST_JOS, "Config.INI Read.Start " + sFile, sProc)
                lResult=nlSys.NF_INI_Read(sFile)
                sResult=lResult[0]
        # Prende tabella config
        # Aggiunge Config Extra
                if sResult=="":
                    self.dictConfig=lResult[1].copy()
                    dictAdd=self.dictConfigINI.copy()
                    nlSys.NF_DictMerge(self.dictConfig,dictAdd)
                    self.TabData[nKey]=self.dictConfig.copy()
                    nlSys.NF_DebugFase(NT_ENV_TEST_JOS, "Config.INI Read.End " + str(self.dictConfig), sProc)
# Le altre sono dei CSV
            else:
                nlSys.NF_DebugFase(NT_ENV_TEST_JOS, "Config.CSV Read.Start " + sFile, sProc)
                asFields=self.asJobsFields[nKey]
                dictParams={
                    "TRIM": True,
                    "FIELDS": asFields,
                    "FILE.IN": sFile,
                    "FIELD.KEY": asFields[0]}
                sResult=objCSV.Read(dictParams)
                # Prende tabella dati caricata
                if sResult=="":
                   self.TabData[nKey]=objCSV.avTable.copy()
                   nRows=nlSys.NF_ArrayLen(objCSV.avTable)
                   nlSys.NF_DebugFase(NT_ENV_TEST_JOS, "Config.CSV Read.End " + sFile + ", Rows: " + str(nRows), sProc)
        # Uscita
        return nlSys.NF_ErrorProc(sResult, sProc)

# Costruisce stringa di dump di tutto
#    def Sys_Dump(self):
        # sResult=""
 #        sProc="JOS.DUMP"
# DA VERIFICARE
        #sResult=str(self)
        #return sResult

# Search: Ricerca tra i path jobs.ini, lo legge  e lo sposta in inbox insieme ai files associati
# Se Trova JOB ma non trova tutti i file con errori effettua un return senza spostamento all'utente
# ------------------------------------------------------------------------------------------
    def Jobs_Search(self):
        sProc="JOS.SEARCH"
        sResult=""
        self.sResult=""

    # Per tutti i Paths Previsti
        for sPath in nlSys.NF_DictKeys(self.dictPaths):
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
                        sResultGet=self.Jobs_Move(sFile)
                        if sResultGet != "":
                            dictReturn={"USER": sUser, "RESULT": sResult, "JOBFILE": sFile, "TYPE": "G"}
                            self.Jobs_Return(dictReturn)
        # Uscita
        return nlSys.NF_ErrorProc(sResult, sProc)

# Legge INI di un file jobs.ini ---- DEVONO ESSERE ESEGUITI SUBITO DOPO LETTI
# perché lo spazio "config"  è unico per .ini e viene ripristinato ogni volta
# -----------------------------------------------------------------------------
    def Jobs_Read(self, sFileJob):
        sProc="JOS.READ"
        sResult=""

    # Legge INI
    # Ritorna lResult 0=Ritorno, 1=IniDict, dove Trim/UCASE.KEY e valori "trimmati"
        lResult=nlSys.NF_INI_Read(sFileJob)
        sResult=lResult[0]
        asFilesJob=[]

    # Crea Lista di files associati
        if (sResult==""):
            self.dictJobs=lResult[1]
            self.asFilesJob=[]
            asKeys=nlSys.NF_DictKeys(self.dictJobs)
            for sKey in asKeys:
            # Se lo trova, lo estra, lo Normalizza e lo aggiunge ai file Extra
                if nlSys.NF_StrSearch("FILE.",sKey,-1):
                    asFileExtra=self.dictJobs[sKey]
                    lResult=nlSys.NF_PathNormal(asFileExtra)
                    sFileExtra=lResult[1]
                    asFilesJob.append(sFileExtra)
            # Aggiunge File Jobs
            self.asFilesJob.Append(sFileJob)

    # Reset Config con nuovo INI letto master+read
        if sResult=="":
            sResult=self.Sys_ConfigReset()

    # Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)

# Sposta i files di un job in cartella Inbox\JOB_ID
# dictJob.JOBFILE: Cartella da spostare dove ci deve essere almeno un file jobs.ini ma ci sono anche più jobs
# Nella stessa cartella ci devono essere tutti i file associati
# Importante ci siano anche i files associati o il processo viene bloccato
# -----------------------------------------------------------------------------
    def Jobs_Move(self, dictJob):
        sProc="JOS.MOVE"
        sResult=""

    # Estrae
        sPath=dictJob["JOBFILE"]
        if nlSys.NF_NullToStr(sPath)=="": sResult="job.ini non specificato"

    # Estrae Job. Toglie "_" che identifica finito
        lResult=nlSys.NF_PathScompose(sPath)
        sJobID_in=lResult[1]
        sJobPath_in=lResult[1]

    # Lista files da spostare
        if sResult=="":
            asFiles=[sPath]
            for sKey in nlSys.NF_DictKeys(dictJob):
                if nlSys.NF_StrSearch(-1,sKey,"FILE."):
                    sFileToMove=nlSys.NF_PathMake(self.sInbox,dictJob[sKey],"")
                    asFiles.append(sFileToMove)

    # Verifica esisgtenza, se non esistono tutti NON PROSEGUE
            for sFile in asFiles:
                if nlSys.NF_FileExist(sFile)==False: sResult=nlSys.NF_StrAppendExt(sResult, "not.exist=" + sFile, ",")

    # Creazione Folder + Spostamento files
            if sResult=="":
            # Crea Folder
                sJobID_out=nlSys.NF_TS_Now()
                sPathJob_out=nlSys.NF_PathMake(self.sInbox,sJobID_out)
                sResult=os.makedir(self.sPathJob)
            # Se creato folder, sposta file
                if sResult=="":
                    for sFile in asFiles:
                        lResult=nlSys.NF_PathScompose(sFile)
                        sFileOut=nlSys.NF_PathMake(self.sInbox, lResult[1], lResult[2])
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
    def Jobs_Exec(self):
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
    def Jobs_Login(self):
        sProc="JOS.LOGIN"
        sResult=""

# Parametri
        sUser=self.Sys_Config("USER",type="j")
        sPassword=self.Sys_Config("PASSWORD", type="j")

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

# Estrae Azione corrente e verifica che sia eseguibile da utente corrente
# -----------------------------------------------------------------------------
    def Jobs_Exec_Get_Act(self):
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

# Esecuzione j
    def Jobs_Exec_Run(self):
        sProc="JOS.EXEC.RUN"
        sResult=""

# Esecuzione
        sResult=nlSys.NF_Exec(self.sScript)

    # Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)

# Exec.Quit: Check Fine jobs.ini corrente
# --------------------------------------------------------------------
    def Jobs_Exec_Quit(self):
        sProc="JOS.EXEC.Quit"
        sResult=""

    # Cerca se esiste ma lo cancela anche per sicurezza
    # Se errore in cancellazione ritorna errore
        sFileJobEnd=nlSys.NF_PathMake(self.jData.sSys_Path,"jobs","end")
        if nlSys.NF_FileExist(self.sFileJobend):
            self.sResult=nlSys.NF_FileDelete(self.sFileJobend)
    # Ritorno
        return sResult

# Cerca Cartelle Job con caratteristiche - Ritorna lResult. Se 0=ERROR, 1=Lista path jobs da arhiviare
# Type="A"= DaArchiviare, "J": Da Eseguire
# -----------------------------------------------------------------------------
    def Jobs_Find(self, sType="J"):
        sProc="JOBS.FIND"
        asResult=[]
        sType=sType.upper()

    # Calcola folder di base su inbox che inizia per jobs
        sPathInbox=self.Config("INBOX")
        sPathInboxJ=nlSys.NF_PathMake(sPathInboxJ,"jobs*","")
        sResult=nlSys.NF_FileExistsErr(sPathInbox)

    # Dal folder jobs Cerca Path da archiviare. Solo Folder non ricorsivo
        if sType=="A":
            sPath="_" + sPath

    # Ricerca valida sia per J che per A
        lResult=nlSys.NF_PathFind(sPath,"DN")

    # Uscita
        return lResult

# Crea Cartella in Inbox temp jobs con jobs.ini al suo interno con dictINIs (con config ed altre azioni)
# Parametri: sResult=Ritorno da scrivere nel job
# ----------------------------------------------------------------------------
    def Jobs_Temp(self,dictINIs):
        sProc="JOBS.TEMP"
        lResult=nlSys.PathTemp(self.Config("P.INBOX"),"D")
        sResult=lResult[0]
        sPathTemp=self.Sys_Config("INBOX")
        if sResult=="":
            sFileName=nlSys.NF_PathMake(sPathTemp,"jobs","ini")
            sResult=nlSys.NF_INI_Write(sFileName,self.dicINI)
    # Uscita
        return nlSys.NF_ErrorProc(sResult, sProc)

# Archiviazione Jobs Finiti
# Ritorno: sResult
# -----------------------------------------------------------------------------
    def Jobs_Archive(self):
        sProc="JOBS.ARC"
        sResult=""
    # DA VERIFICARE
        sPathInbox=self.Sys_Config("INBOX")
        sPathArchive=self.Sys_Config("ARCHIVE")
    # Muove Files
        sResult=nlSys.NF_FolderMove(sPathInbox, sPathArchive)
    # Uscita
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        self.sResult=sResult
        return sResult

# Estrae Dato da Tabelle
#  JOB_DAT_ACT=1   JOB_DAT_USR=2  JOB_DAT_USG=3
# Parametri: ID_Tabella, Campo Chiave, Valore Ch
# Ritorno: sResult + Dato Estratto
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
    def Jobs_Archive(self):
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
    def Jobs_End_Archive(self, sPathInboxJ):
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
    def Jobs_Kill(self, sJob):
        sProc="JOS.KILL"
        sResult=""

# AZIONE: Ciclo Get -> Exec -> Return -> Archive
# -----------------------------------------------------
    def Jobs_Loop(self):
        sProc="JOS.LOOP"
        sResult=""
# Log
        sResult=self.objLog.Log("NJOS Start: " +  sResult, cat="NJOS")

# Inizio Loop
        while self.bExit==False:

# Prende Jobs Nuovi Nelle Cloud e copia in INBOX su cartelle dedicate al JOB
            sResult=self.Jobs_Search()
            if sResult != "":
                self.bExit=True
                break
            nlSys.NF_Wait(JOBS_WAIT_STD)

# Esegue Processi in INBOX accumulati
            sResult=self.Jobs_Exec()
            if sResult != "":
                self.bExit=True
                break
            nlSys.NF_Wait(JOBS_WAIT_STD)

# Verifica se ci sono processi conclusi
            sResult=self.Jobs_End()
            if sResult != "":
                self.bExit=True
                break
            nlSys.NF_Wait(JOBS_WAIT_STD)

# Return
            sResult=self.Jobs_Return()
            if sResult != "":
                bExit=True
                break
            nlSys.NF_Wait(JOBS_WAIT_STD)

# Archiviazione
            sResult=self.Jobs_Archive()
            if sResult != "":
                bExit=True
                break
            nlSys.NF_Wait(JOBS_WAIT_STD)

# Uscita forzata da NTJOBOS
            sResult=self.Jobs_Exit()
            if (sResult=="") or self.bExitNJOS:
                bExit=True
                break
# Uscita da motore ntJobs
            sResult=self.Jobs_Quit()
            if sResult != "":
                bExit=True
                break
# Uscita
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        return sResult

# AZIONE: Quit jobs.ini corrente - Forzato
# ID di job corrente = uso path esecuzione
# -----------------------------------------------------
    def Jobs_Quit(self):
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
    def Jobs_Restart(self):
        sProc="JOS.RESTART"
        sResult=""
# Log
        sResult=self.objLog.Log("NJOS Restart: " +  sResult, cat="NJOS")

# Scrive File Restart per batch che lo esegue
        sFileJobRestart=nlSys.NF_PathMake(self.jData.sSys_Path,"jobs","restart")
        sResult=nlSys.NF_FileWrite(sFileJobRestart,"Restart")

# Scrive File Quit
        if sResult=="": sResult=self.act_Quit()

# Uscita
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        self.sResult=sResult
        return sResult

# Ritorno MAIL, FILE risultanti e jobs.end
# Cerca tutti i jobs dichiarati come end (_ + jobs.end dentro)
# -----------------------------------------------------------------------------
    def Jobs_Return(self):
        sProc="JOS.RETURN"
        sResult=""

    # Parametri
        sUser=self.dictReturn["USER"]
        sType=self.dictReturn["TYPE"]
        sJobID=self.dictReturn["JOBID"]
        sPath=self.dictReturn["JOBFILE"]
        sReturn=self.dictReturn["RESULT"]

        if sType=="A":
            sSubject="Completamento Job: " + sJobID
            sBody = sSubject + ", archiviato job."
        else:
            sSubject="Errore lettura job in file " + sPath
            sBody = sSubject + "\n" + sReturn

    # Invia Mail
        dictMail={
            "TO": sUser,
            "SUBJECT": sSubject,
            "BODY": sBody
            }
        sResult=self.objMail.Send(dictMail)

    # Uscita
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        self.sResult=sResult
        return sResult

# End Action
# 1: Cerca in Inbox se ci sono jobs terminati
# 2: Se trova jobs.end rinomina cartella con "_" davanti per indicare che è da archiviare
# -------------------------------------------------------------------------------------------------------
    def Jobs_End(self):
        sProc="JOS.END"
        sResult=""

# Prende Inbox Path e ed
        lResult=self.Jobs_Find("E")
        sResult=lResult[0]
        asPathInboxJ=[]

# Cancellazione e Rinomina
        if sResult=="":
            asPathInboxJ=lResult[1]
            for sPathInBoxJ in asPathInboxJ:
                sResult=nlSys.NF_StrAppendExt(sResult,self.End_Archive(asPathInboxJ))
# Uscita
        return nlSys.NF_ErrorProc(sResult, sProc)

# Exec Live
# 1: Cerca in Inbox se ci sono jobs da eseguire
# 2: Se trova jobs.end rinomina cartella con "_" davanti per indicare che è da archiviare
# -------------------------------------------------------------------------------------------------------
    def Jobs_Live(self):
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