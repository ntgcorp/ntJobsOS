#-------------------------------------------------------------------------------
# Name:        ncWS
#-------------------------------------------------------------------------------

# IN PREPARAZIONE. MODULO DI INTERFACCIA VARI SERVIZI WEB SERVICE

# Interface to Panda with debug & errors management
# -----------------------------------------------------------------------
import nlSys

# Engine caricate
NT_ENV_WSENG_REQ=False

# ----------------------- CLASSI ---------------------------
# PANDA_XLS Class
# For Excel Object
class NC_WS(**kwargs):
    sType=""
    objWS=None
    bOpen=False
    sFilename=""
    sUser=""
    sPwd=""
    sHost=""
    sOther=""

# -------------- METODI --------------
    def __init__(self, **kwargs):

# Parametri
#   sType(type)=sqlite3, ....
#   sURL(name)=Filename o NameDb
#   sUser(user)
#   sPwd(pwd)
#   sHost(host)
#   sOher(other)

# PER ORA C'è SOLO L'INIT, POI DA IMPLEMENTARE LE ALTRE FUNZIONI

# Init DB Engine - CARICATA UNA VOLTA SOLA
        if sType=="sqlite3":
            if NT_ENV_DBENG_SQLITE3==False:
                import sqlite3
                NT_ENV_DBENG_SQLITE3=True
            try:
                sqlite3.connect(self.sFilename)
            except Exception as e:
                sResult=getattr(e, 'message', repr(e)) + "Errore DB "
        else:
            sResult="DB Type null"
# Ritorno
        nlSys.NF_DebugFase(bDebug,"End: " + sResult,sProc)
        return sResult

# Chiude Connessione
# ------------------------------------------------------------------------------
    def End():
        sProc="WS.END"
        sResult=""

# Uscita
        sResult=nlSys.NF_ErrorProc(sResult,sProc)

# Esegue POST
# ------------------------------------------------------------------------------
    def Post(self,):
        sProc="DB.SQLEXEC"
        sResult=""

# Init DB Engine - CARICATA UNA VOLTA SOLA
        if self.sType=="sqlite3":
            try:
                sqlite3.connect(self.sFilename)
            except Exception as e:
                sResult=getattr(e, 'message', repr(e)) + "Errore DB "
        elif sType=="goo_bqry":
            try:
                self.objDb = bigquery.Client()
            except Exception as e:
                sResult=getattr(e, 'message', repr(e)) + "Errore DB "
        elif sType=="oracle":
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
        sResult=nlSys.NF_ErrorProc(sResult,sProc)

# Esegue Stringa SQL con sostituzione di chiavi
# ------------------------------------------------------------------------------
    def SqlExec2(sSQL,dictData):
        sProc="DB.SQLEXEC2"
        sResult=""

# Uscita
        sResult=nlSys.NF_ErrorProc(sResult,sProc)

# Esegue Stringa SQL da Tabella
# ------------------------------------------------------------------------------
    def SqlTableExec(**kwargs):
        sProc="DB.TABLE.EXEC"
        sResult=""

# Uscita
        sResult=nlSys.NF_ErrorProc(sResult,sProc)

# Carica Tabella da Query
# ------------------------------------------------------------------------------
    def SqlTablLoad(**kwargs):
        sProc="DB.TABLE.LOAD"
        sResult=""

# Uscita
        sResult=nlSys.NF_ErrorProc(sResult,sProc)

# Salva Tabella su Query
# ------------------------------------------------------------------------------
    def SqlTablSave(**kwargs):
        sProc="DB.TABLE.SAVE"
        sResult=""

# Uscita
        sResult=nlSys.NF_ErrorProc(sResult,sProc)