#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
acJobsApp.py - Classe per orchestrare micro applicazioni batch (ntJobsApp)
"""

import os
import sys
import json
import configparser
from datetime import datetime
from typing import Dict, Any, Optional, Union, List, Tuple

# ============================================================================
# COSTANTI
# ============================================================================
# Data di generazione della classe (YYYYMMDDHH)
NTJOBSAPP_VER = "2026041412"  # 14 Aprile 2026, ore 12:00


# ============================================================================
# CLASSE acLog (integrata)
# ============================================================================
class acLog:
    """Classe per la gestione dei log"""

    def __init__(self):
        self.sLog = ""
        self.sAppName = ""

    def Start(self, sLogfile: Optional[str] = None, sLogFolder: Optional[str] = None) -> str:
        """Inizializza il file di log"""
        sProc = "Start"

        try:
            sResult = ""

            # Calcola nome applicazione
            self.sAppName = self._get_app_name()

            # Determina cartella log
            if not sLogFolder or sLogFolder == "":
                sLogFolder = os.path.dirname(os.path.abspath(sys.argv[0]))

            # Determina nome file log
            if not sLogfile or sLogfile == "":
                sLogfile = self.sAppName

            # Crea percorso completo
            self.sLog = os.path.join(sLogFolder, f"{sLogfile}.log")

            # Crea directory se non esiste
            os.makedirs(os.path.dirname(self.sLog), exist_ok=True)

            return sResult

        except Exception as e:
            sResult = f"Errore Log.Start: {str(e)}"
            return _error_proc(sResult, sProc)

    def _get_app_name(self) -> str:
        """Ottiene il nome dell'applicazione corrente"""
        try:
            app_path = sys.argv[0]
            app_filename = os.path.basename(app_path)
            app_name, _ = os.path.splitext(app_filename)
            return app_name
        except:
            return "unknown_app"

    def Log(self, sType: str, sValue: str = "") -> None:
        """Scrive una riga nel log"""
        if not self.sLog:
            return

        try:
            timestamp = _timestamp(sType)
            sLine = f"{timestamp}:{sValue}"

            # Scrivi su console
            print(sLine)

            # Scrivi su file
            with open(self.sLog, 'a', encoding='utf-8') as f:
                f.write(sLine + "\n")

        except Exception:
            pass

    def Log0(self, sResult: str, sValue: str = "") -> None:
        """Logga con gestione automatica del tipo"""
        if sResult != "":
            self.Log("ERR", f"{sResult}: {sValue}")
        else:
            self.Log("INFO", sValue)

    def Log1(self, sValue: str = "") -> None:
        """Logga come INFO"""
        self.Log("INFO", sValue)


# ============================================================================
# FUNZIONI DI SUPPORTO INTEGRATE (ex aiSys.*)
# ============================================================================

def _timestamp(sPostfix: str = "") -> str:
    """Genera un Timestamp nel formato AAAAMMGG:HHMMSS"""
    sResult = datetime.now().strftime("%Y%m%d:%H%M%S")
    if sPostfix:
        sResult = f"{sResult}:{sPostfix.lower()}"
    return sResult


def _error_proc(sResult: str, sProc: str) -> str:
    """Ritorna errore formattato con nome procedura"""
    if sResult != "":
        print(f"Eseguita ntjobsapp.{sProc}: {sResult}")
        return f"{sProc}: Errore {sResult}"
    return sResult


def _dict_exist(dictParam: Dict, sKey: str, xDefault: Any) -> Any:
    """Ritorna valore di una chiave oppure un valore di default"""
    if not isinstance(dictParam, dict):
        return xDefault
    return dictParam.get(sKey, xDefault)


def _string_bool(sText: str) -> bool:
    """Converte una stringa in valore booleano"""
    if not sText:
        return False
    return sText.strip().lower() == "true"


