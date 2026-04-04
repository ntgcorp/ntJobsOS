# =============================================================================
# aiJobsOS2.py  –  versione light monolitica di aiJobsOS
# Root: K:\ntjobsai2
#
# Lanciato da aiJobsOs2.cmd che gestisce il loop esterno:
#   - Cancella ntjobs.reload / ntjobs.restart / ntjobs.shutdown all'avvio
#   - Lancia questo script
#   - Se al ritorno esiste ntjobs.restart  → rilancia (SYS.RELOAD)
#   - Se al ritorno esiste ntjobs.shutdown → esegue SHUTDOWN.EXE /S
#
# Comandi interni gestiti:
#   SYS.RELOAD    → crea ntjobs.restart   in SYSROOT e poi esce
#   SYS.SHUTDOWN  → crea ntjobs.shutdown  in SYSROOT e poi esce
#   SYS.REBOOT    → crea ntjobs.shutdown  (il CMD non gestisce reboot separato)
#   SYS.QUIT      → esce senza creare flag (il CMD termina normalmente)
#
# Sintassi variabili in ntjobs_config.ini:
#   $NOMEVAR   → espande la variabile NOMEVAR dal dizionario config
#   %$         → carattere letterale $
#   %%         → carattere letterale %
#   %n         → newline
# =============================================================================

import os
import sys
import re
import time
import shutil
import subprocess
import configparser
import csv as _csv_module
import smtplib
import json
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Tuple

# ---------------------------------------------------------------------------
# COSTANTE DI BOOTSTRAP
# Usata SOLO per trovare ntjobs_config.ini, ntjobs_users.csv, ntjobs_actions.csv.
# Non viene mai usata come fallback per path operativi né per creare cartelle.
# Tutti i path operativi (INBOX, ARCHIVE, LOG, ...) vengono esclusivamente
# dal file ntjobs_config.ini.
# ---------------------------------------------------------------------------
SYSROOT_BOOT = r"K:\ntjobsai2"
CONFIG_FILE  = os.path.join(SYSROOT_BOOT, "ntjobs_config.ini")
USERS_FILE   = os.path.join(SYSROOT_BOOT, "ntjobs_users.csv")
ACTIONS_FILE = os.path.join(SYSROOT_BOOT, "ntjobs_actions.csv")

CYCLE_WAIT   = 60     # default secondi tra un ciclo e l'altro
PROC_TIMEOUT = 300    # default timeout processo esterno (secondi)

# Flag files attesi dal CMD launcher (nella CWD = SYSROOT)
FLAG_RESTART  = "ntjobs.restart"
FLAG_SHUTDOWN = "ntjobs.shutdown"

# ---------------------------------------------------------------------------
# LOG
# Prima che _load_config() venga eseguito _log_file è vuoto: si stampa
# solo su console. Dopo la lettura del .ini viene impostato con il path
# estratto dalla chiave LOG di ntjobs_config.ini.
# ---------------------------------------------------------------------------
_log_file: str = ""


def ts() -> str:
    """Timestamp corrente nel formato AAAAMMGG:HHMMSS (per log e campi ini)."""
    return datetime.now().strftime("%Y%m%d:%H%M%S")


