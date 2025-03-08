import os
import datetime
import csv
from pathlib import Path

def scan_files(directory, pattern="*"):
    """
    Scansiona ricorsivamente una directory e raccoglie informazioni sui file che corrispondono al pattern.
    
    Args:
        directory (str): Il percorso della directory da scansionare
        pattern (str): Il pattern per filtrare i file (es. "*.txt", "*.pdf", ecc.)
    
    Returns:
        list: Lista di dizionari contenenti le informazioni sui file trovati
    """
    files_info = []
    
    try:
        # Converti il percorso in oggetto Path per una gestione più robusta
        base_path = Path(directory)
        
        # Scansiona ricorsivamente tutti i file che corrispondono al pattern
        for file_path in base_path.rglob(pattern):
            if file_path.is_file():  # Verifica che sia un file e non una directory
                # Ottieni le statistiche del file
                stats = file_path.stat()
                
                # Crea un dizionario con le informazioni del file
                file_info = {
                    'nome_file': file_path.name,
                    'percorso_completo': str(file_path),
                    'dimensione_bytes': stats.st_size,
                    'dimensione_leggibile': convert_size(stats.st_size),
                    'data_creazione': datetime.datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                    'ultimo_aggiornamento': datetime.datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                }
                
                files_info.append(file_info)
                
    except Exception as e:
        print(f"Errore durante la scansione: {e}")
    
    return files_info

def convert_size(size_bytes):
    """
    Converte la dimensione da bytes in un formato leggibile (KB, MB, GB, ecc.)
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0

def save_to_csv(files_info, output_file):
    """
    Salva le informazioni dei file in un file CSV.
    
    Args:
        files_info (list): Lista di dizionari contenenti le informazioni dei file
        output_file (str): Percorso del file CSV di output
    """
    try:
        # Definisci i campi del CSV
        fieldnames = ['nome_file', 'percorso_completo', 'dimensione_bytes', 
                     'dimensione_leggibile', 'data_creazione', 'ultimo_aggiornamento']
        
        # Scrivi il file CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(files_info)
            
        print(f"\nDati salvati con successo nel file: {output_file}")
        
    except Exception as e:
        print(f"Errore durante il salvataggio del CSV: {e}")

def print_files_info(files_info):
    """
    Stampa le informazioni dei file in formato leggibile.
    
    Args:
        files_info (list): Lista di dizionari contenenti le informazioni dei file
    """
    print(f"\nTrovati {len(files_info)} file:")
    for file in files_info:
        print("\n-------------------")
        print(f"Nome file: {file['nome_file']}")
        print(f"Percorso: {file['percorso_completo']}")
        print(f"Dimensione: {file['dimensione_leggibile']}")
        print(f"Data creazione: {file['data_creazione']}")
        print(f"Ultimo aggiornamento: {file['ultimo_aggiornamento']}")

def get_user_input():
    """
    Raccoglie l'input dell'utente per la scansione dei file.
    
    Returns:
        tuple: (directory, pattern)
    """
    directory = input("Inserisci il percorso della directory da scansionare: ")
    pattern = input("Inserisci il pattern di ricerca (es. *.txt, *.pdf, oppure * per tutti i file): ")
    return directory, pattern

def process_files():
    """
    Funzione principale che gestisce il flusso del programma.
    """
    try:
        # Ottieni input utente
        directory, pattern = get_user_input()
        
        # Esegui la scansione
        print("\nScansione in corso...")
        files_info = scan_files(directory, pattern)
        
        # Mostra i risultati
        print_files_info(files_info)
        
        # Gestisci il salvataggio CSV
        save_csv = input("\nVuoi salvare i risultati in un file CSV? (s/n): ").lower()
        if save_csv == 's':
            output_file = input("Inserisci il nome del file CSV di output: ")
            if not output_file.endswith('.csv'):
                output_file += '.csv'
            save_to_csv(files_info, output_file)
            
    except Exception as e:
        print(f"Si è verificato un errore: {e}")

def main():
    process_files()

if __name__ == "__main__":
    main()
