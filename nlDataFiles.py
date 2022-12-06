# ntJobs FILE DATA LIBRARY
# -----------------------------------------------------------
import ntSys
# Lib er gestione file .II
import configparser, csv, copy
NT_ENV_TEST_DATAF=True
sCSV_DELIMITER=";"
sCSV_QUOTE='"'

# INI: Ritorna Sezioni lette come dict di dict in lResult
# Nomefile già normalizzato
# Ritorna lResult 0=Ritorno, 1=IniDict, dove Trim/UCASE.KEY e valori "trimmati"
# -----------------------------------------------------------------------------
def NF_INI_Read(sFileINI):
    sProc="NF_INI_Read"
    sResult=""
    dictINI=dict()

# Verifica esistenza
    sResult=ntSys.NF_FileExistErr(sFileINI)

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
                sKey=ntSys.NF_StrNorm(sKey)
                # Trim Value e Str per sicurezza
                vValue=(str(vValue)).lstrip().rstrip()
                # Assegnazione di ritorno
                dictSection[sKey]=vValue
            # Assegna KEYS a SEZIONE
            ntSys.NF_DebugFase(NT_ENV_TEST_DATAF, ", Tipo dictSection: " + str(type(dictSection)), sProc)
            dictINI[sSection]=dictSection.copy()

# Fine ciclo lettura INI
    sResult=ntSys.NF_ErrorProc(sResult,sProc)
    lResult=[sResult,dictINI]
    ntSys.NF_DebugFase(NT_ENV_TEST_DATAF, ", dictINI: " + ntSys.NF_DictStr(dictINI), sProc)
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
        for sGroup in ntSys.NF_DictKeys(dictINIs):
            dictINI=dictINIs[sGroup]
            for vKey in ntSys.NF_DictKeys(dictINI):
            # Items
                if not config.has_section(sGroup): config.add_section(sGroup)
                config.set(sGroup,vKey,dictINI[vKey])

# Salva File
    lResult=ntSys.NF_FileOpen(sFileINI,sAttr)
    sResult=lResult[0]
    if sResult=="":
        hFile=lResult[1]
        config.write(hFile)
    # Chiusura file
        hFile.close()

# Ritorno Scrittura
    sResult=ntSys.NF_ErrorProc(sResult,sProc)
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
    if ntSys.NF_FileExist(sFileINI):
# Legge INI
        lResult=NF_INI_Read(sFileINI)
        sResult=lResult[0]
        if sResult=="":
            dictINIs_read=lResult[1]
        # Merge (del tipo 2o livello)
            dictINIs_read=ntSys.NF_DictMerge2(dictINIs_read, dictINIs_update)
        # Salva dictINI
            sResult=NF_INI_Write(sFileINI, dictINIs_read)
# Ritorno Scrittura
    sResult=ntSys.NF_ErrorProc(sResult,sProc)
    return sResult

# ----------------------- CLASSI ---------------------------
# CSV Class
class NC_CSV:
# Dati
    nLines=0                       # Record, letti/scritti, compreso header
    sFileCSV=""                    # Nome file csv
    dictSchema={}                  # NON USATO PER ORA
    avTable=[]                     # TABELLA DEI DATI. Array Doppio. 0=Record, 1=Colonna (come asHeader)
    asHeader=[]                    # Header Effettivo
    asFields=[]                    # Header Da verificare
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
# Ritorna sResult, self.sHeader, self.dictTable
# Params: FILE.IN=CSV, FIELDS=Array che ci deve essere, DELIMITER=Delimiter campi, TRIM=Trim Prima e dopo. QUOTE=Campo delimitatore testi
# ---------------------------------------------------------------------------------------
    def Read(self,dictParams):
        sProc="CSV.READ"
        sResult=""

# Legge Parametri
        sResult=ntSys.NF_DictExistKeys(dictParams,("FILE.IN","FIELDS"))
        if sResult=="":
            ntSys.NF_DebugFase(NT_ENV_TEST_DATAF, "Parametri CSV.READ: " + str(dictParams), sProc)
            self.bTrim=ntSys.NF_DictGet(dictParams,"TRIM",False)
            self.sDelimiter=ntSys.NF_DictGet(dictParams,"DELIMITER",sCSV_DELIMITER)
            self.asFields=ntSys.NF_DictGet(dictParams,"FIELDS",[])
            self.sFileCSV=ntSys.NF_DictGet(dictParams,"FILE.IN","")
            self.sFieldKey=ntSys.NF_DictGet(dictParams,"FIELD.KEY","")

