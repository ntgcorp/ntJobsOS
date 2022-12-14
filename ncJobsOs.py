#
# CLASSE Jobs Orchestratore. Gestisce Users e dati correlati, Actions e dati correlati
# Fasi:
# 1: Legge USERS
# 2: Legge ACTIONS
# 3: Legge Groups
# 4: Legge CONFIG (comune a tutti gli scripts JOBS) - A differenza degli altri è un dict non un Table
# 5: Genera lista PATHS/CANALI da ricercare
# ---- Actions ----
# __init__: Inizializzazione
# Get: Cerca jobs nei folders e sposta in Inbox
# Exec: Esegue Jobs
# End: Trova quelli finiti
# Archive: Ritorna risultati Jobs & Archiviazione del Job da Inbox in Archive
# -----------------------------------------------------------------------------

# Per Wait ed altro
import ntSys, ntDataFiles, ntTableClass, os, subprocess
from ntJobsApp import NC_Sys
from ntDataFiles import NC_CSV
# Per Mail di partenza
from ntMailClass import NC_Mail
# Test Mode
NT_ENV_TEST_JOBS=True

# ----------------------------- CLASSI ---------------------------
# ntJobs System Class APP + LOGF
# ID dictUsers="ID"(id_utente), dictActions=ID(idAction). Poi Array con camp
class NC_Jobs:
# Classe Appliczione ntJobs.App
    jData=None
# Risultato ultima elaborazione
    sResult=""
# File INI jobs.ini letto (che può contenere più jobs) compreso [CONFIG] di login ed altro
    dictJobsINI={}
# Job Singolo
    dictJob={}
# Paths da Leggere
    dictPaths=dict()
# Tabelle CSV da leggere
    asCSV=["CONFIG","ACTION","USERS","GROUPS"]
# Oggetto Mail di ritorno
    objMail=None
# Tabelle Dati Jobs
    asFMT_JOBS_USERS=("USER_ID","USER_PASSWORD","USER_NAME","USER_NOTES","USER_GROUPS","USER_PATHS","USER_RMAIL","USER_ACTIONS")
    asFMT_JOBS_GROUPS=("GROUP_ID","GROUP_NAME","GROUP_NOTES")
    asFMT_JOBS_ACTIONS=("ACTION_ID","ACTION_NAME","ACTION_GROUPS","ACTION_SCRIPT","ACTION_ENABLED","ACTION_PATH","ACTION_ORDER","ACTION_TIPS","ACTION_HELP")
    asFMT_JOBS_CONFIG=("ADMIN.EMAIL","SMTP.AUTH","SMTP.FROM","SMTP.PASSWORD","SMTP.PORT","SMTP.SERVER","SMTP.SSL","SMTP.TLS","SMTP.USER","NTJOBS.VER")
# Tabelle di supporto, ID Tabelle, Array Chiavi Rapide
    asUsers=[]
    asActions=[]
    asGroups=[]
    asConfig=[]
    asPath=[]
    JOB_DAT_INI=0
    JOB_DAT_ACT=1
    JOB_DAT_USR=2
    JOB_DAT_USG=3
    tabData[self.JOB_DAT_INI]={}
    tabData[self.JOB_DAT_ACT]=NC_Table()
    tabData[self.JOB_DAT_USR]=NC_Table()
    tabData[self.JOB_DAT_USG]=NC_Table()

# Init
# ------------------------------------------------------------------------------------------------------------
    def __init__(self):
        self.jData=NC_Sys("NTJOBS")
        self.sResult=self.INI_Read()
        if (self.sResult==""): self.sResult=self.Paths()

# Quit: Chiusura motore Jobs se presente jobs.end (che viene cancellato)
# --------------------------------------------------------------------
    def Quit(self):
        sFileJobEnd=ntSys.NF_PathMake(self.jData.sSys_Path,"jobs","end")
        bResult=ntSys.NF_FileExist(sFileJobend)
        return bResult

