#-------------------------------------------------------------------------------
# Name:        ncDB
# Uso:
# 1: Chiamare la OpenDb con type=tipodb, obbligaotorio ed altri parametri in base al tipo di parametro
# 2: Chiamare SqlExec o SqlExec2 per query con sostituzione di parametri
# 3: CloseDb() per chiudere DB
# 4: Se si utilizza query da tabella occorre avere prima caricato tabella query per esecuzione
# 5: TableLoad o TableSave per salvare tabella in memoria su engine
#-------------------------------------------------------------------------------

# IN PREPARAZIONE. MODULO DI INTERFACCIA MULTI DATABASE

# Interface to Panda with debug & errors management
# -----------------------------------------------------------------------
import nlSys
import ncTable

# Engine caricate
NT_ENV_DBENG_SQLITE3=False
NT_ENV_DBENG_ORACLE=False
NT_ENV_DBENG_GOOBQRY=False
NT_ENV_DBENG_MARIADB=False

# Tabella DB.Exec
NT_ENV_DBEXEC_FIELDS=[""]
NT_ENV_DBEXEC_TABLE=NC_Table(NT_ENV_DBEXEC_FIELDS,"ID")

# ----------------------- CLASSI ---------------------------
# PANDA_XLS Class
# For Excel Object
class NC_DB(**kwargs):
    sType=""
    objDb=None
    bOpen=False
    sFilename=""
    sUser=""
    sPwd=""
    sHost=""
    sOther=""
    dictTableExec={}        # Tabella Stringhe SQL
    dictTable={}            # Tabelle caricate in memoria come dict

# -------------- METODI --------------
    def __init__(self):
        pass


# Alias OpenDb
    def Init(self, **kwargs):
        return self.OpenDb(**kwargs):

# Apertura DB
    def OpenDb(self, **kwargs):
        sResult=""
        sProc="DB.OPEN"

# Parametri
#   sType(type)=sqlite3, ....
#   sFilename(name)=Filename o NameDb
#   sUser(user)
#   sPwd(pwd)
#   sHost(host)
#   sOher(other)

# Argomenti opzionali
        for key, value in kwargs.items():
            if key=='type':
                self.sType=value
                self.bInit=True
            elif key=='user':
                self.sUser=value
            elif key=='name':
                self.sFilename=value
            elif key=='pwd':
                self.sPwd=value
            elif key=='host':
                self.sHost=value
            elif key=='other':
                self.sOther=value
            else:
                sResult="Parameter invalid " + key

# Init DB Engine - CARICATA UNA VOLTA SOLA
        if sResult=="":
            if self.sType=="sqlite3":
                if NT_ENV_DBENG_SQLITE3==False:
                    import sqlite3
                    NT_ENV_DBENG_SQLITE3=True
                try:
                    sqlite3.connect(self.sFilename)
                except Exception as e:
                    sResult=getattr(e, 'message', repr(e)) + "Errore DB "
            elif self.sType=="goo_bqry":
                if NT_ENV_DBENG_GOOBQRY==False:
                    from google.cloud import bigquery
                    NT_ENV_DBENG_GOOBQRY=True
                try:
                    self.objDb = bigquery.Client()
                except Exception as e:
                    sResult=getattr(e, 'message', repr(e)) + "Errore DB "
            elif self.sType=="oracle":
                if NT_ENV_DBENG_ORACLE==False:
                    import oracledb
                    NT_ENV_DBENG_ORACLE=True
                try:
                    self.objDb = oracledb.connect(
                        user=self.sUser,
                        password=self.sPwd,
                        dsn=self.sOther)
                    self.objDb.cursor()
                except Exception as e:
                    sResult=getattr(e, 'message', repr(e)) + "Errore DB "
            else:
                sResult="DB Type null"
# Uscita
       return nlSys.NF_ErrorProc(sResult,sProc)

# Chiude Connessione
# ------------------------------------------------------------------------------
    def CloseDb(self):
        sProc="DB.SQLEXEC"
        sResult=""

# Verifica
        if self.bOpen==False:
            sResult="Db not open"

# Reset Tabelle caricate
        if sResult=="":
            self.dictTable={}

# Uscita
       return nlSys.NF_ErrorProc(sResult,sProc)

# Esegue Stringa SQL
# ------------------------------------------------------------------------------
    def SqlExec(self,sSQL):
        sProc="DB.SQLEXEC"
        sResult=""

