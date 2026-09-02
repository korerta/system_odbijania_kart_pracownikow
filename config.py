"""
Plik konfiguracyjny
"""

# region Importy
# Biblioteki
import os
from typing import Dict
from dotenv import load_dotenv

# endregion
load_dotenv() # To ładuje dane z pliku .env

ip = '0.0.0.0'
port = 5001
debug = True
secret_key = os.getenv("secret_key")
admin_password = os.getenv("admin_password")
raport_password = os.getenv("raport_password")

# region Przygotowanie ścieżek plików używanych
base_dir = os.path.dirname(os.path.abspath(__file__)) # Ścieżka bezwzględna obecnego pliku
paths: Dict[str, str] = {
    'base_dir': base_dir,
    'db_file': os.path.join(base_dir, 'database.db'),

}
# endregion