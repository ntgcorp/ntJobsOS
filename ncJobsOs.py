#
# CLASSE Jobs Orchestratore. Gestisce Users e dati correlati, Actions e dati correlati
# Fasi:
# 1: _Init_
# 2: Start() - Legge INI (INI_Read) + Setup
# 2.1: Legge USERS
# 2.2: Legge CMDS
# 2.3: Legge GROUPS
# 2.4: Legge CONFIG (comune a tutti gli scripts JOBS) - A differenza degli altri è un dict non un Table
# 3: Genera lista PATHS/CANALI da ricercare
# 4: Loop che chiama le altre azioni
# ---- Actions ----
# __init__: Inizializzazione
# Read: Legge INI
# Get: Cerca jobs nei folders e sposta in Inbox
# Exec: Esegue Jobs
# End: Trova quelli finiti
# Archive: Ritorna risultati Jobs & Archiviazione del Job da Inbox in Archive
# -----------------------------------------------------------------------------

# Librerie
import nlSys, os
import nlDataFiles
from nlDataFiles import NC_CSV
from ncTable import NC_Table
from ncJobsApp import NC_Sys
from ncMail import NC_Mail
from ncLog import objLog

# Test Mode
NT_ENV_TEST_JOBS=True
JOBS_WAIT_STD=5

# ----------------------------- CLASSI ---------------------------
class NC_Jobs:
# ntJobs System Class APP + LOGF
# ID dictUsers=
# Classe Appliczione ntJobs.App - Obbligatoria sua Presenza
    jData=None
# Oggetto Mail di ritorno
    objMail=None
# Risultato ultima elaborazione
    sResult=""
# File INI jobs.ini letto (che può contenere più jobs) compreso [CONFIG] di login ed altro
    dictJobsINI=dict()
# Job Singolo
    dictJob=dict()
# Files associati al Job Corrente
    asFilesJob=[]
# Paths da Leggere
    dictPaths=dict()
# Config
    dictConfig=dict()
# Tabelle Dati Jobs
    asFMT_JOBS_USR=("USER_ID","USER_PASSWORD","USER_NAME","USER_NOTES","USER_GROUPS","USER_PATHS","USER_MAIL","USER_CMDS")
    asFMT_JOBS_USG=("GROUP_ID","GROUP_NAME","GROUP_NOTES")
    asFMT_JOBS_CMD=("CMD_ID","CMD_NAME","CMD_GROUPS","CMD_SCRIPT","CMD_ENABLED","CMD_USERS","CMD_PATH","CMD_ORDER","CMD_TIPS","CMD_HELP")
    asFMT_JOBS_CFG=("ADMIN.EMAIL","SMTP.AUTH","SMTP.FROM","SMTP.PASSWORD","SMTP.PORT","SMTP.SERVER","SMTP.SSL","SMTP.TLS","SMTP.USER","NTJOBS.VER")
# Tabelle di supporto per Tabelle BI/MULTIDIMENSIONALI JobOS, Users, Comandi, Gruppi, Paths da cercare, non CFG
    asUsers=[]
    asCmds=[]
    asGroups=[]
    asPath=[]
# Tabelle CSV da leggere - STESSO ORDINE DI JOB_DAT_*
    asCSV=["CONFIG","CMD","USERS","GROUPS"]
    JOB_DAT_CFG=0   # Data/ntjobs_config.ini
    JOB_DAT_CMD=1   # Data/ntjobs_cmds.csv
    JOB_DAT_USR=2   # Data/ntjobs_users.csv
    JOB_DAT_USG=3   # Data/ntjobs_groups.csv
# Repository in memoria Tabelle Interne CARICATE DA CSV ESTERNO - CREATO SPAZIO IN ARRAY
    TabData=["","","",""]
# User CURRENT Details
    User_ID=""
    User_asGroups=[]

# Init - Richiede presenza jData già inizializzata
# ------------------------------------------------------------------------------------------------------------
    def __init__(self, objJData=None):
# jData Init
        if objJData != None:
            self.jData=objJData
        else:
            self.sResult="Errore jData non inizializzata"