# Init DB Engine - CARICATA UNA VOLTA SOLA
        if self.sType=="sqlite3":
            try:
                sqlite3.connect(self.sFilename)
            except Exception as e:
                sResult=getattr(e, 'message', repr(e)) + "Errore DB "
        elif self.sType=="goo_bqry":
            try:
                self.objDb = bigquery.Client()
            except Exception as e:
                sResult=getattr(e, 'message', repr(e)) + "Errore DB "
        elif self.sType=="oracle":
            try:
                self.objDb = oracledb.connect(
                    user=self.sUser,
                    password=self.sPwd,
                    dsn=self.sOther)
                self.objDb.cursor()
            except Exception as e:
                sResult=getattr(e, 'message', repr(e)) + "Errore DB "
        else:
            sResult="DB Type null"
# Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)

# Esegue Stringa SQL in modalità estesa
# sqL=singolo
# sql_list=insieme da eseguire
# vars=dictData da sostituire per ogni variabile
# ------------------------------------------------------------------------------
    def SqlExec2(self,**kwargs):
        sProc="DB.SQLEXEC2"
        sResult=""
        asSQL=[]
        sSQL=""
        dictData={}
        nItems=0

# Argomenti opzionali
        for key, value in kwargs.items():
            if key=='sql':
                sSQL=value
            elif key=='sql_list':
                asSQL=value
            elif key=='vars':
                dictData={}
            else:
                sResult="Parameter invalid " + key

# Costruzione Lista degli SQL (1 o tanti)
        if sResult=="":
            if (len(asSQL)==0) and (len()>0):
                asSQL=[sSQL]
                sSQL=""
                nItems=len(asSQL)
# Items Null
            if nItems==0: sResult="List SQL to Exec empty"

# Parte 1: Change multiplo variabili (per diagnostica diviso in 2 parti)
        for nIndex in range(nItems):
            sSQL=nlSys.NF_StrReplaceDict(asSQL[nIndex],dictData)
            asSQL[nIndex]=sSQL
# Parte 2: Exec multiplo - Con Log - Memorizza almeno uno degli errori per uscita ma tutto nei log con ID davanti da 0 a n
        if sResult=="":
            for nIndex in range(nItems):
                sResult2=self.SqlExec(sSQL)
                sTemp=str(nIndex) & ": " & sResult2
                if sResult2 != "": sResult=sTemp
                asLog[nIndex]=sTemp
# Uscita
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        lResult=[sSQL,asLog]

# Esegue Stringa SQL da Tabella
# DA FARE
# Parametri: id=, group= (o GROUP o ID)
# Ritorno: lResult:
#    0: sResult ultimo
#    1: Log Esecuzioni. 0..N

# ------------------------------------------------------------------------------
    def SqlTableExec(self,**kwargs):
        sProc="DB.TABLE.EXEC"
        sResult=""
        sID=""
        sGroup=""

# Argomenti opzionali
        for key, value in kwargs.items():
            if key=='id':
                sID=value
            elif key=='group':
                sGroup=""
            else:
                sResult="Parameter invalid " + key

# Verifica Exec non caricati
        if NT_ENV_DBEXEC_TABLE.len()==0:
            sResult="Tabella Sql non caricata"

# Ricerca ID o GROUP
        if sResult=="":
            pass

# Se singolo Id crea lista con solo quello
        if (sResult=="") and (sID != ""):
            asExec=[sId]

# Ricerca Esistenza tutte le ID
        if sResult=="":
            pass

# Caricamento di tutti SQL
        if sResult=="":
            pass

# Estrazione Query
        if sResult=="":
            for sID in asID:
                lResult=NT_ENV_DBEXEC_TABLE.GetRecordDict("ID",sID)
                sResult=lResult[0]
                if sResult=="":
                    sSQL=lResult[1]
                    dictSQL.append(sID,sSQL)


# Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)

# Carica Tabella da Query in dictionary
# DA FARE
# ------------------------------------------------------------------------------
    def SqlTablLoad(self,**kwargs):
        sProc="DB.TABLE.LOAD"
        sResult=""

# Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)

# Salva Tabella su Query
# DA FARE
# ------------------------------------------------------------------------------
    def SqlTablSave(self,**kwargs):
        sProc="DB.TABLE.SAVE"
        sResult=""

# Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)