"""
Serwer WWW
"""

# region importy
#biblioteki
from flask import Flask, render_template, session, redirect, url_for, request, jsonify
import json
from uuid import uuid4

#inne pliki
from config import ip, port, debug, secret_key, admin_password
# endregion

def data_home() -> dict:
    data_return = {}
    return data_return

def data_login(form) -> dict:
    data_return = {}

    # sprawdzenie czy istnieją wymagane pola formularza
    if not 'password' in form:
        data_return['message'] = 'Wprowadź hasło'
        return data_return

    # sprawdzenie poprawności hasła
    if not form['password'] == admin_password:
        data_return['message'] = 'Nieprawidłowe hasło'
        return data_return

    data_return['message'] = 'Jeśli to widzisz to odśwież stronę'
    session['logged'] = 'good'
    return data_return

def data_admin(form) -> dict:
    data_return = {}

    # region wczytanie zawartości pliku json
    try:
        with open('employees.json', 'r') as f:
            contents_file_json = json.load(f)
            data_return['list_employees'] = contents_file_json['employees']

    except (FileNotFoundError, json.JSONDecodeError):
        print(f'Plik json nie istnieje lub jest pusty/uszkodzony')
        data_return['message'] = 'Nieoczekiwany błąd. Skontaktuj się z Administratorem.'
        return data_return
    # endregion

    # region obsługa formularza dodawania pracownika
    if 'add_employee' in form:
        # region czy wszystkie elementy formularza istnieją
        for element in ('add_employee', 'name_employee'):
            if not element in form:
                print(f'Brakuje elementu w formularzu: {element}')
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
        contents_file_json['employees'][id_employee] = name_employee

        try:
            with open('employees.json', 'w') as f:
                json.dump(contents_file_json, f, indent=4)  # indent=4 dla czytelniejszego formatowania
                print('Pomyślnie dodano pracownika')
                data_return['message_add'] = 'Pomyślnie dodano pracownika'
                data_return['message_add_id'] = f'Identyfikator pracownika: {id_employee}'

        except Exception as error:
            print(f'Wystąpił nieoczekiwany błąd, podczas aktualizowania pliku json, błąd: {error}')
            data_return['message_add'] = 'Nieoczekiwany błąd. Skontaktuj się z Administratorem.'
            return data_return
        # endregion

    # endregion

    # region formularz usuwania pracownika
    if 'del_employee' in form:
        # region czy wszystkie elementy formularza istnieją
        for element in ('del_employee', 'employee'):
            if not element in form:
                print(f'Brakuje elementu w formularzu: {element}')
                data_return['message_del'] = 'Wypełnij poprawnie cały formularz.'
                return data_return
        # endregion

        try:
            contents_file_json['employees'].pop(form['employee'])

        except Exception as error:
            print(f'Wystąpił nieoczekiwany błąd, podczas aktualizowania pliku json, błąd: {error}')
            data_return['message_del'] = 'Nieoczekiwany błąd. Skontaktuj się z Administratorem.'
            return data_return

        # region aktualizowanie pliku json
        try:
            with open('employees.json', 'w') as f:
                json.dump(contents_file_json, f, indent=4)  # indent=4 dla czytelniejszego formatowania
                print('Pomyślnie usunięto pracownika')
                data_return['message_add'] = 'Pomyślnie usunięto pracownika'

        except Exception as error:
            print(f'Wystąpił nieoczekiwany błąd, podczas aktualizowania pliku json, błąd: {error}')
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
    # Pobranie danych JSON przesłanych z przeglądarki
    data = request.get_json()

    # region czy otrzymano jakiekolwiek dane
    if not data:
        return jsonify({"status": "error", "message": "Brak danych"}), 400
    # endregion

    # Odpowiedź zwracana do przeglądarki
    return jsonify({
        "status": "success",
    }), 200

    #region zapis czasu w pliku json

    # endregion

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