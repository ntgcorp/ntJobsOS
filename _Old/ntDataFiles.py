# ntJobs FILE DATA LIBRARY
# -----------------------------------------------------------
import ntSys
# Lib er gestione file .II
import configparser, csv
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
    #print(sProc + " lettura ini: " + sResult)
    
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
            ntSys.NF_DebugFase(NT_ENV_TEST_DATAF, ": Tipo dictSection " + str(type(dictSection)), sProc)    
            dictINI[sSection]=dictSection.copy()
    
# Fine ciclo lettura INI
    sResult=ntSys.NF_ErrorProc(sResult,sProc)
    lResult=[sResult,dictINI]
    return lResult

# INI: Salva 
# Nomefile già normalizzato. SEMPRE IN SCRITTURA. sE UPDATE USARE NF_INI_Update
# Passato in forma dict di dict
# Ritorna sResult
# -----------------------------------------------------------------------------
def NF_INI_Write(sFileINI, dictINIs):
    sProc="NF_INI_Read"
    sResult=""
    sGroup=""

# Setup
    config = configparser.ConfigParser()
    if ntSys.NF_FileExist(sFileINI): sAttr="a"

# Per tutte le chiavi. Se inizia per #=Nome Sezione
    for sGroup in NF_DictKeys(dictINIs):
        dictINI=dictINIs[sGroup]
        for vKey in NF_DictKeys(dictINI):    
        # Items    
            if not config.has_section(sGroup): config.add_section(sGroup)    
            config.set(sGroup,vKey,dictINI[vKey])
             
# Salva File
    lResult=ntSys.NF_FileOpen(sFileINI,"w")
    sResult=lResult[0]
    if sResult==""
        hFile=lResult[1]
        config.write(hFile)
        
# Ritorno Scrittura
    sResult=ntSys.NF_ErrorProc(sResult,sProc)
    return sResult

# INI: Update
# Se esiste lo legge e update del dict passato come parametro
# Ritorna sResult
# -----------------------------------------------------------------------------
def NF_INI_Update(sFileINI, dictINI):
    sProc="NF_INI_Update"
    sResult=""
    sGroup=""

# Se non Esiste va a INI_Write ed ESCE
    if ntSys.NF_FileExist(sFileINI): 
# Legge INI
        sResult=NF_INI_Read(sFileINI, dictINIs)
# Merge
        dictINI=NF_DictMerge2(dictINI, dictINIs)
# Salva dictINI 
    sResult=NF_INI_Write(sFileINI, dictINI)        
# Ritorno Scrittura
    sResult=ntSys.NF_ErrorProc(sResult,sProc)
    return sResult

# Read CSV Input in DICT di list. 1,2=Header, 3..N: Record
# Campi di dictParams
# TRIM=True/False, DELIMITER=","(def) FILE.IN=, FILE.OUT
# FIELDS[ucase,trimmato]. Se specificato viene utilizzato come confronto con quello da leggere
# Se CSV_Append viene usato come confronto con quello da appendere
# Il file deve già essere normalizzato
# Ritorna lResult. 0=RitornoStr, 1=Campi, 2=SchemaCompleto(OPZIOMALE o None), 3=dictTableCSV
# Params: FILE.IN=CSV, FIELDS=Array che ci deve essere, DELIMITER=Delimiter campi, TRIM=Trim Prima e dopo. QUOTE=Campo delimitatore testi
# ---------------------------------------------------------------------------------------
def NF_CSV_Read(dictParams):
    sProc="CSV_READ"
    sResult=""
    nLineaRead=0
    lResult=[]
    dictSchema=dict()
    dictTable=dict()
    asHeader=[]
    
# Legge Parametri    
    sResult=ntSys.NF_DictExistKeys(dictParams,("FILE.IN","FIELDS"))
    if sResult=="":
        bTrim=ntSys.NF_DictGet(dictParams,"TRIM",False)
        sDelimiter=dictParams.get("DELIMITER",sCSV_DELIMITER)
        asFields=dictParams.get("FIELDS",[])
        #sQuote=ntSys.NF_DictGet(dictParams,"QUOTE","'")
        sFileCSV=ntSys.NF_DictGet(dictParams,"FILE.IN","")
        ntSys.NF_DebugFase(NT_ENV_TEST_DATAF, "Parametri CSV.READ: " + str(dictParams), sProc)
    
# Verifica Header se specificato asFields(FILE.IN)
    if ntSys.NF_ArrayLen(asFields)>0:
        lResult=NF_CSV_Header(dictParams)
        sResult=lResult[0]
    ntSys.NF_DebugFase(NT_ENV_TEST_DATAF, "CSV.HEADER: " + sResult, sProc)        
                                    
