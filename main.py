"""
Serwer WWW
"""

# region importy
# Biblioteki
from flask import Flask, render_template, session, redirect, url_for, request, jsonify
import json, re
from uuid import uuid4
from datetime import datetime, timedelta

# Inne pliki
from config import ip, port, debug, secret_key, admin_password, raport_password
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

def data_raporty(form) -> dict:
    data_return = {'show_data': False, 'data': {}}

    # region obsługa formularza odblokowywania raportów
    if 'unlock_data' in form:

        # region czy wszystkie elementy formularza istnieją
        if not 'password' in form:
            print('Brakuje elementu formularzu: password.')
            data_return['message_unlock_data'] = 'Wypełnij poprawnie cały formularz.'
            return data_return
        # endregion

        # region czy hasło poprawne
        if raport_password != form['password']:
            print('Hasło niepoprawne')
            data_return['message_unlock_data'] = 'Hasło jest nieprawidłowe.'
            return data_return
        # endregion

        # wczytanie zawartości pliku json
        contents_file_json_employees = return_employees_json()
        contents_file_json_calendar = return_calendar_json()

        # region dodawanie pracowników do słownika
        for key, value in contents_file_json_employees['list_employees'].items(): # iterowanie po pracownikach
            if key in contents_file_json_calendar['calendar']: # zabezpieczenie jeśli danego klucza by nie byłó w kalendarzu
                data_calendar = contents_file_json_calendar['calendar'][key] # odczytanie dat z kalendarza danego pracownika
                data_return['data'][key] = [data_calendar]
                pass
        # endregion

        data_return['show_data'] = True
    # endregion

    return data_return

# region Konfiguracja flask
app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key
# endregion

# region Trasy
@app.route('/api/nfc', methods=['POST'])
def handle_nfc():
    def update_json(data_to_update) -> bool:
        # region zapis do pliku json czasu odbicia karty
        try:
            json_str = json.dumps(data_to_update, indent=4)

            with open('calendar.json', 'w') as f:
                formatted_json = re.sub(r'\[\s*\n\s*(".*?",?)\s*\n\s*(".*?")\s*\n\s*\]',r'[\1 \2]',json_str)
                f.write(formatted_json)
                print('Pomyślnie zapisano czas odbicia karty.')
                data_return = True

        except Exception as error:
            print(f'Wystąpił nieoczekiwany błąd, podczas aktualizowania pliku json, błąd: {error}.')
            data_return = False
        # endregion

        return data_return

    # pobranie danych JSON przesłanych z przeglądarki
    data = request.get_json()

    # region czy otrzymano jakiekolwiek dane
    if not data:
        return jsonify({"status": "error", "message": "Brak danych"}), 400
    # endregion

    # wczytanie zawartości pliku json
    contents_file_json_employees = return_employees_json()
    contents_file_json_calendar = return_calendar_json()

    # region walidacja operacji czy pracownik wchodzi czy wychodzi z pracy
    type_operation = data['type_operation']

    if type_operation not in 'in, out, out_temp, in_back':
        print('Nie wybrano z listy wyboru odpowiedniej opcji.')
        return jsonify({"status": "error", "message": "Wybierz czy wchodzisz czy wychodzisz z zakładu pracy."}), 400

    # endregion

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

    # region pobieranie daty i czasu
    now = datetime.now()
    yesterday_date = (now - timedelta(days=1)).date()
    curr_time = now.strftime("%H:%M:%S")
    curr_date = now.strftime("%Y-%m-%d")
    # endregion

    # region czy klucz pracownika jest już w kalendarzu jeśli nie to go utworzyć.
    if not id_employee in contents_file_json_calendar['calendar']:
        contents_file_json_calendar['calendar'].setdefault(id_employee, {})  # utworzenie klucza pracownika w kalendarzu jeśli nie istnieje
        if not update_json(contents_file_json_calendar):
            return jsonify({"status": "error", "message": "Nieoczekiwany błąd. Skontaktuj się z Administratorem."}), 400

        print('Pomyślnie utworzono pracownika w kalendarzu')
        return jsonify({"status": "success", "message": "Pomyślnie zarejestrowano pracownika."}), 200
    # endregion

    # region wrzucenie do kalendarza odbicie karty
    if type_operation == 'out':
        if curr_date not in contents_file_json_calendar['calendar'][id_employee]:
            if yesterday_date in contents_file_json_calendar['calendar'][id_employee]:
                update_json(contents_file_json_calendar['calendar'][id_employee][yesterday_date].append(['out', curr_time]))
                if not update_json(contents_file_json_calendar):
                    return jsonify({"status": "error", "message": "Nieoczekiwany błąd. Skontaktuj się z Administratorem."}), 400
            else:
                update_json(contents_file_json_calendar['calendar'][id_employee].setdefault(curr_date, []).append(['out', curr_time]))
                if not update_json(contents_file_json_calendar):
                    return jsonify({"status": "error", "message": "Nieoczekiwany błąd. Skontaktuj się z Administratorem."}), 400
        else:
            update_json(contents_file_json_calendar['calendar'][id_employee].setdefault(curr_date, []).append(['out', curr_time]))
            if not update_json(contents_file_json_calendar):
                return jsonify({"status": "error", "message": "Nieoczekiwany błąd. Skontaktuj się z Administratorem."}), 400
    else:
        contents_file_json_calendar['calendar'][id_employee].setdefault(curr_date, []).append([type_operation, curr_time])
        if not update_json(contents_file_json_calendar):
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

# Strona logowania do panelu Administratora
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

# Panel Administratora
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

# Raporty
@app.route("/raporty", methods=['GET', 'POST'])
def raporty():
    return_data = data_raporty({})

    # przesłanie formularza
    if request.form:
        return_data = data_raporty(request.form)

    return render_template("raporty.html", data=return_data)
# endregion

if __name__ == "__main__":
    print('Uruchamianie serwera WWW.')
    app.run(debug=debug, host=ip, port=port)