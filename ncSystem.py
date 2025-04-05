import os
import platform
import subprocess
import signal
import psutil
import time


class SystemInterface:
    """
    Classe per interfacciarsi al sistema operativo con compatibilità
    sia per Linux che per Windows.
    """

    def __init__(self):
        self.platform = platform.system()
        if self.platform not in ["Windows", "Linux"]:
            raise Exception(f"Sistema operativo non supportato: {self.platform}")

    def sys_shutdown(self, delay=0):
        """
        Spegne il PC dopo un eventuale ritardo.
        
        Args:
            delay (int): Ritardo in secondi prima dello spegnimento (default: 0)
        """
        print(f"Spegnimento del sistema tra {delay} secondi...")
        try:
            if self.platform == "Windows":
                os.system(f"shutdown /s /t {delay}")
            else:  # Linux
                os.system(f"shutdown -h +{delay//60}")
            return True
        except Exception as e:
            print(f"Errore durante lo spegnimento: {str(e)}")
            return False

    def sys_reload(self, delay=0):
        """
        Riavvia il PC dopo un eventuale ritardo.
        
        Args:
            delay (int): Ritardo in secondi prima del riavvio (default: 0)
        """
        print(f"Riavvio del sistema tra {delay} secondi...")
        try:
            if self.platform == "Windows":
                os.system(f"shutdown /r /t {delay}")
            else:  # Linux
                os.system(f"shutdown -r +{delay//60}")
            return True
        except Exception as e:
            print(f"Errore durante il riavvio: {str(e)}")
            return False

    def sys_kill(self, target, use_pid=False):
        """
        Termina un processo in base al PID o al nome del processo/finestra.
        
        Args:
            target: Il PID (int) o il nome (str) del processo da terminare
            use_pid (bool): Se True, target è interpretato come PID, altrimenti come nome processo
            
        Returns:
            bool: True se il processo è stato terminato con successo, False altrimenti
        """
        try:
            if use_pid:
                pid = int(target)
                if self.platform == "Windows":
                    subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=True)
                else:  # Linux
                    os.kill(pid, signal.SIGTERM)
                print(f"Processo con PID {pid} terminato con successo")
                return True
            else:
                # Cerca per nome processo
                name = str(target)
                if self.platform == "Windows":
                    subprocess.run(["taskkill", "/F", "/IM", name], check=True)
                    print(f"Processo '{name}' terminato con successo")
                    return True
                else:  # Linux
                    killed = False
                    for proc in psutil.process_iter(['pid', 'name']):
                        if name.lower() in proc.info['name'].lower():
                            pid = proc.info['pid']
                            os.kill(pid, signal.SIGTERM)
                            killed = True
                            print(f"Processo '{name}' (PID: {pid}) terminato con successo")
                    return killed
        except Exception as e:
            print(f"Errore durante la terminazione del processo: {str(e)}")
            return False

    def get_process_list(self):
        """
        Restituisce una lista di processi attivi
        
        Returns:
            list: Lista di tuple (pid, nome) dei processi attivi
        """
        processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                processes.append((proc.info['pid'], proc.info['name']))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return processes

    def cancel_shutdown(self):
        """
        Annulla un'operazione di spegnimento o riavvio pianificata
        
        Returns:
            bool: True se l'operazione è stata annullata con successo, False altrimenti
        """
        try:
            if self.platform == "Windows":
                os.system("shutdown /a")
            else:  # Linux
                os.system("shutdown -c")
            print("Operazione di spegnimento/riavvio annullata")
            return True
        except Exception as e:
            print(f"Errore durante l'annullamento: {str(e)}")
            return False


# Esempio di utilizzo
if __name__ == "__main__":
    sys_interface = SystemInterface()
    
    # Esempi (decommentare con cautela!)
    # print("Ottengo la lista dei processi...")
    # processes = sys_interface.get_process_list()
    # for pid, name in processes[:5]:  # Mostra solo i primi 5 processi
    #     print(f"PID: {pid}, Nome: {name}")
    
    # Per terminare un processo specifico:
    # sys_interface.sys_kill("notepad.exe")  # Per nome (Windows)
    # sys_interface.sys_kill(1234, use_pid=True)  # Per PID
    
    # Per riavviare il sistema con un ritardo di 60 secondi:
    # sys_interface.sys_reload(60)
    
    # Per annullare uno spegnimento/riavvio pianificato:
    # sys_interface.cancel_shutdown()
    
    # Per spegnere il sistema (ATTENZIONE!):
    # sys_interface.sys_shutdown(120)  # Spegnimento tra 2 minuti
