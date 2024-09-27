#
# ntDataJson: Conversions to/from json
#
import nlSys, nlDataFiles
import json

class NC_Json:
    dictData=dict()
    bSet=False

# Load JSON file to Dict
# Return lResult. 0=sResult, 1=dict
# ----------------------------------------------------------------------------------------
    def FileRead(self, sFile):
        sProc="JSON_Read"
        sResult=""
# Open File
        lResult=nlSys.NF_FileOpen(sFile, "r")
        sResult=lResult[0]
# Load JSON
        if (sResult==""):
            hFile=lResult[1]
            try:
                self.dictData=json.load(hFile)
                bSet=True
            except:
                sResult="lettura json"
# Write JSON file From Dict
# ----------------------------------------------------------------------------------------
    def Write(self, sFile, sAttr):
        sProc="JSON_Write"
        sResult=""

# Open File
        lResult=nlSys.NF_FileOpen(sFile, sAttr)
        sResult=lResult[0]

# Write JSON
        if sResult=="":
            hFile=lResult[1]
            try:
                self.dictData = json.load(hFile)
                bSet=True
            except:
                sResult="lettura json"

# Return Index to Key
# ----------------------------------------------------------------------------------------
    def Index(self, sKey):
        nResult=self.dictData[sKey][0]

# Len  0=Clear, -1=NotSet >0=Valori
# ----------------------------------------------------------------------------------------
    def Len(self):
        nResult=nlSys.NF_DictLen(self.dictData)

# -------------------------- DICTIONARY --------------------------------------------------

# Estrae Dictonary da JSON
    def DictTo(self):
        return self.dictData.copy()

# Aggiunge un altro dictionary a quello del JSON
    def DictAppend(self, dictJson):
        sResult=""
        sProc="JSON.DictAppend"

        if nlSys.NF_IsDict(dictJson) == False:
            sResult="no dict"
        else:
            nlSys.NF_DictMerge(self.dictData,dictJson)
# Ritorno
        return nlSys.NF_ErrorProc(sResult, sProc)

# Set da Altro dictionary
    def DictFrom(self, dictJson):
        sResult=""
        sProc="JSON.DictFrom"

        if nlSys.NF_IsDict(dictJson) == False:
            sResult="no dict"
        else:
            self.dictData=dictJson
# Ritorno
        return nlSys.NF_ErrorProc(sResult, sProc)

