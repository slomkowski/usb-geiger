# Licznik Geigera USB

2013 Michał Słomkowski

Licencja GNU GPL wersja 3.0.

Repozytorium główne projektu prostego licznika Geigera na USB opartego o czujnik STS-5, ATTiny24 i oprogramowanie hosta napisane w Pythonie.

~~Wyniki mogą być publikowane w serwisie xively.com~~, wysyłane do pliku CSV (który można zaimportować do Excela), bazy MySQLa lub e-mailem do zdefiniowanych osób, jeżeli poziom promieniowania przekroczy bezpieczny poziom.

Szczegółowy opis licznika opublikowano w *Elektronice dla Wszystkich* 10/2013, artykuł jest [dostępny online](https://serwis.avt.pl/manuals/AVT3074.pdf).

Repozytorium zawiera:
* *datasheets* - noty katalogowe podzespołów wykorzystywanych w projekcie, szczególnie detektora STS-5,
* *firmare* - kod źródłowy firmware dla ATTiny24 napisany w C,
* *host/geiger-controller* - prosty program w C++ do odczytywania danych i zapisywania ustawień do urządzenia,
* *host/geiger-manager* - główny program do obsługi urządzenia napisany w Pythonie. Regularnie odczytuje pomiary z urządzenia i wysyła je do serwisu xively.com, bazy MySQL, e-mail lub pliku CSV, w zależności od konfiguracji,
* *pcb* - wzór płytki drukowanej w programie Eagle, schemat w PNG i lustrzany obraz płytki w PDF do termotransferu.
