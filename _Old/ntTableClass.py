# Classe Table in Array. Prima Riga Fields
import ntSys, ntDataFiles
class NC_Table:
# Campi
    avData=[]
    
# Set Valore in Matrice - Ritorna sResult
    def Set(self, sKey, vKeyValue, vValue):
        sProc="Table.Set"
        
    # 2 Indici
        nIndex=self.Index(sKey,sKeyValue)
        lResult=self.IndexField2(sKey)
        nIndexField=lResult[1]
        sResult=lResult[0]
        if nIndex==-1: sResult=ntSys.NF_StrAppendExt(sResult, "Value non trovato: " + sKey)
        
    # Set o Errori
        if (sResult==""): avData[nIndex][nIndexField]=vValue
            
    # Uscita
        sResult=ntSys.NF_ErrorProc(sResult,sProc)
        return sResult
    
# Set Array Righe x Colonne - Ritorna sResult
    def SetArray(self, avTable):
        sProc="Table.SetArray"
        
    # Check & Set
        nIndex=len(avTable)
        if nIndex != -1:
            self.avData=avTable.copy()
        else:
            sResult="Index errato source"
        
    # Uscita
        sResult=ntSys.NF_ErrorProc(sResult,sProc)
        return sResult

# Set Singola Riga. Ritorna sResult
# -----------------------------------------------------------------------------
    def SetRowArray(self, sKey, avTable):
        sProc="Table.SetRowArray"
        sResult=""
        
    # Ricerca Indice e controllo dimensione riga
        nIndex=self.Index(sKey)
        if nIndex<1: sResult="Non trovata key " + str(sKey)
        if ntSys.NF_ArrayLen(avTable) != ntSys.NF_ArrayLen(self.asFields): sResult="Dimensione diversa n.valori e n.campi " + str(avTable)
    
    # Set
        for sField in asFields:
            sResult=self
        self.avData=avTable.copy()        

    # Uscita
        sResult=ntSys.NF_ErrorProc(sResult,sProc)
        return sResult

# Get in Matrice. Ritorna lResult, 0=Result, 1=Valore
# -----------------------------------------------------------------------------
    def Get(self, sKey, vKeyValue, nIndex):
        sProc="Table.Get"
        sResult=""
        vValue=None
        
    # Ricerca Indice e controllo dimensione riga. Controllo indice non
        lResult=self.IndexField2(sKey)
        sResult=lResult[0]
        nIndexField=lResult[1]
    # Test Index
        sResult=ntSys.NF_StrAppendText(sResult,self.IndexTest(nIndex))
                
    # GetValore
        if sResult=="": vValue=self.avData[nIndex][nIndexField]       

    # Uscita
        sResult=ntSys.NF_ErrorProc(sResult,sProc)
        lResult=[sResult,vValue]
        return sResult
        
# Get in Matrice. Ritorna lResult, 0=Result, 1=Valore
# -----------------------------------------------------------------------------
    def GetRow(self, nIndex):
        sProc="Table.Get.Row"
        sResult=""
        vValue=None
        
    # Ricerca Indice e controllo dimensione riga. Controllo indice non
        sResult=self.IndexText()
    # Prende Valore
        if sResult=="": vValue=self.avData[nIndex]       

    # Uscita
        sResult=ntSys.NF_ErrorProc(sResult,sProc)
        lResult=[sResult,vValue]
        return lResult
    
# Set Riga o Colonna con unico valore, di solito None
# -----------------------------------------------------------------------------
    def FillRow(self, nIndex, vValue=None):
        sProc="Table.Fill.Row"
        sResult=""
        
    # Test Riga
        sResult=self.IndexText(nIndex)
        
    # Set Every Col
        if sResult=="":
            nIndexField=-1
            for sField in self.Fields():
                nIndexField=nIndexField+1
                self.avData[nIndex][nIndexField]=vValue
    # Uscita
        sResult=ntSys.NF_ErrorProc(sResult,sProc)
        return sResult
        
    def FillCol(self, sKey, vValue=None):
        sProc="Table.Fill.Col"
        sResult=""

   # Test Colonna
        lResult=self.IndexField2(sKey)
        nIndexField=lResult[1]
        sResult=lResult[0]
        
    # Set Every Col
        nRows=self.Len()
        if (sResult=="") and (nRows>0):
            for nIndex in range(nRows):
                self.avData[nIndex][nIndexField]=vValue
 
    # Uscita
        sResult=ntSys.NF_ErrorProc(sResult,sProc)
        return sResult
# Get Colonna
# -----------------------------------------------------------------------------
    def GetCol(self, vKey):
        sProc="Table.Get.Col"
        sResult=""
        vValue=None
        vRow=None 
       
    # Ricerca Indice e controllo dimensione riga. Controllo key
        lResult=self.IndexField2(vKey)
        nIndexField=lResult[1]
        sResult=lResult[0]
        
    # Solo se non ci sono errori, prende valori
        if sResult=="":
            nIndex=-1
            for sKey in self.Fields():
                vRecord=self.avData[nIndexField][nIndex]
                nIndex = nIndex + 1
                vRow[nIndex]=vRecord

    # Uscita
        sResult=ntSys.NF_ErrorProc(sResult,sProc)
        lResult=[sResult,vValue]
        return lResult
                
