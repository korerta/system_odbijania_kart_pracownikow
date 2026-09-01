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

# region Zapytania
def result_get_list_employees() -> dict:
    """
    Funkcja zwracająca listę pracowników
    :return: Zwraca rezultat zapytania z bazy danych
    """

    res_conn = conn_cursor() # Połączenie z bazą danych
    data_return = {}

    # Jeśli nie zwróciło żadnego błędu
    if 'status' in res_conn:
        try:
            cursor = res_conn['cursor']

            cursor.execute("SELECT id, name_surname FROM users")
            data_return['result'] = cursor.fetchall()
            data_return['status'] = True

        except Exception as error:
            print('Błąd podczas zwracania rezultatu w result_get_hired_accounts, błąd:', error)
            data_return['status'] = False
            data_return['error'] = f'Błąd podczas zwracania rezultatu w result_get_hired_accounts, błąd: {error}'

        finally:
            conn = res_conn['conn']
            close_connection(conn)

    # Jeśli zwróciło błąd
    else:
        print('Błąd podczas zwracania rezultatu w result_get_list_employees')
        data_return['status'] = False
        data_return['error'] = 'Błąd podczas zwracania rezultatu w result_get_list_employees'

    return data_return

def add_new_employee(id: str, name_surname: str) -> dict:
    """
    Funkcja dodająca pracownika
    :param id: Identyfikator pracownika
    :param name_surname: Imię i Nazwisko pracownika
    :return: Zwraca rezultat zapytania z bazy danych
    """

    res_conn = conn_cursor() # Połączenie z bazą danych
    data_return = {}

    # Jeśli nie zwróciło żadnego błędu
    if 'status' in res_conn:
        conn = res_conn['conn']

        try:
            cursor = res_conn['cursor']

            cursor.execute("INSERT INTO users (id, name_surname) VALUES (?, ?)", (id, name_surname))
            conn.commit()
            data_return['status'] = True

        except Exception as error:
            print('Błąd podczas zwracania rezultatu w add_new_employee, błąd:', error)
            data_return['status'] = False
            data_return['error'] = f'Błąd podczas zwracania rezultatu w add_new_employee, błąd: {error}'

        finally:
            close_connection(conn)

    # Jeśli zwróciło błąd
    else:
        print('Błąd podczas zwracania rezultatu w result_get_list_employees')
        data_return['status'] = False
        data_return['error'] = 'Błąd podczas zwracania rezultatu w add_new_employee'

    return data_return

def del_employee(id: str) -> dict:
    """
    Funkcja usuwająca pracownika
    :param id: Identyfikator pracownika
    :return: Zwraca rezultat zapytania z bazy danych
    """

    res_conn = conn_cursor() # Połączenie z bazą danych
    data_return = {}

    # Jeśli nie zwróciło żadnego błędu
    if 'status' in res_conn:
        conn = res_conn['conn']

        try:
            cursor = res_conn['cursor']

            cursor.execute("DELETE FROM users WHERE id = ?", (id,))
            conn.commit()
            data_return['status'] = True

        except Exception as error:
            print('Błąd podczas zwracania rezultatu w del_employee, błąd:', error)
            data_return['status'] = False
            data_return['error'] = f'Błąd podczas zwracania rezultatu w del_employee, błąd: {error}'

        finally:
            close_connection(conn)

    # Jeśli zwróciło błąd
    else:
        print('Błąd podczas zwracania rezultatu w del_employee')
        data_return['status'] = False
        data_return['error'] = 'Błąd podczas zwracania rezultatu w del_employee'

    return data_return

def check_exist_employee(id: str) -> dict:
    """
    Funkcja zwracająca czy jest pracownik o podanym ID
    :return: Zwraca rezultat zapytania z bazy danych
    """

    res_conn = conn_cursor() # Połączenie z bazą danych
    data_return = {}

    # Jeśli nie zwróciło żadnego błędu
    if 'status' in res_conn:
        try:
            cursor = res_conn['cursor']

            cursor.execute("SELECT COUNT(id) FROM users WHERE id=?", (id,))
            data_return['result'] = cursor.fetchone()
            data_return['status'] = True

        except Exception as error:
            print('Błąd podczas zwracania rezultatu w check_exist_employee, błąd:', error)
            data_return['status'] = False
            data_return['error'] = f'Błąd podczas zwracania rezultatu w check_exist_employee, błąd: {error}'

        finally:
            conn = res_conn['conn']
            close_connection(conn)

    # Jeśli zwróciło błąd
    else:
        print('Błąd podczas zwracania rezultatu w check_exist_employee')
        data_return['status'] = False
        data_return['error'] = 'Błąd podczas zwracania rezultatu w check_exist_employee'

    return data_return

def add_new_row_calendar(id: str, type: str, date: str) -> dict:
    """
    Funkcja dodająca nowy wpis do kalendarza
    :param id: Identyfikator pracownika
    :param type: Typ operacji (czy wejście do firmy/wyjście z firmy itp
    :param date: Czas odbicia karty
    :return: Zwraca rezultat zapytania z bazy danych
    """

    res_conn = conn_cursor() # Połączenie z bazą danych
    data_return = {}

    # Jeśli nie zwróciło żadnego błędu
    if 'status' in res_conn:
        conn = res_conn['conn']

        try:
            cursor = res_conn['cursor']

            cursor.execute("INSERT INTO calendar (id, type, date) VALUES (?, ?, ?)", (id, type, date))
            conn.commit()
            data_return['status'] = True

        except Exception as error:
            print('Błąd podczas zwracania rezultatu w add_new_row_calendar, błąd:', error)
            data_return['status'] = False
            data_return['error'] = f'Błąd podczas zwracania rezultatu w add_new_row_calendar, błąd: {error}'

        finally:
            close_connection(conn)

    # Jeśli zwróciło błąd
    else:
        print('Błąd podczas zwracania rezultatu w add_new_row_calendar')
        data_return['status'] = False
        data_return['error'] = 'Błąd podczas zwracania rezultatu w add_new_row_calendar'

    return data_return

# endregion