# Legge DATI di partenza, config.ini, users.csv, actions.csv
# --------------------------------------------------------------------
    def INI_Read(self):
        sProc="JOBS.INI.Read"
        sResult=""
        objCSV=NC_CSV()

        # Lettura DATI
        for nIndex in range(0,ntSys.NF_DictLen(self.asCSV)-1):

        # NomeFile e Normalizzazione
            sFile="Data/ntjobs_" + asCSV[nIndex] + ".csv"
            lResult=ntSys.NF_PathNormal(sFile)
            sResult=lResult[0]
            if sResult=="": sResult=ntSys.NF_FileExistErr(lResult[1])

        # Lettura INI o CSV =dict Interno
            if sResult=="":
                sFile=lResult[1]
                ntSys.NF_DebugFase(NT_ENV_TEST_JOBS, "Legge ntJobs config " + sFile, sProc)
                if nIndex==self.JOB_DAT_INI:
                    lResult=ntDataFiles.NF_INI_Read(sFile)
                    sResult=lResult[0]
                    self.tabData[nIndex]=lResult[1].copy()
                else:
                    sResult=objCSV.Read(sFile)
                    if sResult=="": self.tabData[nIndex]=lResult[1].copy()

        # Aggiorna Tabelle
        if sResult=="":
            asUsers=self.Users()
            asActions=self.Actions()
            asGroups=self.Groups()
            asConfig=self.Configs()

        # Uscita
        sResult=ntSys.NF_ErrorProc(sResult, sProc)
        self.sResult=sResult
        return sResult

# Users/Groups/Actions/Configs
# --------------------------------------------------------------------
    def Users(self):
        asResult=self.tabData[JOB_DAT_USR].GetCol("USER_NAME")
        return asResult

    def Configs(self):
        asResult=ntSys.NF_DictKeys(self.tabData[JOB_DAT_INI])
        return asResult

    def Groups(self):
        asResult=self.tabData[JOB_DAT_USG].GetCol("GROUP_NAME")
        return asResult

    def Actions(self):
        asResult=self.tabData[JOB_DAT_ACT].GetCol("ACTION_NAME")
        return asResult

# Prende Azioni ADP per utente
# Ritorna: Array[] o riempito
# --------------------------------------------------------------------
    def Actions_UserAdp(self, sUser):
        asActions=[]
        for sAction in self.Actions():
            dictAction=self.Action_Get(sAction)
            asUsers=dictAction["ACTION_USERS"]
            for sUser in asUsers:
                if ntSys.NF_ArrayFind(asUsers,sUser)==-1: asActions.append(sUser)
        return Actions

# Prende informazioni utente.
# Ritorna: sResult, dictUser(o EmptyDict)
# --------------------------------------------------------------------
    def User_Get(self, sUser):
        sProc="JOBS.USER.GET"
        dictUser={}

    # Ricerca utente
        if ntSys.NF_ArrayFind(self.asUsers,sUser)==-1:
            sResult="User not found " + sUser
        else:
            dictUser["USER"]=self.Jobs_TabDato(JOBS_CFG, "USER_ID", sUser, "USER_PASSWORD")
        # Grouppi utente
            sGroups=self.Jobs_TabDato(JOBS_CFG, "USER_ID", sUser, "USER_GROUPS")
            asGroups=ntSys.NF_StrSplitKeys(sGroup)
            dictUser["GROUPS"]=asGroups
        # Azioni concesse utente (ad personam)
            sUserActions=self.Actions_UserAdp(sUser)
        # Azioni concesse utente (per gruppi di appartenenza)
            asActions2=Groups_Actions(asGroups)
            asActions=ntSys.NF_ArrayAppend(asActions,asActions2)
            dictUser["ACTIONS"]=asActions
        # Uscita
        sResult=ntSys.NF_ErrorProc(sResult, sProc)
        return sResult

# Prende Azioni da lista gruppi
# Ritorna Array[] o lista di tutte le azioni concesse in base a asGroups. Se non specificato, allora tutti i gruppi
# --------------------------------------------------------------------

