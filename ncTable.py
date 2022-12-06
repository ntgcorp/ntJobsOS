# Classe Table in Array. Correlato a CSV
# -----------------------------------------------------------
import nlSys, nlDataFiles
from nlDataFiles import NC_CSV
class NC_Table:
# Campi
    avData=[]
    avFields=[]
    sFieldKey=""

# Set Valore in Matrice in base a KeyValue - Ritorna sResult
# -----------------------------------------------------------------------------
    def Set(self, vKeyValue, sField, vValue):
        sProc="Table.Set"

    # 2 Indici
        nIndex=self.Index(self.sFieldKey,sKeyValue)
        lResult=self.IndexField2(sKeyValue)
        nIndexField=lResult[1]
        sResult=lResult[0]
        if nIndex==-1: sResult=ntSys.NF_StrAppendExt(sResult, "Value non trovato: " + sKey)

    # Set o Errori
        if (sResult==""): avData[nIndex][nIndexField]=vValue

    # Uscita
        sResult=ntSys.NF_ErrorProc(sResult,sProc)
        return sResult

# Set Array Righe x Colonne - Ritorna sResult
# -----------------------------------------------------------------------------
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
    def Get2(self, sKey, vKeyValue, sField):
        sProc="Table.Get2"
        sResult=""

    # Cerca Index in Tabella
        nIndex=self.IndexField(sField)
        if nIndex==-1: sResult="Field non trovato: " + sField
        sResult=ntSys.NF_ErrorProc(sResult,sProc)

    # Valore
        if sResult=="":
            lResult=self.Get(sKey,vKeyValue,nIndex)
        else:
            lResult=[sResult,""]

    # Uscita
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

# ???
# -----------------------------------------------------------------------------
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
        sProc="Table.Row.Add"
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
        sProc="Table.Row.Delete"
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

# Esiste Riga con Valore Key v -1=No, Oppure >0
# -----------------------------------------------------------------------------
    def Index(self, sKey, vKeyValue):
    # Setup
        nResult=-1
    # Ricerca
        for sField in self.asFields():
            if sField==sKey:
                break
            else:
                nResult=nResult+1

    # Uscita
        return nResult

# ?????
# -----------------------------------------------------------------------------
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
# -----------------------------------------------------------------------------
    def IndexField2(self, sKey):
        sResult=""
        lResult=self.IndexField(vKey)
        if nIndexField==-1: sResult="Key non trovato: " + str(sKey)
        lResult[0]=sResult
        lResult[1]=nIndexField
        return lResult

# Numero Records
# -----------------------------------------------------------------------------
    def Len(self):
        if self.avData==None: return -1
        return len(self.avData)

# Numero Campi
# -----------------------------------------------------------------------------
    def FieldsLen(self):
        return len(self.asFields)

# Print
# -----------------------------------------------------------------------------
    def Print(self):
        sResult=""
        x=0
        for x in range(self.Len()):
            sResult=ntSys.NF_StrAppendExt(sResult, str(self.avData[x]) + "\n")
        return sResult

# From Table to CSV
# ---------------------------------------------------------------------------------------
    def CSV_TableToDict():
    # Conversione
        objCSV=NC_CSV
        objCSV.asFields = self.Fields
        objCSV.avTable=self.avData
        objCSV.sFieldKey=self.

#  From CSV_DICT to Table
# -----------------------------------------------------------------------------
    def CSV_DictToTable(self, dict):
    # Conversione
        self.avData=dict["DATA"]
        self.Fields=dict["HEADER"]

# Inizializzazione
# -----------------------------------------------------------------------------
    def __init__(self, asFields, sFieldKey=""):
        sProc="Table.Init"
        self.asFields=asFields
        self.avData=[]
        self.sFieldKey=sFieldKey
