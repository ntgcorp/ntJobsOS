# ntJobs FILE DATA LIBRARY
# Lib  gestione file .INI, CSV, Altri Formati NON DB (per CONVERSIONI Excel/CSV usare NC_Panda)
# --------------------------------------------------------------------------------
import nlSys
import configparser, copy

# Test mode
NT_ENV_TEST = True

# Costanti
sCSV_DELIMITER = ";"

# ----------------------- CLASSI ---------------------------
# CSV Class
class NC_CSV:
# Dati
    sFileCSV=""                    # Nome file csv
    nLines=-1                      # Numero Record. -1=Empty, 0=Header, 1..N=Record
    dictSchema={}                  # NON USATO PER ORA
    avTable=[]                     # TABELLA DEI DATI. Array Doppio di Record
    asHeader=[]                    # Header Effettivo
    asFields=[]                    # Header Da verificare in caso di lettura
    bTrim=False                    # Trim in Lettura
    nFields=0                      # Numero campi. Deve essere impostata da Header
    sDelimiter=sCSV_DELIMITER      # Delimiter
    bOpen=False                    # File CSV Aperto
    hFile=0                        # Handler File
    sFieldKey=""                   # Campo Chiave. FACOLTATIVO (SE C'E' il ToDict è convertibile in tabella)

# -------------- METODI --------------
    def __init__(self):
        pass

# Legge le Righe di file aperto. Ritorno sResult status operazione
    def ReadFileLines(self) -> str:
        sProc="CSV.READ.FILE.LINES"        
        sResult=""
# Apre File
        if self.bOpen==False: 
            sResult="File not open"
# Lettura Righe
        if sResult=="":
# Reset Tabella
            self.avTable=[]
            self.nLines=-1
# Legge Righe
            try:
                for linea in self.hFile:
                    self.nLines += 1
                    linea = linea.strip()  # Rimuove spazi e newline
                    if linea:  # Ignora righe vuote
                        self.avTable.append(linea)
            except Exception as e:
                sResult="Error reading line " + str(self.nLines) + " " + e.message
# Ritorno   
        return nlSys.NF_ErrorProc(sResult,sProc)

# Legge le Righe di file aperto
# Ritorna sResult status operazione
    def WriteFileLines(self) -> str:
        sProc="CSV.WRITE.FILE.LINES"        
        sResult=""
        nLine=0
# Apre File
        if self.bOpen==False: 
            sResult="File not open"
# Lettura Righe
        if sResult=="":
# Reset Tabella
            self.avTable=[]
            self.nLines=-1
# Create Header
        header = self.avTable[0]
        header_line = []
        for item in header:
            if isinstance(item, (int, float)):
                header_line.append(str(item))
            else:
                header_line.append(f'"{str(item)}"')
# Write Header
        sResult=nlSys.NF_FileWriteLine(self.hFile, header_line)
# Process data rows
        if sResult=="":
            for row in self.avTable[1:]:
                line_items = []
                nLine += 1
                for item in row:
                    if isinstance(item, (int, float)):
                        line_items.append(str(item))
                    else:
                        # Escape existing quotes by doubling them
                        escaped_item = str(item).replace('"', '""')
                        line_items.append(f'"{escaped_item}"')
# Write String
            sResult=nlSys.NF_FileWriteLine(self.hFile, line_items)
            if sResult != "":
                sResult = sResult + ", Line: " + str(nLine)
# Fine
        return nlSys.NF_ErrorProc(sResult,sProc)

# Read CSV Input in DICT di list. 1,2=Header, 3..N: Record
# Campi di dictParams
# TRIM=True/False, DELIMITER=","(def) FILE.IN=, FILE.OUT
# FIELDS[ucase,trimmto]. Se specificato viene utilizzato come confronto con quello da leggere
# Se CSV_Append viene usato come confronto con quello da appendere
# Il file deve già essere normalizzato
# Ritorna sResult, self.sHeader, self.avTable
# Params: FILE.IN=CSV, FIELDS=Array che ci deve essere, DELIMITER=Delimiter campi, TRIM=Trim Prima e dopo. QUOTE=Campo delimitatore testi
# Return. sResult e nel dictParams aggiunge ROWS=Righe Lette
# ---------------------------------------------------------------------------------------
    def Read(self,**kwargs):
        sProc="CSV.READ"
        sResult=""