# Prende Azioni da lista gruppi
# Ritorna Array[] o lista di tutte le azioni concesse in base a asGroups. Se non specificato, allora tutti i gruppi
# --------------------------------------------------------------------
    def Groups_Actions(self,asGroups=None):
        asActions=[]
        asGroups_List=[]
    # Gruppi
        asGroups_List=self.Groups
        if asGroups==None: asGroups=asGroups_List.copy()
    # Ciclo di ricerca
        for sGroup in asGroups:
            for sGroup_List in asGroups_List:
                if sGroup==sGroup_List: asActions.append(sGroup_List)
    # Ritorno
        return asActions

# Creazione path da esplorare
# Dato Array di Paths divisi da ",", vengono splittati ed aggiunti ad Array finale, togliendo gli spazi
# Per gestire il ritorno di errori legati al path viene creato un dict ed associato lo user
# --------------------------------------------------------------------
    def Paths(self):
        asPaths=self.tabData[JOB_DAT_USR].GetCol("USER_PATHS")

    # Split di tutti i paths e manda su array asResult
        for sTemp in asPath:
        # Split+Norm
            asPaths=sTemp.split(",")
            asPaths=NF_ArrayNorm(asPaths,"LR")
        # Cerca Usser
            nIndex=tabData[JOB_DAT_USR].Index("USER_PATHS",sTemp)
            if nIndex > 0:
                sUser=tabData[JOB_DAT_USR].GetValue(nIndex, "USER_ID")
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
        for sPath in ntSys.NF_DictKeys(self.dictPaths):
        # Prende utente associato al path
            sUser=self.dictPaths[sPath]
        # Lista dei files jobs*.ini
            lResult=self.Jobs_Find(sPath,"J")
            sResult=lResult[0]
        # Per tutti i files JOBS*.INI del path trovato, salvo errore
            if sResult=="":
                asFiles=lResult[1]
                nFiles=NF_ArrayLen(asFiles)
            # Se Trovato almeno 1
                if nFiles>0:
            # Legge INI e Sposta File o ritorno MAIL
                    for sFile in asFiles:
                        sResultGet=self.Get_Move(sFile)
                        if sResultGet != "":
                            dictReturn={"USER": sUser, "RESULT": sResult, "JOBFILE": sFile, "TYPE": "G"}
                            self.Jobs_Return(dictReturn)

        # Uscita
        sResult=ntSys.NF_ErrorProc(sResult, sProc)
        self.sResult=sResult
        return sResult

# Prende da JOBS.INI informazioni di login utente
# -----------------------------------------------------------------------------
    def Jobs_GetUser():
        sUser=self.dictJobs["CONFIG"]["USER"]
        sPwd=self.dictJobs["CONFIG"]["PASSWORD"]
        return sUser, sPwd

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
            asKeys=ntSys.NF_DictKeys(self.dictJob)
            for sKey in asKeys:
            # Se lo trova, lo estra, lo Normalizza e lo aggiunge ai file Extra
                if ntSys.NF_StrSearch("FILE.",sKey,-1):
                    asFileExtra=self.dictJob(sKey)
                    lResult=ntSys.NF_PathNormal(asFileExtra)
                    sFileExtra=lResult[1]
                    asFilesJob.append(sFileExtra)
            # Aggiunge File Jobs
            self.asFilesJob.Append(sFileJob)
    # Uscita
        sResult=ntSys.NF_ErrorProc(sResult, sProc)
        return sResult