def _expand(sText: str, dictConfig: Dict) -> str:
    """Espande una stringa con sequenze di escape e variabili"""
    if not sText:
        return sText

    result = []
    i = 0
    length = len(sText)

    while i < length:
        char = sText[i]

        if char == '%' and i + 1 < length:
            next_char = sText[i + 1]

            if next_char == '#' and i + 2 < length and sText[i + 2] == '#':
                result.append('#')
                i += 3
                continue
            elif next_char == '#':
                result.append('"')
                i += 2
                continue
            elif next_char == '%':
                result.append('%')
                i += 2
                continue
            elif next_char == 'n':
                result.append('\n')
                i += 2
                continue
            elif next_char == '$':
                result.append('$')
                i += 2
                continue
            else:
                result.append('%')
                result.append(next_char)
                i += 2
                continue

        elif char == '%' and i + 1 == length:
            result.append('%')
            i += 1
            continue

        result.append(char)
        i += 1

    phase1_result = ''.join(result)

    # FASE 2: Espansione variabili
    result = []
    i = 0
    length = len(phase1_result)

    while i < length:
        char = phase1_result[i]

        if char == '$' and i + 1 < length:
            j = i + 1
            var_name = []

            while j < length:
                c = phase1_result[j]
                if c.isalnum() or c == '_':
                    var_name.append(c)
                    j += 1
                else:
                    break

            if var_name:
                var_name_str = ''.join(var_name)

                if var_name_str in dictConfig:
                    result.append(str(dictConfig[var_name_str]))
                else:
                    result.append('$' + var_name_str)

                i = j
                continue

        result.append(char)
        i += 1

    return ''.join(result)


def _expand_dict(dictExpand: Dict, dictParam: Dict) -> Dict:
    """Applica Expand a tutti i valori di un dizionario"""
    if not isinstance(dictExpand, dict):
        return {}

    result = {}

    for key, value in dictExpand.items():
        if isinstance(value, dict):
            result[key] = _expand_dict(value, dictParam)
        elif isinstance(value, str):
            result[key] = _expand(value, dictParam)
        else:
            result[key] = value

    return result


def _dict_print(dictParam: Dict) -> None:
    """Visualizza un dizionario su schermo in formato JSON"""
    try:
        print(json.dumps(dictParam, indent=2, ensure_ascii=False))
    except Exception:
        print(dictParam)


def _read_ini_to_dict(ini_file_path: str) -> Tuple[str, Dict]:
    """Legge un file INI e lo converte in un dizionario di dizionari"""
    sProc = "_read_ini_to_dict"

    try:
        if not os.path.exists(ini_file_path):
            return (f"File non esistente: {ini_file_path}", {})

        config = configparser.ConfigParser(
            interpolation=None,
            comment_prefixes=(';',),
            inline_comment_prefixes=()
        )
        config.optionxform = str

        config.read(ini_file_path, encoding='utf-8')

        dictINI = {}
        for section in config.sections():
            dictINI[section] = {}
            for key in config[section]:
                dictINI[section][key] = config[section][key]

        print(f"Letto file .ini {ini_file_path}, Numero Sezioni: {len(dictINI)}")
        return ("", dictINI)

    except Exception as e:
        return (_error_proc(str(e), sProc), {})


def _save_dict_to_ini(data_dict: Dict, ini_file_path: str) -> str:
    """Salva un dizionario di dizionari in un file INI"""
    sProc = "_save_dict_to_ini"

    try:
        config = configparser.ConfigParser()
        config.optionxform = str

        for section, section_dict in data_dict.items():
            config[section] = {}
            for key, value in section_dict.items():
                config[section][key] = str(value)

        os.makedirs(os.path.dirname(ini_file_path), exist_ok=True)

        with open(ini_file_path, 'w', encoding='utf-8') as f:
            config.write(f)

        return ""

    except Exception as e:
        return _error_proc(str(e), sProc)


def _config(dictConfig: Dict, sKey: str) -> Any:
    """Legge un valore da un dizionario di configurazione"""
    if not dictConfig or not isinstance(dictConfig, dict):
        return ""
    return dictConfig.get(sKey, "")


# ============================================================================
# CLASSE acJobsApp
# ============================================================================

