from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class CryptoUtils:
    """
    Classe per la crittografia e decrittografia di stringhe e file
    utilizzando la libreria cryptography con Fernet (AES-128).
    """
    
    def __init__(self, password):
        """
        Inizializza la classe con una password.
        
        Args:
            password (str): La password per generare la chiave
        """
        try:
            self.password = password.encode()
            self.salt = os.urandom(16)
            self.key = self._generate_key()
            self.cipher = Fernet(self.key)
        except Exception as e:
            self.password = None
            self.salt = None
            self.key = None
            self.cipher = None
    
    def _generate_key(self):
        """
        Genera una chiave di crittografia basata sulla password.
        
        Returns:
            bytes: Chiave di crittografia
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password))
        return key
    
    def encrypt_string(self, text):
        """
        Cripta una stringa.
        
        Args:
            text (str): Testo da crittografare
            
        Returns:
            tuple: (sResult, risultato)
                - sResult (str): Stringa vuota in caso di successo o messaggio di errore
                - risultato (dict/None): Dizionario con dati crittografati o None in caso di errore
        """
        sResult = ""
        result = None
        
        try:
            encrypted_data = self.cipher.encrypt(text.encode())
            result = {
                'salt': base64.urlsafe_b64encode(self.salt).decode(),
                'encrypted': base64.urlsafe_b64encode(encrypted_data).decode()
            }
        except Exception as e:
            sResult = f"Errore nella crittografia della stringa: {str(e)}"
            
        return sResult, result
    
    def decrypt_string(self, encrypted_dict):
        """
        Decripta una stringa.
        
        Args:
            encrypted_dict (dict): Dizionario con salt e testo crittografato
            
        Returns:
            tuple: (sResult, risultato)
                - sResult (str): Stringa vuota in caso di successo o messaggio di errore
                - risultato (str/None): Testo decrittografato o None in caso di errore
        """
        sResult = ""
        decrypted_data = None
        
        try:
            # Recupera il salt originale
            original_salt = base64.urlsafe_b64decode(encrypted_dict['salt'].encode())
            self.salt = original_salt
            self.key = self._generate_key()
            self.cipher = Fernet(self.key)
            
            # Decripta
            encrypted_data = base64.urlsafe_b64decode(encrypted_dict['encrypted'].encode())
            decrypted_data = self.cipher.decrypt(encrypted_data).decode()
        except KeyError as e:
            sResult = f"Errore nel formato del dizionario di input: {str(e)}"
        except Exception as e:
            sResult = f"Errore nella decrittografia della stringa: {str(e)}"
            decrypted_data = None
            
        return sResult, decrypted_data
    
    def encrypt_file(self, input_file, output_file=None):
        """
        Cripta un file.
        
        Args:
            input_file (str): Percorso del file da crittografare
            output_file (str, optional): Percorso del file crittografato
            
        Returns:
            tuple: (sResult, risultato)
                - sResult (str): Stringa vuota in caso di successo o messaggio di errore
                - risultato (str/None): Percorso del file crittografato o None in caso di errore
        """
        sResult = ""
        
        if output_file is None:
            output_file = input_file + '.encrypted'
        
        try:
            # Verifica che il file di input esista
            if not os.path.exists(input_file):
                return f"Errore: Il file '{input_file}' non esiste", None
            
            with open(input_file, 'rb') as f:
                data = f.read()
            
            encrypted_data = self.cipher.encrypt(data)
            
            with open(output_file, 'wb') as f:
                # Salva prima il salt
                f.write(len(self.salt).to_bytes(2, byteorder='big'))
                f.write(self.salt)
                # Poi salva i dati crittografati
                f.write(encrypted_data)
                
        except PermissionError:
            sResult = f"Errore di permessi: impossibile leggere o scrivere i file"
            output_file = None
        except IOError as e:
            sResult = f"Errore di I/O durante la crittografia del file: {str(e)}"
            output_file = None
        except Exception as e:
            sResult = f"Errore durante la crittografia del file: {str(e)}"
            output_file = None
        
        return sResult, output_file
    
    def decrypt_file(self, input_file, output_file=None):
        """
        Decripta un file.
        
        Args:
            input_file (str): Percorso del file crittografato
            output_file (str, optional): Percorso del file decrittografato
            
        Returns:
            tuple: (sResult, risultato)
                - sResult (str): Stringa vuota in caso di successo o messaggio di errore
                - risultato (str/None): Percorso del file decrittografato o None in caso di errore
        """
        sResult = ""
        
        if output_file is None:
            if input_file.endswith('.encrypted'):
                output_file = input_file[:-10]
            else:
                output_file = input_file + '.decrypted'
        
        try:
            # Verifica che il file di input esista
            if not os.path.exists(input_file):
                return f"Errore: Il file crittografato '{input_file}' non esiste", None
            
            with open(input_file, 'rb') as f:
                # Leggi il salt
                salt_len = int.from_bytes(f.read(2), byteorder='big')
                self.salt = f.read(salt_len)
                # Aggiorna la chiave con il salt recuperato
                self.key = self._generate_key()
                self.cipher = Fernet(self.key)
                # Leggi i dati crittografati
                encrypted_data = f.read()
            
            decrypted_data = self.cipher.decrypt(encrypted_data)
            
            with open(output_file, 'wb') as f:
                f.write(decrypted_data)
                
        except PermissionError:
            sResult = f"Errore di permessi: impossibile leggere o scrivere i file"
            output_file = None
        except IOError as e:
            sResult = f"Errore di I/O durante la decrittografia del file: {str(e)}"
            output_file = None
        except Exception as e:
            sResult = f"Errore durante la decrittografia del file: {str(e)}"
            output_file = None
        
        return sResult, output_file
