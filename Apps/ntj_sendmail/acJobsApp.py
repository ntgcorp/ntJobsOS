"""
acJobsApp.py - Orchestratore per applicazioni ntJobsApp
File unico e autocontenuto. Zero dipendenze esterne.
"""
import os
import sys
import configparser
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# =============================================================================
# COSTANTI E VARIABILI GLOBALI
# =============================================================================
NTJOBSAPP_VER = "2024102412"  # Formato YYYYMMDDHH (statico, come da specifica)

# =============================================================================
# FUNZIONI DI SUPPORTO INGLOBATE (ex aiSys)
# =============================================================================

def NormalizePath(sPath: str) -> str:
    """Normalizza i separatori di percorso in base al SO."""
    if not sPath: return ""
    if sys.platform == "win32":
        return os.path.normpath(sPath.replace("/", os.sep))
    else:
        return os.path.normpath(sPath.replace("\\", os.sep))

def ErrorProc(sResult: str, sProc: str) -> str:
    if sResult:
        return f"{sProc}: Errore {sResult}"
    return sResult

def Timestamp(sPostfix: str = "") -> str:
    try:
        now = datetime.now()
        sResult = now.strftime("%Y%m%d:%H%M%S")
        if sPostfix:
            sResult = f"{sResult}:{sPostfix.lower()}"
        return sResult
    except Exception:
        return ""

def TimestampDiff(sTimestamp1: str, sTimestamp2: str, sMode: str = "s") -> Optional[float]:
    def _to_sec(ts):
        if not ts or ':' not in ts: return None
        parts = ts.split(':')
        if len(parts) < 2: return None
        d, t = parts[0], parts[1]
        if len(d) != 8 or len(t) != 6: return None
        try:
            dt = datetime(int(d[:4]), int(d[4:6]), int(d[6:8]), int(t[:2]), int(t[2:4]), int(t[4:6]))
            return (dt - datetime(1970, 1, 1)).total_seconds()
        except: return None
    try:
        sec1, sec2 = _to_sec(sTimestamp1), _to_sec(sTimestamp2)
        if sec1 is None or sec2 is None: return None
        diff = abs(sec1 - sec2)
        return diff / 86400.0 if sMode.lower() == "d" else diff
    except: return None

def Expand(sText: str, dictConfig: Dict[str, str]) -> str:
    try:
        # Fase 1: Escape
        sText = sText.replace('%##', '#').replace('%#', '"').replace('%%', '%').replace('%n', '\n').replace('%$', '$')
        # Fase 2: $SYS. e $ENV.
        import re
        def repl_sys_env(match):
            prefix = match.group(1)
            varname = match.group(2)
            if prefix == "ENV.": return os.environ.get(varname, "")
            elif prefix == "SYS.":
                sys_vars = {"OS": os.name.upper(), "OS2": sys.platform, "USER": os.environ.get("USERNAME", os.environ.get("USER", "")),
                            "COMPUTER": os.environ.get("COMPUTERNAME", ""), "CD": os.getcwd(), "TEMP": os.environ.get("TEMP", ""),
                            "YYYYMMDD": datetime.now().strftime("%Y%m%d"), "NOW": Timestamp()}
                return sys_vars.get(varname, "NOTFOUND")
            return match.group(0)
        sText = re.sub(r'\$(SYS\.|ENV\.)([A-Za-z0-9_]+)', repl_sys_env, sText)
        # Fase 3: $NOMEVAR
        def repl_config(match):
            return dictConfig.get(match.group(1), match.group(0))
        return re.sub(r'\$([A-Za-z0-9_]+)', repl_config, sText)
    except: return sText

def ExpandDict(dictExpand: Dict, dictParam: Dict) -> Dict:
    try:
        result = dictExpand.copy()
        for k, v in result.items():
            if isinstance(v, dict):
                result[k] = {sk: Expand(sv, dictParam) for sk, sv in v.items()}
            elif isinstance(v, str):
                result[k] = Expand(v, dictParam)
        return result
    except: return dictExpand

def StringToNum(sNumber: str) -> int:
    try: return int(float(sNumber.replace(',', '.')))
    except: return 0

def StringBool(sText: str) -> bool:
    return str(sText).strip().lower() == "true"

