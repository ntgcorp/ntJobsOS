# Classe Table in Array 2x 1=Record, 2=ColonneInRecord. Correlato a CSV
# Gestione di record cancellati, Ordinamento tramite campo chiave o singolo campo,
# inserimento, cancellazione di record, compattazione, Sort Chiave/Tabella/Campo
# Campo Indice OBBLIGATORIO (eventualmente creare un campo ID progressivo con range())
# Nomi dei campi "case sensitive" e ora ricerche "case sensitive"
# Gestione OBBLIGATORIA con un Index che serve a tener conto ordinamento e record cancellati.
# Con Sort() avviene anche IndexUpdate
# DA COMPLETARE
# - SORT
# - Load/Save tabella da DB (sqLite/mySql) gestito solo da classe NC_DB
# History:
# 202308: Prima versione
# 202407: Aggiunto GetRecord
# -----------------------------------------------------------------------------
import nlSys, nlDataFiles
from nlDataFiles import NC_CSV

class NC_Table:
# Campi
    avData=[]      # Tabella
    avFields=[]    # Nomi dei Campi (correlato a sFieldKey)
    sFieldKey=""   # Campo Chiave - DEVE ESSERE PRESENTE in avFields
    sResult=""     # Stato Interno. ""=OK, Altrimenti ERRORE
    IndexKey=-1    # Posizione Campo Indice in avFields- OBBLIGATORIO SPECIFICARLO E CHE SIA TRA I FIELDS
    dictIndex={}   # Indice Chiave->Indice (al netto dei record cancellati). Aggiornato con IndexUpdate()

# Inizializzazione
# -----------------------------------------------------------------------------
    def __init__(self, asFields, sFieldKey):
        sProc="Table.Init"

        self.asFields=asFields
        self.avData=[]
        self.sFieldKey=sFieldKey
        self.nIndexKey=nlSys.NF_ArrayFind(self.asFields,self.sFieldKey)
        if nlSys.NF_ArrayLen(self.asFields): self.sResult="Invalid Array Fields"
        if self.nIndexKey == -1: self.sResult="Key name not valid: " + sFieldKey

# Set Valore in Matrice in base a KeyValue - Ritorna sResult. Singola cella
# -----------------------------------------------------------------------------
    def SetValue(self, vKeyValue, sField, vValue):
        sProc="Table.Set.Value"

    # Trova Riga
        nIndex=self.Find(vKeyValue)
        if nIndex==-1: sResult="Key Value non trovato: " + str(vKeyValue)

    # Trova Riga con Index
        if sResult == "":
            lResult=self.IndexField2(sField)
            nIndexField=lResult[1]
            sResult=lResult[0]

    # Set Valore in Riga,Campo
        if sResult == "": self.avData[nIndex][nIndexField]=vValue

    # Uscita
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        self.sResult=sResult
        return sResult

# Set Valore in Matrice in base a Valore Campo Chiave Per Riga e Poi Altro Camp - Ritorna sResult. Singola cella
# -----------------------------------------------------------------------------
    def SetMatrix(self, sKeyName, vKeyValue, sField, vValue):
        sProc="Table.Set.Matrix"

    # Trova Riga
        nIndex=self.Find(vKeyValue)
        if nIndex==-1: sResult="Key Value non trovato: " + str(vKeyValue)

    # Set Field in riga
        if sResult == "":
            lResult=self.IndexField2(sField)
            nIndexField=lResult[1]
            sResult=lResult[0]

    # Set o Errori
        if (sResult == ""): self.avData[nIndex][nIndexField]=vValue

    # Uscita
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        self.sResult=sResult
        return sResult

# Index Update - Verifica che non ci siano chiavi doppie
# -----------------------------------------------------------------------------
    def IndexUpdate(self):
    # Recupera Posizione CampoChiave + Reset dictIndex
        nIndexKey=self.nIndexKey
        self.dictIndex={}
    # Ricostruisce dizionario indice
        for nF1 in range(0,self.Len()-1):
            sKey=self.avTable[nF1][nIndexKey]
            if nlSys.NF_DictExists(self.dictIndex,sKey):
                self.dictIndex[sKey]=nF1
            else:
                sResult="Error key exist: " + sKey
                break
    # Fine
        return sResult