# Sposta i files di un job in cartella Inbox\JOB_ID
# Path: Cartella da spostare dove ci deve essere almeno un file jobs.ini ma ci sono anche più jobs
# Importante ci siano anche i files associati o il processo viene bloccato
# -----------------------------------------------------------------------------
    def Jobs_Move(self, dictJob):
        sProc="JOBS.MOVE"
        sResult=""

    # Estrae
        sPath=dictJob["JOBFILE"]
        if ntSys.NF_NullToStr(sPath)=="": sResult="job.ini non specificato"

    # Estrae Job. Toglie "_" che identifica finito
        lResult=ntSys.NF_PathScompose(sPath)
        sJobID_in=lResult[1]
        sJobPath_in=lResult[1]

    # Lista files da spostare
        if sResult=="":
            asFiles=[sPath]
            for sKey in ntSys.NF_DictKeys(dictJob):
                if ntSys.NF_StrSearch(-1,sKey,"FILE."):
                    sFileToMove=ntSys.NF_PathMake(self.sInbox,dictJob[sKey],"")
                    asFiles.append(sFileToMove)

    # Verifica esisgtenza, se non esistono tutti NON PROSEGUE
            for sFile in asFiles:
                if ntSys.NF_FileExist(sFile)==False: sResult=NF_StrAppendExt(sResult, "not.exist=" + sFile, ",")

    # Creazione Folder + Spostamento files
            if sResult=="":
            # Crea Folder
                sJobID_out=ntSys.NF_TS_Now()
                sPathJob_out=ntSys.NF_PathMake(self.sInbox,sJobID_out)
                sResult=os.makedir(sPathJob)
            # Se creato folder, sposta file
                if sResult=="":
                    for sFile in asFiles:
                        lResult=ntSys.NF_PathScompose(sFile)
                        sFileOut=ntSys.NF_PathMake(self.sInbox, lResult[1], lResult[2])
                        sResult=os.move(sFile,sPathJob_Out)
    # Uscita
        sResult=ntSys.NF_ErrorProc(sResult, sProc)
        return sResult

# Job.Vars sostituzione
# -----------------------------------------------------------------------------
    def Jobs_Vars(sText):
        sText=ntSys.NF_StrReplaceDict(sText,self.dictVars)
        return sText

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
                    sResult=self.Exec_Verify(self)
                else:
                   self.Jobs_End(sFind)
            # Login Utente
                if sResult=="": sResult=self.Exec_Login(self)
            # Esecuzione
                if sResult=="": sResult=self.Exec_Run(self)

    # Uscita
        sResult=ntSys.NF_ErrorProc(sResult, sProc)
        return sResult

# Verifica dictJob se le informazioni sono corrette (user,password,action)
# -----------------------------------------------------------------------------
    def Exec_Verify(self):
        sProc="JOBS.EXEC.VERIFY"
        sResult=""

# Prametri utente
        sJob_User=self.dictJob["USER"]
        sJob_Pwd=self.dictJob["PASSWORD"]
        sJob_Action=self.dictJob["ACTION"]

# Verifica utente password
        sUser,dictUser=self.User_Get(sJob_User)
        if sResult=="":
            if sJob_Pwd != dictUser["PASSWORD"]: sResult="User " + sUser + " password invalid"

# Verifica che JOB sia tra quelli concessi al gruppo dell'utente
        if sResult=="":
            if ntSys.NF_ArrayFind(self.asActions,Job_sAction)==-1:
                sResult="Action " + sJob_Action  + " not permitted for user: " + sJob_User
# Uscita
        sResult=ntSys.NF_ErrorProc(sResult, sProc)
        return sResult

# Esecuzione Jobs del file ini
# -----------------------------------------------------------------------------
# asFMT_JOBS_ACTIONS=("ACTION_ID","ACTION_NAME","ACTION_GROUPS","ACTION_SCRIPT","ACTION_ENABLED","ACTION_PATH","ACTION_ORDER","ACTION_TIPS","ACTION_HELP")
    def Exec_Run(self):
        sProc="Jobs.Exec.Run"
        sResult=""

    # Parametri
        sJob_Action=self.dictJob["ACTION"]
        dictAction=self.Action_Get(sJob_Action)
        sAction_Path=self.dictJob["ACTION_PATH"]
        sAction_Script=self.dictJob["ACTION_SCRIPT"]

    # Cambio Script con Parametri
        sAction_Script=Jobs_Var(sAction_Script)

    # Cambio path
        if sAction_Path != "": os.chdir(sAction_Path)

    # Esecuzione
        sResult=ntSys.NF_Exec(sAction_Script)

    # Uscita
        sResult=ntSys.NF_ErrorProc(sResult, sProc)
        return sResult

