# ntJobs FILE DATA LIBRARY
# Lib  gestione file .IN, CSV, Altri Database (per Excel/CSV usare NC_Panda)
# -----------------------------------------------------------------------------
import nlSys

import configparser, csv, copy
NT_ENV_TEST_DATAF = True
sCSV_DELIMITER = ";"
sCSV_QUOTE = '"'

# INI: Ritorna Sezioni lette come dict di dict in lResult
# Nomefile già normalizzato
# Ritorna lResNF_DictStr: NF_DictExistKey.Key: ['ACTION', 'FILE.PDF', 'FILE.CSV', 'FIELDS.CSV', 'FIELD.KEY', 'FILE.PDF.PREFIX']ult 0=Ritorno, 1=IniDict, dove Trim/UCASE.KEY e valori "trimmati"
# -----------------------------------------------------------------------------
def NF_INI_Read(sFileINI):
    sProc="NF_INI_Read"
    sResult=""
    dictINI=dict()

# Verifica esistenza
    sResult=nlSys.NF_FileExistErr(sFileINI)

# Lettura INI Fase 1
    if sResult=="":
        try:
            config=configparser.ConfigParser(allow_no_value=True)
            config.read(sFileINI)
            asSections=config.sections()
        except:
            sResult="apertura file INI " + sFileINI

# Lettura INI Fase 2
    if (sResult==""):
    # Legge SEZIONE->KEYS, crea dict per ogni sections che aggiunge in dictINI
        for sSection in asSections:
            dictSection=dict()
            #Lettura KEYS
            for sKey in config[sSection]:
                vValue=config[sSection][sKey]
                # La chiave viene Trimmata+UCase
                sKey=nlSys.NF_StrNorm(sKey)
                # Trim Value e Str per sicurezza
                vValue=(str(vValue)).lstrip().rstrip()
                # Assegnazione di ritorno
                dictSection[sKey]=vValue
            # Assegna KEYS a SEZIONE
            nlSys.NF_DebugFase(NT_ENV_TEST_DATAF, ", Tipo dictSection: " + str(type(dictSection)), sProc)
            dictINI[sSection]=dictSection.copy()

# Fine ciclo lettura INI
    sResult=nlSys.NF_ErrorProc(sResult,sProc)
    lResult=[sResult,dictINI]
    #nlSys.NF_DebugFase(NT_ENV_TEST_DATAF, ", dictINI: " + nlSys.NF_DictStr(dictINI), sProc)
    return lResult

# INI: Salva
# Nomefile già normalizzato. SEMPRE IN SCRITTURA. sE UPDATE USARE NF_INI_Update
# Passato in forma dict di dict
# Parametri:
#  sFileINI=File
#  dictINIs=INI doppio livello, sezione->dict
#  sAttr=Attributo scrittura, w/a (non r)
# Ritorna sResult
# -----------------------------------------------------------------------------
def NF_INI_Write(sFileINI, dictINIs, sAttr="w"):
    sProc="NF_INI_Read"
    sResult=""
    sGroup=""

# Verifica
    if (sAttr != "w") and (sAttr != "a"): sResult="Attributo errato: " + sAttr

# Setup
    if sResult=="":
        config = configparser.ConfigParser()
# Per tutte le chiavi. Se inizia per #=Nome Sezione
        for sGroup in nlSys.NF_DictKeys(dictINIs):
            dictINI=dictINIs[sGroup]
            for vKey in nlSys.NF_DictKeys(dictINI):
                if not config.has_section(sGroup): config.add_section(sGroup)
                config.set(sGroup,vKey,dictINI[vKey])

# Salva File
    lResult=nlSys.NF_FileOpen(sFileINI,sAttr)
    sResult=lResult[0]
    if sResult=="":
        hFile=lResult[1]
        config.write(hFile)
    # Chiusura file
        hFile.close()

# Ritorno Scrittura
    sResult=nlSys.NF_ErrorProc(sResult,sProc)
    return sResult

# INI: Update
# Se esiste lo legge e update del dict passato come parametro
# Parametri: sFileINI, dictINIs (con sezione)
# Ritorno: sResult
# -----------------------------------------------------------------------------
def NF_INI_Update(sFileINI, dictINIs_update):
    sProc="NF_INI_Update"
    sResult=""

# Se non Esiste va a INI_Write ed ESCE
    if nlSys.NF_FileExist(sFileINI):
# Legge INI
        lResult=NF_INI_Read(sFileINI)
        sResult=lResult[0]
        if sResult=="":
            dictINIs_read=lResult[1]
        # Merge (del tipo 2o livello)
            dictINIs_read=nlSys.NF_DictMerge2(dictINIs_read, dictINIs_update)
        # Salva dictINI
            sResult=NF_INI_Write(sFileINI, dictINIs_read)