# Set Array Righe x Colonne - Ritorna sResult
# Parametri:
# avTable: Array Righe/Colonne Dati
# asFields: Nomi dei campi
# asFieldIndex: Nome del campo Index "obbligatorio"
# DA COMPLETARE CON VERIFICHE
# -----------------------------------------------------------------------------
    def SetArray(self, avTable, asFields, sFieldIndex):
        sProc="Table.SetArray"

    # Verifiche
        nIndex=len(self.avTable)

        if nIndex != -1:
            self.avData=avTable.copy()
            self.IndexUpdate()
        else:
            sResult="Index errato source"

    # Uscita
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        self.sResult=sResult
        return sResult

# Set Singola Riga. Ritorna sResult
# Se Chiave non esiste effettua un Append.
# Elementi devono essere stessa dimensione Record o ritorna Errore
# -----------------------------------------------------------------------------
    def SetRow(self, avTable):
        sProc="Table.SetRow"
        sResult=""

    # Verifica dimensione Record da modificare o aggiiungere
        if nlSys.NF_ArrayLen(avTable) != nlSys.NF_ArrayLen(self.asFields): sResult="Dimensione diversa n.valori e n.campi " + str(avTable)

    # Ricerca Riga
        if sResult=="":
            sKey=avTable[self.nIndexKey]
            nIndex=self.Find(sKey)
    # Aggiung Riga o sostituisce
            if nIndex==-1:
                sResult=self.Append(avTable)
                # Update Index
                if self.bIndex: self.dictIndex[sKey]=self.len()-1
            else:
                self.avData[nIndex]=avTable.copy()
    # Uscita
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        self.sResult=sResult
        return sResult

# Get in Matrice. Ritorna lResult, 0=Result, 1=Valore
# -----------------------------------------------------------------------------
    def Get(self, sKey, vKeyValue, nIndex):
        sProc="Table.Get"
        sResult=""
        vValue=""
    # Ricerca Indice e controllo dimensione riga. Controllo indice non
        lResult=self.IndexField2(sKey)
        sResult=lResult[0]
        nIndexField=lResult[1]
    # Test Index
        sResult=nlSys.NF_StrAppendText(sResult,self.IndexTest(nIndex))
    # GetValore
        if sResult=="": vValue=self.avData[nIndex][nIndexField]
    # Uscita
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        self.sResult=sResult
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
        sResult=nlSys.NF_ErrorProc(sResult,sProc)

    # Valore
        if sResult=="":
            lResult=self.Get(sKey,vKeyValue,nIndex)
        else:
            lResult=[sResult,""]

    # Uscita
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        self.sResult=sResult
        return sResult

# Get Record. In base a key=keyValue ritorna dict con campo=valore
# Ritorna lResult. 0=Errore, 1=Posizione Record Trovato 0..N-1, -1=NonTrovato, 2=record come dict
# Parametri, key, KeyValue, Opzionali: type=(0=key, 1=index)
# -----------------------------------------------------------------------------
    def GetRecord(self, vKey, sKeyValue, **kwargs):
        sProc="Table.Get.Record"
        sResult=""
        dictRecord={}
        nType=0

# Argomenti opzionali
        for key, value in kwargs.items():
            if key=='type':
                nType=value

    # Ricerca INDICE RECORD
        if nType==1:
            nIndex=vKey
        else:
            lResult=self.Index(key, value)
            sResult=lResult[0]
            if sResult=="": nIndex=lResult[1]

    # Estrazione Record CON INDICE
        if sResult=="" and (nIndex>-1):
            lResult=self.GetRow(nIndex)
    # Conversione Record in dict
        if sResult=="":
            lResult=nlSys.NF_DictFromArr(self.Keys(),self.avData)
            sResult=lResult[0]
    # Prende Record
        if sResult=="":
            dictRecord=lResult[1].copy

    # Uscita
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        self.sResult=sResult
        lResult=[sResult,nIndex,dictRecord]
        return lResult


# Get in Matrice. Ritorna lResult, 0=sResult, 1=Array di Valori di una riga
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
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        self.sResult=sResult
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
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        self.sResult=sResult
        return sResult

