#-------------------------------------------------------------------------------
# Name:  ncExpert
# Stato: MODULO DI RISOLUZIONE PROBLEMI IN MODALITA' DATA EXPERT
# Uso:
# 1: Chiamare la INIT,
#    Obbligatorio parametro asKeysFrom() con chiavi necessarie calcolate per concludere il sistema
#    Chiavi già presenti (start come dict) - Facoltativo
# 2: Fare un Loop dove si impostano le regole testando l'esistenza della chiave con Get() che ritorna due parametri e la Set() per impostare la chiave
#     GetZero se sufficiente chiave con valore zero o GetNull con valore ""
# 3: Chiamare la LoopTest a fine giro e se bExit=True esci dal loop
# 4: self.dictK{} contiene le chiavi calcolate e self.asLog[] contiene il log di calcolo
#-------------------------------------------------------------------------------
# IN TEST
# Interface to Panda with debug & errors management
# -----------------------------------------------------------------------
import nlSys
bDebug=True

# ----------------------- CLASSI ---------------------------
# EXPERT CLASS
class NC_EXPERT():
    dictK={}               # Dict Chiavi da risolvere, dove Valore None=Non Risolto
    asKeys=[]              # Lista Chiavi attuali da dict - - Aggiornato solo da LoopTest
    dictKn={}              # Note per chiavi risolte
    asKeysFrom=[]          # (keys) Lista Chiavi da risolvere "obbligatoriamente"
    asKeysTo=[]            # Lista Chiavi Risolte
    nLoops=0               # Loops Effettuati
    nKeysTo_last=0         # Chiavi risolte nell'ultimo loop
    nKeysTo=0              # Chiavi Risolte (come len asKeyTo) - Aggiornato solo da LoopTest
    nKeysFrom=0            # Chiavi da Risolvere
    bLoopC=False           # Cambiamenti avventui nell'ultimo loop da testare ad ogni loop -
    bNotResolved=False     # Sistema non Risolvibile
    bResolved=False        # Sistema Risolto
    bEnd=False             # Sistema non continuabile
    asLog=[]               # Loop Log
    bInit=False            # Non inizializzato (da cambiare Init con parametri vari)

# -------------- METODI --------------
    def __init__(self):
        pass

# Set di una chiave risolta o aggiunta di altra chiave
# ---------------------------------------------------------------
    def Set(self,sKey,vValue):
        self.dictK[sKey]=vValue

# Get di una chiave. Ritorna "esistenza=True, valore"
# ---------------------------------------------------------------
    def Get(self, sKey):
        vResult=None
        vValue=None
        bExist=False
# Esistenza Chiave
        if nlSys.NF_DictExistKey(sKey): bExist=True
# Prende valore
        if self.bExist: vResult=self.dictK(sKey)
# Ritorno
        return bExist,vValue

# GetZero: Ritorna un solo numero anche se chiave non esiste
    def GetToZero(self, sKey):
        bExist,vValue=self.Get(sKey)
        return nlSys.iif(bExist, vValue, 0)

# GetZero: Ritorna "" solamente se non esiste
    def GetToNull(self, sKey):
        bExist,vValue=self.Get(sKey)
        return nlSys.iif(bExist, vValue, "")

# Inizializzazione chiave
# ----------------------------------------------------------------
    def Init(self, **kwargs):
        sProc="EXP.Loop"
        sResult=""

# Argomenti opzionali
        for key, value in kwargs.items():
            if key=='keys':
                self.asKeysFrom=value
                self.bInit=True
            elif key=='notes':
                self.asKeysN=value
                self.bInit=True
            elif key=='values':
                self.dictK=value
                if self.bInit==False:
                    self.asKeysFrom=self.dictK.keys
                    self.bInit=True
            else:
                sResult="Parameter invalid " + key
# Uscita
        sResult=nlSys.NF_ErrorProc(sResult,sProc)

# ----------------------------- Loop ----------------------------
    def Loop(self):
        sProc="EXP.Loop"
        sResult=""

# Verifiche
        if self.bInit==False: sResult="Expert data not init"
# Loop . Uscita se non ci sono stati cambiamenti ma giro maggiore di 1 o errori
        if sResult=="":
            while ((self.nLoopC == False) and (self.nLoops>0)) or (sResult != ""):
# Increment numero Lops e Reset Cambiamenti
                self.nLoops += 1
                self.nLoopC=False
# Per ogni chiave verifica se è stata risolta vedendo la lista dei risolti
                self.asKeys=self.dictK.keys()
                for sKey in self.asKeysFrom:
                    vValue=self.dictK[sKey]
# Se chiave risolta guardare se non è in lista risolte
                    if vValue != None:
                        if nlSys.NF_ArrayFind(self.asKeysTo, sKey)==False:
# Se non è in lista risolte, attiva processo aggiunta chiave risolte
                            sResult=self.LoopResolved((sKey))
# Test Fine loop - Esce se Errori
                sResult=self.LoopTest()
                if sResult != "": break
                nlSys.NF_DebugFase(bDebug,"EXP Loop. C: " + str(self.nLoops)  + ", K.Res: " + str(self.nKeysTo), sProc)
# Uscita
        sResult=nlSys.NF_ErrorProc(sResult,sProc)

# Chiave Risolta
# ---------------------------------------------------------------
    def LoopResolved(self, sKey):
        sProc="EXP.Loop"
        sResult=""

# Flag cambiamenti avvenuti
        self.nLoopC=True
# Aggiunta chiave alla lista di Risolte
        self.asKeysTo.append(sKey)
        self.nKeysTo_last += 1
# Log
        if nlSys.NF_DictExistKey(self.asKeysN):
            self.LoopLog(sKey,"Resolved: " + self.asKeysN[sKey])
# Uscita
        sResult=nlSys.NF_ErrorProc(sResult,sProc)

# Test di fine Looop
# Esce con 2 ritorni
# 1: sResult, 2: bExit (Esce in caso di errore o non risolvibile o risolto)
# --------------------------------------------------------------------------
    def LoopTest(self):
        sProc="EXP.Test"
        sResult=""

# Incremento Risolti, Aggiornamento Chiavi Risolte e da Risolvere (se si incrementano chiavi nel durante)
        self.nKeysTo += self.nKeysTo_last
        self.nKeysFrom=self.asKeysFrom.keys()
# Sistema Risolto per numero chiavi da risolvere = numero chiavi risolte
        if self.nKeysTo==self.nKeysFrom:
            self.bResolved=True
            self.LoopLog("","Resolved")
# Sistema non risolvibile per chiavi non cambiate da ultimo loop e nemmeno flag di cambiamenti
        if (self.nKeysTo_last==0) and (self.bLoopC==False):
            self.bNotResolved=True
            self.LoopLog("","Not Resolvable")
# Test Errore
        if sResult != "": self.bNotResolved=True
# Uscita
        bExit=self.bNotResolved or (sResult != "") or (self.bResolved)
        sResult,bExit=nlSys.NF_ErrorProc(sResult,sProc)

# Loop Log
# ---------------------------------------------------------------
    def LoopLog(self, sKey="", sNote=""):
        sResult=nlSys.NF_TS_ToStr() + ": " + sKey + ", N: " + sNote
        return sResult
