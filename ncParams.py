import os
import re

class NC_Params:
    sDELIM_MAIL = ';'
    sDELIM_PATH = ';'
    
    def __init__(self):
        self.Reset()
    
    def Reset(self):
        self.dictInput = {}
        self.dictCheck = {}
        self.sParamInput = ""
        self.sParamCheck = ""
        self.sCheck = ""
        self.sValue = ""
        self.sAttr = ""
        self.sType = ""
        self.bMandatory = True
        self.bList = False
        self.bCheckList = False
        self.sList = ""
        self.asList = []
        self.sResult = ""
        self.dictResult = {}
    
    def Check(self, dictInputTemp, dictOutputTemp):
        sProc = "Check"
        self.Reset()
        self.dictInput = dictInputTemp
        self.dictCheck = dictOutputTemp
        
        for self.sParamInput in self.dictInput:
            if self.sParamInput == "G":
                continue
                
            self.sValue = str(self.dictInput[self.sParamInput])
            
            for self.sParamCheck in self.dictCheck:
                self.sCheck = str(self.dictCheck[self.sParamCheck])
                self.Scompose()
                self.CheckType()
                
                if len(self.dictResult) > 0:
                    self.sResult = str(self.dictResult)
                    return self.sResult
                    
        return self.sResult
    
    def Scompose(self):
        sProc = "Scompose"
        self.sCheck = self.sCheck.strip()
        
        # Extract attributes
        attr_part = ""
        while len(self.sCheck) > 0 and not self.sCheck[0].isalpha():
            attr_part += self.sCheck[0]
            self.sCheck = self.sCheck[1:]
        
        self.sAttr = attr_part
        self.sType = self.sCheck[0].upper() if len(self.sCheck) > 0 else ""
        self.sCheck = self.sCheck[1:]
        
        self.sList = ""
        self.asList = []
        
        if len(self.sCheck) > 0:
            if self.sCheck[0] == ':':
                self.sCheck = self.sCheck[1:]
                self.sList = self.sCheck
                self.asList = [item.strip() for item in self.sList.split(',')]
            else:
                self.sResult = f"Formato sbagliato per {self.sParamInput}, {sProc}"
                return self.sResult
        
        self.Attr()
        return self.sResult
    
    def CheckType(self):
        sProc = "CheckType"
        self.sValue = str(self.dictInput.get(self.sParamInput, ""))
        sCheckError = ""
        
        # Type checks
        if self.sType == "N":
            if not self.sValue.isdigit():
                sCheckError = "Controllo errato N"
        elif self.sType == "F":
            try:
                float(self.sValue)
            except ValueError:
                sCheckError = "Controllo errato F"
        elif self.sType == "D":
            if not self.sValue.isalpha() or not self.sValue.isupper():
                sCheckError = "Controllo errato D"
        elif self.sType == "I":
            try:
                int(self.sValue)
            except ValueError:
                sCheckError = "Controllo errato I"
        elif self.sType == "B":
            if self.sValue.lower() not in ["true", "false", "1", "0"]:
                sCheckError = "Controllo errato B"
        elif self.sType == "A":
            if not self.sValue.isalnum():
                sCheckError = "Controllo errato A"
        elif self.sType == "S":
            if len(self.sValue) != 1 or ord(self.sValue) < 33 or ord(self.sValue) > 47:
                sCheckError = "Controllo errato S"
        elif self.sType == "C":
            if len(self.sValue) != 1 or not (
                (33 <= ord(self.sValue) <= 47) or 
                ('a' <= self.sValue <= 'z') or 
                ('A' <= self.sValue <= 'Z')
            ):
                sCheckError = "Controllo errato C"
        elif self.sType == "X":
            try:
                self.sValue.encode('ascii')
            except UnicodeEncodeError:
                sCheckError = "Controllo errato X"
        elif self.sType == "M":
            if not re.match(r"[^@]+@[^@]+\.[^@]+", self.sValue):
                sCheckError = "Controllo errato M"
        elif self.sType == "M0":
            emails = self.sValue.split(self.sDELIM_MAIL)
            for email in emails:
                if not re.match(r"[^@]+@[^@]+\.[^@]+", email.strip()):
                    sCheckError = "Controllo errato M0"
                    break
        elif self.sType == "Z0":
            paths = self.sValue.split(self.sDELIM_PATH)
            for path in paths:
                if not re.match(r"^[a-zA-Z]:[\\/](?:[^\\/]+[\\/])*[^\\/]+$", path.strip()):
                    sCheckError = "Controllo errato Z0"
                    break
        elif self.sType == "H":
            if not re.match(r"https?://[^\s/$.?#].[^\s]*", self.sValue):
                sCheckError = "Controllo errato H"
        elif self.sType == "F":
            if not os.path.isfile(self.sValue):
                sCheckError = "Controllo errato F"
        elif self.sType == "Z":
            if not re.match(r"^[a-zA-Z]:[\\/](?:[^\\/]+[\\/])*[^\\/]+$", self.sValue):
                sCheckError = "Controllo errato Z"
        else:
            sCheckError = f"Tipo di controllo sconosciuto: {self.sType}"
        
        # Mandatory check
        if self.bMandatory and not self.sValue:
            sCheckError = "Parametro obbligatorio " + sCheckError
        
        # List check
        if self.bList and self.asList and self.sValue not in self.asList:
            sCheckError = "Parametro non trovato in stringa " + sCheckError
        
        if sCheckError:
            error_msg = f"Parametro {self.sParamInput} non soddisfa il controllo: {sCheckError}, {sProc}"
            self.dictResult[self.sParamInput] = error_msg
            self.sResult = error_msg
        
        return self.sResult
    
    def Attr(self):
        sProc = "Attr"
        self.bList = False
        self.bMandatory = True
        self.bCheckList = False
        
        if '*' in self.sAttr:
            self.bMandatory = False
        if '!' in self.sAttr:
            self.sValue = self.sValue.strip().upper()
        if '@' in self.sAttr:
            self.bCheckList = True
        if self.sList:
            self.bList = True
        
        return self.sResult