# Reset
        self.avTable=[]
        self.sFileCSV=""
        self.bTrim=False
        self.sDelimiter=sCSV_DELIMITER
        self.sFieldKey=""
# Che non sia già aperto
        if self.bOpen:
            sResult="File just opened"
# Legge Parametri
# Iterating over the Python kwargs dictionary
        for key, value in kwargs.items():
            if key=="file_in":
                self.sFileCSV=value
            elif key=="trim":
                self.bTrim=value
            elif key=="delimiter":
                self.sDelimiter=value
            elif key=="fieldkey":
                self.FieldKey=value
            elif key=="fields":
                self.asFields=value
                self.nFields=len(self.asFields)           
            else:
                sResult="key invalid " + key
                break
# Verifiche parametri
        if self.nFields==0:
            sResult="Invalid struct Fields"     
# Apertura file.in
        nlSys.NF_DebugFase(NT_ENV_TEST, f"Parametri CSV.READ: File: {self.sFileCSV}, Trim: {self.bTrim}, delimiter: {self.sDelimiter}", sProc)
        if (sResult==""):
            lResult=nlSys.NF_FileOpen(self.sFileCSV,"r")
            sResult=lResult[0]
            nlSys.NF_DebugFase(NT_ENV_TEST, "Apertura csv file " + self.sFileCSV + ", Result: " + sResult, sProc)
            if sResult=="":
                self.bOpen=True
                self.hFile=lResult[1]
# Verifica Header se specificato asFi
# Lettura FileCSV + Lettura CSV LIST in tabella, un record per riga. riga zero contiene header
        if (sResult==""):
            sResult=self.ReadFileLines()
        if sResult=="":
            nlSys.NF_DebugFase(NT_ENV_TEST, "Righe Lette da CSV: " + str(self.nLines), sProc)
# Chiusura file
        if self.bOpen:
            self.hFile.close()
            self.bOpen=False
# Verifica Header
        if (sResult==""):
            sResult=self.Header()
# Conversione da Tabella di Stringhe a Tabella di Valori
        if sResult=="":
            nlSys.NF_DebugFase(NT_ENV_TEST, "Convert Line in Record", sProc)
            for nLine in range(1, self.nLines):
# Split
                sRiga=str(self.avTable[nLine])
                sResult,asRow=nlSys.NF_StrSplitString(sRiga,self.sDelimiter)
                if sResult=="":
# Verifica numero di dati estratti. Se Ok prende il Record
                    nData=len(asRow)
                    if nData != self.nFields:
                        sResult=f"Row invalid. values {nData} instead {self.nFields}, Line: {nLine}/{self.nLines}, Line: {sRiga}" 
                        break                
                    else:
# Replace Chars & Split + Assign
                        nIndex=0
                        for sRow in asRow:
                            # Strip Evoluto. X=NoASC, S=NoSpazi interni, D=Left & Right Space, A=Left & Right Apici, K= doppi apici in uno solo
                            sRow=nlSys.NF_StrStrip(sRow,"XDAK")
                            asRow[nIndex]=sRow
                        self.avTable[nLine]=asRow.copy()   
# Fine
        return nlSys.NF_ErrorProc(sResult,sProc)

# Legge solo Header CSV. FILE.IN
# Ritorno sResult
# Se FIELDS già avvalorato, allora VERIFICA che l'Header letto corrisponda a quello di FIELD
# FILE.IN deve già essere normalizzato
# Converte l'header stringa in Arrray di stringhe con nomi dei campi
# ------------------------------------------------------------------------------------------
    def Header(self):
        sProc="CSV.HEADER"
        sResult=""
# Reset        
        self.asHeader=list[str]
        sHeader=self.avTable[0]
# Join fields with delimiter
        sFields=sCSV_DELIMITER.join(self.asFields)
        if self.nLines==-1:
            sResult="File Empty"
# Prende Header come stringa prima di essere trasformato in un array   
        if (sResult==""):
            sResult,asTemp=nlSys.NF_StrSplitString(sHeader,bNames=True)
        if sResult=="":
            self.asHeader=asTemp.copy()