def ts_folder() -> str:
    """Timestamp senza ':' per nomi di cartella compatibili con Windows."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def log(msg: str) -> None:
    """Scrive una riga di log su file (se noto) e sempre su console."""
    line = f"{ts()} {msg}"
    print(line)
    if _log_file:
        try:
            with open(_log_file, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception:
            pass


# ---------------------------------------------------------------------------
# ESPANSIONE VARIABILI
#
# Sintassi nel .ini:
#   $NOMEVAR  → sostituito con cfg["NOMEVAR"]
#   %$        → carattere letterale $  (escape)
#   %%        → carattere letterale %  (escape)
#   %n        → newline
#
# expand_config() esegue DUE passaggi sullo stesso dizionario per risolvere
# dipendenze in cascata. Esempio:
#   SYSROOT = K:\ntjobsai2
#   INBOX   = $SYSROOT\Inbox   →  dopo passaggio 1 = K:\ntjobsai2\Inbox
# ---------------------------------------------------------------------------

def expand(text: str, cfg: Dict[str, str]) -> str:
    """Espande le variabili $NOME e le sequenze di escape nel testo."""
    if not isinstance(text, str) or not text:
        return text
    text = text.replace("%$", "\x00DOLLAR\x00")
    text = text.replace("%%", "\x00PCT\x00")
    text = text.replace("%n",  "\x00NL\x00")

    def _repl(m):
        var = m.group(1)
        return cfg.get(var, cfg.get(var.upper(), m.group(0)))

    text = re.sub(r'\$([A-Za-z_][A-Za-z0-9_.]*)', _repl, text)
    text = text.replace("\x00DOLLAR\x00", "$")
    text = text.replace("\x00PCT\x00",    "%")
    text = text.replace("\x00NL\x00",     "\n")
    return text


def expand_dict(d: Dict, cfg: Dict[str, str]) -> Dict:
    """Espande ricorsivamente i valori stringa di d usando cfg."""
    return {k: expand(v, cfg) if isinstance(v, str) else v for k, v in d.items()}


def expand_config(flat: Dict[str, str]) -> Dict[str, str]:
    """
    Espansione in due passaggi per risolvere dipendenze in cascata.
      Passaggio 1: SYSROOT è già noto → espande $SYSROOT in INBOX, ARCHIVE, ecc.
      Passaggio 2: risolve eventuali riferimenti a valori espansi al passo 1.
    """
    step1 = expand_dict(flat, flat)
    step2 = expand_dict(step1, step1)
    return step2


# ---------------------------------------------------------------------------
# LETTURA / SCRITTURA FILE INI
# ---------------------------------------------------------------------------

def read_ini(filepath: str) -> Tuple[str, Dict[str, Dict[str, str]]]:
    """
    Legge un file .ini e ritorna (errore, dict_di_dict).
    Tutte le sezioni e le chiavi vengono convertite in MAIUSCOLO.
    """
    if not os.path.isfile(filepath):
        return f"File non trovato: {filepath}", {}
    try:
        cfg = configparser.ConfigParser(
            interpolation=None,
            comment_prefixes=(";",),
            inline_comment_prefixes=()
        )
        cfg.optionxform = str
        cfg.read(filepath, encoding="utf-8")
        result: Dict[str, Dict[str, str]] = {}
        for section in cfg.sections():
            result[section.upper()] = {k.upper(): v for k, v in cfg.items(section)}
        return "", result
    except Exception as e:
        return f"Errore lettura INI {filepath}: {e}", {}


def write_ini(data: Dict[str, Dict[str, str]], filepath: str) -> str:
    """Scrive un dict-di-dict in formato .ini. Ritorna '' se OK."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        cfg = configparser.ConfigParser(interpolation=None)
        cfg.optionxform = str
        for section, values in data.items():
            cfg[section] = {str(k): str(v) for k, v in values.items()}
        with open(filepath, "w", encoding="utf-8") as f:
            cfg.write(f)
        return ""
    except Exception as e:
        return f"Errore scrittura INI {filepath}: {e}"


# ---------------------------------------------------------------------------
# LETTURA CSV
# ---------------------------------------------------------------------------

def read_csv(filepath: str, delimiter: str = ";") -> Tuple[str, Dict[str, Dict[str, str]]]:
    """
    Legge un CSV con intestazione; prima colonna = chiave del dizionario esterno.
    Ritorna (errore, dict_di_dict).
    """
    if not os.path.isfile(filepath):
        return f"File non trovato: {filepath}", {}
    try:
        result: Dict[str, Dict[str, str]] = {}
        with open(filepath, newline="", encoding="utf-8") as f:
            content = f.read()
        if content.startswith("\ufeff"):
            content = content[1:]
        lines = content.splitlines()
        if not lines:
            return f"CSV vuoto: {filepath}", {}
        headers = [h.strip().strip('"').strip("'")
                   for h in lines[0].split(delimiter)]
        if not headers:
            return f"Intestazione mancante: {filepath}", {}
        key_field = headers[0]
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            row_vals = next(_csv_module.reader(
                [line], delimiter=delimiter, skipinitialspace=True), [])
            if not row_vals:
                continue
            while len(row_vals) < len(headers):
                row_vals.append("")
            clean = {headers[i]: row_vals[i].strip().strip('"').strip("'")
                     for i in range(len(headers))}
            key = clean.get(key_field, "").strip()
            if not key:
                continue
            if key in result:
                return f"Chiave duplicata '{key}' in {filepath}", {}
            result[key] = clean
        return "", result
    except Exception as e:
        return f"Errore lettura CSV {filepath}: {e}", {}


