USB Geiger counter
==================

2013 Michał Słomkowski

Licencja GNU GPL wersja 3.0.

Repozytorium główne projektu prostego licznika Geigera na USB opartego o czujnik STS-5, ATTiny24 i oprogramowanie hosta napisane w Pythonie.

Wyniki mogą być publikowane w serwisie cosm.com, wysyłane do pliku CSV (który można zaimportować do Excela) lub do bazy MySQL.

Wykresy natężenia promieniowania dostępne pod:
https://cosm.com/feeds/120299

Repozytorium zawiera:
* *datasheets* - noty katalogowe podzespołów wykorzystywanych w projekcie, szczególnie detektora STS-5,
* *firmare* - kod źródłowy firmware dla ATTiny24 napisany w C,
* *host/geiger-controller* - prosty program w C++ do odczytywania danych i zapisywania ustawień do urządzenia,
* *host/geiger-manager* - główny program do obsługi urządzenia napisany w Pythonie. Regularnie odczytuje pomiary z urządzenia i wysyła je do serwisu cosm.com, bazy MySQL lub pliku CSV, w zależności od konfiguracji,
* *pcb* - wzór płytki drukowanej w programie Eagle, schemat w PNG i lustrzany obraz płytki w PDF do termotransferu.