# Ritorno Scrittura
    sResult=nlSys.NF_ErrorProc(sResult,sProc)
    return sResult

# ----------------------- CLASSI ---------------------------
# CSV Class
class NC_CSV:
# Dati
    sFileCSV=""                    # Nome file csv
    dictSchema={}                  # NON USATO PER ORA
    avTable=[]                     # TABELLA DEI DATI. Array Doppio di Record
    asHeader=[]                    # Header Effettivo
    asFields=[]                    # Header Da verificare in caso di lettura
    bTrim=False                    # Trim in Lettura
    sDelimiter=sCSV_DELIMITER      # Delimiter
    sFieldKey=""                   # Campo Chiave. FACOLTATIVO (SE C'E' il ToDict è convertibile in tabella)

# -------------- METODI --------------
    def __init__(self):
        pass

# Read CSV Input in DICT di list. 1,2=Header, 3..N: Record
# Campi di dictParams
# TRIM=True/False, DELIMITER=","(def) FILE.IN=, FILE.OUT
# FIELDS[ucase,trimmto]. Se specificato viene utilizzato come confronto con quello da leggere
# Se CSV_Append viene usato come confronto con quello da appendere
# Il file deve già essere normalizzato
# Ritorna sResult, self.sHeader, self.avTable
# Params: FILE.IN=CSV, FIELDS=Array che ci deve essere, DELIMITER=Delimiter campi, TRIM=Trim Prima e dopo. QUOTE=Campo delimitatore testi
# ---------------------------------------------------------------------------------------
    def Read(self,dictParams):
        sProc="CSV.READ"
        sResult=""

# Legge Parametri
        sResult=nlSys.NF_DictExistKeys(dictParams,("FILE.IN","FIELDS"))
        if sResult=="":
            nlSys.NF_DebugFase(NT_ENV_TEST_DATAF, "Parametri CSV.READ: " + str(dictParams), sProc)
            self.bTrim=nlSys.NF_DictGet(dictParams,"TRIM",False)
            self.sDelimiter=nlSys.NF_DictGet(dictParams,"DELIMITER",sCSV_DELIMITER)
            self.asFields=nlSys.NF_DictGet(dictParams,"FIELDS",[])
            self.sFileCSV=nlSys.NF_DictGet(dictParams,"FILE.IN","")
            self.sFieldKey=nlSys.NF_DictGet(dictParams,"FIELD.KEY","")

# Verifica Header se specificato asFields(FILE.IN)
        if nlSys.NF_ArrayLen(self.asFields)>0: sResult=self.Header()
        print(sProc + ": " + sResult)
        #nlSys.NF_DebugFase(NT_ENV_TEST_DATAF, "CSV.HEADER: " + sResult, sProc)

# Apertura FileCSV + Lettura CSV LIST in tabella dictTable, un record per riga + Chiusura
# Riga zero(numerico) contiene header
        if (sResult==""):
            lResult=nlSys.NF_FileOpen(self.sFileCSV,"r")
            sResult=lResult[0]
            if sResult=="":
                csv_file_in=lResult[1]
        # Setup
                self.nLines=0
                csv_reader = csv.reader(csv_file_in, delimiter=self.sDelimiter)
                self.avTable=[]
                nlSys.NF_DebugFase(NT_ENV_TEST_DATAF, "Letto file CSV: " + self.sFileCSV, sProc)
        # Per N.Righe
                for row in csv_reader:
            # Normalizza Riga
                    asRow=nlSys.NF_ArrayT2L(row)
                    if self.bTrim: asRow=nlSys.NF_ArrayStrNorm(asRow,"LR")
            # Header
                    if (self.Len()==0):
                        nlSys.NF_DebugFase(NT_ENV_TEST_DATAF, f'Column names {", ".join(self.asHeader)}', sProc)
                        self.asHeader=asRow.copy()

                    else:
            # Salva Riga Dati Array
                        print(sProc + ": Legge CSV Riga " + str(self.nLines))
                        self.avTable.append(asRow.copy())
            # Prossima Riga
                    self.nLines+=1


        # Chiue file e fine (toglie header)
                csv_file_in.close()
                nlSys.NF_DebugFase(NT_ENV_TEST_DATAF, "Record Letti CSV: " + str(len(self.avTable)), sProc)
# Fine
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        return sResult

# Legge solo Header CSV. FILE.IN
# Ritorno sResult
# Se FIELDS già avvalorato, allora VERIFICA che l'Header letto corrisponda a quello di FIELD
# FILE.IN deve già essere normalizzato
# ------------------------------------------------------------------------------------------
    def Header(self):
        sProc="CSV.HEADER"
        sResult=""
        self.asHeader=[]
        sHeader=""

