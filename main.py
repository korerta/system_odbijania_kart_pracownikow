"""
Serwer WWW
"""

# region importy
#biblioteki
from flask import Flask, render_template, session, redirect, url_for, request
import json

#inne pliki
from config import ip, port, debug, secret_key, admin_password
# endregion

def data_home(form) -> dict:
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

    # region obsługa formularza dodawania pracownika
    if 'add_employee' in form:
        # region czy wszystkie elementy formularza istnieją
        for element in ('add_employee', 'name_employee'):
            if not element in form:
                print(f'Brakuje elementu w formularzu: {element}')
                data_return['message'] = 'Wypełnij poprawnie cały formularz.'

        # endregion

        name_employee = form['name_employee']

        # region długość imienia i nazwiska
        if not len(name_employee):
            print('Długość nazwy pracownika jest za krótka')
            data_return['message'] = 'Wprowadź Imię i Nazwisko pracownika'

        if len(name_employee) > 50:
            print('Długość nazwy pracownika jest za długa')
            data_return['message'] = 'Imię i Nazwisko pracownika jest za długie'
        # endregion

        # region dodawanie pracownika
        try:
            with open('employees.json', 'r') as f:
                contents_file_json = json.load(f)
                contents_file_json['employees'].append(name_employee)

        except (FileNotFoundError, json.JSONDecodeError):
            print(f'Plik json nie istnieje lub jest pusty/uszkodzony')
            data_return['message'] = 'Nieoczekiwany błąd. Skontaktuj się z Administratorem.'

        try:
            with open('employees.json', 'w') as f:
                json.dump(contents_file_json, f, indent=4)  # indent=4 dla czytelniejszego formatowania

        except Exception as error:
            print(f'Wystąpił nieoczekiwany błąd, podczas aktualizowania pliku json, błąd: {error}')
            data_return['message'] = 'Nieoczekiwany błąd. Skontaktuj się z Administratorem.'

        # endregion

        print('Pomyślnie dodano pracownika')
        data_return['message'] = 'Pomyślnie dodano pracownika'

    # endregion

    return data_return

# region konfiguracja flask
app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key
# endregion

# region trasy
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
    return_data = {}

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