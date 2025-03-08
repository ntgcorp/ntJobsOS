# ntJobs DB DATA LIBRARY
# Lib  gestione file .IN, CSV, Altri Database (per Excel/CSV usare NC_Panda)
# -----------------------------------------------------------------------------
import nlSys
import mariadb

# DA COMPLETARE
# DATABASE - Con unica interfaccia di accesso sqLite3, MariaDB/MySql
# -----------------------------------------------------------------------------------------
# DB(DATABASE) CLASS
class NC_DB:
# Dati
    sFileDB=""                     # Nome file DB o Nome del DB
    sTypeDB=""                     # SQLT3, MARIADB, ODBC
    dictSchema={}                  # NON USATO PER ORA
    sConnectDB=""                  # ODBC CONNECT STRING
    objDB=None					   # DB OBJECT
    objCursor=None                 # CURSOR OBJECT
    dictConnect=None               # Altri parametri connessione
    sResult=""					   # DB Status

# -------------- METODI --------------
# Type= SQLT/"", MARIADB
# File=Nome file
# dictParams: AltriParametri di connect (user,pwd,host,port)
    def __init__(self, sType, sFile, dictParams={}):
        sResult=""
        sProc="DB.INI"
        pass

    # Connect & Check Parametri
        if self.sTypeDB=="SQLT":
            import sqlite3
            try:
                self.objDB=sqlite3.connect(self.sFileDB)
            except:
                sResult="SqLite3 error connect"
    # SQLT. Cursor
            if sResult=="":
                try:
                    self.objCursor=self.objDB.cursor()
                except:
                    sResult="SqLite3 error cursor"
        elif self.sTypeDB=="MARIADB":
            import mariadb
            try:
                self.objDB=mariadb.connect(
                    user=dictParams["user"],
                    password=dictParams["pwd"],
                    host=dictParams["host"],
                    port=dictParams["port"],
                    database=sFile)
                self.dictConnect=dictParams.copy()
            except mariadb.Error as e:
                sResult=str(e)
        # Cursor
            if sResult=="":
                try:
                    self.objCursor=self.objDB.cursor()
                except:
                    sResult="MariaDB error cursor"

# Uscita
        self.sResult=sResult

# Close DB
# --------------------------------------------------------------------------------------
    def Close(self):
        sProc="DB.Close"
        sResult=""

    # Close
        try:
            self.objDB.close()
            self.objDB=None
            self.objCursor=None
        except:
            sResult="Close DB"

    # Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)

# ExecuteSQL
# DA VERIFICARE
# Parametri: Stringa o Array/list) di SQL
# Ritorno: sResult
# --------------------------------------------------------------------------------------
    def NF_ExecuteSql(self, avSQLparam):
        sProc="ExecuteSQL"
        sResult=""
        sSQL=""
        avSQL

    # Check & Array To Execute
        if nlSys.NF_IsArray(avSQLparam)==False:
            avSQL=[avSQLparam]

    # Esecuzione - Uscita al primo errore
        if sResult=="":
            for sSQL in avSQL:
                sSQL=str(sSQL)
                try:
                    self.objCursor.execute(sSQL)
                except mariadb.Error as e:
                    sResult=str(e)
                    break

    # Commit
        if sResult=="":
            try:
                self.objCursor.execute(sSQL)
            except mariadb.Error as e:
                    sResult=str(e)

    # Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)

# ReadQuery()
# DA VERIFICARE
# Parametri:
# 	sSQL: Query SQL da leggere
# Ritorno:
#   lResult
# --------------------------------------------------------------------------------------
    def NF_DbfReadQuery(self, sSqlParam):
        lResult=[]
        sResult=""
        sProc="DbfReadQuery"
        sSQL=""

# Db Opened
        sResult==self.OpenDb()

# Read Query
        if sResult=="":
            sSQL=str(sSqlParam)
            try:
                rows = self.objCursor.execute(sSQL).fetchall()
            except:
                sResult="Error Read Query " + sSQL

# Uscita
        return nlSys.NF_Result(sResult,sProc,rows)

# DA VERIFICARE
# Ritorno:
#   sResult
# --------------------------------------------------------------------------------------
    def OpenDb(self):
        sResult=""
        if self.objDb==None: sResult="DB not opened " + str(self.sFile)
        return sResult