# ---------------------------------------------------------------------------
# INVIO MAIL
# ---------------------------------------------------------------------------

def send_mail_smtp(cfg: Dict[str, str], to: str, subject: str, body: str) -> str:
    """Invia mail via SMTP. Ritorna '' se OK."""
    try:
        msg = MIMEMultipart()
        msg["From"]    = cfg.get("SMTP.FROM", "")
        msg["To"]      = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))
        host    = cfg.get("SMTP.SERVER", "")
        port    = int(cfg.get("SMTP.PORT", "25"))
        user    = cfg.get("SMTP.USER", "")
        pwd     = cfg.get("SMTP.PASSWORD", "")
        use_ssl = cfg.get("SMTP.SSL", "False").strip().lower() == "true"
        use_tls = cfg.get("SMTP.TLS", "False").strip().lower() == "true"
        if use_ssl:
            srv = smtplib.SMTP_SSL(host, port, timeout=30)
        else:
            srv = smtplib.SMTP(host, port, timeout=30)
            if use_tls:
                srv.starttls()
        if user and pwd:
            srv.login(user, pwd)
        srv.sendmail(msg["From"], [to], msg.as_string())
        srv.quit()
        return ""
    except Exception as e:
        return f"Errore SMTP: {e}"


def send_mail_olk(olk_exe: str, to: str, subject: str, body: str) -> str:
    """
    Invia mail via processo esterno OLK (fire-and-forget).
    olk_exe è il path completo dell'eseguibile (MAIL.PATH).
    Crea ntjobs_mail.json nella stessa cartella dell'eseguibile
    e lo passa come argomento al processo.
    """
    try:
        olk_dir   = os.path.dirname(olk_exe)
        json_file = os.path.join(olk_dir, "ntjobs_mail.json")
        payload = {
            "config": {"nWaitStart": 3, "nWaitMail": 20,
                       "bOlkStart": True, "bOlkEnd": False},
            "mail_1": {
                "id": "mail_001", "to": [to], "cc": [], "ccn": [],
                "subject": subject, "format": "txt",
                "body": body, "attach": []
            }
        }
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        log(f"  OLK mail: json scritto in {json_file}")
        # Lancia l'eseguibile passando il path completo del json come argomento
        subprocess.Popen([olk_exe, json_file], shell=False, cwd=olk_dir)
        return ""
    except Exception as e:
        return f"Errore OLK mail: {e}"


# ---------------------------------------------------------------------------
# CLASSE PRINCIPALE
# ---------------------------------------------------------------------------