# Fill every record with value. Return sResult
# -----------------------------------------------------------------------------
    def FillCol(self, sFieldName, vValue=None):
        sProc="Table.Fill.Col"
        sResult=""

    # Non per IndexField
        if (sFieldName==self.sFieldKey): sResult="No FieldKey"

    # Test Colonna
        lResult=self.IndexField2(sFieldName)
        sResult=lResult[0]

    # Set Every Col
        if sResult=="":
            nRows=self.Len()
            if (sResult=="") and (nRows>0):
                nIndexField=lResult[1]
                for nIndex in range(nRows):
                    self.avData[nIndex][nIndexField]=vValue

    # Uscita
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        self.sResult=sResult
        return sResult

# Get Colonna. Return lResult 0=sResult, 1=ArrayRecords_one_field
# Senza Record Cancellati
# -----------------------------------------------------------------------------
    def GetCol(self, vKey):
        sProc="Table.Get.Col"
        sResult=""
        avRows=[]

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
                avRows.append(vRecord)

    # Uscita
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        self.sResult=sResult
        lResult=[sResult,avRows]
        return lResult

# Append di un Array alla tabella (con controllo ci sia lo stesso numero di campi. Ritorna sResult)
# Fa anche UPDATE()
# ------------------------------------------------------------------------------------------------
    def Append(self, avValues):
        sProc="Table.Row.Add"
        sResult=""

    # Verifica len fields
        if self.FieldsLen() != nlSys.NF_ArrayLen(avValues): sResult="Dimensione diversa"

    # Verifica che la chiave non ci sia già'
        sKey=nlSys.NF_NullToStr(avValues,self.IndexKey)

    # Aggiunta delle'Array di valori alla tabella
        if sResult == "": self.avData.append(avValues)

    # Aggiorna indice 1: Prende Chiave, Nuova Len, Indice
        if sResult == "":
            nNewLen=nlSys.NF_ArrayLen(self.avData)

    # Update
        sResult=self.Update()

    # Uscita
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        self.sResult=sResult
        return sResult

# Remove Riga in base a Key - Rimuove anche da Indice
# -----------------------------------------------------------------------------
    def Remove(self, sKey, vKeyValue):
        sProc="Table.Row.Delete"
        nIndex=self.Len()

    # Ricerca e Rimozione
        if nIndex>0:
            nIndex=self.Index(sKey,vKeyValue)
            if nIndex>0:
                self.avData.remove[nIndex]
                self.dictIndex.remove(sKey)
        else:
            sResult="Errore Array Index " + str(nIndex)

    # Ritorno
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        self.sResult=sResult
        return sResult

# Cerca Riga Record in Tabella. -1=No, Oppure>=0
# -----------------------------------------------------------------------------
    def Find(self, vKeyValue):
    # Setup
        nResult=-1

    # Ricerca
        for sField in self.avFields:
            if sField==self.sFieldKey: break            
            nResult=nResult+1

    # Uscita
        return nResult

# Come Find ma su qualunque campo della Tabella v -1=No, Oppure>=0
# -----------------------------------------------------------------------------
    def Index(self, sKey, vKeyValue):
    # Setup
        nResult=-1

    # Ricerca
        for sField in self.avFields:
            if sField==self.sFieldKey:
                break
            else:
                nResult=nResult+1
    # Uscita
        return nResult

# Come IndexField ma ritorna stringa con errore
# -----------------------------------------------------------------------------
    def IndexTest(self,nIndex):
        sProc="TABLE.INDEX.TEST"
        sResult=""

        if nIndex<0 or (not nlSys.NF_Range(nIndex, 0, self.Len())): sResult="Valore non trovato: " + str(self.sFieldKey)
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        return sResult

# Trova numero colonna corrispondente a stringa sKey come nome campo. v. -1=No, Oppure >=0
# --------------------------------------------------------------------------------------------------
    def IndexField(self, sKey):
    # Indice
        nIndex=nlSys.NF_ArrayFind(self.avFields(), sKey)
    # Fine
        return nIndex

