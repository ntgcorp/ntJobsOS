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
    def FileRead(sFile):
        sProc="JSON_Read"
        sResult=""
# Open File
        lResult=NF_FileOpen(sFile, "r")
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
    def Write(sFile, sAttr):
        sProc="JSON_Write"
        sResult=""

# Open File
        lResult=NF_FileOpen(sFile, sAttr)
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
    def Index(sKey):
        nResult=dictData[sKey][0]

# Len  0=Clear, -1=NotSet >0=Valori
# ----------------------------------------------------------------------------------------
    def Len():
        nResult=ntSys.NF_DictLen(self.dictData)

