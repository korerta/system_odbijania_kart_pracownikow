"""
Plik obsługujący bazę danych
"""

# region importy
# Biblioteki
import sqlite3

# Moje pliki
from config import paths

# endregion

#region Funkcje wykorzystywane wiele razy
# Zamknięcie połączenia z bazą danych
def close_connection(conn) -> None:
    """
    Funkcja zamykająca połączenie z bazą danych
    :param conn: Połączenie z bazą danych
    :return: Nic nie zwraca
    """

    try:
        conn.close()

    except Exception as error:
        print('Błąd podczas zamykania połączenia z bazą danych, błąd:', error)

# Otwieranie połączenia i tworzenie kursora
def conn_cursor() -> dict:
    """
    Funkcja otwierająca połączenie z bazą danych i tworzy kursor
    :return: Zwraca kursor i połączenie z bazą danych
    """
    data_return = {}

    try:
        conn = sqlite3.connect(paths['db_file'], timeout=30.0)  # Otwieranie połączenia
        cursor = conn.cursor()  # Tworzenie kursora do zapytań
        data_return['cursor'] = cursor
        data_return['conn'] = conn
        data_return['status'] = True

    except Exception as error:
        data_return['error'] = error
        data_return['status'] = False

    finally:
        return data_return
#endregion