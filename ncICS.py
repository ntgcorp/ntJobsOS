import pandas as pd
from icalendar import Calendar, Event, vText, vDatetime
from datetime import datetime, timedelta
import uuid
import pytz
import os

class NC_ICS:
    def __init__(self):
        """
        Inizializza la classe NC_ICS per convertire dati Excel o dizionario in file iCalendar.
        """
        self.calendar = Calendar()
        self.calendar.add('prodid', '-//NC_ICS Converter//IT')
        self.calendar.add('version', '2.0')
        self.calendar.add('calscale', 'GREGORIAN')
        self.calendar.add('method', 'PUBLISH')
        
    def _create_event(self, data_ora, titolo, promemoria, note):
        """
        Crea un evento iCalendar con i dati forniti.
        
        Args:
            data_ora (datetime): Data e ora dell'evento
            titolo (str): Titolo dell'evento
            promemoria (int/float): Ore prima dell'evento per il promemoria
            note (str): Note dell'evento
            
        Returns:
            Event: Oggetto evento iCalendar
        """
        event = Event()
        
        # Generare un UID univoco per l'evento
        event.add('uid', str(uuid.uuid4()))
        
        # Aggiungere titolo
        event.add('summary', titolo)
        
        # Aggiungere data e ora dell'evento
        event.add('dtstart', data_ora)
        
        # Impostare durata predefinita di 1 ora
        event.add('dtend', data_ora + timedelta(hours=1))
        
        # Aggiungere note
        if isinstance(note, str) and note.strip():
            event.add('description', note)
            
        # Timestamp di creazione
        event.add('dtstamp', datetime.now(pytz.UTC))
        
        # Aggiungere promemoria
        if promemoria and not pd.isna(promemoria):
            try:
                ore_promemoria = float(promemoria)
                alarm = self._create_alarm(ore_promemoria)
                event.add_component(alarm)
            except (ValueError, TypeError):
                pass
                
        return event
    
    def _create_alarm(self, ore_prima):
        """
        Crea un allarme/promemoria per l'evento.
        
        Args:
            ore_prima (float): Ore prima dell'evento per il promemoria
            
        Returns:
            Component: Componente allarme per l'evento
        """
        from icalendar import Alarm
        
        alarm = Alarm()
        alarm.add('action', 'DISPLAY')
        alarm.add('description', 'Reminder')
        
        # Convertire ore in minuti
        minuti = int(ore_prima * 60)
        trigger = timedelta(minutes=-minuti)  # Negativo perché è prima dell'evento
        
        alarm.add('trigger', trigger)
        return alarm
    
    def _process_event_data(self, data_ora, titolo, promemoria, note):
        """
        Elabora e valida i dati dell'evento.
        
        Args:
            data_ora: Data e ora dell'evento (datetime o str)
            titolo: Titolo dell'evento
            promemoria: Ore prima dell'evento per il promemoria
            note: Note dell'evento
            
        Returns:
            tuple: (data_ora, titolo, promemoria, note) processati o None se i dati non sono validi
        """
        # Verificare che la data ora sia valida
        if pd.isna(data_ora):
            return None
        
        if isinstance(data_ora, str):
            # Tentare di convertire stringhe in datetime
            try:
                data_ora = datetime.strptime(data_ora, "%d/%m/%Y %H:%M")
            except ValueError:
                try:
                    data_ora = datetime.strptime(data_ora, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    return None
        
        # Assicurarsi che data_ora sia un oggetto datetime con timezone
        if isinstance(data_ora, datetime):
            if data_ora.tzinfo is None:
                data_ora = data_ora.replace(tzinfo=pytz.UTC)
        else:
            return None
        
        titolo = str(titolo) if not pd.isna(titolo) else "Evento senza titolo"
        promemoria = promemoria if not pd.isna(promemoria) else None
        note = str(note) if not pd.isna(note) else ""
        
        return (data_ora, titolo, promemoria, note)
    
    def _reset_calendar(self):
        """
        Resetta il calendario per una nuova creazione.
        """
        self.calendar = Calendar()
        self.calendar.add('prodid', '-//NC_ICS Converter//IT')
        self.calendar.add('version', '2.0')
        self.calendar.add('calscale', 'GREGORIAN')
        self.calendar.add('method', 'PUBLISH')
    
    def CreateFromXLS(self, excel_file_path, ics_file_path):
        """
        Legge un file Excel e crea un file iCalendar con gli eventi.
        
        Args:
            excel_file_path (str): Percorso del file Excel di input
            ics_file_path (str): Percorso del file iCalendar di output
            
        Returns:
            bool: True se la conversione è avvenuta con successo, False altrimenti
        """
        try:
            # Resettare il calendario
            self._reset_calendar()
            
            # Leggere il file Excel
            df = pd.read_excel(excel_file_path)
            
            # Verificare che le colonne necessarie siano presenti
            required_columns = ['DataOra', 'Titolo', 'Promemoria', 'Note']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Colonne mancanti nel file Excel: {', '.join(missing_columns)}")
            
            # Iterare su ogni riga e creare eventi
            for idx, row in df.iterrows():
                try:
                    processed_data = self._process_event_data(
                        row['DataOra'], 
                        row['Titolo'], 
                        row['Promemoria'], 
                        row['Note']
                    )
                    
                    if processed_data:
                        data_ora, titolo, promemoria, note = processed_data
                        event = self._create_event(data_ora, titolo, promemoria, note)
                        self.calendar.add_component(event)
                except Exception as e:
                    print(f"Errore durante l'elaborazione della riga {idx}: {e}")
            
            # Scrivere il file iCalendar
            with open(ics_file_path, 'wb') as f:
                f.write(self.calendar.to_ical())
            
            return True
        except Exception as e:
            print(f"Errore durante la conversione: {e}")
            return False
    
    def CreateFromDict(self, events_dict, ics_file_path):
        """
        Crea un file iCalendar a partire da un dizionario di eventi.
        
        Args:
            events_dict (dict): Dizionario contenente gli stessi campi del file Excel
                Formato: {
                    'events': [
                        {
                            'DataOra': datetime o str,
                            'Titolo': str,
                            'Promemoria': float/int,
                            'Note': str
                        },
                        ...
                    ]
                }
            ics_file_path (str): Percorso del file iCalendar di output
            
        Returns:
            bool: True se la conversione è avvenuta con successo, False altrimenti
        """
        try:
            # Resettare il calendario
            self._reset_calendar()
            
            # Verificare che il dizionario abbia il formato corretto
            if not isinstance(events_dict, dict) or 'events' not in events_dict:
                raise ValueError("Il dizionario deve contenere una chiave 'events' con una lista di eventi")
            
            # Iterare su ogni evento e creare componenti calendario
            for idx, event_data in enumerate(events_dict['events']):
                try:
                    # Verificare che l'evento abbia i campi necessari
                    required_fields = ['DataOra', 'Titolo', 'Promemoria', 'Note']
                    missing_fields = [field for field in required_fields if field not in event_data]
                    
                    if missing_fields:
                        print(f"Evento {idx}: campi mancanti {', '.join(missing_fields)}. Saltato.")
                        continue
                    
                    processed_data = self._process_event_data(
                        event_data['DataOra'], 
                        event_data['Titolo'], 
                        event_data['Promemoria'], 
                        event_data['Note']
                    )
                    
                    if processed_data:
                        data_ora, titolo, promemoria, note = processed_data
                        event = self._create_event(data_ora, titolo, promemoria, note)
                        self.calendar.add_component(event)
                except Exception as e:
                    print(f"Errore durante l'elaborazione dell'evento {idx}: {e}")
            
            # Scrivere il file iCalendar
            with open(ics_file_path, 'wb') as f:
                f.write(self.calendar.to_ical())
            
            return True
        except Exception as e:
            print(f"Errore durante la conversione: {e}")
            return False

# Esempio di utilizzo
if __name__ == "__main__":
    converter = NC_ICS()
    
    # Esempio con file Excel
    input_file = "eventi.xlsx"
    output_file = "calendario_eventi.ics"
    
    if converter.CreateFromXLS(input_file, output_file):
        print(f"Conversione da Excel completata con successo. File salvato: {output_file}")
    else:
        print("La conversione da Excel è fallita.")
    
    # Esempio con dizionario
    events_dict = {
        'events': [
            {
                'DataOra': datetime(2025, 3, 15, 10, 0),
                'Titolo': 'Riunione di progetto',
                'Promemoria': 1.5,
                'Note': 'Preparare documentazione'
            },
            {
                'DataOra': datetime(2025, 3, 16, 14, 30),
                'Titolo': 'Call con cliente',
                'Promemoria': 1.0,
                'Note': 'Rivedere offerta commerciale'
            }
        ]
    }
    
    dict_output_file = "eventi_da_dict.ics"
    
    if converter.CreateFromDict(events_dict, dict_output_file):
        print(f"Conversione da dizionario completata con successo. File salvato: {dict_output_file}")
    else:
        print("La conversione da dizionario è fallita.")
