# Założenia systemu biletowego

1. Każdy teatr ma różne spektakle, daty i godziny.
2. Każdy spektakl ma przypisane miejsca.
3. Użytkownik może rezerwować bilety, a status miejsca musi się zmieniać.

# Schemat bazy danych

## 1. Tabela spektakli (`shows`)

Trzyma informacje o spektaklach w danym teatrze.

| **Kolumna**     | **Typ**                                               | **Opis**                         |
| --------------- | ----------------------------------------------------- | -------------------------------- |
| `show_id`       | `UUID`                                                | Unikalny identyfikator spektaklu |
| `show_date`     | `DATE`                                                | Data spektaklu                   |
| `show_time`     | `TIME`                                                | Godzina spektaklu                |
| `title`         | `TEXT`                                                | Tytuł spektaklu                  |
| **PRIMARY KEY** | ((`show_date`, `show_time`), `show_id`) | Klucz główny                     |

---

## 2. Tabela miejsc w spektaklu (`seats_by_show`)

Śledzi dostępność miejsc dla konkretnego spektaklu.

| **Kolumna**        | **Typ**                | **Opis**                             |
| ------------------ | ---------------------- | ------------------------------------ |
| `show_id`          | `UUID`                 | Unikalny identyfikator spektaklu     |
| `seat_id`          | `TEXT`                 | Identyfikator miejsca (np. A1, B2)   |
| `seat_number`      | `INT`                  | Numer miejsca                        |
| `status`           | `TEXT`                 | Status (available, reserved, sold)   |
| `reservation_id`   | `UUID`                 | Id rezerwacji                       |
| `reservation_time` | `TIMESTAMP`            | Czas rezerwacji                      |
| **PRIMARY KEY**    | ((`show_id`), `seat_id`) | Klucz główny                         |

- Kolumna `status` pozwala na zarządzanie dostępnością miejsc (np. `available`, `reserved`, `sold`).

---

## 3. Tabela rezerwacji użytkownika (`reservations_by_user`)

Przechowuje listę rezerwacji użytkownika.

| **Kolumna**        | **Typ**                       | **Opis**                  |
| ------------------ | ----------------------------- | ------------------------- |
| `reservation_id`   | `UUID`                        | Identyfikator rezerwacji  |
| `show_id`          | `UUID`                        | Id spektaklu              |
| `seat_id`          | `TEXT`                        | Id miejsca                |
| `seat_reservation_time` | `TIMESTAMP`                   | Czas rezerwacji           |
| **PRIMARY KEY**    | ((show_id), seat_reservation_time, reservation_id) | Klucz główny               |

---

## 4. Tabela danych o rezerwacjach użytkownika (`reservations_info`)

Przechowuje szczegóły o rezerwacji.

| **Kolumna**        | **Typ**                       | **Opis**                  |
| ------------------ | ----------------------------- | ------------------------- |
| `reservation_id`   | `UUID`                        | Identyfikator rezerwacji  |
| `show_id`          | `UUID`                        | Id spektaklu              |
| `tickets_count`          | `INTEGER`                     | Liczba zarezerwowanych biletów |
| `user_name`        | `TEXT`                        | Imię i nazwisko użytkownika |
| `email`            | `TEXT`                        | Email użytkownika         |
| `reservation_time` | `TIMESTAMP`                   | Czas rezerwacji           |
| **PRIMARY KEY**    | ((reservation_id), show_id, reservation_time) | Klucz główny               |

---

# Dozwolone operacje

## Klient:
- **Rezerwacja miejsc**: Klient może zarezerwować określoną ilość konkretnych miejsc na dany spektakl.
  - Operacja ta będzie polegała na utworzeniu wpisów w tabeli `reservations_by_user`, gdzie zapisane będą szczegóły dotyczące rezerwacji miejsc (np. `show_id`, `seat_id`, `seat_reservation_time`).