#
# Come self.IndexField ma invece di numero ritorna lResult (per usi ritorno vari), dove 0=sResult, 1=Index campo
# -------------------------------------------------------------------------------------------------------
    def IndexField2(self, sKey):
        sProc="IndexField2"
        sResult=""

        sKey=str(sKey)
        lResult=self.IndexField(sKey)
        if self.nIndexField==-1: sResult="Key non trovato: " + sKey

    # Uscita
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        self.sResult=sResult
        lResult=[sResult, self.nIndexField]
        return lResult

# Numero Records. -1=NonEsistente 0=Vuoto, Altrimenti >0
# -----------------------------------------------------------------------------
    def Len(self):
        return nlSys.NF_ArrayLen(self.avData)

# Numero Campi. -1=Errore, 0=Vuoto, Altrimenti >0
# -----------------------------------------------------------------------------
    def FieldsLen(self):
        return nlSys.NF_ArrayLen(self.asFields)

# Print
# -----------------------------------------------------------------------------
    def StrPrint(self):
        sResult=""
        x=0
        sResult=self.asFields.join(",") + "\n"
        for x in range(self.Len()):
            sResult=nlSys.NF_StrAppendExt(sResult, str(self.avData[x]) + "\n")
        return sResult

# From Table to CSV
# Ritorno lResult 0=sResult, 1=Oggetto CSV
# ---------------------------------------------------------------------------------------
    def CSV_TableToDict(self):
        sResult=""
        sProc="TABLE.TO.CSV"

    # Conversione
        objCSV=NC_CSV()
        objCSV.asFields = self.Fields
        objCSV.avTable=self.avData
        objCSV.sFieldKey=self.sFieldKey

    # Uscita
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        self.sResult=sResult
        return [sResult,objCSV]

#  From objCSV to Table
#  dictTable con 3 Entry. DATA=Dati, HEADER=Campi Header, FIELDKEY=Campo Chiave
#  Ritorno sResult=Errori eventuali
#  DA COMPLETARE con CONTROLLI
# -----------------------------------------------------------------------------
    def CSV_DictToTable(self, objCSV):
        sResult=""
        sProc="CSV.TO.TABLE"

    # Conversione
        try:
            self.avData=objCSV.avTable.copy()
            self.avFields=objCSV.avFields.copy()
            self.sFieldKey=objCSV.sFieldKey
        except:
            sResult="Errore conversione da CSV a TABLE"

    # Uscita
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        self.sResult=sResult
        return sResult

# Sort Table
# Input: Mode(K=Key, F=Field, KR=KeyReverse, FR=FieldReverse), Optional sField Sort(se Mode="K")
# DA COMPLETARE
# ------------------------------------------------------------------------------
    def Sort(self, sMode="K", sField=""):
        sResult=""
        avKeySort=[]

# Verifiche
        if (sMode=="K") or (sMode=="") or (sMode=="KR"):
            avKeySort=self.Keys()
        elif (sMode=="F") or (sMode=="FR"):
            lResult=self.GetCol(sField)
            sResult=lResult[0]
            if sResult=="": avKeySort=lResult[1]
        else:
            sResult="Mode not valid " + str(sMode)

# Check avKeySort
        if sResult=="":
            nLen=nlSys.NF_ArrayLen(avKeySort)
            if nLen<1: sResult="Table Empty"

# Dictionary Keys->Index
        if sResult == "":
            dictKeys=nlSys.NF_DictFromArray(avKeySort,avKeySort)
            for nF1 in range(0,nLen-1):
                dictKeys[nF1]=nF1
# Sort Dictionary
#     dictParams (Input), sMode (K o "": Keys, "V"=Values), "KR"=Key/Reverse, "VA"=Value/Reverse
# Result: lResult (0=Status, 1=NewDictionaryResultSorted)
# -------------------------------------------------------------------------------------
            lResult=nlSys.NF_DictSort(dictKeys,sMode)

# Uscita
        return sResult

# Keys
# ID campo Keys da avData
# DA VERIFICARE
# ------------------------------------------------------------------------------
    def Keys(self):
        sProc="Table Keys"
        sResult=""

    # Prende colonna campo chiave
        nIndexKey=self.IndexKey
        lResult=self.GetCol(nIndexKey)

    # uscita
        return nlSys.NF_Result(lResult[0],sProc,lResult[1])