# Verifica Header se specificato asFields(FILE.IN)
        if ntSys.NF_ArrayLen(self.asFields)>0: sResult=self.Header()
        ntSys.NF_DebugFase(NT_ENV_TEST_DATAF, "CSV.HEADER: " + sResult, sProc)

# Apertura FileCSV + Lettura CSV LIST in tabella dictTable, un record per riga + Chiusura
# Riga zero(numerico) contiene header
        if (sResult==""):
            lResult=ntSys.NF_FileOpen(self.sFileCSV,"r")
            sResult=lResult[0]
            if sResult=="":
                csv_file_in=lResult[1]
        # Setup
                self.nLines=0
                csv_reader = csv.reader(csv_file_in, delimiter=self.sDelimiter)
                self.avTable=[]
                ntSys.NF_DebugFase(NT_ENV_TEST_DATAF, "Letto file CSV: " + self.sFileCSV, sProc)
        # Per N.Righe
                for row in csv_reader:
            # Normalizza Riga
                    asRow=ntSys.NF_ArrayT2L(row)
                    if self.bTrim: asRow=ntSys.NF_ArrayStrNorm(asRow,"LR")
            # Header
                    if (self.nLines == 0):
                        ntSys.NF_DebugFase(NT_ENV_TEST_DATAF, f'Column names {", ".join(self.asHeader)}', sProc)
                        self.asHeader=asRow.copy()
            # Prossima Riga
                # Salva Riga Dati Array
                    self.avTable[nLineaRead]=asRow.copy()
                    self.nLines+=1
        # Chiue file e fine
                csv_file_in.close()
                ntSys.NF_DebugFase(NT_ENV_TEST_DATAF, "Righe Lette CSV: " + str(len(self.dictTable)), sProc)
                sResult=""
# Fine
        sResult=ntSys.NF_ErrorProc(sResult,sProc)
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
            ntSys.NF_DebugFase(NT_ENV_TEST_DATAF, "Recupero header csv file " + self.sFileCSV, sProc)
            lResult=ntSys.NF_FileOpen(self.sFileCSV,"r")
            sResult=lResult[0]

# Lettura Riga
        if (sResult==""):
            try:
                csv_reader = csv.reader(csv_file_in, delimiter=self.sDelimiter)
            except:
                sResult="Lettura header"
        if (sResult==""):
            self.asHeader=[]
            for row in csv_reader:
                self.asHeader=row
                break
            csv_file_in.close()

# Trim/UCASE Header
        if ntSys.NF_ArrayLen(self.asHeader)>0:
            self.asHeader=ntSys.NF_ArrayStrNorm(self.asHeader,"LRU")
        else:
            sResult="Header non leggibile"

# Verifica Header come previsto uguali o genera stringa di errore
        if sResult=="":
            sResult=ntSys.NF_ArrayCompare(self.asFields, self.asHeader)
        if sResult!="":
            sHeader=sCSV_DELIMITER.join(self.asHeader)
            sFields=sCSV_DELIMITER.join(self.asFields)
            sResult="Header non uguali. Previsto: [" + sFields + "]/ Letto: [" + sHeader + "]"

    # Ritorno
        sResult=ntSys.NF_ErrorProc(sResult, sProc)
        return sResult

# Append CSV Memory Dictionary in CSV File - Stesso Header
# Ritorna sResult=""=Ok, altrimenti Errore
# Params: DELIMITER(obbligatorio, FIELDS(obbligatorio), FILE.IN(obbligatorio), FILE.ADD (obbligatorio), FILE.OUT(obbligatorio)
    def Append(self,dictParams):
        sProc="CSV_APPEND"
        sResult=""
        lResult=[]
        avTableCSVadd=[]