# TabData INI
        if self.sResult != "": self.TabData[self.JOB_DAT_CFG]=NC_Table(self.asFMT_JOBS_CFG,"ADMIN.EMAIL")
        if self.sResult != "": self.TabData[self.JOB_DAT_CMD]=NC_Table(self.asFMT_JOBS_CMD,"CMD_ID")
        if self.sResult != "": self.TabData[self.JOB_DAT_USR]=NC_Table(self.asFMT_JOBS_USR,"USER_ID")
        if self.sResult != "": self.TabData[self.JOB_DAT_USG]=NC_Table(self.asFMT_JOBS_USG,"GROUP_ID")
# dictFMT_JOS_FIELDS
#        dictFMT_JOBS_FIELDS={
#        JOB_DAT_CMD: asFMT_JOBS_CMD,
#        JOB_DAT_CFG: asFMT_JOBS_CFG,
#        JOB_DAT_USR: asFMT_JOBS_USR,
#        JOB_DAT_USG: asFMT_JOBS_USG}

# Quit: Chiusura motore Jobs se presente jobs.end (che viene cancellato)
# --------------------------------------------------------------------
    def Quit(self):
        sProc="JOBS.Quit"
        sResult=""

    # Cerca se esiste ma lo cancela anche per sicurezza
    # Se errore in cancellazione ritorna errore
        sFileJobEnd=nlSys.NF_PathMake(self.jData.sSys_Path,"jobs","end")
        if nlSys.NF_FileExist(self.sFileJobend):
            self.sResult=nlSys.NF_FileDelete(self.sFileJobend)
    # Ritorno
        return sResult

# Legge DATI di partenza, config.ini, users.csv, actions.csv
# Rirorna sResult / self.sResult
# --------------------------------------------------------------------
    def INI_Read(self):
        sProc="JOBS.INI.Read"
        sResult=""

        # Lettura DATI INI o CSV
        objCSV=NC_CSV()
        for nIndex in range(0,nlSys.NF_DictLen(self.asCSV)-1):
        # NomeFile e Normalizzazione
            sFile="Data/ntjobs_" + self.asCSV[nIndex].lower() + nlSys.iif(nIndex==JOB_DAT_CFG,"ini",".csv")
            lResult=nlSys.NF_PathNormal(sFile)
            sResult=lResult[0]
            if sResult=="": sResult=nlSys.NF_FileExistErr(lResult[1])

        # Lettura INI o CSV =dict Interno
            if sResult=="":
                sFile=lResult[1]
                nlSys.NF_DebugFase(NT_ENV_TEST_JOBS, "Legge config " + sFile, sProc)
                if nIndex==self.JOB_DAT_CFG:
                    lResult=nlDataFiles.NF_INI_Read(sFile)
                    sResult=lResult[0]
                    # Prende tabella config
                    # Aggiunge Config Extra
                    if sResult=="":
                        self.dictConfig=lResult[1].copy()
                        dictAdd=self.ConfigPaths()
                        self.TabData[nIndex]=nlSys.NF_DictMerge(self.dictConfig,dictAdd)
                else:
                    asFields=dictFMT_JOBS_FIELDS[nIndex]
                    dictParams={
                        "TRIM": True,
                        "FIELDS": asFields,
                        "FILE.IN": sFile,
                        "FIELD.KEY": asFields[0]}
                    sResult=objCSV.NF_CSV_Read(sFile)
                    # Prende tabella dati caricata
                    if sResult=="":
                        avTable=objCSV.avTable.copy()
                        avself.TabData[nIndex]
        # Fine Ciclo e Ritorno
            else:
                break

        # Aggiorna Tabelle
        if sResult=="":
            self.asUsers=self.Users()
            self.asCmds=self.Cmds()
            self.asGroups=self.Groups()
            self.asConfig=self.Configs()

        # Uscita
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        self.sResult=sResult
        return sResult

# Users/Groups/Actions/Configs. Ritorna NULL o ARRAY USERS/GROUPS/ACTIONS/CONFIGS
# --------------------------------------------------------------------
    def Users(self):
        asResult=[]
        lResult=self.TabData[self.JOB_DAT_USR].GetCol("USER_NAME")
        if lResult=="": asResult=lResult[1]
        return asResult

    def Groups(self):
        asResult=[]
        asResult=self.TabData[self.JOB_DAT_USG].GetCol("GROUP_NAME")
        if lResult=="": asResult=lResult[1]
        return asResult

    def Cmds(self):
        asResult=[]
        asResult=self.TabData[self.JOB_DAT_CMD].GetCol("CMD_NAME")
        if lResult=="": asResult=lResult[1]
        return asResult