# Apertura FileCSV + Lettura CSV LIST in tabella dictTable, un record per riga + Chiusura
# Riga zero(numerico) contiene header    
    if (sResult==""):
        sResult="Apertura " + sFileCSV
        with open(sFileCSV, newline='', encoding=ntSys.NT_ENV_ENCODING) as csv_file_in:    
        # Setup
            nLineaRead=0
            csv_reader = csv.reader(csv_file_in, delimiter=sDelimiter)
            dictTable.clear()
            ntSys.NF_DebugFase(NT_ENV_TEST_DATAF, "Apertura CSV: " + sFileCSV, sProc)
        # Per N.Righe
            for row in csv_reader:            
            # Header
                if (nLineaRead == 0):
                    asHeader=asFields
                    row=ntSys.NF_ArrayT2L(asFields)
                    ntSys.NF_DebugFase(NT_ENV_TEST_DATAF, f'Column names {", ".join(asHeader)}', sProc)
            # Prossima Riga
                # Trim
                if bTrim: row=ntSys.NF_ArrayStrNorm(row,"LR")
                # Salva Riga Dati Array
                dictTable[nLineaRead]=row
                nLineaRead+=1        
        # Chiue file e fine
            csv_file_in.close()
            ntSys.NF_DebugFase(NT_ENV_TEST_DATAF, " Righe Lette CSV: " + str(len(dictTable)), sProc)
            sResult=""
# Fine
    sResult=ntSys.NF_ErrorProc(sResult,sProc)
    lResult=[sResult,asHeader,dictSchema,dictTable]
    return lResult

# Legge solo Header CSV. FILE.IN
# Ritorno lResult 0=Result, 1=HeaderArrayStr
# Se FIELDS già avvalorato, allora VERIFICA che l'Header letto corrisponda a quello di FIELD
# IN.FILE deve già essere normalizzato
# ------------------------------------------------------------------------------------------
def NF_CSV_Header(dictParams):
    sProc="CSV_HEADER"
    sResult=""
    asFields=[]
    asHeader=[]
    sHeader=""
        
# Legge Parametri
    ntSys.NF_DebugFase(NT_ENV_TEST_DATAF, "params:" + str(dictParams), sProc)
    sResult=ntSys.NF_DictExistKeys(dictParams,("FILE.IN","FIELDS"))

# Prende Parametri
    if sResult=="":
        sDelimiter=ntSys.NF_DictGet(dictParams,"DELIMITER",sCSV_DELIMITER)    
        sFileIn=ntSys.NF_DictGet(dictParams,"FILE.IN","")
        asFields=ntSys.NF_DictGet(dictParams,"FIELDS",None)
    else:
        sResult = sResult + " in parametro dictParams entrata"
        
# Verifica Parametri
    if  ntSys.NF_ArrayLen(asFields)>0:
        sResult=ntSys.NF_FileExistErr(sFileIn)
        #print(sProc + " Check: " + str(sResult) + ", " + str(type(sResult)))
    else:
        sResult="Header Fields non passato"    
    
# Lettura Riga 1 File - Preimpostato errore
    if (sResult==""):
        ntSys.NF_DebugFase(NT_ENV_TEST_DATAF, "Recupero header csv file " + sFileIn, sProc)
        try:
            csv_file_in=open(sFileIn, newline='', encoding=ntSys.NT_ENV_ENCODING)
        except:
            sResult="Apertura file CSV: " + sFileIn        
        if (sResult==""):
            try:
                csv_reader = csv.reader(csv_file_in, delimiter=sDelimiter)
            except:
                sResult="Creazione oggetto CSV"
            if (sResult==""):
                asHeader=[]
                for row in csv_reader:
                    asHeader=row
                    break
            csv_file_in.close()
    # Split
        if ntSys.NF_ArrayLen(asHeader)>0:     
            asHeader=ntSys.NF_ArrayStrNorm(asHeader,"LRU")
            sResult=""
        else:
            sResult="Header non leggibile"
            
    # Verifica Header come previsto uguali o genera stringa di errore
    if sResult=="":
        sResult=ntSys.NF_ArrayCompare(asFields, asHeader)
        if sResult!="":
            sHeader=sCSV_DELIMITER.join(asHeader)
            sFields=sCSV_DELIMITER.join(asFields)
            sResult="Header non uguali. Previsto: " + sFields + "/ Letto: " + sHeader

# Ritorno
    sResult=ntSys.NF_ErrorProc(sResult, sProc)
    lResult=[sResult,asFields]
    return lResult            