def DictExist(dictParam: Any, sKey: str, xDefault: Any = None) -> Any:
    return dictParam.get(sKey, xDefault) if isinstance(dictParam, dict) else xDefault

def DictMerge(dictSource: Dict, dictAdd: Dict) -> Dict:
    if dictAdd: dictSource.update(dictAdd)
    return dictSource

def DictPrint(dictParam: Dict, sFile: Optional[str] = None) -> str:
    try:
        if not isinstance(dictParam, dict): dictParam = {}
        import json
        sText = json.dumps(dictParam, indent=2, ensure_ascii=False)
        print(sText)
        if sFile:
            with open(NormalizePath(sFile), 'a', encoding='utf-8') as f: f.write(sText + '\n')
        return ""
    except Exception as e: return ErrorProc(str(e), "DictPrint")

def FileExists(sFile: str) -> bool: return os.path.isfile(NormalizePath(sFile))
def isValidPath(sPath: str) -> bool: return os.path.isdir(NormalizePath(sPath))

def read_ini_to_dict(ini_file_path: str) -> Tuple[str, Dict[str, Dict[str, str]]]:
    sProc = "read_ini_to_dict"
    try:
        ini_norm = NormalizePath(ini_file_path)
        if not os.path.exists(ini_norm): return (f"File non esistente: {ini_norm}", {})
        config = configparser.ConfigParser(interpolation=None, comment_prefixes=(";",), inline_comment_prefixes=())
        config.optionxform = str
        config.read(ini_norm, encoding='utf-8')
        result = {section: dict(config[section]) for section in config.sections()}
        print(f"Letto file .ini {ini_norm}, Numero Sezioni: {len(result)}")
        return ("", result)
    except Exception as e: return (ErrorProc(str(e), sProc), {})

def save_dict_to_ini(data_dict: Dict[str, Dict[str, str]], ini_file_path: str) -> str:
    sProc = "save_dict_to_ini"
    try:
        ini_norm = NormalizePath(ini_file_path)
        os.makedirs(os.path.dirname(ini_norm), exist_ok=True)
        config = configparser.ConfigParser(interpolation=None)
        config.optionxform = str
        for section, items in data_dict.items():
            if not config.has_section(section): config.add_section(section)
            for k, v in items.items(): config.set(section, k, str(v))
        with open(ini_norm, 'w', encoding='utf-8') as f: config.write(f)
        return ""
    except Exception as e: return ErrorProc(str(e), sProc)

# =============================================================================
# CLASSE LOG INGLOBATA (ex aiSys.acLog)
# =============================================================================
class acLog:
    def __init__(self): self.sLog = ""
    def Start(self, sLogfile: Optional[str] = None, sLogFolder: Optional[str] = None) -> str:
        sProc = "acLog.Start"
        try:
            if not sLogFolder or sLogFolder == "": sLogFolder = os.path.dirname(os.path.abspath(sys.argv[0]))
            sAppName = os.path.splitext(os.path.basename(sys.argv[0]))[0]
            if not sLogfile or sLogfile == "": sLogfile = sAppName
            self.sLog = os.path.join(sLogFolder, f"{sLogfile}.log")
            return ""
        except Exception as e: return ErrorProc(str(e), sProc)
    def Log(self, sType: str, sValue: str = "") -> None:
        if not self.sLog: return
        sLine = f"{Timestamp(sType)}: {sValue}"
        print(sLine)
        try:
            with open(NormalizePath(self.sLog), 'a', encoding='utf-8') as f: f.write(sLine + '\n')
        except: pass
    def Log0(self, sResult: str, sValue: str = "") -> None:
        self.Log("ERR", f"{sResult}: {sValue}") if sResult else self.Log("INFO", sValue)
    def Log1(self, sValue: str = "") -> None: self.Log("INFO", sValue)