# Creazione path da esplorare
# Dato Array di Paths divisi da ",", vengono splittati ed aggiunti ad Array finale, togliendo gli spazi
# Per gestire il ritorno di errori legati al path viene creato un dict ed associato lo user
# ------------------------------------------------------------------------------------------------------
    def Paths(self):
        asPaths=self.TabData[self.JOB_DAT_USR].GetCol("USER_PATHS")
        if nlSys.NF_ArrayEmpty(asPaths): return asPaths

    # Split di tutti i paths e manda su array asResult
        for sTemp in asPath:
        # Split+Norm
            asPaths=sTemp.split(",")
            asPaths=nlSys.NF_ArrayNorm(asPaths,"LR")
        # Cerca Usser
            nIndex=TabData[self.JOB_DAT_USR].Index("USER_PATHS",sTemp)
            if nIndex > 0:
                sUser=TabData[self.JOB_DAT_USR].GetValue(nIndex, "USER_ID")
        # Per Ogni Path attribuisce user come valore
            for sPath in asPaths:
                self.dictPaths[sPath]=sUxdf

# Get: Ricerca tra i path jobs.ini, lo legge  e lo sposta in inbox insieme ai files associati
# Se Trova JOB ma non trova tutti i file con errori effettua un return senza spostamento all'utente
# ------------------------------------------------------------------------------------------
    def Get(self):
        sProc="JOBS.GET"
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
                        sResultGet=self.Get_Move(sFile)
                        if sResultGet != "":
                            dictReturn={"USER": sUser, "RESULT": sResult, "JOBFILE": sFile, "TYPE": "G"}
                            self.Jobs_Return(dictReturn)
        # Uscita
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        self.sResult=sResult
        return sResult

# Legge INI di un JOB. Tutti i file che iniziano per jobs
# -----------------------------------------------------------------------------
    def Jobs_Read(self, sFileJob):
        sProc="JOBS.READ"
        sResult=""

    # Legge INI
    # Ritorna lResult 0=Ritorno, 1=IniDict, dove Trim/UCASE.KEY e valori "trimmati"
        lResult=ntDataFile.NF_INI_Read(sFileJob)
        sResult=lResult[0]
        if (sResult==""):
            self.dictJob=lResult[1]
            self.asFilesJob=[]
            asKeys=nlSys.NF_DictKeys(self.dictJob)
            for sKey in asKeys:
            # Se lo trova, lo estra, lo Normalizza e lo aggiunge ai file Extra
                if nlSys.NF_StrSearch("FILE.",sKey,-1):
                    asFileExtra=self.dictJob(sKey)
                    lResult=nlSys.NF_PathNormal(asFileExtra)
                    sFileExtra=lResult[1]
                    asFilesJob.append(sFileExtra)
            # Aggiunge File Jobs
            self.asFilesJob.Append(sFileJob)
    # Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)


# Sposta i files di un job in cartella Inbox\JOB_ID
# Path: Cartella da spostare dove ci deve essere almeno un file jobs.ini ma ci sono anche più jobs
# Importante ci siano anche i files associati o il processo viene bloccato
# -----------------------------------------------------------------------------
    def Jobs_Move(self, dictJob):
        sProc="JOBS.MOVE"
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
                sResult=os.makedir(sPathJob)
            # Se creato folder, sposta file
                if sResult=="":
                    for sFile in asFiles:
                        lResult=nlSys.NF_PathScompose(sFile)
                        sFileOut=nlSys.NF_PathMake(self.sInbox, lResult[1], lResult[2])
                        sResult=os.move(sFile,sPathJob_Out)
    # Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)

# Exec Action
# 1: Cerca in Inbox se ci sono jobs da eseguire
# 2: Per quelli trovati legge jobs.ini nella cartella. SOLO se TROVA JOBS.INI esegue
# 3: Read jobs.ini
# 4: Crea file JOBS.RUN
# 5: Esegue processo con wait o no.
# -----------------------------------------------------------------------------
    def Exec(self):
        sProc="JOBS.EXEC"
        sResult=""

    # Ricerca
        asFind=self.Jobs_Find("J")
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
                    sResult=self.Exec_VerifyLogin(self)
                else:
                   self.Jobs_End(sFind)
            # Login Utente
                if sResult=="": sResult=self.Exec_Login(self)
            # Esecuzione
                if sResult=="": sResult=self.Exec_Run(self)

    # Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)