# Append CSV Memory Dictionary in CSV File - Stesso Header
# Ritorna sResult=""=Ok, altrimenti Errore
# Params: DELIMITER(obbligatorio, FIELDS(obbligatorio), FILE.IN(obbligatorio), FILE.OUT(obbligatorio)
def NF_CSV_Append(dictParams):
    sProc="CSV_APPEND"
    sResult=""
    lResult=[]
    dictTableCSVadd=dict()
    
# Legge Parametri
    sFileIn=ntSys.NF_DictGet(dictParams,"FILE.IN","")
    asHeader=ntSys.NF_DictGet(dictParams,"FIELDS","")
    sFileOut=ntSys.NF_DictGet(dictParams,"FILE.OUT","")

# Verifica Presenza Fields
    if not ntSys.NF_IsArray(asHeader): sResult="FIELDS mancante"
        
# Normalizza File IN
    if (sResult==""):
        lResult=ntSys.NF_PathNormal(sFileIn)
        sFileIn=lResult[5]
        sResult=lResult[0]
        
# Normalizza File OUT        
    if sResult=="": 
        lResult=ntSys.NF_PathNormal(sFileOut)
        sResult=lResult[0]
        sFileOut=lResult[5]        

# Ritorna lResult. 0=Ritorno, 1=Campi, 2=SchemaCompleto(OPZIOMALE o None), 3=dictTableCSV
# Lettura Dictionary Originale
    if sResult=="": 
        lResultIn=NF_CSV_Header(dictParams)
        sResult=lResultIn[0]
        if sResult=="":
            asHeaderIn=lResult[1]

# Lettura Dictionary Da Aggiungere        
    if sResult=="":
        dictParamsToAdd=dictParams.copy()            
        lResultAdd=NF_CSV_Header(dictParamsToAdd)
        sResult=lResultAdd[0]
        if sResult=="":
            asHeaderAdd=lResult[1]
            dictTableCSVadd=lResult[3]

# Confronta Header
    if (sResult=="") and (asHeaderIn != asHeaderAdd): sResult = "Header diversi"

# Apertura file CSV in Append
    if sResult=="":
        dictParams["MODE"]="APPEND"
        dictParams["DATA"]=dictTableCSVadd
        sResult=NF_CSV_Write(dictParams)
        
# Ritorno
    sResult=ntSys.NF_ErrorProc(sResult, sProc)
    return sResult

# CSV Write Output - READ OR APPEND -
# Per Append di altro dictCSV con stesso Header, utilizzare NF_CSV_Append()
# Ritorno: sResult
# -----------------------------------------------------------------------------
def NF_CSV_Write(dictParams):
    sProc="CSV_WRITE"    
# Setup    
    nLinea=0
    
# Legge Parametri
    sResult=ntSys.NF_DictExistKeys(dictParams,("FILE.OUT","FIELDS","DATA"))
    
# Verifica Parametri
    if sResult=="":
        asFields=dictParams.get("FIELDS",[])
        sDelimiter=ntSys.NF_DictGet(dictParams, "DELIMITER", sCSV_DELIMITER)    
        sFileOut=ntSys.NF_DictGet(dictParams,"FILE.OUT","")
        dictCSV=dictParams.get("DATA",{})
        sMode=ntSys.NF_DictGet(dictParams,"MODE","WRITE")
    
# TEST
    print(sProc + " Righe da esportare: " + str(len(dictCSV)))
    ntSys.NF_DebugFase(NT_ENV_TEST_DATAF, "Recupero PARAMS da dict", sProc)
    
# Scrive File CSV. Lo scrive comunque anche se vuoto
    sModeFile=ntSys.iif(sMode=="APPEND","a","w+")
    sResult=ntSys.NF_ErrorProc("Errore apertura file: " + sFileOut, sProc)
    with open(sFileOut, mode=sModeFile, newline='', encoding=ntSys.NT_ENV_ENCODING) as csv_file_out:        
    # Scrive Header
        csv_writer = csv.DictWriter(csv_file_out,fieldnames=asFields,delimiter=sDelimiter)    
        if (sMode=="WRITE"): csv_writer.writeheader()                
    # Scrive Linee
        anKeys=ntSys.NF_DictKeys(dictCSV)
        for nKey in anKeys:
        # Prende riga da dictionary (la riga è un array str asFMT_MAIL_SDB_HDR)
            asRow=dictCSV.get(nKey)
            csv_writer.writerow(asRow)
            nLinea = nLinea + 1
    # Close
        csv_file_out.close()
        print(f'Fine Scrittura file ntMail. Record OUT: {nLinea} linee.')
        sResult=""
# Fine    
    return sResult
