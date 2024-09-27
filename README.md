# Informační systémy (IIS) - Zvířecí útulek 🐻‍❄️

>Zadání není finální.

Úkolem zadání je vytvořit jednoduchý informační systém pro evidenci opuštěných zvířat zvířecím útulkem (např. králíků, koček nebo psů) a možnost jejich zapůjčení a venčení dobrovolníky.

Každé zvíře je identifikováno jménem, druhem a dalšími vhodně zvolenými atributy (např. věk, fotky, případně se inspirujte např. popisem zvířat pana Zdeňka Srstky, apod.). Zvíře má dále svoji historii (např. informace o nalezení) a evidenci svého zdravotního stavu (např. informace o očkování) a průběžných prohlídkách veterinářem. Zvíře je možné přidat do rozvrhu pro možné venčení.

Ověření dobrovolníci mohou tyto zvířata vyhledávat a provádět rezervace pro jejich zapůjčení dle volných termínů v rozvrhu.

---

>Konkrétně budou v systému vystupovat následující role:

#### *Administrátor:*
- Spravuje uživatele, jako jediný vytváří pečovatele a veterináře.

#### *Pečovatel:*
- Spravuje zvířata, vede jejich evidenci.
- Vytváří rozvrhy pro venčení.
- Ověřuje dobrovolníky.
- Schvaluje rezervace zvířat na venčení, eviduje zapůjčení a vrácení.
- Vytváří požadavky na veterináře.

#### *Veterinář:*
- Vyřizuje požadavky od pečovatele (plánuje vyšetření zvířat dle požadavků).
- Udržuje zdravotní záznamy zvířat.

#### *Dobrovolník:*
- Rezervuje zvířata na venčení.
- Vidí historii svých venčení.

#### *Neregistrovaný uživatel:*
- Prochází informace o útulku a zvířatech.

---

### Náměty na možná rozšíření:
- Sestavování plánu pro medikaci léků zvířatům.
- Dle vlastní fantazie, popište v dokumentaci…

## Rozjetí projektu
Vyzkoušeno na Windows 11, jelikož na WSLku nelze rozjet Apache (ani jiný) web server.

### Postup
1. Stažení XAMPP: https://sourceforge.net/projects/xampp/files/XAMPP%20Windows/8.1.25/xampp-windows-x64-8.1.25-0-VS16-installer.exe
2. Stažení Composer: https://getcomposer.org/Composer-Setup.exe

3. Naklonování repa:
```
git clone https://github.com/Dandys3900/IIS-Project.git .
```
4. Vlézt do adresáře `./code`
5. Instalace projektových závislostí:
```
composer install
npm install
```
6. Spuštění serveru:
```
php artisan serve
```

---

### Hosting projektu
Projekt je hostován na platformě InfinityFree.

#### URL: `http://vutfitissproject.kesug.com`

MySQL databáze je hostována na platformě Aiven, konfigurační detaily a přihlašovací údaje jsou uloženy v `/code/.env`:

* URL: `mysql://avnadmin:AVNS_nKlEyXmnpYpTucczgnZ@mysql-1eeb8483-iisproject2024.g.. aivencloud.com:17370/defaultdb?ssl-mode=REQUIRED`
* DB name: `defaultdb`
* Host: `mysql-1eeb8483-iisproject2024.g.aivencloud.com`
* Port: `17370`
* User: `avnadmin`
* Password: `AVNS_nKlEyXmnpYpTucczgnZ`

## Vzdálený přístup k databázi
Ověřeno a funknční s nástrojem [MySQL WorkBench](https://dev.mysql.com/downloads/workbench/).

Postup připojení:

1. Přejít na `Database -> Connect to Database`
2. Vyplnit přihlašovací údaje:
    * Host: `mysql-1eeb8483-iisproject2024.g.aivencloud.com`
    * Port: `17370`
    * User: `avnadmin`
3. Přejít do `SSL` tabu a pro `SSL CA file` vybrat certifikát, který se nachází v projektovém repositáři `/code/storage/app/certs/ca.pem`