# Prende Parametri
        if self.sDelimiter=="" or self.sFileCSV=="": sResult = "Delimiter/File empty"

# Apertura file.in
        if (sResult==""):
            nlSys.NF_DebugFase(NT_ENV_TEST_DATAF, "Recupero header csv file " + self.sFileCSV, sProc)
            lResult=nlSys.NF_FileOpen(self.sFileCSV,"r")
            sResult=lResult[0]
            print("Apertura file csv(0): " + sResult)

# Lettura Riga
        if (sResult==""):
            print("Apertura file csv(1): " + sResult)
            csv_file_in=lResult[1]
            try:
                csv_reader=csv.reader(csv_file_in, delimiter=self.sDelimiter)
            except:
                sResult="Lettura header"
        if (sResult==""):
            self.asHeader=[]
            for row in csv_reader:
                self.asHeader=row
                break
            csv_file_in.close()
            print("Header: " + str(self.asHeader))

# Trim/UCASE Header
        if nlSys.NF_ArrayLen(self.asHeader)>0:
            self.asHeader=nlSys.NF_ArrayStrNorm(self.asHeader,"LRU")
        else:
            sResult="Header non leggibile"

# Verifica Header come previsto uguali o genera stringa di errore
        if sResult=="":
            sResult=nlSys.NF_ArrayCompare(self.asFields, self.asHeader)
        if sResult!="":
            sHeader=sCSV_DELIMITER.join(self.asHeader)
            sFields=sCSV_DELIMITER.join(self.asFields)
            sResult="Header non uguali. Previsto: [" + sFields + "]/ Letto: [" + sHeader + "]"

# Ritorno
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        return sResult

# Append CSV Memory Dictionary in CSV File - Stesso Header
# Ritorna sResult=""=Ok, altrimenti Errore
# Presupporto già letto csv da appendere
# Params: DELIMITER(obbligatorio, FIELDS(obbligatorio), FILE.ADD(obbligatorio)
    def Append(self,dictParams):
        sProc="CSV_APPEND"
        sResult=""
        lResult=[]
        dictAppend={}

# 1: Legge File ADD come CSV_ADD
        sFile=nlSys.NF_DictGet(dictParams,"FILE.IN")
        lResult=nlSys.NF_PathNormal(sFile)
        csv_ADD=NC_CSV()
        dictAppend={"FILE.IN": lResult[5], "FIELDS": dictParams["IN.FIELDS"]}
        sResult=csv_ADD.Read(dictAppend)
# 2: Out. Verifica Header,
        if self.asHeader != csv_ADD.asHeader: sResult="IN/ADD Header diversi"
# 4: Copia IN, aggiunge tabella di ADD
        if sResult=="": nlSys.NF_ArrayAppend(self.avTable,csv_ADD.avTable)
# Ritorno
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        return sResult

# CSV Write Output - READ OR APPEND -
# Per Append di altro dictCSV con stesso Header, utilizzare NF_CSV_Append()
# Ritorno: sResult
# -----------------------------------------------------------------------------
    def Write(self, dictParams):
        sProc="CSV.WRITE"
# Setup
        nLinesWrite=0
# Legge Parametri
        sResult=nlSys.NF_DictExistKeys(dictParams,("FILE.OUT","FIELDS"))
# Verifica Parametri
        if sResult=="":
            self.asHeader=nlSys.NF_DictGet(dictParams,"FIELDS",[])
            self.sDelimiter=nlSys.NF_DictGet(dictParams, "DELIMITER", sCSV_DELIMITER)
            sFileOut=nlSys.NF_DictGet(dictParams,"FILE.OUT","")
            self.avTable=nlSys.NF_DictGet(dictParams,"DATA",[])
            sMode=nlSys.NF_DictGet(dictParams,"MODE","WRITE")
# TEST
        nlSys.NF_DebugFase(NT_ENV_TEST_DATAF, "Righe da esportare: " + str(self.nLines), sProc)
# Scrive File CSV. Lo scrive comunque anche se vuoto
        sModeFile=nlSys.iif(sMode=="APPEND","a","w+")
        lResult=nlSys.NF_FileOpen(sFileOut,sModeFile)
        sResult=lResult[0]
        if sResult=="":
            csv_file_out=lResult[1]
# Scrive Header
            csv_writer = csv.DictWriter(csv_file_out,fieldnames=self.asHeader,delimiter=self.sDelimiter)
            if (sMode=="WRITE"): csv_writer.writeheader()
# Scrive Linee
            for vRow in self.avTable:
# Prende riga da dictionary (la riga è un array str asFMT_MAIL_SDB_HDR)
                csv_writer.writerow(vRow)
                nLinesWrite = nLinesWrite + 1