class NtJobsAi2:
    """
    Orchestratore light di aiJobsOS.
    Unico file Python, senza dipendenze interne multiple.
    Progettato per essere lanciato da aiJobsOs2.cmd.
    """

    def __init__(self):
        self.cfg:         Dict[str, str]  = {}
        self.users:       Dict[str, Dict] = {}
        self.actions:     Dict[str, Dict] = {}
        self.sysroot:     str             = ""
        self.inbox:       str             = ""
        self.archive:     str             = ""
        self.mail_engine: str             = ""
        self.olk_path:    str             = ""
        self.exit_flag:   bool            = False

    # ------------------------------------------------------------------
    # AVVIO
    # ------------------------------------------------------------------

    def start(self) -> str:
        """Carica tutta la configurazione. Ritorna '' se OK."""
        log("=== aiJobsOS2 START ===")

        err = self._load_config()
        if err:
            return err

        err = self._load_csv()
        if err:
            return err

        err = self._init_mail()
        if err:
            log(f"WARN mail non inizializzata: {err}")

        # ------------------------------------------------------------------
        # Riepilogo a schermo
        # ------------------------------------------------------------------
        log("=" * 60)
        log("SETTINGS da ntjobs_config.ini (valori espansi)")
        log("=" * 60)
        for k, v in sorted(self.cfg.items()):
            log(f"  {k:<20} = {v}")

        log("=" * 60)
        log("CARTELLE IMPORTANTI - verifica esistenza")
        log("=" * 60)
        check_paths = [
            ("SYSROOT",   self.sysroot,                          "dir"),
            ("INBOX",     self.inbox,                            "dir"),
            ("ARCHIVE",   self.archive,                          "dir"),
            ("LOG dir",   os.path.dirname(self.cfg.get("LOG", "")), "dir"),
            ("USERS",     self.cfg.get("USERS", ""),             "dir"),
            ("TEMP",      self.cfg.get("TEMP",  ""),             "dir"),
            ("MAIL.PATH", self.cfg.get("MAIL.PATH", ""),         "file"),
        ]
        for label, path, kind in check_paths:
            if not path:
                continue
            if kind == "file":
                exists = os.path.isfile(path)
            else:
                exists = os.path.isdir(path)
            status = "OK" if exists else "NON TROVATA"
            log(f"  [{status}]  {label:<12}  {path}")

        log("=" * 60)
        log("CARTELLE DI RICERCA jobs.ini per utente")
        log("=" * 60)
        found_any = False
        for uid, udata in self.users.items():
            raw_paths = udata.get("USER_PATHS", "")
            for upath in [p.strip() for p in raw_paths.split(",") if p.strip()]:
                upath_exp = expand(upath, self.cfg)
                status    = "OK" if os.path.isdir(upath_exp) else "NON TROVATA"
                log(f"  [{status}]  utente={uid:<10}  {upath_exp}")
                found_any = True
        if not found_any:
            log("  (nessun path utente configurato)")

        log("=" * 60)
        log(f"Utenti  : {list(self.users.keys())}")
        log(f"Azioni  : {list(self.actions.keys())}")
        log(f"Mail    : {self.mail_engine or '(non configurata)'}")
        log("=" * 60)
        return ""

    # ------------------------------------------------------------------

    def _load_config(self) -> str:
        global _log_file

        # 1. Leggi il .ini grezzo (valori non ancora espansi)
        err, raw = read_ini(CONFIG_FILE)
        if err:
            return err
        flat = raw.get("CONFIG", {})
        if not flat:
            return f"Sezione [CONFIG] mancante in {CONFIG_FILE}"

        # 2. Espansione in due passaggi:
        #      SYSROOT = K:\ntjobsai2          (valore diretto, niente $)
        #      INBOX   = $SYSROOT\Inbox        (passaggio 1 risolve $SYSROOT)
        #      ARCHIVE = $SYSROOT\Archive      (passaggio 1)
        #      LOG     = $SYSROOT\Log          (passaggio 1)
        flat = expand_config(flat)

        # 3. Verifica path obbligatori: devono esistere già, non vengono creati
        errors = []

        sysroot = flat.get("SYSROOT", "").strip()
        if not sysroot:
            errors.append("SYSROOT non definito in ntjobs_config.ini")
        elif not os.path.isdir(sysroot):
            errors.append(f"SYSROOT non esiste: {sysroot}")

        inbox = flat.get("INBOX", "").strip()
        if not inbox:
            errors.append("INBOX non definito in ntjobs_config.ini")
        elif not os.path.isdir(inbox):
            errors.append(f"INBOX non esiste: {inbox}")

        archive = flat.get("ARCHIVE", "").strip()
        if not archive:
            errors.append("ARCHIVE non definito in ntjobs_config.ini")
        elif not os.path.isdir(archive):
            errors.append(f"ARCHIVE non esiste: {archive}")

        # LOG nel .ini è la CARTELLA di log (es. $SYSROOT\Log).
        # Il file di log effettivo è aiJobsOS2.log dentro quella cartella.
        log_dir = flat.get("LOG", "").strip()
        if not log_dir:
            errors.append("LOG non definito in ntjobs_config.ini")
        elif not os.path.isdir(log_dir):
            errors.append(f"Cartella LOG non esiste: {log_dir}")

        if errors:
            return "Errori configurazione:\n" + "\n".join(f"  - {e}" for e in errors)

        # 4. Default per parametri operativi (non strutturali)
        if not flat.get("TIMEOUT"):
            flat["TIMEOUT"] = str(PROC_TIMEOUT)
        if not flat.get("CYCLE.WAIT"):
            flat["CYCLE.WAIT"] = str(CYCLE_WAIT)

        # 5. Imposta i campi dell'istanza
        self.cfg     = flat
        self.sysroot = sysroot
        self.inbox   = inbox
        self.archive = archive

        # 6. Attiva il log su file: LOG è la cartella, il file è aiJobsOS2.log
        global _log_file
        _log_file = os.path.join(log_dir, "aiJobsOS2.log")
        log(f"Log attivo: {_log_file}")

        return ""

    def _load_csv(self) -> str:
        err, self.users = read_csv(USERS_FILE)
        if err:
            return f"Utenti: {err}"
        for udata in self.users.values():
            for k, v in udata.items():
                udata[k] = expand(v, self.cfg)

        err, self.actions = read_csv(ACTIONS_FILE)
        if err:
            return f"Azioni: {err}"
        for adata in self.actions.values():
            for k, v in adata.items():
                adata[k] = expand(v, self.cfg)
        return ""

    def _init_mail(self) -> str:
        engine = self.cfg.get("MAIL.ENGINE", "").strip().upper()
        if engine == "SMTP":
            required = ["SMTP.SERVER", "SMTP.USER", "SMTP.PASSWORD",
                        "SMTP.PORT",   "SMTP.FROM"]
            missing = [k for k in required if not self.cfg.get(k)]
            if missing:
                return f"Settings SMTP mancanti: {missing}"
            self.mail_engine = "SMTP"
        elif engine == "OLK":
            # MAIL.PATH è il path completo del programma python da eseguire
            olk_exe = self.cfg.get("MAIL.PATH", "").strip()
            if not olk_exe:
                return "MAIL.PATH non definito in ntjobs_config.ini"
            if not os.path.isfile(olk_exe):
                return f"MAIL.PATH OLK non trovato: {olk_exe}"
            self.olk_path    = olk_exe
            self.mail_engine = "OLK"
        else:
            return f"MAIL.ENGINE non riconosciuto: '{engine}'"
        return ""

    # ------------------------------------------------------------------
    # CICLO PRINCIPALE
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Loop principale: search → process → archive → attesa."""
        cycle = 0
        while not self.exit_flag:
            cycle += 1
            log(f"--- Ciclo {cycle}  {ts()} ---")
            self._search()
            if not self.exit_flag:
                self._process_inbox()
            if not self.exit_flag:
                self._archive()
            if self.exit_flag:
                break
            wait = int(self.cfg.get("CYCLE.WAIT", str(CYCLE_WAIT)))
            log(f"Attesa {wait}s...")
            time.sleep(wait)
        log("=== aiJobsOS2 EXIT ===")

    # ------------------------------------------------------------------
    # SEARCH
    # ------------------------------------------------------------------

    def _search(self) -> None:
        """Scansiona le cartelle di tutti gli utenti cercando jobs.ini."""
        log("SEARCH: inizio scansione cartelle utenti")
        for uid, udata in self.users.items():
            raw_paths = udata.get("USER_PATHS", "")
            for upath in [p.strip() for p in raw_paths.split(",") if p.strip()]:
                upath = expand(upath, self.cfg)
                if not os.path.isdir(upath):
                    log(f"  SEARCH: cartella non trovata utente={uid} path={upath}")
                    continue
                log(f"  SEARCH: scansione utente={uid} path={upath}")
                if os.path.isfile(os.path.join(upath, "jobs.ini")):
                    log(f"  SEARCH: trovato jobs.ini per utente={uid} in {upath}")
                    err = self._move_to_inbox(upath, uid)
                    if err:
                        log(f"ERRORE move: {err}")

    def _move_to_inbox(self, src_folder: str, uid: str) -> str:
        """
        Sposta jobs.ini e i file FILE.* da src_folder a una nuova
        sottocartella univoca di self.inbox. Aggiunge USER= in [CONFIG].
        """
        jobs_src = os.path.join(src_folder, "jobs.ini")
        err, data = read_ini(jobs_src)
        if err:
            self._rename_to_end_in_place(jobs_src)
            return err
        if "CONFIG" not in data:
            self._rename_to_end_in_place(jobs_src)
            return f"jobs.ini senza sezione [CONFIG]: {jobs_src}"

        counter = 0
        while True:
            dest = os.path.join(self.inbox, f"jobs_{ts_folder()}_{counter}")
            if not os.path.exists(dest):
                break
            counter += 1
            time.sleep(0.05)

        try:
            os.makedirs(dest, exist_ok=True)
        except Exception as e:
            return f"Impossibile creare {dest}: {e}"

        data["CONFIG"]["USER"]      = uid
        data["CONFIG"]["USER_PATH"] = src_folder
        err = write_ini(data, os.path.join(dest, "jobs.ini"))
        if err:
            return err

        for section_data in data.values():
            for key, val in section_data.items():
                if key.startswith("FILE.") and val:
                    src_f = os.path.join(src_folder, val)
                    if os.path.isfile(src_f):
                        try:
                            shutil.move(src_f, os.path.join(dest, val))
                            log(f"  Allegato spostato: {val}")
                        except Exception as e:
                            log(f"  WARN allegato {val}: {e}")

        try:
            os.remove(jobs_src)
        except Exception:
            pass

        log(f"MOVE: jobs.ini e allegati spostati in {dest}")
        return ""

    def _rename_to_end_in_place(self, ini_path: str) -> None:
        try:
            os.rename(ini_path, os.path.splitext(ini_path)[0] + ".end")
        except Exception:
            pass

    # ------------------------------------------------------------------
    # PROCESS INBOX
    # ------------------------------------------------------------------

    def _process_inbox(self) -> None:
        """Esegue ogni cartella Inbox che ha jobs.ini ma non jobs.end."""
        log("INBOX: inizio scansione jobs da eseguire")
        if not os.path.isdir(self.inbox):
            log("INBOX: cartella Inbox non trovata")
            return
        for entry in sorted(os.listdir(self.inbox)):
            if self.exit_flag:
                break
            folder = os.path.join(self.inbox, entry)
            if not os.path.isdir(folder):
                continue
            if (os.path.isfile(os.path.join(folder, "jobs.ini")) and
                    not os.path.isfile(os.path.join(folder, "jobs.end"))):
                log(f"INBOX: avvio elaborazione {entry}")
                self._exec_jobs(folder)

    def _exec_jobs(self, folder: str) -> None:
        """Legge jobs.ini, esegue i job, scrive jobs.end, manda mail."""
        err, data = read_ini(os.path.join(folder, "jobs.ini"))
        if err:
            log(f"ERRORE lettura jobs.ini: {err}")
            self._write_end(folder, {}, err)
            return

        cfg_section = data.get("CONFIG", {})
        uid         = cfg_section.get("USER", "")
        user_mail   = self.users.get(uid, {}).get("USER_MAIL", "")
        exit_on_err = cfg_section.get("EXIT", "True").strip().lower() == "true"
        job_ids     = [s for s in data.keys() if s != "CONFIG"]
        results: Dict[str, str] = {}

        log(f"JOB: inizio esecuzione jobs.ini utente={uid} jobs={job_ids}")
        for jid in job_ids:
            if self.exit_flag:
                break
            log(f"JOB: avvio job={jid} utente={uid}")
            data[jid]["TS.START"] = ts()
            err_job = self._exec_single_job(jid, data[jid], folder, uid)
            data[jid]["TS.END"]       = ts()
            data[jid]["RETURN.TYPE"]  = "E" if err_job else "S"
            data[jid]["RETURN.VALUE"] = err_job if err_job else "Completato"
            results[jid] = err_job if err_job else "OK"
            if err_job:
                log(f"JOB: ERRORE job={jid} utente={uid}: {err_job}")
                if exit_on_err:
                    break
            else:
                log(f"JOB: completato job={jid} utente={uid} esito=OK")

        self._write_end(folder, data, "")

        # RETURN: copia tutta la cartella nella cartella utente
        self._return_to_user(folder, uid)

        if user_mail:
            summary = "\n".join(f"  {k}: {v}" for k, v in results.items())
            body = (f"Elaborazione completata.\n"
                    f"Utente  : {uid}\n"
                    f"Cartella: {os.path.basename(folder)}\n\n"
                    f"Risultati:\n{summary}\n")
            err_mail = self._send_mail(user_mail, "Completamento jobs.ini", body)
            if err_mail:
                log(f"  WARN mail: {err_mail}")
        else:
            log(f"  WARN: mail utente '{uid}' non trovata")

    def _return_to_user(self, folder: str, uid: str) -> None:
        """
        RETURN: copia tutta la cartella di lavoro (folder) nella cartella
        utente originale (USER_PATH salvata in [CONFIG] da _move_to_inbox).
        Permette all'utente di recuperare jobs.end e gli eventuali file di ritorno.
        """
        # Leggi USER_PATH dal jobs.end (o jobs.ini) nella cartella corrente
        src_ini = os.path.join(folder, "jobs.end")
        if not os.path.isfile(src_ini):
            src_ini = os.path.join(folder, "jobs.ini")
        err, data = read_ini(src_ini)
        if err:
            log(f"RETURN ERRORE: impossibile leggere {src_ini}: {err}")
            return

        user_path = data.get("CONFIG", {}).get("USER_PATH", "").strip()
        if not user_path:
            log(f"RETURN WARN: USER_PATH non trovato in [CONFIG] per utente={uid}")
            return
        if not os.path.isdir(user_path):
            log(f"RETURN ERRORE: cartella utente non trovata: {user_path}")
            return

        folder_name = os.path.basename(folder)
        dest = os.path.join(user_path, folder_name)

        log(f"RETURN: copia cartella {folder_name} → {user_path}")
        try:
            if os.path.exists(dest):
                shutil.rmtree(dest)
            shutil.copytree(folder, dest)
            log(f"RETURN: completata copia in {dest}")
        except Exception as e:
            log(f"RETURN ERRORE: copia fallita verso {dest}: {e}")

    def _exec_single_job(self, jid: str, jdata: Dict[str, str],
                          folder: str, uid: str) -> str:
        """Esegue un singolo job. Ritorna '' se OK, stringa errore altrimenti."""
        action = jdata.get("ACTION", "").strip().upper()
        if not action:
            action = jdata.get("COMMAND", "").strip().upper()
        if not action:
            return f"Job {jid}: nessuna ACTION o COMMAND definita"

        if action.startswith("SYS."):
            return self._exec_sys(action, uid)

        act_info = (self.actions.get(action) or
                    self.actions.get(action.lower()) or None)
        if act_info is None:
            return f"Azione '{action}' non trovata in ntjobs_actions.csv"
        if act_info.get("ACT_ENABLED", "False").strip().lower() != "true":
            return f"Azione '{action}' disabilitata"

        act_groups  = [g.strip() for g in act_info.get("ACT_GROUPS", "").split(",") if g.strip()]
        user_groups = [g.strip() for g in
                       self.users.get(uid, {}).get("USER_GROUPS", "").split(",") if g.strip()]
        if act_groups and not any(g in user_groups for g in act_groups):
            return f"Utente '{uid}' non autorizzato per azione '{action}'"

        script   = act_info.get("ACT_SCRIPT", "").strip()
        act_path = act_info.get("ACT_PATH",   "").strip()
        timeout  = int(act_info.get("ACT_TIMEOUT", "0") or 0)
        if timeout <= 0:
            timeout = int(self.cfg.get("TIMEOUT", str(PROC_TIMEOUT)))
        if not script:
            return f"ACT_SCRIPT non definito per azione '{action}'"

        app_ini = os.path.join(folder, "ntjobsapp.ini")
        err = write_ini({"CONFIG": {**self.cfg, **jdata, "ACTION": action}}, app_ini)
        if err:
            return f"Errore creazione ntjobsapp.ini: {err}"

        cwd = act_path if (act_path and os.path.isdir(act_path)) else folder
        try:
            proc = subprocess.Popen(script, shell=True, cwd=cwd,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            log(f"    Avviato PID {proc.pid}: {script}")
        except Exception as e:
            return f"Errore avvio processo '{script}': {e}"

        end_app    = os.path.join(folder, "ntjobsapp.end")
        elapsed    = 0
        result_err = ""
        while elapsed < timeout:
            time.sleep(10)
            elapsed += 10
            if os.path.isfile(end_app):
                log(f"    ntjobsapp.end trovato ({elapsed}s)")
                break
            if proc.poll() is not None:
                log(f"    Processo terminato (exit {proc.returncode})")
                break
        else:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
            result_err = f"Timeout ({timeout}s) per azione '{action}'"

        try:
            if os.path.isfile(app_ini):
                os.remove(app_ini)
        except Exception:
            pass

        return result_err

    def _exec_sys(self, action: str, uid: str) -> str:
        """Gestisce i comandi interni SYS.*"""
        action = action.upper()
        if action == "SYS.RELOAD":
            err = self._create_flag(FLAG_RESTART)
            if err:
                return err
            self.exit_flag = True
            log("  SYS.RELOAD: flag restart creato, uscita in corso")
        elif action in ("SYS.QUIT", "SYS.END"):
            self.exit_flag = True
            log("  SYS.QUIT: uscita richiesta")
        elif action == "SYS.SHUTDOWN":
            err = self._create_flag(FLAG_SHUTDOWN)
            if err:
                return err
            self.exit_flag = True
            log("  SYS.SHUTDOWN: flag shutdown creato, uscita in corso")
        elif action == "SYS.REBOOT":
            err = self._create_flag(FLAG_SHUTDOWN)
            if err:
                return err
            self.exit_flag = True
            log("  SYS.REBOOT: flag shutdown creato (reboot non gestito dal CMD), uscita in corso")
        elif action in ("SYS.MAIL.ADMIN", "SYS.EMAIL.ADMIN"):
            admin_mail = self.cfg.get("ADMIN.EMAIL", "")
            if not admin_mail:
                return "ADMIN.EMAIL non configurato"
            return self._send_mail(admin_mail,
                                   "Test mail admin da aiJobsOS2",
                                   "Mail di test dall'orchestratore aiJobsOS2.")
        elif action in ("SYS.MAIL.USER", "SYS.EMAIL.USER"):
            user_mail = self.users.get(uid, {}).get("USER_MAIL", "")
            if not user_mail:
                return f"Mail utente '{uid}' non trovata"
            return self._send_mail(user_mail,
                                   "Test mail utente da aiJobsOS2",
                                   f"Mail di test per l'utente {uid}.")
        else:
            return f"Azione SYS sconosciuta: {action}"
        return ""

    def _create_flag(self, filename: str) -> str:
        """Crea un file flag in self.sysroot."""
        try:
            with open(os.path.join(self.sysroot, filename), "w") as f:
                f.write(ts())
            return ""
        except Exception as e:
            return f"Errore creazione flag {filename}: {e}"

    # ------------------------------------------------------------------
    # WRITE END / ARCHIVE / MAIL
    # ------------------------------------------------------------------

    def _write_end(self, folder: str,
                   data: Dict[str, Dict[str, str]], global_err: str) -> None:
        if global_err:
            data.setdefault("CONFIG", {})["GLOBAL.ERROR"] = global_err
        err = write_ini(data, os.path.join(folder, "jobs.end"))
        if err:
            log(f"ERRORE scrittura jobs.end: {err}")
        else:
            log(f"  jobs.end scritto in {folder}")

    def _archive(self) -> None:
        """Sposta in Archive le cartelle di Inbox che hanno jobs.end."""
        log("ARCHIVE: inizio scansione Inbox")
        if not os.path.isdir(self.inbox):
            log("ARCHIVE: cartella Inbox non trovata")
            return
        for entry in os.listdir(self.inbox):
            folder = os.path.join(self.inbox, entry)
            if not os.path.isdir(folder):
                continue
            if os.path.isfile(os.path.join(folder, "jobs.end")):
                dest = os.path.join(self.archive, entry)
                if os.path.exists(dest):
                    dest = f"{dest}_{ts_folder()}"
                try:
                    shutil.move(folder, dest)
                    log(f"ARCHIVE: archiviata cartella {entry} → {dest}")
                except Exception as e:
                    log(f"ARCHIVE ERRORE: {entry}: {e}")

    def _send_mail(self, to: str, subject: str, body: str) -> str:
        if self.mail_engine == "SMTP":
            return send_mail_smtp(self.cfg, to, subject, body)
        elif self.mail_engine == "OLK":
            return send_mail_olk(self.olk_path, to, subject, body)
        else:
            log(f"  WARN: mail non inviata a {to} (engine non configurato)")
            return ""


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Posizionati in SYSROOT_BOOT così i file flag vengono creati
    # nella stessa cartella dove il CMD launcher li cerca.
    try:
        os.chdir(SYSROOT_BOOT)
    except Exception:
        pass

    bot = NtJobsAi2()
    err = bot.start()
    if err:
        log(f"ERRORE avvio: {err}")
        sys.exit(1)

    try:
        bot.run()
    except KeyboardInterrupt:
        log("Interruzione utente (Ctrl+C)")

    sys.exit(0)
