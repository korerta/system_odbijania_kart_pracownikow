# System Rejestracji Czasu Pracy (Web NFC)

Prosty system rejestracji czasu pracy oparty o technologię Web NFC i bazę SQLite. 
Użytkownik wybiera typ akcji (Rozpoczęcie pracy, Zakończenie pracy, Wyjście na chwilę, Powrót do pracy) i przykłada kartę/tag NFC do czytnika.

Projekt ma celowo uproszczony interfejs bez rozbudowanego front-endu — nacisk położony jest na logikę backendową, niezawodność i działanie lokalne.

System jest zaprojektowany do uruchomienia na jednym urządzeniu (localhost) pełniącym rolę terminala i serwera.

---

## Funkcjonalności

- **Rejestracja wejść/wyjść:** Obsługa operacji przez Web NFC API w przeglądarce.
- **Panel Administratora:** Dodawanie pracowników, usuwanie oraz bezpośrednie programowanie/kodowanie tagów NFC unikalnym ID (UUID).
- **Raporty:** Przegląd historii zdarzeń zabezpieczony osobnym hasłem, z filtrowaniem według pracowników.
- **Baza danych:** Lokalny plik SQLite zabezpieczony transakcyjnie przed uszkodzeniem danych.

---

## Wymagania

- Python 3.10+
- Przeglądarka obsługująca Web NFC (np. Google Chrome na systemie Android)
- Dostęp w bezpiecznym kontekście (`http://localhost` lub `https://`)