# Trim/UCASE Header
        if nlSys.NF_ArrayLen(self.asHeader)>0:
            self.asHeader=nlSys.NF_ArrayStrNorm(self.asHeader,"LRU")
            self.avTable[0]=self.asHeader.copy()
            nlSys.NF_DebugFase(NT_ENV_TEST, "Header: " + str(self.avTable[0]), sProc)
        else:
            sResult="Header non leggibile"
# Verifica Header come previsto uguali o genera stringa di errore
        if sResult=="":
            sResult=nlSys.NF_ArrayCompare(self.asFields, self.asHeader)
        if sResult!="":
            sResult="Header non uguali. Previsto: [" + sFields + "]/ Letto: [" + sHeader + "]"

# Ritorno
        return nlSys.NF_ErrorProc(sResult,sProc)
    
# Append CSV Memory Dictionary in CSV File - Stesso Header
# Ritorna sResult=""=Ok, altrimenti Errore
# Presupporto già letto csv da appendere
# Params: DELIMITER(obbligatorio, FIELDS(obbligatorio), FILE.ADD(obbligatorio)
    def Append(self,sFile):
        sProc="CSV_APPEND"
        sResult=""
        lResult=list[str]
        dictAppend={}

# 1: Legge File ADD come CSV_ADD
        lResult=nlSys.NF_PathNormal(sFile)
        csv_ADD=NC_CSV()
        sResult=csv_ADD.Read(in_file=lResult[5], trim=True)

        if sResult=="":
# 2: Out. Verifica Header,
            if self.asHeader != csv_ADD.asHeader: 
                sResult="IN/ADD Header diversi"
# 4: Copia IN, aggiunge tabella di ADD
        if sResult=="": 
            nlSys.NF_ArrayAppend(self.avTable,csv_ADD.avTable)
# Ritorno
        return nlSys.NF_ErrorProc(sResult,sProc)
    
# CSV Write Output - READ OR APPEND -
# Per Append di altro dictCSV con stesso Header, utilizzare NF_CSV_Append()
# Ritorno: sResult
# -----------------------------------------------------------------------------
    def Write(self, **kwargs):
        sProc="CSV.WRITE"
        sResult=""
        sFileOut=""
        sMode=""
# Setup
        nLinesWrite=0
# Legge Parametri
# Iterating over the Python kwargs dictionary
        for key, value in kwargs.items():
            if key=="file_out":
                sFileOut=value
            elif key=="mode":
                sMode=value
            else:
                sResult="key invalid " + key
                break
# TEST
        nlSys.NF_DebugFase(NT_ENV_TEST, "Righe da esportare: " + str(self.nLines), sProc)
# Scrive File CSV. Lo scrive comunque anche se vuoto
        sModeFile=nlSys.iif(sMode=="APPEND","a","w+")
# Verifica
        if (sMode=="" or sFileOut==""):
            sResult="mode or fileout invalid"
# Apertura        
        if sResult=="":
            lResult=nlSys.NF_FileOpen(sFileOut,sModeFile)
            sResult=lResult[0]
            if sResult=="":
                self.hFile=lResult[1]
                self.bOpen=True
# Scrive Linee
        if sResult=="":
            sResult=self.write_csv_file()
# Close
        if sResult=="":
            self.hFile.close()
            self.bOpen=False
# Ritorno
        return nlSys.NF_ErrorProc(sResult,sProc)

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
# Fine
        return nlSys.NF_ErrorProc(sResult,sProc)
    
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

# Array delle Chiavi - Se specificato FieldKey
# -------------------------------------------------
    def Keys(self):
        asKey=[]
        if self.sFieldKey != "":
            nFieldIndex=self.IndexField(self.sFieldKey)
            if nFieldIndex != -1:
                for nRow in range(0,self.Len()-1):
                    vValue=self.avTable[nRow][nFieldIndex]
                    asKey.append(vValue)
        return asKey

# Estrae Dictionary da Record in base a valore campo chiave o numero record
# Ritorna dictResult. Se numerico da 1 a N.
# -------------------------------------------------------------------------
    def Record(self, vKey):
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