# =============================================================================
# CLASSE PRINCIPALE acJobsApp
# =============================================================================
class acJobsApp:
    def __init__(self):
        self.sJobIni = ""
        self.sUser = os.environ.get("NTJ_USER", "")
        sUsg = os.environ.get("NTJ_USERG", "")
        self.asUsg = [x.strip() for x in sUsg.split(",") if x.strip()] if sUsg else []
        self.bErrExit = False
        self.sName = ""
        self.tsStart = ""
        self.sType = ""
        self.sLogFile = ""
        self.sCommand = ""
        self.dictJob = {}
        self.dictJobs = {}
        self.sJobEnd = ""
        self.jLog = acLog()

    def Start(self) -> str:
        sProc = "Start"
        sResult = ""
        self.tsStart = Timestamp()
        
        # 1. Verifica parametri
        if len(sys.argv) < 2:
            sResult = "NTJOBSAPP: Eseguire con parametro file .ini o nella forma ntjobsapp.py command parametro valore ecc."
            print(sResult)
            return sResult

        # 2. Controllo estensione .ini o MakeIni
        if not sys.argv[1].lower().endswith('.ini'):
            sResult = self.MakeIni()
            if sResult: return sResult
        else:
            self.sJobIni = sys.argv[1]

        # 3. Normalizzazione ed esistenza
        self.sJobIni = NormalizePath(self.sJobIni)
        if not os.path.exists(self.sJobIni):
            sResult = f"File .ini non esistente {self.sJobIni}"
            return sResult

        # 4. Prepara .end e leggi INI
        base, _ = os.path.splitext(self.sJobIni)
        self.sJobEnd = base + ".end"
        sResult, self.dictJobs = read_ini_to_dict(self.sJobIni)
        if sResult: return sResult
        print(f"Letto {self.sJobIni}")

        # 5. Verifica chiavi riservate
        RESERVED = ["TS.START", "TS.END", "RETURN.TYPE", "RETURN.VALUE"]
        RESERVED_PREFIX = "RETURN.FILE."
        for sec, vals in self.dictJobs.items():
            for k in vals.keys():
                if k in RESERVED or k.startswith(RESERVED_PREFIX):
                    return ErrorProc(f"Usate chiavi riservate {k}", sProc)

        print(f"Processato {self.sJobIni}, Sezioni {', '.join(self.dictJobs.keys())}")

        # 6. Verifica CONFIG
        if "CONFIG" not in self.dictJobs:
            return ErrorProc(f"Sezione CONFIG non trovata in file {self.sJobIni}", sProc)

        # 7. Verifica file allegati (FILE.*)
        for sKey in self.dictJobs:
            if sKey == "CONFIG": continue
            dictTemp = self.dictJobs[sKey]
            for k, v in dictTemp.items():
                if k.startswith("FILE."):
                    sFile = os.path.basename(str(v).strip())
                    if not os.path.isfile(sFile):
                        sResult += f"File richiesto non presente {sFile}\n"
        if sResult: return sResult

        # 8. ESPANSIONE MULTI-PASS CONFIG (2 cicli)
        config_section = self.dictJobs.get("CONFIG", {})
        for _ in range(2):
            config_temp = config_section.copy()
            for k, v in config_temp.items():
                if isinstance(v, str):
                    config_section[k] = Expand(v, config_temp)

        # 9. Espansione altre sezioni
        for sKey in self.dictJobs:
            if sKey == "CONFIG": continue
            print(f"Sezione: {sKey}")
            dictTemp = self.dictJobs[sKey].copy()
            self.dictJobs[sKey] = ExpandDict(dictTemp, config_section)
            DictPrint(self.dictJobs[sKey])

        # 10. Inizializzazione attributi da CONFIG
        self.sLogFile = self.Config("LOG") or ""
        self.sType = self.Config("TYPE")
        self.sName = self.Config("NAME")
        self.bErrExit = StringBool(self.Config("EXIT"))
        
        sResult = self.jLog.Start(self.sLogFile)
        if sResult: return sResult

        # 11. Rimozione password e verifiche finali
        if "PASSWORD" in self.dictJobs.get("CONFIG", {}):
            del self.dictJobs["CONFIG"]["PASSWORD"]

        if not self.sName: return ErrorProc("NAME APP non precisato", sProc)
        if not self.sType.startswith("NTJOBS.APP."): return ErrorProc("Type INI non NTJOBSAPP", sProc)

        self.Log0(sResult)
        return sResult

    def MakeIni(self) -> str:
        sProc = "MakeIni"
        self.sJobIni = ""
        args = sys.argv[1:]
        if len(args) < 1 or (len(args) - 1) % 2 != 0:
            return ErrorProc("Errore numero parametri comando chiave=valore ecc.", sProc)

        sCommand = args[0]
        dictTemp = {}
        i = 1
        while i < len(args):
            k = args[i].strip('"')
            v = args[i+1].strip('"')
            dictTemp[k] = v
            i += 2

        sFileTemp = NormalizePath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "ntjobsapp.ini"))
        temp_dict = {"CONFIG": {"TYPE": "NTJOBS.APP.1"}, "JOB_01": {"COMMAND": sCommand}}
        temp_dict["JOB_01"].update(dictTemp)
        
        sResult = save_dict_to_ini(temp_dict, sFileTemp)
        if sResult: return sResult
        
        self.sJobIni = sFileTemp
        return sResult

    def Config(self, sKey: str) -> str:
        return DictExist(self.dictJobs.get("CONFIG", {}), sKey, "")

    def AddTimestamp(self, dictTemp: Dict) -> None:
        dictTemp["TS.START"] = self.tsStart
        dictTemp["TS.END"] = Timestamp()

    def Return(self, sResult: str, sValue: str = "", dictFiles: Optional[Dict] = None) -> str:
        sProc = "Return"
        sReturnType = "E" if sResult else "S"
        if not sValue and sReturnType == "E": sValue = sResult

        if dictFiles:
            for fid, fpath in dictFiles.items():
                if not os.path.isfile(NormalizePath(fpath)):
                    return ErrorProc(f"Errore file non presente : {fpath}", sProc)
                dictFiles[fid] = os.path.basename(fpath)
            for k, v in dictFiles.items():
                self.dictJob[f"RETURN.FILE.{k}"] = v

        if not sReturnType: sReturnType = "S"
        self.dictJob["RETURN.TYPE"] = sReturnType
        self.dictJob["RETURN.VALUE"] = sValue
        self.AddTimestamp(self.dictJob)
        return ErrorProc(sResult, sProc)

    def Run(self, cbCommands) -> str:
        sResult = ""
        for sKey in self.dictJobs:
            if sKey == "CONFIG": continue
            print(f"Esecuzione Command {sKey}")
            
            self.dictJob = self.dictJobs[sKey].copy()
            self.sCommand = DictExist(self.dictJob, "COMMAND", "")
            
            if not self.sCommand:
                sResult = f"COMMAND non trovato in {sKey}"
                self.Log(sResult)
            else:
                self.Log1(f"Eseguo il comando: {self.sCommand}, Sezione : {sKey}, TS: {Timestamp()}, Risultato: {sResult}")
                sResult = cbCommands(self.dictJob)
                self.dictJobs[sKey] = self.dictJob.copy()
                self.Log1(f"Eseguito il comando: {self.sCommand}, Sezione : {sKey}, TS: {Timestamp()}, Risultato: {sResult}")
            
            if sResult and self.bErrExit:
                break
        return sResult

    def End(self, sResult: str) -> None:
        sProc = "End"
        bIsFatalError = False
        nResult = 0
        
        if not self.dictJobs:
            nResult = 1
            self.dictJobs = {"CONFIG": {}}
            bIsFatalError = True
            
        if sResult:
            nResult = 2
            bIsFatalError = True
            
        dictTemp = {"RETURN.TYPE": "", "RETURN.VALUE": ""}
        if bIsFatalError:
            dictTemp["RETURN.TYPE"] = "E"
            dictTemp["RETURN.VALUE"] = sResult
            
        self.AddTimestamp(dictTemp)
        DictMerge(self.dictJobs.get("CONFIG", {}), dictTemp)
        
        sWriteRes = save_dict_to_ini(self.dictJobs, self.sJobEnd)
        if not sWriteRes: print(f"Creato file {self.sJobEnd}")
        
        self.Log(sResult, f"Fine applicazione {self.sName}")
        if nResult != 0: sys.exit(nResult)

    def Log(self, sType: str, sValue: str = ""): self.jLog.Log(sType, sValue)
    def Log0(self, sResult: str, sValue: str = ""): self.jLog.Log0(sResult, sValue)
    def Log1(self, sValue: str = ""): self.jLog.Log1(sValue)