# Creazione file jobs.End
# -----------------------------------------------------------------------------

    def Jobs_End(self, sFileJobs, sStatus):
        sProc="Jobs.End"

    # Crea jobs.end
        lResult=ntSys.NF_PathScompose(sFileJobs)
        sFileEnd=ntSys.NF_PathMake(lResult[1],"jobs","end")
        sStrDictReturn=ntSys.NF_DictPrintToINI(self.dictReturn=
        sResult=ntSys.NF_FileWrite(sFileEnd, sStrDictReturn)

    # Uscita
        sResult=ntSys.NF_ErrorProc(sResult, sProc)
        return sResult

# Archive & Return
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
        sResult=ntSys.NF_ErrorProc(sResult, sProc)
        self.sResult=sResult
        return sResult

# Cerca Cartelle Job con caratteristiche - Ritorna lResult. Se 0=ERROR, 1=Lista path jobs da arhiviare
# Type="A"= DaArchiviare, "J": Da Eseguire
# -----------------------------------------------------------------------------
    def Jobs_Find(self, sType="J"):
        sProc="Jobs.Arc.Return"
        asResult=[]

    # Prende Inbox
        sPathInbox=self.Config("INBOX")
        sPathInboxJ=ntSys.NF_PathMake(sPathInboxJ,"jobs*","")
        sResult=ntSys.NF_FileExistsErr(sPathInbox)

    # Cerca Path da archiviare. Solo Folder non ricorsivo
        if sType=="A":
            sPath="_" + sPath
        lResult=ntSys.NF_PathFind(sPath,"DN")

    # Uscita
        return lResult

# Archiviazione Jobs Finiti
# -----------------------------------------------------------------------------
    def Jobs_Archive(self):
        sProc="Jobs.Arc"
        sResult=""

    # Muove Files
        sResult=ntSys.NF_FolderMove(sPath, sFolderArc)

    # Uscita
        return sResult

# Estrae Dato da Tabelle
# -----------------------------------------------------------------------------
    def Jobs_TabDato(self, nID_TAB, sKey, sKeyValue, sField):
        objTable=NC_Table()
        objTable=self.tabData[nID_TAB]
        objTable.

# Ritorno MAIL ed eventuale LOG
# -----------------------------------------------------------------------------
    def Jobs_Return(self, dictReturn):
        sProc="Jobs.Return"
        sResult=""

    # Parametri
        sUser=dictReturn["USER"]
        sType==dictReturn["TYPE"]
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
        return sResult

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
        sResult=ntSys.NF_ErrorProc(sResult, sProc)
        self.sResult=sResult
        return sResult

# Prende Config Diretto da TabConfig (che è un dictionary)
# -----------------------------------------------------------------------------
    def Config(self, sKey):
        if ntSys.NF_ArrayFind(sKey,self.asConfig)>-1:
            vValue=self.tabData[JOB_DAT_INI][sKey]
        return vValue

# End Action
# 1: Se trova jobs.end rinomina cartella con "_" davanti per indicare che è da archiviare
# -------------------------------------------------------------------------------------------------------
    def End(self):
        sProc="Job.End"
        sResult=""

    # Cerca in Inbox se ci sono jobs.end tra i jobs presenti in esecuzione
        lResult=self.Jobs_Find("E")
        sResult=lResult[0]

    # Cancellazione jobs.end e Rinomina cartella con "_" davanti (Archive)
        if sResult=="":
            asPathInboxJ=lResult[1]
            for sPathInBoxJ in asPathInbox:
                sResult=ntSys.NF_StrAppendExt(sResult,End_Archive(sPathInboxJ))

    # Uscita
        sResult=ntSys.NF_ErrorProc(sResult, sProc)
        return sResult

# Sottofunzione di Job.End, Rinomina Path in Archiviazione ("_")
    def End_Archive(self, sPathInboxJ):
        sProc="Job.End.Arc"
        sResult=""

    # Ricerca jobs.end
        lResult=ntSys.NF_PathNormal(sPathInboxJ)
        if sResult=="":
            sPathInboxA=ntSys.NF_PathMake("_" + lResult[1])
            sResult=ntSys.NF_FileRename(sPathJobxJ,sPathInboxA)

    # Uscita
        sResult=ntSys.NF_ErrorProc(sResult, sProc)
        return sResult