# Normalizza IN/ADD Legge e fusione
        for sF in ("IN","ADD","OUT"):
            if sResult=="":
                sFile=ntSys.NF_DictGet(dictParams,"FILE." + sF, "")
                lResult=ntSys.NF_PathNormal(sFile)
# 1: Legge IN
                if sF=="IN":
                    csv_IN=NC_CSV()
                    csv_IN.sFileCSV=lResult[5]
                    sResult=csv_IN.Read()
# 2: Legge ADD
                if sF=="ADD":
                    csv_ADD=NC_CSV()
                    csv_ADD.sFileCSV=lResult[5]
                    sResult=csv_ADD.Read()
# 3: Out. Verifica Header,
                if sF=="OUT":
                    if csv_IN.asHeader != csv_IN.asHeader: sResult="IN/ADD Header diversi"
# 4: Copia IN, aggiunge tabella di ADD
                    if sResult=="":
                        self.csvFrom=csv_ADD
                        self.Copy(CSV_IN)
                        self.sFileCSV=lResult[5]
                        ntSys.NF_ArrayAppend(self.avTable,csv_ADD.avTable)
# 5: Scrive nuovo
        if sResult=="": sResult=self.Write()

# Ritorno
        sResult=ntSys.NF_ErrorProc(sResult, sProc)
        return sResult

# CSV Write Output - READ OR APPEND -
# Per Append di altro dictCSV con stesso Header, utilizzare NF_CSV_Append()
# Ritorno: sResult
# -----------------------------------------------------------------------------
    def Write(dictParams):
        sProc="CSV.WRITE"
# Setup
        self.nLines=0
# Legge Parametri
        sResult=ntSys.NF_DictExistKeys(dictParams,("FILE.OUT","FIELDS"))
# Verifica Parametri
        if sResult=="":
            self.asHeader=ntSys.NF_DictGet(dictParams,"FIELDS",[])
            self.sDelimiter=ntSys.NF_DictGet(dictParams, "DELIMITER", sCSV_DELIMITER)
            sFileOut=ntSys.NF_DictGet(dictParams,"FILE.OUT","")
            self.avTable=ntSys.NF_DictGet(dictParams,"DATA",[])
            sMode=ntSys.NF_DictGet(dictParams,"MODE","WRITE")
# TEST
        ntSys.NF_DebugFase(NT_ENV_TEST_DATAF, "Righe da esportare: " + str(len(dictCSV)), sProc)
# Scrive File CSV. Lo scrive comunque anche se vuoto
        sModeFile=ntSys.iif(sMode=="APPEND","a","w+")
        lResult=ntSys.NF_FileOpen(sFileOut,sModeFile)
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
                self.nLines = self.nLines + 1
# Close
        csv_file_out.close()
        print(f'Fine Scrittura file CSV. Record OUT: {self.nLines} linee.')
# Fine
        return sResult

# Copia CSV da altro CSV in memoria
# -------------------------------------------------
    def FromDict(self, dictParams):
        self.asFields=dictParams["FIELDS"]
        self.asHeader=copy.deepcopy(dictParams["HEADER"])
        self.avTable= copy.deepcopy(dictParams["DATA"])
        self.sFileCSV=dictParams["FILE.CSV"]
        self.nLines=dictParams["LINES"]
        self.sFieldKey=dictParams["FIELD.KEY"]

# Copia CSV in DICT
# -------------------------------------------------
    def ToDict(self):
        dictParams=[]
        dictParams["FIELDS"]=self.asFields
        dictParams["HEADER"]=self.asHeader
        dictParams["DATA"]=self.avTable
        dictParams["FILE.CSV"]=self.sFileCSV
        dictParams["LINES"]=self.nLines
        dictParams["FIELD.KEY"]=self.sFieldKey
        return dictParams

# Indice Campo. Ritorna -1 o Numero
# -------------------------------------------------
    def IndexField(self,sFieldName):
        return ntSys.NF_ArrayFind(self.asHeader,sFieldName)

# Array delle Chiavi
# -------------------------------------------------
    def Keys(self):
        asKey=[]
        nFieldIndex=self.FieldIndex(self.sFieldKey)
        if nFieldIndex != -1:
            for nRow in range(0,self.nLines):
                vValue=self.avTable[nRow,]
                asKey.append(vValue)
        return asKey
