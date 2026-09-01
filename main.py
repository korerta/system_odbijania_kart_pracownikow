"""
Serwer WWW
"""

# region importy
# Biblioteki
from flask import Flask, render_template, session, redirect, url_for, request, jsonify
from uuid import uuid4
from datetime import datetime

# Moje pliki
from config import ip, port, debug, secret_key, admin_password, raport_password
import database
# endregion

def return_employees() -> dict:
    return database.result_get_list_employees() #Zapytanie do bazy danych

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
    data_return = {
        'list_employees': return_employees() # Wczytanie listy pracowników
    }

    # region Jakby się nie udało zdobyć danych z bazy danych
    if not data_return['list_employees']['status']:
        data_return['message_del'] = data_return['message_add'] = 'Nieoczekiwany błąd. Skontaktuj się z Administratorem.'
        return data_return
    # endregion

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

        # region dodawanie pracownika do bazy danych
        if database.add_new_employee(id_employee, name_employee)['status']:
            data_return['message_add'] = 'Pomyślnie dodano pracownika.'
            data_return['message_add_id'] = f'Identyfikator pracownika: {id_employee}.'

        else:
            print(f'Wystąpił nieoczekiwany błąd, podczas dodawania pracownika.')
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

        # region aktualizowanie bazy danych
        if database.del_employee(form['employee'])['status']:
            print('Pomyślnie usunięto pracownika.')
            data_return['message_del'] = 'Pomyślnie usunięto pracownika.'

        else:
            print('Wystąpił nieoczekiwany błąd, podczas usuwania pracownika z bazy danych.')
            data_return['message_del'] = 'Nieoczekiwany błąd. Skontaktuj się z Administratorem.'

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
        else:
            data_return['show_data'] = True
        # endregion

        # region pobranie listy pracowników
        database_result = database.result_get_list_employees()

        if database_result['status']: # jeśli udało się pobrać dane
            # region dodawanie pracowników do słownika
            for value in database_result['result']: # iterowanie po pracownikach
                data_return['data'][value[0]] = {'name':value[1], 'calendar':[]}
            # endregion

            # region dodawanie wpisów z kalendarza do danego pracownika
            database_result = database.get_calendar()
            for row in database_result['result']:
                data_return['data'][row[1]]['calendar'].append(row[2:])
            # endregion
        # endregion

    # endregion

    return data_return

# region Konfiguracja flask
app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key
# endregion

# region Trasy
@app.route('/api/nfc', methods=['POST'])
def handle_nfc():
    # pobranie danych JSON przesłanych z przeglądarki
    data = request.get_json()

    # region czy otrzymano jakiekolwiek dane
    if not data:
        return jsonify({"status": "error", "message": "Brak danych"}), 400
    # endregion

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
    if not database.check_exist_employee(id_employee)['result'][0]:
        print('Nie znaleziono pracownika z podanym identyfikatorem.')
        return jsonify({"status": "error", "message": "Nie znaleziono pracownika z podanym identyfikatorem."}), 400
    # endregion

    # region pobieranie daty i czasu
    now = datetime.now()
    curr_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
    # endregion

    # region wrzucenie do kalendarza odbicie karty
    if database.add_new_row_calendar(id_employee, type_operation, curr_date_time)['status']:
        return jsonify({"status": "success", "message": "Pomyślnie zarejestrowano czas odbicia karty."}), 200
    else:
        return jsonify({"status": "error", "message": "Nieoczekiwany błąd. Skontaktuj się z Administratorem."}), 400

    # endregion

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