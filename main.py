"""
Serwer WWW
"""

# region importy
#biblioteki
from flask import Flask, render_template, session, redirect, url_for, request, jsonify
import json, time
from uuid import uuid4

#inne pliki
from config import ip, port, debug, secret_key, admin_password
# endregion

def return_employees_json():
    data_return = {}

    # region wczytanie zawartości pliku json
    try:
        with open('employees.json', 'r') as f:
            contents_file_json = json.load(f)
            data_return['list_employees'] = contents_file_json['list_employees']

    except (FileNotFoundError, json.JSONDecodeError):
        print(f'Plik json nie istnieje lub jest pusty/uszkodzony')
        data_return['message'] = 'Nieoczekiwany błąd. Skontaktuj się z Administratorem.'

    return data_return
    # endregion

def return_calendar_json():
    data_return = {}

    # region wczytanie zawartości pliku json
    try:
        with open('calendar.json', 'r') as f:
            contents_file_json = json.load(f)
            data_return['calendar'] = contents_file_json['calendar']

    except (FileNotFoundError, json.JSONDecodeError):
        print(f'Plik json nie istnieje lub jest pusty/uszkodzony')
        data_return['message'] = 'Nieoczekiwany błąd. Skontaktuj się z Administratorem.'

    return data_return
    # endregion

def data_home() -> dict:
    data_return = {}
    return data_return

def data_login(form) -> dict:
    data_return = {}

    # sprawdzenie czy istnieją wymagane pola formularza
    if not 'password' in form:
        data_return['message'] = 'Wprowadź hasło.'
        return data_return

    # sprawdzenie poprawności hasła
    if not form['password'] == admin_password:
        data_return['message'] = 'Nieprawidłowe hasło.'
        return data_return

    data_return['message'] = 'Jeśli to widzisz to odśwież stronę.'
    session['logged'] = 'good'
    return data_return

def data_admin(form) -> dict:
    data_return = {}

    # wczytanie zawartości pliku json
    contents_file_json = return_employees_json()
    data_return['list_employees'] = contents_file_json

    # region obsługa formularza dodawania pracownika
    if 'add_employee' in form:
        # region czy wszystkie elementy formularza istnieją
        for element in ('add_employee', 'name_employee'):
            if not element in form:
                print(f'Brakuje elementu w formularzu: {element}.')
                data_return['message_add'] = 'Wypełnij poprawnie cały formularz.'
                return data_return
        # endregion

        name_employee = form['name_employee']

        id_employee = str(uuid4())

        # region długość imienia i nazwiska
        if not len(name_employee):
            print('Długość nazwy pracownika jest za krótka.')
            data_return['message_add'] = 'Wprowadź Imię i Nazwisko pracownika.'
            return data_return

        if len(name_employee) > 50:
            print('Długość nazwy pracownika jest za długa.')
            data_return['message_add'] = 'Imię i Nazwisko pracownika jest za długie.'
            return data_return
        # endregion

        # region aktualizowanie pliku json
        contents_file_json['list_employees'][id_employee] = name_employee

        try:
            with open('employees.json', 'w') as f:
                json.dump(contents_file_json, f, indent=4)  # indent=4 dla czytelniejszego formatowania
                print('Pomyślnie dodano pracownika')
                data_return['message_add'] = 'Pomyślnie dodano pracownika.'
                data_return['message_add_id'] = f'Identyfikator pracownika: {id_employee}.'

        except Exception as error:
            print(f'Wystąpił nieoczekiwany błąd, podczas aktualizowania pliku json, błąd: {error}.')
            data_return['message_add'] = 'Nieoczekiwany błąd. Skontaktuj się z Administratorem.'
            return data_return
        # endregion

    # endregion

    # region formularz usuwania pracownika
    if 'del_employee' in form:
        # region czy wszystkie elementy formularza istnieją
        for element in ('del_employee', 'employee'):
            if not element in form:
                print(f'Brakuje elementu w formularzu: {element}.')
                data_return['message_del'] = 'Wypełnij poprawnie cały formularz.'
                return data_return
        # endregion

        # region aktualizowanie pliku json
        try:
            contents_file_json['list_employees'].pop(form['employee'])

        except Exception as error:
            print(f'Wystąpił nieoczekiwany błąd, podczas aktualizowania pliku json, błąd: {error}.')
            data_return['message_del'] = 'Nieoczekiwany błąd. Skontaktuj się z Administratorem.'
            return data_return

        try:
            with open('employees.json', 'w') as f:
                json.dump(contents_file_json, f, indent=4)  # indent=4 dla czytelniejszego formatowania
                print('Pomyślnie usunięto pracownika.')
                data_return['message_del'] = 'Pomyślnie usunięto pracownika.'

        except Exception as error:
            print(f'Wystąpił nieoczekiwany błąd, podczas aktualizowania pliku json, błąd: {error}.')
            data_return['message_del'] = 'Nieoczekiwany błąd. Skontaktuj się z Administratorem.'
            return data_return
        # endregion

    # endregion

    return data_return