# Append (con controllo ci siano i campi. Ritorna sResult
# -----------------------------------------------------------------------------
    def Append(self, avValues):
        sProc="Table.Add"
        sResult=""

    # Verifica len fields
        if self.FieldsLen()!=ntSys.NF_ArrayLen(avValues): sResult="Dimensione diversa"
            
    # Aggiunta
        if sResult == "": self.avData.append(avValues)

    # Uscita
        sResult=ntSys.NF_ErrorProc(sResult,sProc)
        return sResult
        
# Remove Riga
# -----------------------------------------------------------------------------
    def Remove(self, sKey, vKeyValue):
        sProc="Table.Rem"
        nIndex=self.Len()
    # Ricerca e Rimozio0ne
        if nIndex>0:
            nIndex=self.Index(sKey,vKeyValue)
            if nIndex>0:
                self.avData.remove[nIndex]
        else:            
            sResult="Errore " + str(nIndex)
    # Ritorno
        sResult=ntSys.NF_ErrorProc(sResult,sProc)
        return sResult
        
# Esiste Riga con Valore v. -1=No, Oppure >0
# -----------------------------------------------------------------------------
    def Index(self, sKey, vKeyValue):
    # Setup
        nLen=self.len()
        nResult=0
    # Ricerca
        if nLen>0:
            for sField in self.asFields():
                if sField==sKey:
                    break
                else:
                    nResult=nResult+1
        else:
            nResult=nLen
    # Uscita
        return nResult
 
    def IndexTest(self,nIndex):
        sResult=""
        if nIndex<0 or (not ntSys.NF_Range(nIndex, 0, self.Len())): sResult="Valore non trovato: " + str(sKey)
        return sResult 
        
# Trova campo. v. -1=No, Oppure >=0
# -----------------------------------------------------------------------------
    def IndexField(self, sKey):
    # Indice
        nIndex=ntSys.NF_ArrayFind(self.Fields(), sKey)
    # Fine
        return nIndex
# Ritorna come lResult 0=sResult, 1=IndexTrovato
    def IndexField2(self, sKey):
        sResult=""
        lResult=self.IndexField(vKey)
        if nIndexField==-1: sResult="Key non trovato: " + str(sKey)
        lResult[0]=sResult
        lResult[1]=nIndexField
        return lResult
        
# Numero Records (escluso Fields)
# -----------------------------------------------------------------------------
    def Len(self):
        if self.avData==None: return -1
        return len(self.avData)-1
        
# Array Fields
# -----------------------------------------------------------------------------
    def Fields(self):
        return self.avData[0]
    def FieldsLen(self):
        if self.avData==None:
            return -1
        else:
            return len(self.avData[0])
        
# Print
# -----------------------------------------------------------------------------
    def Print(self):
        sResult=""
        x=0
        for x in range(self.Len()):
            sResult=ntSys.NF_StrAppendExt(sResult, str(self.avData[x]) + "\n")
        return sResult
    
# ReadCSV. Ritorna, dict Standard
# Read CSV Input in DICT di list. 1,2=Header, 3..N: Record
# Campi di dictParams
# TRIM=True/False, DELIMITER=","(def) FILE.IN=, FILE.OUT
# FIELDS[ucase,trimmato]. Se specificato viene utilizzato come confronto con quello da leggere
# Ritorna lResult. 0=RitornoStr, 1=Campi, 2=SchemaCompleto(OPZIOMALE o None), 3=dictTableCSV
# Params: FILE.IN=CSV, FIELDS=Array che ci deve essere, DELIMITER=Delimiter campi, TRIM=Trim Prima e dopo. QUOTE=Campo delimitatore testi
# ---------------------------------------------------------------------------------------
    def CSV_Read(dictParams):
        sResult=""
        sProc="Tab.CSV.Read"
        
    # Imposta FIELDS
        dictParams[FIELDS]=self.Fields()
    
    # Lettura
        lResult=NF_CSV_Read(dictParams)
        
    # Verifica
        sResult=lResult[0]
        
    # Copia in Table
        if sResult=="":
            dictTableCSV=lResult[3]
            anKeys=ntSys.NF_DictKeys(dictTableCSV)
            for nKey in anKeys:
                if nKey!=0:
                    avValues=dictTableCSV[nKey]
                    self.Append(avValues)
    # Uscita
        sResult=ntSys.NF_ErrorProc(sResult,sProc)
        return sResult
    
# WriteCSV. Ritorna sResult
# -----------------------------------------------------------------------------
    def CSV_Write(self, sFilename, sAttr):                
        sResult=""
        sProc="Tab.CSV.Write"
        
    # Imposta FIELDS
        dictParams["FIELDS"]=self.Fields()
    
    # Lettura
        lResult=ntDataFiles.NF_CSV_Write(dictParams, sFilename, sAttr)
        
    # Verifica
        sResult=lResult[0]
        
    # Copia in Table
        if sResult=="":
            dictTableCSV=lResult[3]
            anKeys=ntSys.NF_DictKeys(dictTableCSV)
            for nKey in anKeys:
                if nKey!=0:
                    avValues=dictTableCSV[nKey]
                    self.Append(avValues)
    # Uscita
        sResult=ntSys.NF_ErrorProc(sResult,sProc)
        return sResult

# Inizializzazione
# -----------------------------------------------------------------------------
    def __init__(self, asFields):
        sProc="Table.Init"
        self.avData.append(asFields)
        print(sProc + str(self.avData))