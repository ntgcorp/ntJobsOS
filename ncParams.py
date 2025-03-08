class NC_Params:
    def __init__(self, dictInputemp=None, dictOutputtemp=None):
        self.dictInput = dictInputemp if dictInputemp is not None else {}
        self.dictCheck = dictOutputtemp if dictOutputtemp is not None else {}
        self.sParamInput = ""
        self.sParamCheck = ""
        self.sCheck = ""
        self.sValue = ""
        self.sAttr = ""
        self.sType = ""
        self.bMandatory = True  # Default è True
        self.bList = False
        self.bCheckList = False
        self.sList = ""
        self.asList = []
        self.sResult = ""
        self.dictResult = {}

    def Check(self):
        self.sProc = "Check"
        self.dictResult = {}
        
        for self.sParamInput in self.dictInput:
            self.sValue = self.dictInput[self.sParamInput]
            
            for self.sParamCheck in self.dictCheck:
                self.sCheck = self.dictCheck[self.sParamCheck]
                self.Scompose()
                self.CheckType()
                
                if len(self.dictResult) > 0:
                    self.sResult = str(self.dictResult)
                    return self.sResult
        
        return self.sResult

    def Scompose(self):
        self.sProc = "Scompose"
        self.sCheck = self.sCheck.strip()
        self.sAttr = ""
        self.sType = ""
        self.sList = ""
        self.asList = []
        
        # Estrai sAttr (caratteri non alfabetici all'inizio)
        for char in self.sCheck:
            if not char.isalpha():
                self.sAttr += char
            else:
                break
        
        # Estrai sType (primo carattere alfabetico)
        if len(self.sCheck) > len(self.sAttr):
            self.sType = self.sCheck[len(self.sAttr)].upper()
        
        # Estrai sList (se presente)
        remaining = self.sCheck[len(self.sAttr) + 1:]
        if remaining:
            if remaining[0] == ":":
                self.sList = remaining[1:]
                self.asList = [item.strip() for item in self.sList.split(",")]
            else:
                self.sResult = f"Formato sbagliato per {self.sParamInput}, {self.sProc}"
                return self.sResult
        
        self.Attr()
        return self.sResult

    def CheckType(self):
        self.sProc = "CheckType"
        self.sCheckError = ""
        
        # Controllo del tipo
        if self.sType == "N":
            if not self.sValue.isdigit() or int(self.sValue) < 0:
                self.sCheckError = "Controllo errato N"
        elif self.sType == "F":
            try:
                float(self.sValue)
            except ValueError:
                self.sCheckError = "Controllo errato F"
        elif self.sType == "D":
            if not self.sValue.isalpha() or not self.sValue.isupper():
                self.sCheckError = "Controllo errato D"
        elif self.sType == "I":
            try:
                int(self.sValue)
            except ValueError:
                self.sCheckError = "Controllo errato I"
        elif self.sType == "B":
            if self.sValue.lower() not in ["true", "false", "1", "0"]:
                self.sCheckError = "Controllo errato B"
        elif self.sType == "A":
            if not self.sValue.isalnum():
                self.sCheckError = "Controllo errato A"
        elif self.sType == "S":
            if not (33 <= ord(self.sValue) <= 47):
                self.sCheckError = "Controllo errato S"
        elif self.sType == "C":
            if not (33 <= ord(self.sValue) <= 47 or 97 <= ord(self.sValue) <= 122 or 65 <= ord(self.sValue) <= 90):
                self.sCheckError = "Controllo errato C"
        elif self.sType == "X":
            if not (0 <= ord(self.sValue) <= 127):
                self.sCheckError = "Controllo errato X"
        elif self.sType == "M":
            if "@" not in self.sValue or "." not in self.sValue:
                self.sCheckError = "Controllo errato M"
        elif self.sType == "H":
            if not self.sValue.startswith("http://") and not self.sValue.startswith("https://"):
                self.sCheckError = "Controllo errato H"
        elif self.sType == "F":
            import os
            if not os.path.isfile(self.sValue):
                self.sCheckError = "Controllo errato F"
        elif self.sType == "Z":
            import os
            if not os.path.exists(self.sValue):
                self.sCheckError = "Controllo errato Z"
        
        # Controllo obbligatorietà
        if self.bMandatory and not self.sValue:
            self.sCheckError += " Parametro obbligatorio"
        
        # Controllo lista
        if self.bList and self.sValue not in self.asList:
            self.sCheckError += " Parametro non trovato in stringa"
        
        # Controllo bCheckList
        if self.bCheckList and self.sValue not in self.asList:
            self.sCheckError += " Parametro non trovato nella lista di verifica"
        
        # Assegna errore se necessario
        if self.sCheckError:
            self.dictResult[self.sParamInput] = f"Parametro {self.sParamInput} non soddisfa il controllo: {self.sCheckError}, {self.sProc}"
        
        return self.sResult

    def Attr(self):
        self.sProc = "Attr"
        self.bList = False
        self.bMandatory = True  # Default è True
        self.bCheckList = False
        
        if "*" in self.sAttr:
            self.bMandatory = False
        if "!" in self.sAttr:
            self.sValue = self.sValue.strip().upper()
        if "@" in self.sAttr:
            self.bCheckList = True
        if self.sList:
            self.bList = True
        
        return self.sResult