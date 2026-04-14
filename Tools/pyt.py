#!/usr/bin/env python3
"""
pyt.py - Python Tool per eseguire comandi via command line
"""

import sys
import os
import subprocess
import shutil
from datetime import datetime

# ========== VARIABILI INTERNE ==========
QEMU_IMG = r"X:\_Applic\Qemu\qemu-img.exe"
PYT_VER = "20260414"
LOG_FILE = os.path.join(os.path.dirname(__file__), "pyt.log")

# ========== FUNZIONI INTERNE ==========
def pyt_Timestamp():
    """Ritorna YYYYMMDD:HHMMSS"""
    return datetime.now().strftime("%Y%m%d:%H%M%S")

def pyt_Print(msg):
    """Stampa a video e scrive su pyt.log in append"""
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{msg}\n")

def pyt_End():
    """Fine del programma"""
    pyt_Print("PYT.END: " + pyt_Timestamp())

# ========== DIRETTIVE ==========
def app_help(args=None):
    """
    Direttiva help/h - Mostra l'help in console (non va nel log)
    """
    print(f"pyt versione {PYT_VER}")
    print("")
    print("Comandi disponibili:")
    print("  help, h              - Mostra questo help")
    print("  vhdx2vmdk f1 f2      - Converte file vhdx in vmdk")
    print("  compress7z f1        - Comprime una cartella con 7-Zip (max compressione)")
    print("")
    print("Uso:")
    print("  pyt help")
    print("  pyt vhdx2vmdk disco.vhdx disco.vmdk")
    print("  pyt compress7z C:\\myfolder")
    print("  pyt @script.txt")
    print("")
    print("Note:")
    print("  - I timestamp nei file compressi usano il formato YYYYMMDD-HHMMSS")
    print("  - Il file pyt.log viene creato nella stessa cartella di pyt.py")

def app_vhdx2vmdk(args):
    """
    Direttiva vhdx2vmdk - Converte file vhdx in vmdk usando qemu-img
    Parametri: f1=file vhdx, f2=file vmdk
    """
    # Verifica numero parametri
    if len(args) != 2:
        pyt_Print(f"ERRORE: vhdx2vmdk richiede 2 parametri, forniti {len(args)}")
        return False
    
    f1, f2 = args[0], args[1]
    
    # Verifica esistenza file sorgente
    if not os.path.isfile(f1):
        pyt_Print(f"ERRORE: File sorgente '{f1}' non trovato")
        return False
    
    # Costruzione comando
    cmd = f'"{QEMU_IMG}" convert -f vhdx -O vmdk "{f1}" "{f2}"'
    pyt_Print(f"Esecuzione: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            pyt_Print(f"Conversione completata: {f1} -> {f2}")
            return True
        else:
            pyt_Print(f"ERRORE: {result.stderr}")
            return False
    except Exception as e:
        pyt_Print(f"ECCEZIONE: {str(e)}")
        return False

def app_compress7z(args):
    """
    Direttiva compress7z - Comprime una cartella con 7-Zip aggiungendo timestamp
    Parametri: f1=cartella da comprimere
    """
    # Verifica numero parametri
    if len(args) != 1:
        pyt_Print(f"ERRORE: compress7z richiede 1 parametro, forniti {len(args)}")
        return False
    
    cartella = args[0]
    
    # Verifica esistenza cartella
    if not os.path.isdir(cartella):
        pyt_Print(f"ERRORE: Cartella '{cartella}' non trovata")
        return False
    
    # Ottieni nome base della cartella
    nome_base = os.path.basename(cartella.rstrip(os.sep))
    
    # Timestamp per filename (sostituisci ':' con '-')
    ts_file = pyt_Timestamp().replace(":", "-")  # YYYYMMDD-HHMMSS
    
    # Cerca 7z.exe nel PATH
    path_7z = shutil.which("7z.exe")
    if not path_7z:
        # Tentativo percorsi comuni Windows
        common_paths = [
            r"C:\Program Files\7-Zip\7z.exe",
            r"C:\Program Files (x86)\7-Zip\7z.exe"
        ]
        for p in common_paths:
            if os.path.isfile(p):
                path_7z = p
                break
    
    if not path_7z:
        pyt_Print("ERRORE: 7-Zip non trovato. Installalo o aggiungi al PATH")
        return False
    
    # Nome archivio
    archivio = f"{nome_base}_{ts_file}.7z"
    
    # Comando compressione (massima compressione -mx9)
    cmd = f'"{path_7z}" a -t7z -mx9 "{archivio}" "{cartella}"'
    pyt_Print(f"Esecuzione: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            pyt_Print(f"Creato: {archivio}")
            return True
        else:
            pyt_Print(f"ERRORE compressione: {result.stderr}")
            return False
    except Exception as e:
        pyt_Print(f"ECCEZIONE: {str(e)}")
        return False

# ========== MOTORE PRINCIPALE ==========
def esegui_direttiva(linea):
    """
    Esegue una singola direttiva dalla stringa linea
    """
    parti = linea.strip().split()
    if not parti:
        return
    
    direttiva = parti[0].lower()
    args = parti[1:]
    
    # Log inizio direttiva
    pyt_Print(f"PYT.START.{direttiva.upper()} {pyt_Timestamp()}")
    
    # Mappatura direttive
    if direttiva in ["help", "h"]:
        app_help(args)  # help ignora i parametri
    elif direttiva == "vhdx2vmdk":
        app_vhdx2vmdk(args)
    elif direttiva == "compress7z":
        app_compress7z(args)
    else:
        pyt_Print(f"ERRORE: Direttiva '{direttiva}' non riconosciuta")
        app_help(args)
    
    # Log fine direttiva
    pyt_Print(f"PYT.END.{direttiva.upper()} {pyt_Timestamp()}")

def esegui_da_file(filename):
    """
    Legge ed esegue comandi da file (modalità @)
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                # Salta righe vuote e righe che iniziano con ';'
                if not line or line.startswith(';'):
                    continue
                pyt_Print(f"\n--- Esecuzione riga {line_num}: {line} ---")
                esegui_direttiva(line)
    except FileNotFoundError:
        pyt_Print(f"ERRORE: File '{filename}' non trovato")
        sys.exit(1)
    except Exception as e:
        pyt_Print(f"ERRORE durante lettura file: {str(e)}")
        sys.exit(1)

def main():
    """
    Funzione principale
    """
    # Avvio programma
    pyt_Print(f"PYT.START: {PYT_VER} {pyt_Timestamp()}")
    
    # Nessun parametro -> help
    if len(sys.argv) < 2:
        app_help()
        pyt_End()
        return
    
    primo_arg = sys.argv[1]
    
    # Modalità file @
    if primo_arg.startswith('@'):
        filename = primo_arg[1:]
        # Gestisci eventuali virgolette
        filename = filename.strip('"')
        esegui_da_file(filename)
    else:
        # Modalità singola direttiva
        linea = " ".join(sys.argv[1:])
        esegui_direttiva(linea)
    
    # Fine programma
    pyt_End()

if __name__ == "__main__":
    main()