class acJobsApp:
    """Classe per orchestrare micro applicazioni batch"""

    def __init__(self):
        """Inizializza gli attributi della classe"""
        self.sJobIni = ""
        self.sUser = ""
        self.asUsg = []
        self.bErrExit = False
        self.sName = ""
        self.tsStart = ""
        self.sType = ""
        self.sLogFile = ""
        self.sCommand = ""
        self.dictJob = {}
        self.dictJobs = {}
        self.sJobEnd = ""

        # Inizializza il log
        self.jLog = acLog()

    # ========================================================================
    # Metodi di logging (wrapper)
    # ========================================================================

    def Log(self, sType: str, sValue: str = "") -> None:
        """Wrapper per self.jLog.Log"""
        self.jLog.Log(sType, sValue)

    def Log0(self, sResult: str, sValue: str = "") -> None:
        """Wrapper per self.jLog.Log0 (accetta anche solo un parametro)"""
        self.jLog.Log0(sResult, sValue)

    def Log1(self, sValue: str = "") -> None:
        """Wrapper per self.jLog.Log1"""
        self.jLog.Log1(sValue)

    # ========================================================================
    # Metodo Config
    # ========================================================================

    def Config(self, sKey: str) -> Any:
        """Legge un valore dalla sezione CONFIG"""
        return _config(self.dictJobs.get("CONFIG", {}), sKey)

    # ========================================================================
    # Metodo AddTimestamp
    # ========================================================================

    def AddTimestamp(self, dictTemp: Dict) -> None:
        """Aggiunge o sostituisce TS.START e TS.END a un dizionario"""
        dictTemp["TS.START"] = self.tsStart
        dictTemp["TS.END"] = _timestamp()

    # ========================================================================
    # Metodo MakeIni
    # ========================================================================

    def MakeIni(self) -> str:
        """Crea un file INI dai parametri della riga di comando"""
        sResult = ""
        sProc = "MakeIni"
        self.sJobIni = ""

        try:
            dictTemp = {}

            # Verifica numero parametri: 1 + multiplo di 2
            if len(sys.argv) < 2:
                sResult = "Errore numero parametri comando chiave=valore ecc."
                return _error_proc(sResult, sProc)

            nParams = len(sys.argv) - 1  # esclude il nome del programma
            if (nParams - 1) % 2 != 0:
                sResult = "Errore numero parametri comando chiave=valore ecc."
                return _error_proc(sResult, sProc)

            # Primo parametro = comando
            sCommand = sys.argv[1].strip('"')

            # Coppie chiave=valore dal secondo parametro in poi
            for i in range(2, len(sys.argv), 2):
                if i + 1 >= len(sys.argv):
                    break
                key = sys.argv[i].strip('"')
                value = sys.argv[i + 1].strip('"')
                dictTemp[key] = value

            # Crea file INI temporaneo
            script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            sFileTemp = os.path.join(script_dir, "ntjobsapp.ini")

            # Costruisci struttura INI
            ini_data = {
                "CONFIG": {"TYPE": "NTJOBS.APP.1"},
                "JOB_01": {"COMMAND": sCommand}
            }

            # Aggiungi le altre chiavi/valori a JOB_01
            for key, value in dictTemp.items():
                ini_data["JOB_01"][key] = value

            # Salva il file
            sResult = _save_dict_to_ini(ini_data, sFileTemp)
            if sResult != "":
                return _error_proc(sResult, sProc)

            self.sJobIni = sFileTemp
            print(f"Creato file INI: {self.sJobIni}")
            return ""

        except Exception as e:
            sResult = str(e)
            return _error_proc(sResult, sProc)

    # ========================================================================
    # Metodo Return
    # ========================================================================

    def Return(self, sResult: str, sValue: str = "", dictFiles: Optional[Dict] = None) -> str:
        """Aggiorna il risultato dell'elaborazione corrente"""
        sProc = "Return"

        try:
            # Determina RETURN.TYPE
            if sResult != "":
                sReturnType = "E"
                if sValue == "":
                    sValue = sResult
            else:
                sReturnType = "S"

            # Gestione dictFiles
            if dictFiles and isinstance(dictFiles, dict):
                for file_id, file_path in dictFiles.items():
                    # Estrai solo il nome del file senza path
                    sFileName = os.path.basename(file_path)

                    # Verifica che il file esista nella cartella corrente
                    if not os.path.exists(sFileName):
                        sResult = f"Errore file non presente: {sFileName}"
                        return _error_proc(sResult, sProc)

                    # Accoda a self.dictJob con prefisso RETURN.FILE.
                    self.dictJob[f"RETURN.FILE.{file_id}"] = sFileName

            # Aggiungi RETURN.TYPE e RETURN.VALUE
            self.dictJob["RETURN.TYPE"] = sReturnType
            self.dictJob["RETURN.VALUE"] = sValue

            # Aggiungi timestamp
            self.AddTimestamp(self.dictJob)

            return _error_proc(sResult, sProc)

        except Exception as e:
            sResult = str(e)
            return _error_proc(sResult, sProc)

    # ========================================================================
    # Metodo Start
    # ========================================================================

    def Start(self) -> str:
        """Legge il file INI e inizializza la struttura jobs"""
        sResult = ""
        sProc = "Start"

        try:
            # Inizializzazioni
            sResult = ""
            self.tsStart = _timestamp()
            self.sUser = os.getenv("ntj_user", "")
            usg_env = os.getenv("ntj_usergrp", "")
            self.asUsg = [x.strip() for x in usg_env.split(",") if x.strip()] if usg_env else []

            # Nessun parametro
            if len(sys.argv) < 2:
                sResult = "NTJOBSAPP: Eseguire con parametro file .ini o nella forma ntjobsapp.py command parametro valore ecc."
                print(sResult)
                return _error_proc(sResult, sProc)

            # Primo parametro non è .ini -> chiama MakeIni
            if not sys.argv[1].lower().endswith('.ini'):
                sResult = self.MakeIni()
                if sResult != "":
                    return _error_proc(sResult, sProc)
            else:
                self.sJobIni = sys.argv[1]

            # Verifica esistenza file
            if not os.path.exists(self.sJobIni):
                sResult = f"File .ini non esistente {self.sJobIni}"
                return _error_proc(sResult, sProc)

            # Imposta sJobEnd
            self.sJobEnd = os.path.splitext(self.sJobIni)[0] + ".end"

            # Leggi file INI
            sResult, self.dictJobs = _read_ini_to_dict(self.sJobIni)
            if sResult != "":
                return _error_proc(sResult, sProc)

            print(f"Letto {self.sJobIni}")

            # Verifica chiavi riservate
            reserved_keys = ["TS.START", "TS.END", "RETURN.TYPE", "RETURN.VALUE"]
            for section, section_dict in self.dictJobs.items():
                for key in section_dict.keys():
                    if key in reserved_keys or key.startswith("RETURN.FILE."):
                        sResult = f"Usate chiavi riservate {key}"
                        return _error_proc(sResult, sProc)

            # Stampa sezioni processate
            sezioni = list(self.dictJobs.keys())
            print(f"Processato {self.sJobIni}, Sezioni {', '.join(sezioni)}")

            # Verifica sezione CONFIG
            if "CONFIG" not in self.dictJobs:
                sResult = f"Sezione CONFIG non trovata in file {self.sJobIni}"
                return _error_proc(sResult, sProc)

            # Verifica COMMAND e FILE.* per ogni sezione (eccetto CONFIG)
            for sKey, dictTemp in self.dictJobs.items():
                if sKey == "CONFIG":
                    continue

                if "COMMAND" not in dictTemp:
                    sResult += f"Per questa sezione COMMAND non presente: {sKey}\n"

                # Verifica FILE.*
                for file_key, sFile in dictTemp.items():
                    if file_key.startswith("FILE."):
                        sFileName = os.path.basename(sFile)
                        if not os.path.exists(sFileName):
                            sResult += f"File richiesto non presente {sFileName}\n"

            if sResult != "":
                return _error_proc(sResult, sProc)

            # Espansione dizionari
            for sKey in self.dictJobs:
                print(f"Sezione: {sKey}")
                self.dictJobs[sKey] = _expand_dict(self.dictJobs[sKey], self.dictJobs["CONFIG"])
                _dict_print(self.dictJobs[sKey])

            # Configurazione log
            sTemp = self.Config("LOG")
            if sTemp != "":
                self.sLogFile = sTemp.strip('"')  # Rimuovi virgolette
            else:
                # Default: nome del programma con estensione .log
                self.sLogFile = os.path.splitext(os.path.basename(sys.argv[0]))[0] + ".log"

            self.sType = self.Config("TYPE")
            self.sName = self.Config("NAME")
            self.bErrExit = _string_bool(self.Config("EXIT"))

            # Avvia il log
            sResult = self.jLog.Start(self.sLogFile)
            if sResult != "":
                return _error_proc(sResult, sProc)

            # Rimuovi PASSWORD dalla sezione CONFIG se presente
            if "PASSWORD" in self.dictJobs.get("CONFIG", {}):
                del self.dictJobs["CONFIG"]["PASSWORD"]

            # Verifiche finali
            if self.sName == "":
                sResult = "NAME APP non precisato"
                return _error_proc(sResult, sProc)

            if not self.sType.startswith("NTJOBS.APP."):
                sResult = "Type INI non NTJOBSAPP"
                return _error_proc(sResult, sProc)

            return ""

        except Exception as e:
            sResult = str(e)
            return _error_proc(sResult, sProc)

        finally:
            self.Log0(sResult)

    # ========================================================================
    # Metodo Run
    # ========================================================================

    def Run(self, cbCommands) -> str:
        """Esegue in sequenza ogni singolo job"""
        sResult = ""
        sProc = "Run"

        try:
            for sKey, dictJobData in self.dictJobs.items():
                if sKey == "CONFIG":
                    continue

                print(f"Esecuzione Command {sKey}")

                # Copia il dizionario del job corrente
                self.dictJob = dictJobData.copy()

                # Estrai COMMAND
                self.sCommand = _dict_exist(self.dictJob, "COMMAND", "")

                if self.sCommand == "":
                    sResult = f"COMMAND non trovato in {sKey}"
                    self.Log0(sResult)
                    if self.bErrExit:
                        break
                    continue

                # Log inizio esecuzione
                self.Log1(f"Eseguo il comando: {self.sCommand}, Sezione: {sKey}, TS: {_timestamp()}, Risultato: {sResult}")

                # Esegui la callback
                sResult = cbCommands(self.dictJob)

                # Aggiorna il record in dictJobs
                self.dictJobs[sKey] = self.dictJob.copy()

                # Log fine esecuzione
                self.Log1(f"Eseguito il comando: {self.sCommand}, Sezione: {sKey}, TS: {_timestamp()}, Risultato: {sResult}")

                if sResult != "" and self.bErrExit:
                    break

            return sResult

        except Exception as e:
            sResult = str(e)
            return _error_proc(sResult, sProc)

    # ========================================================================
    # Metodo End
    # ========================================================================

    def End(self, sResult: str = "") -> int:
        """Salva il file .end e restituisce il codice di uscita"""
        sProc = "End"
        nResult = 0
        bIsFatalError = False

        try:
            # Fase 1: Determinazione codice di uscita
            if not self.dictJobs:
                nResult = 1
                self.dictJobs = {"CONFIG": {}}
                bIsFatalError = True

            dictTemp = {
                "RETURN.TYPE": "",
                "RETURN.VALUE": ""
            }

            if sResult != "":
                nResult = 2
                bIsFatalError = True

            # Fase 2: Aggiornamento dati in caso di errore
            if bIsFatalError:
                dictTemp["RETURN.TYPE"] = "E"
                dictTemp["RETURN.VALUE"] = sResult

            # Aggiungi timestamp
            self.AddTimestamp(dictTemp)

            # Unisci con la sezione CONFIG (priorità a dictTemp)
            if "CONFIG" in self.dictJobs:
                for key, value in dictTemp.items():
                    self.dictJobs["CONFIG"][key] = value
            else:
                self.dictJobs["CONFIG"] = dictTemp

            # Fase 3: Salvataggio file .end
            if self.sJobEnd:
                sSaveResult = _save_dict_to_ini(self.dictJobs, self.sJobEnd)
                if sSaveResult == "":
                    print(f"Creato file {self.sJobEnd}")
                else:
                    print(f"Errore salvataggio {self.sJobEnd}: {sSaveResult}")

            # Log fine applicazione
            self.Log(sResult if sResult else "INFO", f"Fine applicazione {self.sName}")

            return nResult

        except Exception as e:
            print(f"Errore in End: {str(e)}")
            return 2