# Verifica dictJobs (Login Utente)
# -----------------------------------------------------------------------------
    def Exec_VerifyLogin(self):
        sProc="Jobs.Exec.Verify.Config"
        sResult=""

# Parametri
        sUser==self.dictJobs["CONFIG"]["USER"]
        sPasswod=self.dictJobs["CONFIG"]["PASSWORD"]

# Verifica utente dal db config in memoria
        if nlSys.NF_ArrayFind(self.asUsers,sUser)==-1: sResult="User not found " + sUser
        if sResult=="":
            sPwd2=self.Jobs_TabData(self.JOB_DAT_CFG, "USER", sUser, "PASSWORD")
            if sPwd2 != sPwd: sResult="User " + sUser + " password invalid"

# Login Effettivo
        if sResult=="":
            self.User_sID=sUser
            self.User_asGroups=self.Jobs_TabData(self.JOB_DAT_CFG, "USER", sUser, "GROUPS")

        # Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)


# Verifica dictJobs.Job (Singolo Command=CMD che sia nei gruppi dell'utente
# -----------------------------------------------------------------------------
    def Exec_VerifyCmd(self):
        sProc="Jobs.Exec.Verify.Cmd"
        sResult=""

# Verifica Azione Accettata
        if sResult=="":
            self.sCmd=self.dictINI["CMD"]
            if nlSys.NF_ArrayFind(self.asCmds,self.sCmd)==-1:
                sResult="Comando richiesto non previsto: " + self.sCmd

# Verifica cmd in gruppi utente
        if sResult=="":
            sCmd_Groups=self.Jobs_TabData(self.JOB_DAT_CFG, "USER", sUser, "GROUPS")
            nlSys.NF_ArrayFind(self.User_asGroups,sCmd)

# Uscita
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        return sResult

# Esecuzione Jobs del file ini
    def Exec_Run(self):
        sProc="Jobs.Exec.Run"
        sResult=""

# DA COMPLETARE

    # Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)


# Ritorno per Jobs.End (per non inizio)
# Crea jDataTemp e scrive jobs.end per dichiararla compleata
# -----------------------------------------------------------------------------
    def Jobs_EndForced(self, sFileJobs, sStatus):
        sProc="Jobs.End"
        jDataTemp=NC_Sys("TEMP")
        sResult=jDataTemp.Start()
        jDataTemp.End()
        jDataTemp.ReturnCalcAdd()
        jDataTemp.ReturnWrite()

    # Uscita
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        return sResult

# Cerca Cartelle Job con caratteristiche - Ritorna lResult. Se 0=ERROR, 1=Lista path jobs da arhiviare
# Type="A"= DaArchiviare, "J": Da Eseguire
# -----------------------------------------------------------------------------
    def Jobs_Find(self, sType="J"):
        sProc="Jobs.Arc.Return"
        asResult=[]

    # Prende Inbox
        sPathInbox=self.Config("INBOX")
        sPathInboxJ=nlSys.NF_PathMake(sPathInboxJ,"jobs*","")
        sResult=nlSys.NF_FileExistsErr(sPathInbox)

    # Cerca Path da archiviare. Solo Folder non ricorsivo
        if sType=="A":
            sPath="_" + sPath
        lResult=nlSys.NF_PathFind(sPath,"DN")

    # Uscita
        return lResult

# Crea Cartella in Inbox temp jobs con jobs.ini al suo interno con dictINIs (con config ed altre azioni)
# Parametri: sResult=Ritorno da scrivere nel job
# ----------------------------------------------------------------------------
    def Jobs_Temp(self,dictINIs):
        lResult=nlSys.PathTemp(self.Config("P.INBOX"),"D")
        sResult=lResut[0]
        if sResult=="":
            sFileName=nlSys.NF_PathMake(sPathTemp,"jobs","ini")
            sResult=nlDataFiles.NF_INI_Write(sFileName,dicINIs)

    # Uscita
        return nlSys.NF_ErrorProc(sResult, sProc)

