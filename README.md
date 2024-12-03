### Założenia systemu biletowego:

1. System obsługuje wiele teatrów.
2. Każdy teatr ma różne spektakle, daty i godziny.
3. Każdy spektakl ma przypisane miejsca (np. sektor, rząd, miejsce).
4. Użytkownik może rezerwować bilety, a status miejsca musi się zmieniać.

### Schemat bazy danych:

### 1. **Tabela spektakli (`shows_by_theater`)**

Trzyma informacje o spektaklach w danym teatrze.

| **Kolumna**     | **Typ**                                               | **Opis**                         |
| --------------- | ----------------------------------------------------- | -------------------------------- |
| `theater_id`    | `UUID`                                                | Unikalny identyfikator teatru    |
| `show_id`       | `UUID`                                                | Unikalny identyfikator spektaklu |
| `show_date`     | `DATE`                                                | Data spektaklu                   |
| `show_time`     | `TIME`                                                | Godzina spektaklu                |
| `title`         | `TEXT`                                                | Tytuł spektaklu                  |
| **PRIMARY KEY** | ((`theater_id`), `show_date`, `show_time`, `show_id`) |                                  |

- Klucz sortujący to `show_date`, `show_time` dla szybkich odczytów po dacie i godzinie.

---

### 2. **Tabela miejsc w spektaklu (`seats_by_show`)**

Śledzi dostępność miejsc dla konkretnego spektaklu.

| **Kolumna**        | **Typ**                | **Opis**                             |
| ------------------ | ---------------------- | ------------------------------------ |
| `show_id`          | `UUID`                 | Unikalny identyfikator spektaklu     |
| `seat_id`          | `TEXT`                 | Identyfikator miejsca (np. A1, B2)   |
| `section`          | `TEXT`                 | Sekcja miejsca (np. balkon, parter)  |
| `row`              | `TEXT`                 | Rząd miejsca                         |
| `seat_number`      | `INT`                  | Numer miejsca                        |
| `status`           | `TEXT`                 | Status (available, reserved, sold)   |
| `user_id`          | `UUID`                 | Id użytkownika (dla zarezerwowanych) |
| `reservation_time` | `TIMESTAMP`            | Czas rezerwacji                      |
| **PRIMARY KEY**    | (`show_id`, `seat_id`) |                                      |

- Kolumna `status` pozwala na zarządzanie dostępnością miejsc.

---

### 3. **Tabela rezerwacji użytkownika (`reservations_by_user`)**

Przechowuje listę rezerwacji użytkownika.

| **Kolumna**        | **Typ**                       | **Opis**                  |
| ------------------ | ----------------------------- | ------------------------- |
| `user_id`          | `UUID`                        | Identyfikator użytkownika |
| `reservation_id`   | `UUID`                        | Identyfikator rezerwacji  |
| `show_id`          | `UUID`                        | Id spektaklu              |
| `seat_id`          | `TEXT`                        | Id miejsca                |
| `reservation_time` | `TIMESTAMP`                   | Czas rezerwacji           |
| **PRIMARY KEY**    | (`user_id`, `reservation_id`) |                           |

---

### Testowanie:

1. Przeprowadzenie masowych rezerwacji na pojedyncze spektakle z wielu lokalizacji i zliczanie niespójności(overbooking)