## Admin:
- **Tworzenie spektaklu**: Administrator może utworzyć spektakl w systemie.
  - **Tworzenie spektaklu** automatycznie tworzy odpowiednią ilość miejsc w tabeli `seats_by_show`, odpowiadającą liczbie dostępnych biletów (liczba miejsc w spektaklu).
  - Z każdego spektaklu generowane są miejsca w systemie, przypisując im status "available".

## Działanie systemu:

### 1. Rezerwacja przez klienta:
- Klient pobiera listę dostępnych miejsc na wybrany spektaktl z tabeli `seats_by_show`.
- Klient rezerwuje miejsca na spektakl poprzez dodanie nowych rekordów do tabeli `reservations_by_user`.
- System informuje klienta, że rezerwacja została przyjęta, ale nie potwierdza jeszcze zakupu biletów.
- System przekazuje klientowi informację, że w przypadku pomyślnej rezerwacji, bilety zostaną wysłane w ciągu określonego czasu (np. X godzin).

### 2. Monitorowanie konfliktów:
- Co określony interwał czasu Y system monitoruje konflikty rezerwacji, które zostały utworzone Z czasu temu(aby nie rozwiązywać konfliktów które pojawiają się w czasie rzeczywistym i są rozwiązywane przez Cassandrę).
- Konflikt występuje, gdy w tabeli `reservations_by_user` pojawią się dwa wpisy z tym samym `seat_id` (miejsce na spektaklu) dla tego samego `show_id`, co oznacza, że doszło do overbookingu.

### 3. Rozwiązywanie konfliktów:
- System identyfikuje wszystkie rezerwacje, które są częścią konfliktu, sprawdzając tabelę `reservations_by_user` na podstawie `seat_id` i `show_id`.
- System porównuje pole `reservation_time` z tabeli `reservation_info` (timestamp rezerwacji) dla konfliktujących rezerwacji, aby ustalić, która rezerwacja jest wcześniejsza.
- Rezerwacja z najwcześniejszym `reservation_time` uznawana jest za wczesniejszą, a jej konfliktujące miejsca są **potwierdzane**.
- W przypadku konfliktu pózniejsza rezerwacja jest anulowana, co oznacza wycofanie rezerwacji dla wszystkich miejsc.
- **Aktualizacja tabeli `seats_by_show`**: Zmiana statusu miejsc po potwierdzeniu rezerwacji.
- **PYTANIE** Czy TIMESTAMP muszą być tworzone ręcznie jako nowe pola, czy Cassandra udostępnia mechanizm TIMESTAMPów domyślnie?

### 4. Potwierdzenie rezerwacji:
- Po rozwiązaniu konfliktów, system wysyła powiadomienie do klienta o pomyślnym zakupie biletów dla potwierdzonych miejsc.
- Klient otrzymuje także informację o anulowaniu rezerwacji w przypadku konfliktu.

## Założenia:
- **Timestamp w tabeli `reservations_info`**: Każda rezerwacja posiada unikalny `reservation_time`, który jest wykorzystywany do rozwiązywania konfliktów.
- **Brak wsparcia dla zmian w rezerwacjach**: System nie wspiera zmiany dokonanych rezerwacji ani ich anulowania.
- **Brak zmian w tabelach**: Konflikty są rozwiązane na podstawie porównania timestampów (`reservation_time`), ale rezerwacje nie mogą być zmieniane ani usuwane po ich zapisaniu.

## Implementacja w tabelach:

### 1. Tabela `seats_by_show`:
- **Dodatkowe informacje o statusie miejsc**:
  - `status` (values: `available`, `reserved`, `sold`).
- Każde miejsce, które zostanie zarezerwowane, zmienia swój status na `reserved`.
- W momencie potwierdzenia zakupu, zmienia się na `sold`.

- ZMIANA: Ograniczennie przregladania tabeli z uzyciem CZAS w celu nie przegladania calej tabeli, przemyslec cache aplikacji, watek per show na tabeli 3.