# region konfiguracja flask
app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key
# endregion

# region trasy
@app.route('/api/nfc', methods=['POST'])
def handle_nfc():
    # pobranie danych JSON przesłanych z przeglądarki
    data = request.get_json()

    # region czy otrzymano jakiekolwiek dane
    if not data:
        return jsonify({"status": "error", "message": "Brak danych"}), 400
    # endregion

    # wczytanie zawartości pliku json
    contents_file_json_employees = return_employees_json()
    contents_file_json_calendar = return_calendar_json()

    # aktualny czas
    curr_time_unix = time.time()

    # region odczytanie identyfikatora pracownika z tagu NFC
    try:
        id_employee = data['records'][0]['data']

    except Exception as error:
        print(f'Tag posiada nieprawidłowe dane: {error}.')
        return jsonify({"status": "error", "message": "Tag posiada nieprawidłowe dane."}), 400
    # endregion

    # region czy pracownik istnieje z podanym identyfikatorem
    if not id_employee in contents_file_json_employees['list_employees']:
        print('Nie znaleziono pracownika z podanym identyfikatorem.')
        return jsonify({"status": "error", "message": "Nie znaleziono pracownika z podanym identyfikatorem."}), 400
    # endregion

    # region zapis do pliku json czasu odbicia karty
    contents_file_json_calendar['calendar'].setdefault(id_employee, []).append(curr_time_unix)

    try:
        with open('calendar.json', 'w') as f:
            json.dump(contents_file_json_calendar, f, indent=4)  # indent=4 dla czytelniejszego formatowania
            print('Pomyślnie zapisano czas odbicia karty.')

    except Exception as error:
        print(f'Wystąpił nieoczekiwany błąd, podczas aktualizowania pliku json, błąd: {error}.')
        return jsonify({"status": "error", "message": "Nieoczekiwany błąd. Skontaktuj się z Administratorem."}), 400

    # endregion

    # Odpowiedź zwracana do przeglądarki
    return jsonify({"status": "success", "message": "Pomyślnie zarejestrowano czas odbicia karty."}), 200

# Strona główna
@app.route("/", methods=['GET', 'POST'])
def home():
    # jeśli zalogowany to ma wrócić do panelu Administratora
    if 'logged' in session:
        return redirect(url_for('admin'))

    return render_template("index.html")

# strona logowania do panelu Administratora
@app.route("/login", methods=['GET', 'POST'])
#@limiter.limit("10 per minute")
def login():
    return_data = {}
    # jeśli zalogowany to ma wrócić do panelu Administratora
    if 'logged' in session:
        return redirect(url_for('admin'))

    # przesłanie formularza
    if request.form:
        return_data = data_login(request.form)

    return render_template("login.html", data=return_data)

# panel Administratora
@app.route("/admin", methods=['GET', 'POST'])
def admin():
    # jeśli nie zalogowany to ma wrócić do strony głównej
    if not 'logged' in session:
        return redirect(url_for('home'))

    # przesłanie formularza
    if request.form:
        if 'logout' in request.form:
            session.clear()  # usuwanie sesji
            return redirect(url_for('login'))

    return_data = data_admin(request.form)

    return render_template("admin.html", data=return_data)
# endregion

if __name__ == "__main__":
    print('Uruchamianie serwera WWW.')
    app.run(debug=debug, host=ip, port=port)