# Archiviazione Jobs Finiti
# Ritorno: sResult
# -----------------------------------------------------------------------------
    def Jobs_Archive(self):
        sProc="Jobs.Arc"
        sResult=""

    # Muove Files
        sResult=nlSys.NF_FolderMove(sPath, sFolderArc)

    # Uscita
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        self.sResult=sResult
        return sResult

# Estrae Dato da Tabelle
#  JOB_DAT_CFG=0  JOB_DAT_CMD=1   JOB_DAT_USR=2  JOB_DAT_USG=3
# Parametri: ID_Tabella, Campo Chiave, Valore Ch
# Ritorno: Dato Estratto
# -----------------------------------------------------------------------------
    def Jobs_TabData(self, nID_TAB, sKey, sKeyValue, sField):

# Cerca Key (non previsto JOB_DAT_CFG)
        if nID_TAB==self.JOB_DAT_CMD: avFields=self.asCmds
        if nID_TAB==self.JOB_DAT_USR: avFields=self.asUsers
        if nID_TAB==self.JOB_DAT_USG: avFields=self.asGroups
        if nID_TAB==self.JOB_DAT_CFG:
            avFields=self.asCFS
        nIndexField=nlSys.NF_ArrayFind(avFields, sKey)
        vDato=nlSys.NF_ArrayFind(self.avTable[nID_TAB][nIndexField])

# Ritorno
        return vDato

# Inizializzazione ambiente mail
# -----------------------------------------------------------------------------
    def Mail_Init(self):
        sProc="Jobs.Mail.Init"
        sResult=""

    # Esci se già inizializzato
        if self.bMailLogin==True: return ""

    # Inizializzazione oggetto mail
    # Prende da config
        asKeys=["SMTP.FROM","SMTP.USER","SMTP"]
        for sKey in asKeys:
            dictMail[sKey]=self.Config(sKey)
    # Inizializazioneg
        self.objMail=NC_Mail(dictMail)
        sResult=self.objMail.sResult

    # Flag Mail.Init Inizializzazione
        if sResult=="": self.bMailLogin=True

    # Uscita
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        self.sResult=sResult
        return sResult

# Get KEY from GLOBAL CONFIG *config.ini"
# -----------------------------------------------------------------------------
    def Config(self, sKey):
        return nlSys.NF_DictGet(self.dictConfig,sKey,"")

# Get KEY of GLOBAL CONFIG *config.ini"
# -----------------------------------------------------------------------------
    def ConfigSet(self, sKey, vValue):
        return nlSys.NF_DictRepace(self.dictConfig,sKey,vValue)

# Archive
# --------------------------------------------------------------
    def Archive(self):
        sProc="Jobs.Archive"
        sResult=""
        sJobEnd=""
    # Ricerca
        asFind=self.Jobs_Find("A")
        sResult=lResult[0]
        if sResult=="":
    # Spostamento (Archiviazione) + Archiviazione
            # Per ogni cartella...
            asFind=lResult[1]
            for sFind in asFind:
            # Legge Job
                sResult=self.Jobs_Red(sFind)
            # Email di ritorno
                sResult=self.Arc_Return(dictJob)
            # Archiviazione
                if sResult=="": sResult=self.Arc_Archive(sResult)
    # Uscita
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        self.sResult=sResult
        return sResult

# Sottofunzione di Job.End, cerca jobs.end. se lo trova
    def End_Archive(self, sPathInboxJ):
        sProc="Job.End.Arc"
        sResult=""

    # Ricerca jobs.end
        lResult=nlSys.NF_PathNormal(sPathInboxJ)
        if sResult=="":
            sPathInboxA=nlSys.NF_PathMake("_" + lResult[1])
            sResult=nlSys.NF_FileRename(sPathJobxJ,sPathInboxA)

    # Uscita
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        self.sResult=sResult
        return sResult

# AZIONE: Start NC_Jobs
# Ritorna sResult e self.sResult
# -----------------------------------------------------
    def cmd_Start(self, dictParams):
        sProc="JOBS.START"

# Lettura INI
        sResult=self.INI_Read()

# Inizializzazioni dopo INI Read