# Close
        csv_file_out.close()
        print(f'Fine Scrittura file CSV. Record OUT: {nLinesWrite} linee.')
# Fine
        return sResult

# Copia CSV da altro CSV in memoria.
# Ritorno sResult con Eventuali Errori
# Formato dictCSV: FIELDS[Array]=HEADER[Array](letto da csv), DATA=ArrayxRecords, LINES=Record, FIELD.KEY=CampoChiave
# -------------------------------------------------
    def FromDict(self, dictParams):
        sProc="CSV.FromDict"
        sResult=""

        self.asFields=dictParams["FIELDS"]
        self.asHeader=copy.deepcopy(dictParams["HEADER"])
        self.avTable= copy.deepcopy(dictParams["DATA"])
        self.sFileCSV=dictParams["FILE.CSV"]
        self.sFieldKey=dictParams["FIELD.KEY"]

    # Ritorno
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        return sResult


# Converte CSV in DICT per esportazione
# -------------------------------------------------
    def ToDict(self):
        sProc="CSV.ToDict"
        sResult=""
        dictParams={}

    # Verifica
        if nlSys.NF_ArrayLen(self.asHeader)<1: sResult="Header empty"
        if nlSys.NF_ArrayLen(self.avTable)<1: sResult=nlSys.NF_StrAppendExt(sResult,"Data empty")
        if nlSys.NF_ArrayLen(self.avTable)<1: sResult=nlSys.NF_StrAppendExt(sResult,"No File CSV Name")

    # Setup
        if sResult=="":
            dictParams["FIELDS"]=self.asFields
            dictParams["HEADER"]=self.asHeader
            dictParams["DATA"]=self.avTable
            dictParams["FILE.CSV"]=self.sFileCSV
            dictParams["FIELD.KEY"]=self.sFieldKey

    # Ritorno
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        return [sResult, dictParams]

# Stringa del CSV
# -------------------------------------------------
    def ToStr(self):
        lResult=self.ToDict()
        sResult=lResult[0]
        if sResult=="":
            return nlSys.NF_StrObj(lResult[1])
        else:
            return sResult

# Indice Campo. Ritorna -1 o Numero
# -------------------------------------------------
    def IndexField(self,sFieldName):
        return nlSys.NF_ArrayFind(self.asHeader,sFieldName)

# Array delle Chiavi
# -------------------------------------------------
    def Keys(self):
        asKey=[]
        nFieldIndex=self.IndexField(self.sFieldKey)
        if nFieldIndex != -1:
            for nRow in range(0,self.Len()-1):
                vValue=self.avTable[nRow][nFieldIndex]
                asKey.append(vValue)
        return asKey

# Estrae Dictionary da Record in base a valore campo chiave o numero record
# -------------------------------------------------------------------------
    def Record(self,vKey):
        dictResult={}
        avRecord=[]

# Cerca Record
        if type(vKey) == int:
            nRecordIndex=vKey
            if nRecordIndex>self.Len(): nRecordIndex=-1
        elif type(vKey) == str:
            nRecordIndex=self.Find(vKey)

# Estrae Record come Array da Tabella CSV
# Avvalora dict di ritorno
        if nRecordIndex != -1:
            avRecord=self.avTable[nRecordIndex]
            nField=0
            for sField in self.asFields:
                dictResult[sField]=avRecord[nField]
                nField+=1
# dict di Ritorno
        return dictResult

# Cerca Record in base al valore di un Campo o del campo Chiave
# Ritorno. nIndex>=0 o -1
# -------------------------------------------------------------------------
    def Find(self, sFieldValue, sFieldName=""):
        nResult=-1

    # Default Field
        if sFieldName=="": sFieldName=self.sFieldKey
    # Empty Table
        if self.Len()==0: return nResult
    # Indice a Campo
        nFieldIndex=self.IndexField(self.sFieldKey)
        if nFieldIndex==-1: return nFieldIndex
    # Ricerca
        for nIndex in range(0,self.nLines):
            if self.avTable[nIndex][nFieldIndex]==sFieldValue:
                nResult=nIndex
                break
    # Ritorno
        return nResult

# Lunghezza CSV in memoria
# Ritorno. 0..N Record
# -----------------------------------------------------------------------------------------
    def Len(self):
        nResult = nlSys.NF_ArrayLen(self.avTable)
        return nlSys.iif(nResult>0,nResult,0)

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
                    self.objCursor=objDB.cursor()
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
        return ntSys.NF_ErrorProc(sResult,sProc)

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
        if NF_IsArray(avSQLparam)==False:
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
        return ntSys.NF_ErrorProc(sResult,sProc)

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