# Ritorno
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        sResult=objLog.Log("NJOS Start: " +  sResult, cat="NJOS")
        return sResult

# AZIONE: Ciclo Get -> Exec -> Return -> Archive
# -----------------------------------------------------
    def cmd_Loop(self, dictParams):
        sProc="JOBS.LOOP"
        sResult=""
# Log
        sResult=objLog.Log("NJOS Start: " +  sResult, cat="NJOS")

# Inizio Loop
        while bExit==False:

# Prende Jobs Nuovi Nelle Cloud e copia in INBOX su cartelle dedicate al JOB
            sResult=self.cmd_Get()
            if sResult != "":
                bExit=True
                break
            nlSys.NF_Wait(JOBS_WAIT_STD)

# Esegue Processi in INBOX accumulati
            sResult=self.cmd_Exec()
            if sResult != "":
                bExit=True
                break
            nlSys.NF_Wait(JOBS_WAIT_STD)

# Verifica se ci sono processi conclusi
            sResult=self.cmd_End()
            if sResult != "":
                bExit=True
                break
            nlSys.NF_Wait(JOBS_WAIT_STD)

# Return
            sResult=self.cmd_Return()
            if sResult != "":
                bExit=True
                break
            nlSys.NF_Wait(JOBS_WAIT_STD)

# Archiviazione
            sResult=self.cmd_Archive()
            if sResult != "":
                bExit=True
                break
            nlSys.NF_Wait(JOBS_WAIT_STD)

# Uscita da motore ntJobs
            sResult=self.Quit()
            if sResult != "":
                bExit=True
                break

# Uscita
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        self.sResult=sResult
        return sResult

# AZIONE: Quit
# -----------------------------------------------------
    def cmd_Quit(self):
        sProc="JOBS.QUIT"
        sResult=""
# Log
        sResult=objLog.Log("NJOS Quit: " +  sResult, cat="NJOS")

# Scrive File Quit
        sFileJobQuit=nlSys.NF_PathMake(self.jData.sSys_Path,"jobs","end")
        sResult=nlSys.NF_FileWrite(sFileJobQuit,"Quit")

# Uscita
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        self.sResult=sResult
        return sResult


# AZIONE: Restart
# -----------------------------------------------------
    def cmd_Restart(self):
        sProc="JOBS.RESTART"
        sResult=""
# Log
        sResult=objLog.Log("NJOS Restart: " +  sResult, cat="NJOS")

# Scrive File Restart per batch che lo esegue
        sFileJobRestart=nlSys.NF_PathMake(self.jData.sSys_Path,"jobs","restart")
        sResult=nlSys.NF_FileWrite(sFileJobRestart,"Restart")

# Scrive File Quit
        if sResult=="": sResult=self.cmd_Quit()

# Uscita
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        self.sResult=sResult
        return sResult

    # Ritorno MAIL ed eventuale LOG
# -----------------------------------------------------------------------------
    def cmd_Return(self, dictReturn):
        sProc="Jobs.Return"
        sResult=""

    # Parametri
        sUser=dictReturn["USER"]
        sType=dictReturn["TYPE"]
        sJobID=dictReturn["JOBID"]
        sPath=dictReturn["JOBFILE"]
        sReturn=dictReturn["RESULT"]

        if sType=="A":
            sSubject="Completamento Job: " + sJobID
            sBody = sSubject + ", archiviato job."
        else:
            sSubject="Errore lettura job in file " + sPath
            sBody = sSubject + "\n" + sReturn

    # Invia Mail
        sResult=self.Jobs_Mail_Init()
        if sResult=="":
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
# 1: Cerca in Inbox se ci sono jobs da eseguire
# 2: Se trova jobs.end rinomina cartella con "_" davanti per indicare che è da archiviare
# -------------------------------------------------------------------------------------------------------
    def cmd_End(self):
        sProc="Job.End"
        sResult=""

# Prende Inbox Path e ed
        lResult=self.Jobs_Find("E")
        sResult=lResult[0]

# Cancellazione e Rinomina
        if sResult=="":
            asPathInboxJ=lResult[1]
            for sPathInBoxJ in asPathInbox:
                sResult=nlSys.NF_StrAppendExt(sResult,self.End_Archive(sPathInboxJ))
# Uscita
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        return sResult